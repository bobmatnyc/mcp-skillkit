"""Tests for SkillValidator.

Tests cover:
- Skill validation (required fields, content length, categories)
- Frontmatter parsing and splitting
- Skill ID normalization
- Example extraction
"""

from pathlib import Path

import pytest

from mcp_skills.models.skill import Skill
from mcp_skills.services.validators import SkillValidator


@pytest.fixture
def validator() -> SkillValidator:
    """Create SkillValidator instance."""
    return SkillValidator()


@pytest.fixture
def temp_skill_file(tmp_path: Path) -> Path:
    """Create temporary skill file for testing."""
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text(
        """---
name: test-skill
description: Test skill description
category: testing
tags: [test, example]
---

# Test Skill

This is a test skill with enough content.

## Examples

Example 1 content

```python
def test():
    pass
```
""",
        encoding="utf-8",
    )
    return skill_file


class TestSkillValidation:
    """Test skill validation methods."""

    def test_validate_valid_skill(self, validator: SkillValidator) -> None:
        """Test validating a valid skill."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Valid description here",
            instructions="Long enough instructions " * 10,
            category="testing",
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["errors"]) == 0
        # No warnings expected for valid skill with valid category

    def test_validate_missing_name(self, validator: SkillValidator) -> None:
        """Test validation fails for missing name."""
        skill = Skill(
            id="test/skill",
            name="",
            description="Valid description",
            instructions="Long enough instructions " * 10,
            category="testing",
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["errors"]) > 0
        assert any("name" in error.lower() for error in result["errors"])

    def test_validate_short_description(self, validator: SkillValidator) -> None:
        """Test validation fails for short description."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Short",  # Too short
            instructions="Long enough instructions " * 10,
            category="testing",
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["errors"]) > 0
        assert any("description" in error.lower() for error in result["errors"])

    def test_validate_short_instructions(self, validator: SkillValidator) -> None:
        """Test validation fails for short instructions."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Valid description here",
            instructions="Too short",  # Too short
            category="testing",
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["errors"]) > 0
        assert any("instructions" in error.lower() for error in result["errors"])

    def test_validate_invalid_category(self, validator: SkillValidator) -> None:
        """Test warning for invalid category."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Valid description here",
            instructions="Long enough instructions " * 10,
            category="invalid-category",  # Invalid
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["warnings"]) > 0
        assert any("category" in warning.lower() for warning in result["warnings"])

    def test_validate_missing_tags(self, validator: SkillValidator) -> None:
        """Test warning for missing tags."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Valid description here",
            instructions="Long enough instructions " * 10,
            category="testing",
            tags=[],  # No tags
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["warnings"]) > 0
        assert any("tags" in warning.lower() for warning in result["warnings"])

    def test_validate_missing_examples(self, validator: SkillValidator) -> None:
        """Test warning for missing examples."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Valid description here",
            instructions="Instructions without any specific demonstration patterns or code samples to show how to use this skill in practice.",
            category="testing",
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        result = validator.validate_skill(skill)

        assert len(result["warnings"]) > 0
        assert any("example" in warning.lower() for warning in result["warnings"])

    def test_validate_with_dependencies(self, validator: SkillValidator) -> None:
        """Test validation with dependency resolution."""
        skill = Skill(
            id="test/skill",
            name="test-skill",
            description="Valid description here",
            instructions="Long enough instructions " * 10,
            category="testing",
            tags=["test"],
            dependencies=["test/dependency"],
            examples=[],
            file_path=Path("/tmp/test.md"),
            repo_id="test",
        )

        # Mock dependency resolver that returns None (unresolved)
        def mock_resolver(dep_id: str) -> Skill | None:
            return None

        result = validator.validate_skill_with_dependencies(skill, mock_resolver)

        assert len(result["warnings"]) > 0
        assert any("dependency" in warning.lower() for warning in result["warnings"])


class TestFrontmatterParsing:
    """Test YAML frontmatter parsing."""

    def test_split_frontmatter_valid(self, validator: SkillValidator) -> None:
        """Test splitting valid frontmatter."""
        content = """---
name: test
description: Test description
---

# Instructions
Content here"""

        frontmatter, instructions = validator.split_frontmatter(content)

        assert "name: test" in frontmatter
        assert "description: Test description" in frontmatter
        assert "# Instructions" in instructions
        assert "Content here" in instructions

    def test_split_frontmatter_no_frontmatter(
        self, validator: SkillValidator
    ) -> None:
        """Test content without frontmatter."""
        content = "# Just some content\n\nNo frontmatter here"

        frontmatter, instructions = validator.split_frontmatter(content)

        assert frontmatter == ""
        assert instructions == content

    def test_split_frontmatter_whitespace(self, validator: SkillValidator) -> None:
        """Test frontmatter with extra whitespace."""
        content = """---

name: test
description: desc

---

# Content"""

        frontmatter, instructions = validator.split_frontmatter(content)

        assert "name: test" in frontmatter
        assert "# Content" in instructions

    def test_parse_frontmatter_valid(
        self, validator: SkillValidator, temp_skill_file: Path
    ) -> None:
        """Test parsing valid frontmatter from file."""
        metadata = validator.parse_frontmatter(temp_skill_file)

        assert metadata is not None
        assert metadata["name"] == "test-skill"
        assert metadata["description"] == "Test skill description"
        assert metadata["category"] == "testing"

    def test_parse_frontmatter_invalid_yaml(
        self, validator: SkillValidator, tmp_path: Path
    ) -> None:
        """Test parsing invalid YAML."""
        skill_file = tmp_path / "invalid.md"
        skill_file.write_text(
            """---
name: test
description: [unclosed array
---

# Content""",
            encoding="utf-8",
        )

        metadata = validator.parse_frontmatter(skill_file)

        assert metadata is None

    def test_parse_frontmatter_no_frontmatter(
        self, validator: SkillValidator, tmp_path: Path
    ) -> None:
        """Test parsing file without frontmatter."""
        skill_file = tmp_path / "no_frontmatter.md"
        skill_file.write_text("# Just content\n\nNo frontmatter", encoding="utf-8")

        metadata = validator.parse_frontmatter(skill_file)

        assert metadata is None


class TestSkillIDNormalization:
    """Test skill ID normalization."""

    def test_normalize_lowercase(self, validator: SkillValidator) -> None:
        """Test ID is converted to lowercase."""
        assert validator.normalize_skill_id("UPPER/Case") == "upper/case"

    def test_normalize_special_chars(self, validator: SkillValidator) -> None:
        """Test special characters are replaced with hyphens."""
        assert validator.normalize_skill_id("test skill!") == "test-skill"
        assert validator.normalize_skill_id("a@b#c$d") == "a-b-c-d"

    def test_normalize_preserve_slashes(self, validator: SkillValidator) -> None:
        """Test slashes are preserved for path structure."""
        assert validator.normalize_skill_id("repo/path/skill") == "repo/path/skill"

    def test_normalize_consecutive_hyphens(self, validator: SkillValidator) -> None:
        """Test consecutive hyphens are collapsed."""
        assert validator.normalize_skill_id("test---skill") == "test-skill"

    def test_normalize_trim_hyphens(self, validator: SkillValidator) -> None:
        """Test leading/trailing hyphens are removed."""
        assert validator.normalize_skill_id("-test-") == "test"


class TestExampleExtraction:
    """Test example extraction from instructions."""

    def test_extract_examples_section(self, validator: SkillValidator) -> None:
        """Test extracting Examples section."""
        instructions = """# Skill

## Examples

Example 1 content
Example 2 content

## Other Section"""

        examples = validator.extract_examples(instructions)

        assert len(examples) > 0
        assert "Example 1 content" in examples[0]

    def test_extract_code_blocks(self, validator: SkillValidator) -> None:
        """Test extracting code blocks as examples."""
        instructions = """# Skill

```python
def test():
    pass
```

```bash
pytest
```"""

        examples = validator.extract_examples(instructions)

        assert len(examples) == 2
        assert "def test():" in examples[0]
        assert "pytest" in examples[1]

    def test_extract_no_examples(self, validator: SkillValidator) -> None:
        """Test when no examples are present."""
        instructions = "# Skill\n\nJust instructions, no examples."

        examples = validator.extract_examples(instructions)

        assert len(examples) == 0

    def test_extract_example_case_insensitive(
        self, validator: SkillValidator
    ) -> None:
        """Test Examples section is case-insensitive."""
        instructions = """# Skill

## EXAMPLES

Example content here
"""

        examples = validator.extract_examples(instructions)

        assert len(examples) > 0
        assert "Example content" in examples[0]

    def test_extract_examples_limit_code_blocks(
        self, validator: SkillValidator
    ) -> None:
        """Test code block limit (max 3)."""
        instructions = """# Skill

```python
block1
```

```python
block2
```

```python
block3
```

```python
block4
```

```python
block5
```
"""

        examples = validator.extract_examples(instructions)

        # Should only extract first 3 code blocks
        assert len(examples) == 3


class TestValidCategories:
    """Test valid categories definition."""

    def test_valid_categories_defined(self, validator: SkillValidator) -> None:
        """Test that valid categories are defined."""
        assert len(validator.VALID_CATEGORIES) > 0
        assert "testing" in validator.VALID_CATEGORIES
        assert "debugging" in validator.VALID_CATEGORIES
        assert "refactoring" in validator.VALID_CATEGORIES

    def test_valid_categories_is_set(self, validator: SkillValidator) -> None:
        """Test that VALID_CATEGORIES is a set."""
        assert isinstance(validator.VALID_CATEGORIES, set)
