"""Pydantic models for skill data validation."""

from typing import Optional

from pydantic import BaseModel, Field


class SkillMetadataModel(BaseModel):
    """Skill metadata from YAML frontmatter.

    Validates the structure of skill metadata extracted from
    SKILL.md frontmatter.
    """

    name: str = Field(..., min_length=1, description="Skill name")
    description: str = Field(..., min_length=10, description="Skill description")
    category: str = Field(..., description="Skill category")
    tags: list[str] = Field(default_factory=list, description="Skill tags")
    dependencies: list[str] = Field(
        default_factory=list, description="Required skill dependencies"
    )
    version: Optional[str] = Field(None, description="Skill version")
    author: Optional[str] = Field(None, description="Skill author")


class SkillModel(BaseModel):
    """Complete skill data model with validation.

    Validates full skill structure including metadata and instructions.
    """

    id: str = Field(..., min_length=1, description="Unique skill identifier")
    name: str = Field(..., min_length=1, description="Skill name")
    description: str = Field(..., min_length=10, description="Skill description")
    instructions: str = Field(
        ..., min_length=50, description="Full skill instructions (markdown)"
    )
    category: str = Field(..., description="Skill category")
    tags: list[str] = Field(default_factory=list, description="Skill tags")
    dependencies: list[str] = Field(
        default_factory=list, description="Required skill dependencies"
    )
    examples: list[str] = Field(default_factory=list, description="Usage examples")
    file_path: str = Field(..., description="Path to SKILL.md file")
    repo_id: str = Field(..., description="Repository identifier")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "pytest-skill",
                "name": "pytest",
                "description": "Professional pytest testing for Python",
                "instructions": "# Pytest Skill\n\nDetailed instructions...",
                "category": "testing",
                "tags": ["python", "pytest", "tdd"],
                "dependencies": [],
                "examples": ["Example 1", "Example 2"],
                "file_path": "/path/to/pytest/SKILL.md",
                "repo_id": "anthropics-skills",
            }
        }
