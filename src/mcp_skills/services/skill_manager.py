"""Skill lifecycle management - discovery, loading, execution."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SkillMetadata:
    """Skill metadata from YAML frontmatter.

    Attributes:
        name: Skill name
        description: Short description
        category: Skill category (testing, debugging, refactoring, etc.)
        tags: List of tags for categorization
        dependencies: List of skill IDs this skill depends on
    """

    name: str
    description: str
    category: str
    tags: list[str]
    dependencies: list[str]


@dataclass
class Skill:
    """Complete skill data model.

    Attributes:
        id: Unique skill identifier
        name: Skill name
        description: Short description
        instructions: Full skill instructions (markdown)
        category: Skill category
        tags: List of tags
        dependencies: List of skill IDs this depends on
        examples: List of example usage scenarios
        file_path: Path to SKILL.md file
        repo_id: Repository this skill belongs to
    """

    id: str
    name: str
    description: str
    instructions: str
    category: str
    tags: list[str]
    dependencies: list[str]
    examples: list[str]
    file_path: Path
    repo_id: str


class SkillManager:
    """Orchestrate skill lifecycle - discovery, loading, execution.

    Manages the complete lifecycle of skills from discovery through
    loading and caching. Integrates with indexing for search.
    """

    def __init__(self, repos_dir: Optional[Path] = None) -> None:
        """Initialize skill manager.

        Args:
            repos_dir: Directory containing skill repositories.
                      Defaults to ~/.mcp-skills/repos/
        """
        self.repos_dir = repos_dir or Path.home() / ".mcp-skills" / "repos"
        self._skill_cache: dict[str, Skill] = {}

    def discover_skills(self, repos_dir: Optional[Path] = None) -> list[Skill]:
        """Scan repositories for skills.

        Searches for SKILL.md files in repository directories and
        parses their metadata.

        Args:
            repos_dir: Directory to scan (defaults to self.repos_dir)

        Returns:
            List of discovered Skill objects
        """
        # TODO: Implement skill discovery
        # 1. Walk repository directories
        # 2. Find all SKILL.md files
        # 3. Parse each file (frontmatter + content)
        # 4. Create Skill objects
        # 5. Return list

        return []

    def load_skill(self, skill_id: str) -> Optional[Skill]:
        """Load skill from disk with caching.

        Args:
            skill_id: Unique skill identifier

        Returns:
            Skill object or None if not found
        """
        # Check cache first
        if skill_id in self._skill_cache:
            return self._skill_cache[skill_id]

        # TODO: Implement skill loading
        # 1. Query database for skill file path
        # 2. Read and parse SKILL.md
        # 3. Create Skill object
        # 4. Cache in memory
        # 5. Return skill

        return None

    def get_skill_metadata(self, skill_id: str) -> Optional[SkillMetadata]:
        """Extract metadata from SKILL.md.

        Parses YAML frontmatter without loading full instructions.

        Args:
            skill_id: Unique skill identifier

        Returns:
            SkillMetadata object or None if not found
        """
        # TODO: Implement metadata extraction
        # 1. Find skill file
        # 2. Parse frontmatter only (don't load full content)
        # 3. Create SkillMetadata object
        # 4. Return metadata

        return None

    def validate_skill(self, skill: Skill) -> dict[str, list[str]]:
        """Check skill structure and dependencies.

        Args:
            skill: Skill object to validate

        Returns:
            Dictionary with validation results:
            {
                "errors": ["Critical errors"],
                "warnings": ["Non-critical warnings"]
            }
        """
        errors: list[str] = []
        warnings: list[str] = []

        # TODO: Implement skill validation
        # 1. Check required fields (name, description, instructions)
        # 2. Validate category against known categories
        # 3. Check dependency resolution
        # 4. Validate markdown syntax
        # 5. Check for required sections in instructions

        return {"errors": errors, "warnings": warnings}

    def search_skills(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> list[Skill]:
        """Search skills using basic text matching.

        For advanced search, use IndexingEngine with vector + KG.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results to return

        Returns:
            List of matching Skill objects
        """
        # TODO: Implement basic search
        # This is a simple text search - IndexingEngine provides
        # advanced semantic search with vector + KG

        return []

    def clear_cache(self) -> None:
        """Clear in-memory skill cache."""
        self._skill_cache.clear()
