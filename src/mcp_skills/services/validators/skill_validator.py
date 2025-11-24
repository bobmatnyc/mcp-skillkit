"""Validator for skill files and data structures."""

import logging
import re
from collections.abc import Callable
from pathlib import Path

import yaml

from mcp_skills.models.skill import Skill


logger = logging.getLogger(__name__)


class SkillValidator:
    """Validator for skill files and data structures.

    Handles all validation logic for skills including:
    - File format validation (YAML frontmatter)
    - Required field validation
    - Content length validation
    - Category validation
    - Format validation (skill IDs, paths)
    - Business rule validation
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
            - Unresolved dependencies (requires dependency_resolver callback)

        Example:
            >>> validator = SkillValidator()
            >>> result = validator.validate_skill(skill)
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

        return {"errors": errors, "warnings": warnings}

    def validate_skill_with_dependencies(
        self, skill: Skill, dependency_resolver: Callable[[str], Skill | None]
    ) -> dict[str, list[str]]:
        """Validate skill including dependency resolution.

        This is a separate method to avoid circular dependencies between
        SkillValidator and SkillManager.

        Args:
            skill: Skill object to validate
            dependency_resolver: Callable that takes a skill_id and returns a Skill or None

        Returns:
            Dictionary with validation results including dependency warnings
        """
        result = self.validate_skill(skill)

        # Validate dependencies (check if they can be resolved)
        if skill.dependencies:
            for dep_id in skill.dependencies:
                # Check if dependency exists using the provided resolver
                dep_skill = dependency_resolver(dep_id)
                if not dep_skill:
                    result["warnings"].append(f"Unresolved dependency: {dep_id}")

        return result

    def split_frontmatter(self, content: str) -> tuple[str, str]:
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

    def parse_frontmatter(self, file_path: Path) -> dict | None:
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
            frontmatter, _ = self.split_frontmatter(content)

            if not frontmatter:
                return None

            metadata = yaml.safe_load(frontmatter)
            return metadata if isinstance(metadata, dict) else None

        except (yaml.YAMLError, OSError) as e:
            logger.error(f"Failed to parse frontmatter from {file_path}: {e}")
            return None

    def normalize_skill_id(self, skill_id: str) -> str:
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

    def extract_examples(self, instructions: str) -> list[str]:
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
