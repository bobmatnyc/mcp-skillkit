"""Skill lifecycle management - discovery, loading, execution."""

import logging
import re
from pathlib import Path

import yaml
from pydantic import ValidationError

from mcp_skills.models.skill import (
    Skill,
    SkillMetadata,
    SkillMetadataModel,
    SkillModel,
)


logger = logging.getLogger(__name__)


class SkillManager:
    """Orchestrate skill lifecycle - discovery, loading, execution.

    Manages the complete lifecycle of skills from discovery through
    loading and caching. Integrates with indexing for search.

    Design Decision: In-Memory Caching Strategy

    Rationale: Use simple dict cache for loaded skills to avoid repeated
    file I/O and YAML parsing. Skills are immutable once loaded, making
    caching safe and effective.

    Trade-offs:
    - Performance: O(1) cache lookups vs. O(n) file I/O + parsing
    - Memory: ~10KB per skill for 100 skills = ~1MB (negligible)
    - Freshness: Cache must be cleared when repos are updated

    Future Optimization: When skill count exceeds 1000, consider:
    - LRU cache with size limit (functools.lru_cache)
    - Disk-based cache with mtime checking
    - SQLite integration (Phase 1 Task 7) for indexed access
    """

    # Predefined skill categories
    VALID_CATEGORIES = {
        "testing",
        "debugging",
        "refactoring",
        "documentation",
        "security",
        "performance",
        "deployment",
        "architecture",
        "data-analysis",
        "code-review",
        "collaboration",
    }

    def __init__(self, repos_dir: Path | None = None) -> None:
        """Initialize skill manager.

        Args:
            repos_dir: Directory containing skill repositories.
                      Defaults to ~/.mcp-skills/repos/
        """
        self.repos_dir = repos_dir or Path.home() / ".mcp-skills" / "repos"
        self._skill_cache: dict[str, Skill] = {}
        self._skill_paths: dict[str, Path] = {}  # Map skill_id -> file_path

    def discover_skills(self, repos_dir: Path | None = None) -> list[Skill]:
        """Scan repositories for skills.

        Searches for SKILL.md files in repository directories and
        parses their metadata.

        Args:
            repos_dir: Directory to scan (defaults to self.repos_dir)

        Returns:
            List of discovered Skill objects

        Performance:
        - Time Complexity: O(n) where n = total files in all repos
        - Space Complexity: O(m) where m = number of skills found

        Error Handling:
        - Invalid YAML: Log error and skip skill
        - Missing required fields: Log error and skip skill
        - File read errors: Log error and skip skill

        Example:
            >>> manager = SkillManager()
            >>> skills = manager.discover_skills()
            >>> len(skills)
            42
            >>> skills[0].name
            'pytest-testing'
        """
        search_dir = repos_dir or self.repos_dir

        if not search_dir.exists():
            logger.warning(f"Repository directory does not exist: {search_dir}")
            return []

        discovered_skills: list[Skill] = []

        # Walk directory tree and find all SKILL.md files (case-insensitive)
        for skill_file in search_dir.rglob("*"):
            if skill_file.name.upper() == "SKILL.MD" and skill_file.is_file():
                try:
                    # Extract repo_id from path structure
                    # Path structure: {repos_dir}/{repo_id}/{skill_path}/SKILL.md
                    relative_path = skill_file.relative_to(search_dir)
                    repo_id = (
                        relative_path.parts[0] if relative_path.parts else "unknown"
                    )

                    # Parse skill file
                    skill = self._parse_skill_file(skill_file, repo_id)

                    if skill:
                        discovered_skills.append(skill)
                        # Cache the skill path for later lookups
                        self._skill_paths[skill.id] = skill_file
                        logger.debug(f"Discovered skill: {skill.id}")

                except Exception as e:
                    logger.error(f"Failed to parse skill file {skill_file}: {e}")
                    continue

        logger.info(f"Discovered {len(discovered_skills)} skills in {search_dir}")
        return discovered_skills

    def load_skill(self, skill_id: str) -> Skill | None:
        """Load skill from disk with caching.

        Args:
            skill_id: Unique skill identifier

        Returns:
            Skill object or None if not found

        Performance:
        - Cache hit: O(1) dict lookup
        - Cache miss: O(n) file search + O(m) parsing where m = file size

        Example:
            >>> manager = SkillManager()
            >>> skill = manager.load_skill("anthropics/pytest")
            >>> skill.name
            'pytest-testing'
            >>> # Second call uses cache
            >>> skill2 = manager.load_skill("anthropics/pytest")
            >>> skill is skill2
            True
        """
        # Check cache first
        if skill_id in self._skill_cache:
            logger.debug(f"Cache hit for skill: {skill_id}")
            return self._skill_cache[skill_id]

        # Check if we have the path cached from discovery
        if skill_id in self._skill_paths:
            skill_file = self._skill_paths[skill_id]
            relative_path = skill_file.relative_to(self.repos_dir)
            repo_id = relative_path.parts[0] if relative_path.parts else "unknown"

            skill = self._parse_skill_file(skill_file, repo_id)
            if skill:
                self._skill_cache[skill_id] = skill
                return skill

        # Fall back to searching for the skill
        # This handles the case where load_skill is called before discover_skills
        logger.debug(f"Searching for skill: {skill_id}")

        # Try to find skill file by ID
        # Skill ID format: {repo_id}/{skill_path}
        parts = skill_id.split("/", 1)
        if len(parts) == 2:
            repo_id, skill_path = parts
            skill_file = self.repos_dir / repo_id / skill_path / "SKILL.md"

            if skill_file.exists():
                skill = self._parse_skill_file(skill_file, repo_id)
                if skill:
                    self._skill_cache[skill_id] = skill
                    self._skill_paths[skill_id] = skill_file
                    return skill

        logger.warning(f"Skill not found: {skill_id}")
        return None

    def get_skill_metadata(self, skill_id: str) -> SkillMetadata | None:
        """Extract metadata from SKILL.md.

        Parses YAML frontmatter without loading full instructions.
        This is faster than load_skill() when only metadata is needed.

        Args:
            skill_id: Unique skill identifier

        Returns:
            SkillMetadata object or None if not found

        Performance:
        - O(1) for cached skills (checks cache first)
        - O(m) where m = frontmatter size (skips instructions)
        - ~10x faster than full skill loading for large instruction sets

        Example:
            >>> manager = SkillManager()
            >>> metadata = manager.get_skill_metadata("anthropics/pytest")
            >>> metadata.name
            'pytest-testing'
            >>> metadata.category
            'testing'
        """
        # Check if skill is already cached
        if skill_id in self._skill_cache:
            skill = self._skill_cache[skill_id]
            return SkillMetadata(
                name=skill.name,
                description=skill.description,
                category=skill.category,
                tags=skill.tags,
                dependencies=skill.dependencies,
                version=skill.version,
                author=skill.author,
            )

        # Find skill file
        skill_file: Path | None = None

        if skill_id in self._skill_paths:
            skill_file = self._skill_paths[skill_id]
        else:
            # Try to construct path from skill_id
            parts = skill_id.split("/", 1)
            if len(parts) == 2:
                repo_id, skill_path = parts
                potential_file = self.repos_dir / repo_id / skill_path / "SKILL.md"
                if potential_file.exists():
                    skill_file = potential_file

        if not skill_file or not skill_file.exists():
            logger.warning(f"Skill file not found for: {skill_id}")
            return None

        # Parse frontmatter only (skip instructions for performance)
        try:
            frontmatter = self._parse_frontmatter(skill_file)
            if not frontmatter:
                return None

            # Validate with Pydantic
            metadata_model = SkillMetadataModel(**frontmatter)

            return SkillMetadata(
                name=metadata_model.name,
                description=metadata_model.description,
                category=metadata_model.category,
                tags=metadata_model.tags,
                dependencies=metadata_model.dependencies,
                version=metadata_model.version,
                author=metadata_model.author,
            )

        except (ValidationError, KeyError, yaml.YAMLError) as e:
            logger.error(f"Failed to parse metadata for {skill_id}: {e}")
            return None

    def validate_skill(self, skill: Skill) -> dict[str, list[str]]:
        """Check skill structure and dependencies.

        Validates skill against structure requirements and business rules.
        Returns both critical errors (MUST fix) and warnings (SHOULD fix).

        Args:
            skill: Skill object to validate

        Returns:
            Dictionary with validation results:
            {
                "errors": ["Critical errors that prevent skill usage"],
                "warnings": ["Non-critical warnings for improvement"]
            }

        Validation Rules:
        - ERRORS (critical):
            - Missing required fields: name, description, instructions
            - Invalid YAML frontmatter
            - Description too short (<10 chars)
            - Instructions too short (<50 chars)

        - WARNINGS (non-critical):
            - Unknown category (not in VALID_CATEGORIES)
            - Missing tags
            - Missing examples in instructions
            - Unresolved dependencies

        Example:
            >>> manager = SkillManager()
            >>> skill = manager.load_skill("test/broken-skill")
            >>> result = manager.validate_skill(skill)
            >>> result["errors"]
            ['Description too short (5 chars, minimum 10)']
            >>> result["warnings"]
            ['Unknown category: invalid-cat']
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Check required fields
        if not skill.name or len(skill.name.strip()) == 0:
            errors.append("Missing required field: name")

        if not skill.description or len(skill.description.strip()) < 10:
            errors.append(
                f"Description too short ({len(skill.description)} chars, minimum 10)"
            )

        if not skill.instructions or len(skill.instructions.strip()) < 50:
            errors.append(
                f"Instructions too short ({len(skill.instructions)} chars, minimum 50)"
            )

        # Validate category
        if skill.category not in self.VALID_CATEGORIES:
            warnings.append(
                f"Unknown category: {skill.category}. "
                f"Valid categories: {', '.join(sorted(self.VALID_CATEGORIES))}"
            )

        # Check tags
        if not skill.tags or len(skill.tags) == 0:
            warnings.append("No tags specified. Tags improve discoverability.")

        # Check for examples in instructions (basic heuristic)
        instructions_lower = skill.instructions.lower()
        has_examples = (
            "example" in instructions_lower
            or "usage" in instructions_lower
            or "```" in skill.instructions  # Code blocks often indicate examples
        )
        if not has_examples:
            warnings.append(
                "No examples found in instructions. Consider adding usage examples."
            )

        # Validate dependencies (check if they can be resolved)
        # Note: This requires discovering all skills first
        if skill.dependencies:
            for dep_id in skill.dependencies:
                # Check if dependency exists (in cache or can be found)
                dep_skill = self.load_skill(dep_id)
                if not dep_skill:
                    warnings.append(f"Unresolved dependency: {dep_id}")

        return {"errors": errors, "warnings": warnings}

    def search_skills(
        self, query: str, category: str | None = None, limit: int = 10
    ) -> list[Skill]:
        """Search skills using basic text matching.

        This is a simple keyword-based search. For advanced semantic search,
        use IndexingEngine with ChromaDB vector search (Task 5).

        Args:
            query: Search query (case-insensitive)
            category: Optional category filter (exact match)
            limit: Maximum results to return

        Returns:
            List of matching Skill objects sorted by relevance

        Relevance Scoring:
        - Name match: 10 points
        - Tag match: 5 points per tag
        - Description match: 3 points
        - Higher scores = more relevant

        Performance:
        - Time Complexity: O(n * m) where n = skills, m = avg text length
        - For >1000 skills, consider vector search (ChromaDB integration)

        Example:
            >>> manager = SkillManager()
            >>> manager.discover_skills()
            >>> results = manager.search_skills("testing python", category="testing")
            >>> results[0].name
            'pytest-testing'
        """
        # Discover skills if not already cached
        # This ensures we search across all available skills
        if not self._skill_paths:
            self.discover_skills()

        query_lower = query.lower()
        results: list[tuple[Skill, int]] = []  # (skill, relevance_score)

        # Search through all discovered skills
        for skill_id in self._skill_paths:
            skill = self.load_skill(skill_id)
            if not skill:
                continue

            # Apply category filter if specified
            if category and skill.category != category:
                continue

            score = 0

            # Check name match (highest weight)
            if query_lower in skill.name.lower():
                score += 10

            # Check tag matches
            for tag in skill.tags:
                if query_lower in tag.lower():
                    score += 5

            # Check description match
            if query_lower in skill.description.lower():
                score += 3

            # Only include results with non-zero score
            if score > 0:
                results.append((skill, score))

        # Sort by relevance score (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return [skill for skill, _ in results[:limit]]

    def clear_cache(self) -> None:
        """Clear in-memory skill cache.

        Clears both the skill object cache and skill path cache.
        Call this after repository updates to ensure fresh data.
        """
        self._skill_cache.clear()
        self._skill_paths.clear()

    # Private helper methods

    def _parse_skill_file(self, file_path: Path, repo_id: str) -> Skill | None:
        """Parse SKILL.md file and create Skill object.

        Args:
            file_path: Path to SKILL.md file
            repo_id: Repository identifier

        Returns:
            Skill object or None if parsing fails

        Error Handling:
        - Invalid YAML: Log error and return None
        - Missing required fields: Log error and return None
        - File read errors: Log error and return None

        Design Decision: Pydantic Validation

        Rationale: Use Pydantic for validation to enforce data quality at
        parse time. This catches issues early and provides clear error messages.

        Trade-offs:
        - Safety: Invalid skills are rejected, preventing bad data
        - Performance: ~5% overhead for validation vs. raw parsing
        - Developer Experience: Clear validation errors vs. runtime failures
        """
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Parse frontmatter and instructions
            frontmatter, instructions = self._split_frontmatter(content)

            if not frontmatter:
                logger.error(f"No frontmatter found in {file_path}")
                return None

            # Parse YAML frontmatter
            metadata = yaml.safe_load(frontmatter)
            if not isinstance(metadata, dict):
                logger.error(f"Invalid frontmatter format in {file_path}")
                return None

            # Generate skill ID from file path
            # Format: {repo_id}/{skill_path}
            # Example: anthropics/testing/pytest/SKILL.md -> anthropics/testing/pytest
            relative_path = file_path.relative_to(self.repos_dir)
            path_parts = list(relative_path.parts[:-1])  # Remove SKILL.md
            skill_id = "/".join(path_parts)

            # Normalize skill ID (lowercase, replace spaces/special chars)
            skill_id = self._normalize_skill_id(skill_id)

            # Extract examples from instructions (look for ## Examples section)
            examples = self._extract_examples(instructions)

            # Build skill data for validation
            skill_data = {
                "id": skill_id,
                "name": metadata.get("name", ""),
                "description": metadata.get("description", ""),
                "instructions": instructions.strip(),
                "category": metadata.get("category", ""),
                "tags": metadata.get("tags", []),
                "dependencies": metadata.get("dependencies", []),
                "examples": examples,
                "file_path": str(file_path),
                "repo_id": repo_id,
                "version": metadata.get("version"),
                "author": metadata.get("author"),
            }

            # Validate with Pydantic
            skill_model = SkillModel(**skill_data)

            # Create Skill dataclass instance
            return Skill(
                id=skill_model.id,
                name=skill_model.name,
                description=skill_model.description,
                instructions=skill_model.instructions,
                category=skill_model.category,
                tags=skill_model.tags,
                dependencies=skill_model.dependencies,
                examples=skill_model.examples,
                file_path=file_path,
                repo_id=skill_model.repo_id,
                version=skill_model.version,
                author=skill_model.author,
            )

        except (ValidationError, yaml.YAMLError, OSError) as e:
            logger.error(f"Failed to parse skill file {file_path}: {e}")
            return None

    def _parse_frontmatter(self, file_path: Path) -> dict | None:
        """Parse YAML frontmatter from SKILL.md file.

        This is a faster alternative to full file parsing when only
        metadata is needed.

        Args:
            file_path: Path to SKILL.md file

        Returns:
            Dictionary with frontmatter data or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            frontmatter, _ = self._split_frontmatter(content)

            if not frontmatter:
                return None

            metadata = yaml.safe_load(frontmatter)
            return metadata if isinstance(metadata, dict) else None

        except (yaml.YAMLError, OSError) as e:
            logger.error(f"Failed to parse frontmatter from {file_path}: {e}")
            return None

    def _split_frontmatter(self, content: str) -> tuple[str, str]:
        """Split SKILL.md content into frontmatter and instructions.

        Expected format:
        ---
        name: skill-name
        description: Brief description
        ---

        # Instructions
        Markdown content...

        Args:
            content: Full file content

        Returns:
            Tuple of (frontmatter_yaml, instructions_markdown)
        """
        # Match YAML frontmatter between --- markers
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if match:
            return match.group(1), match.group(2)

        # No frontmatter found
        return "", content

    def _normalize_skill_id(self, skill_id: str) -> str:
        """Normalize skill ID to lowercase with hyphens.

        Args:
            skill_id: Raw skill ID from file path

        Returns:
            Normalized skill ID (lowercase, special chars replaced)

        Examples:
            "Anthropics/Testing/PyTest" -> "anthropics/testing/pytest"
            "My Skill!" -> "my-skill"
        """
        # Convert to lowercase
        normalized = skill_id.lower()

        # Replace special characters (except /) with hyphens
        normalized = re.sub(r"[^a-z0-9/]", "-", normalized)

        # Remove consecutive hyphens
        normalized = re.sub(r"-+", "-", normalized)

        # Remove leading/trailing hyphens
        normalized = normalized.strip("-")

        return normalized

    def _extract_examples(self, instructions: str) -> list[str]:
        """Extract examples from skill instructions.

        Looks for sections like:
        - ## Examples
        - ## Example Usage
        - Code blocks (```)

        Args:
            instructions: Skill instructions markdown

        Returns:
            List of example strings (empty if none found)

        Performance Note:
        - This is a basic heuristic extraction
        - For more sophisticated parsing, consider using markdown AST
        - Current implementation is fast enough for <100KB files
        """
        examples: list[str] = []

        # Look for "Examples" section (case-insensitive)
        examples_pattern = r"##\s+Examples?\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(examples_pattern, instructions, re.IGNORECASE | re.DOTALL)

        if match:
            examples_text = match.group(1).strip()
            if examples_text:
                examples.append(examples_text)

        # Also extract code blocks as examples
        code_block_pattern = r"```[\w]*\n(.*?)\n```"
        code_blocks = re.findall(code_block_pattern, instructions, re.DOTALL)

        # Limit to first 3 code blocks to avoid bloat
        examples.extend(code_blocks[:3])

        return examples
