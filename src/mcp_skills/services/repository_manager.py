"""Git repository management for skills repositories."""

import json
import logging
import os
import re
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import git


logger = logging.getLogger(__name__)


@dataclass
class Repository:
    """Repository metadata.

    Attributes:
        id: Unique repository identifier
        url: Git repository URL
        local_path: Path to local clone
        priority: Priority for skill selection (higher = preferred)
        last_updated: Timestamp of last update
        skill_count: Number of skills in repository
        license: Repository license (MIT, Apache-2.0, etc.)
    """

    id: str
    url: str
    local_path: Path
    priority: int
    last_updated: datetime
    skill_count: int
    license: str

    def to_dict(self) -> dict[str, Any]:
        """Convert Repository to dictionary for JSON serialization.

        Returns:
            Dictionary with all fields, Path and datetime converted to strings
        """
        data = asdict(self)
        data["local_path"] = str(self.local_path)
        data["last_updated"] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Repository":
        """Create Repository from dictionary loaded from JSON.

        Args:
            data: Dictionary with repository fields

        Returns:
            Repository instance
        """
        return cls(
            id=data["id"],
            url=data["url"],
            local_path=Path(data["local_path"]),
            priority=data["priority"],
            last_updated=datetime.fromisoformat(data["last_updated"]),
            skill_count=data["skill_count"],
            license=data["license"],
        )


class RepositoryManager:
    """Manage git-based skills repositories.

    Handles cloning, updating, and tracking multiple skill repositories.
    Supports prioritization for resolving conflicts between repositories.
    """

    # Default repositories to clone on setup
    DEFAULT_REPOS = [
        {
            "url": "https://github.com/anthropics/skills.git",
            "priority": 100,
            "license": "Apache-2.0",
        },
        {
            "url": "https://github.com/obra/superpowers.git",
            "priority": 90,
            "license": "MIT",
        },
        {
            "url": "https://github.com/bobmatnyc/claude-mpm-skills.git",
            "priority": 80,
            "license": "MIT",
        },
    ]

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        """Initialize repository manager.

        Args:
            base_dir: Base directory for storing repositories.
                     Defaults to ~/.mcp-skills/repos/
        """
        self.base_dir = base_dir or Path.home() / ".mcp-skills" / "repos"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir.parent / "repos.json"

    def add_repository(
        self, url: str, priority: int = 0, license: str = "Unknown"
    ) -> Repository:
        """Clone new repository.

        Args:
            url: Git repository URL
            priority: Priority for skill selection (0-100)
            license: Repository license (default: "Unknown")

        Returns:
            Repository metadata object

        Raises:
            ValueError: If URL is invalid or repository already exists

        Design Decision: Git Clone Strategy

        Rationale: Using GitPython's clone_from() for simplicity and Python integration.
        Direct subprocess calls would require manual error handling and platform-specific
        git binary management. GitPython provides consistent cross-platform behavior.

        Trade-offs:
        - Simplicity: GitPython handles git binary detection and error wrapping
        - Performance: Slightly slower than subprocess (~5-10% overhead for small repos)
        - Dependency: Requires GitPython library, but already in project dependencies

        Error Handling:
        - InvalidGitRepositoryError: URL is not a valid git repository
        - GitCommandError: Clone operation failed (network, permissions, etc.)
        - ValueError: Invalid priority range or duplicate repository
        """
        # 1. Validate URL
        if not self._is_valid_git_url(url):
            raise ValueError(f"Invalid git URL: {url}")

        # 2. Validate priority range
        if not 0 <= priority <= 100:
            raise ValueError(f"Priority must be between 0-100, got {priority}")

        # 3. Generate repository ID from URL
        repo_id = self._generate_repo_id(url)

        # 4. Check if already exists
        existing = self.get_repository(repo_id)
        if existing:
            raise ValueError(
                f"Repository already exists: {repo_id} at {existing.local_path}"
            )

        # 5. Clone repository using GitPython
        local_path = self.base_dir / repo_id
        logger.info(f"Cloning repository {url} to {local_path}")

        try:
            git.Repo.clone_from(url, local_path, depth=1)
        except git.exc.GitCommandError as e:
            raise ValueError(f"Failed to clone repository {url}: {e}") from e

        # 6. Scan for skills
        skill_count = self._count_skills(local_path)
        logger.info(f"Found {skill_count} skills in {repo_id}")

        # 7. Create Repository object
        repository = Repository(
            id=repo_id,
            url=url,
            local_path=local_path,
            priority=priority,
            last_updated=datetime.now(timezone.utc),
            skill_count=skill_count,
            license=license,
        )

        # 8. Store metadata
        self._save_repository(repository)

        return repository

    def update_repository(self, repo_id: str) -> Repository:
        """Pull latest changes from repository.

        Args:
            repo_id: Repository identifier

        Returns:
            Updated repository metadata

        Raises:
            ValueError: If repository not found

        Error Handling:
        - ValueError: Repository not found in metadata
        - GitCommandError: Pull operation failed (network, conflicts, etc.)
        - InvalidGitRepositoryError: Local clone is corrupted

        Recovery Strategy:
        - Pull failures are propagated to caller for explicit handling
        - Consider re-cloning if local repository is corrupted
        - No automatic conflict resolution (user must handle manually)
        """
        # 1. Find repository by ID
        repository = self.get_repository(repo_id)
        if not repository:
            raise ValueError(f"Repository not found: {repo_id}")

        # 2. Git pull latest changes
        logger.info(f"Updating repository {repo_id} from {repository.url}")

        try:
            repo = git.Repo(repository.local_path)
            origin = repo.remotes.origin
            origin.pull()
        except git.exc.InvalidGitRepositoryError as e:
            raise ValueError(
                f"Local repository is corrupted: {repository.local_path}. "
                f"Consider removing and re-cloning: {e}"
            ) from e
        except git.exc.GitCommandError as e:
            raise ValueError(f"Failed to update repository {repo_id}: {e}") from e

        # 3. Rescan for new/updated skills
        skill_count = self._count_skills(repository.local_path)
        logger.info(f"Rescanned {repo_id}: {skill_count} skills found")

        # 4. Update metadata
        repository.last_updated = datetime.now(timezone.utc)
        repository.skill_count = skill_count

        # 5. Save updated metadata
        self._update_repository_metadata(repository)

        return repository

    def list_repositories(self) -> list[Repository]:
        """List all configured repositories.

        Returns:
            List of Repository objects sorted by priority (highest first)

        Performance Note:
        - Time Complexity: O(n log n) due to sorting
        - Space Complexity: O(n) for loading all repositories

        For current scale (~3-10 repos), this is negligible. If repository count
        exceeds 100, consider:
        - Lazy loading with pagination
        - Maintaining sorted index in JSON
        - Moving to SQLite with indexed queries (planned for Phase 1 Task 7)
        """
        repositories = self._load_all_repositories()

        # Sort by priority descending (highest priority first)
        repositories.sort(key=lambda r: r.priority, reverse=True)

        return repositories

    def remove_repository(self, repo_id: str) -> None:
        """Remove repository and its skills.

        Args:
            repo_id: Repository identifier to remove

        Raises:
            ValueError: If repository not found

        Error Handling:
        - ValueError: Repository not found in metadata
        - OSError: File deletion failed (permissions, locked files)

        Data Consistency:
        - Metadata is removed atomically with temp file strategy
        - If directory deletion fails after metadata removal, directory is orphaned
        - Future enhancement: Two-phase commit for atomic operation

        Failure Recovery:
        - Orphaned directories can be manually deleted from base_dir
        - Re-running remove will fail (metadata already gone) but directory remains
        - Consider: Mark as deleted in metadata, then cleanup in background
        """
        # 1. Find repository by ID
        repository = self.get_repository(repo_id)
        if not repository:
            raise ValueError(f"Repository not found: {repo_id}")

        logger.info(f"Removing repository {repo_id} from {repository.local_path}")

        # 2. Delete local clone
        try:
            if repository.local_path.exists():
                shutil.rmtree(repository.local_path)
                logger.info(f"Deleted local clone at {repository.local_path}")
        except OSError as e:
            logger.error(f"Failed to delete repository directory: {e}")
            raise ValueError(
                f"Failed to delete repository directory {repository.local_path}: {e}"
            ) from e

        # 3. Remove from metadata storage
        # Note: Skill index removal will be handled by SkillManager (Task 4)
        # and ChromaDB integration (Task 5) in later phases
        self._delete_repository_metadata(repo_id)

    def get_repository(self, repo_id: str) -> Optional[Repository]:
        """Get repository by ID.

        Args:
            repo_id: Repository identifier

        Returns:
            Repository object or None if not found

        Performance:
        - Time Complexity: O(n) linear scan of all repositories
        - For current scale (3-10 repos), this is <1ms

        Optimization Opportunity:
        - If repo count >100, consider in-memory dict cache
        - SQLite migration (Task 7) will provide O(1) indexed lookup
        """
        repositories = self._load_all_repositories()

        for repo in repositories:
            if repo.id == repo_id:
                return repo

        return None

    # Private helper methods

    def _is_valid_git_url(self, url: str) -> bool:
        """Validate git repository URL format.

        Args:
            url: URL to validate

        Returns:
            True if URL appears to be a valid git repository URL

        Supported Formats:
        - HTTPS: https://github.com/user/repo.git
        - SSH: git@github.com:user/repo.git
        - Git protocol: git://github.com/user/repo.git

        Note: This is basic format validation, not network reachability check.
        Actual repository validity is tested during clone operation.
        """
        if not url:
            return False

        # HTTPS URLs
        if url.startswith("https://") or url.startswith("http://"):
            try:
                parsed = urlparse(url)
                # Must have scheme, netloc, and path
                return bool(parsed.scheme and parsed.netloc and parsed.path)
            except Exception:
                return False

        # SSH URLs (git@host:path/to/repo.git)
        if url.startswith("git@"):
            # Basic validation: must contain colon separator
            return ":" in url

        # Git protocol URLs
        if url.startswith("git://"):
            return True

        return False

    def _generate_repo_id(self, url: str) -> str:
        """Generate repository ID from URL.

        Args:
            url: Git repository URL

        Returns:
            Repository ID in format "owner/repo" or "hostname/owner/repo"

        Examples:
            "https://github.com/anthropics/skills.git" -> "anthropics/skills"
            "git@github.com:obra/superpowers.git" -> "obra/superpowers"
            "https://gitlab.com/group/subgroup/project.git" -> "group/subgroup/project"

        Design Decision: ID Format

        Rationale: Use path-based IDs that preserve repository identity across
        different clone URLs (HTTPS vs SSH). This allows identifying duplicates
        when users add same repo with different URL formats.

        Trade-offs:
        - Uniqueness: Path-based IDs work for GitHub/GitLab style URLs
        - Collisions: Rare, but possible for self-hosted repos with same path
        - Readability: IDs are human-readable and match repo names
        """
        # Remove .git suffix if present
        clean_url = url.rstrip("/")
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]

        # Handle SSH URLs (git@host:path)
        if url.startswith("git@"):
            # Extract path after colon
            if ":" in clean_url:
                path = clean_url.split(":", 1)[1]
                return path.strip("/")

        # Handle HTTPS/HTTP/Git URLs
        try:
            parsed = urlparse(clean_url)
            # Extract path without leading slash
            path = parsed.path.lstrip("/")
            return path
        except Exception:
            # Fallback: use sanitized URL as ID
            return re.sub(r"[^a-zA-Z0-9_-]", "_", clean_url)

    def _count_skills(self, repo_path: Path) -> int:
        """Count SKILL.md files in repository.

        Args:
            repo_path: Path to repository root

        Returns:
            Number of skill files found

        Performance:
        - Time Complexity: O(n) where n = total files in repo
        - Optimization: Could cache results and only rescan changed files

        Future Enhancement:
        - Use watchdog for incremental updates
        - Store skill metadata during scan for faster access
        """
        skill_files = list(repo_path.rglob("SKILL.md"))
        return len(skill_files)

    def _load_all_repositories(self) -> list[Repository]:
        """Load all repositories from JSON metadata file.

        Returns:
            List of Repository objects (empty list if file doesn't exist)

        Error Handling:
        - Missing file: Returns empty list (no repositories configured)
        - Corrupt JSON: Logs error and returns empty list
        - Invalid data: Logs error and skips malformed entries
        """
        if not self.metadata_file.exists():
            return []

        try:
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
                repositories = []

                for repo_data in data.get("repositories", []):
                    try:
                        repo = Repository.from_dict(repo_data)
                        repositories.append(repo)
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping malformed repository entry: {e}")

                return repositories

        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load repository metadata: {e}")
            return []

    def _save_repository(self, repository: Repository) -> None:
        """Save new repository to metadata file.

        Args:
            repository: Repository to add to metadata

        Design Decision: Atomic File Updates

        Rationale: Use temp file + rename for atomic updates to prevent corruption
        if process crashes during write. POSIX rename() is atomic, ensuring
        metadata is never in half-written state.

        Trade-offs:
        - Safety: Prevents corruption at cost of extra disk I/O
        - Performance: Negligible for small files (<100KB)
        - Complexity: Requires temp file handling

        Error Handling:
        - Write errors: Temp file is not renamed, original preserved
        - Rename errors: Rare, but original file remains unchanged
        """
        repositories = self._load_all_repositories()
        repositories.append(repository)
        self._write_metadata(repositories)

    def _update_repository_metadata(self, repository: Repository) -> None:
        """Update existing repository in metadata file.

        Args:
            repository: Repository with updated metadata

        Note: This replaces the repository entry with matching ID
        """
        repositories = self._load_all_repositories()

        # Replace repository with matching ID
        for i, repo in enumerate(repositories):
            if repo.id == repository.id:
                repositories[i] = repository
                break

        self._write_metadata(repositories)

    def _delete_repository_metadata(self, repo_id: str) -> None:
        """Remove repository from metadata file.

        Args:
            repo_id: ID of repository to remove
        """
        repositories = self._load_all_repositories()

        # Filter out repository with matching ID
        repositories = [repo for repo in repositories if repo.id != repo_id]

        self._write_metadata(repositories)

    def _write_metadata(self, repositories: list[Repository]) -> None:
        """Write repository list to metadata file atomically.

        Args:
            repositories: List of all repositories to persist

        Atomic Write Strategy:
        1. Write to temporary file in same directory
        2. Rename temp file over original (atomic operation on POSIX)
        3. This ensures metadata is never corrupted by partial writes
        """
        # Ensure parent directory exists
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert repositories to dict format
        data = {"repositories": [repo.to_dict() for repo in repositories]}

        # Write to temp file, then atomic rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.metadata_file.parent, prefix=".repos_", suffix=".json.tmp"
        )

        try:
            with os.fdopen(temp_fd, "w") as f:
                json.dump(data, f, indent=2)

            # Atomic rename (POSIX guarantees atomicity)
            os.replace(temp_path, self.metadata_file)

        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
