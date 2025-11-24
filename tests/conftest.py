"""Pytest configuration and fixtures for mcp-skills tests."""

from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary project directory for testing.

    Args:
        tmp_path: Pytest temporary path fixture

    Yields:
        Path to temporary project directory
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    yield project_dir


@pytest.fixture
def sample_python_project(temp_project_dir: Path) -> Path:
    """Create sample Python project for toolchain detection testing.

    Args:
        temp_project_dir: Temporary project directory

    Returns:
        Path to sample Python project
    """
    # Create Python project markers
    (temp_project_dir / "pyproject.toml").write_text(
        "[project]\nname = 'test-project'\n"
    )
    (temp_project_dir / "requirements.txt").write_text("flask>=3.0.0\npytest>=7.0\n")
    (temp_project_dir / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")

    return temp_project_dir


@pytest.fixture
def sample_typescript_project(temp_project_dir: Path) -> Path:
    """Create sample TypeScript project for toolchain detection testing.

    Args:
        temp_project_dir: Temporary project directory

    Returns:
        Path to sample TypeScript project
    """
    # Create TypeScript project markers
    (temp_project_dir / "package.json").write_text(
        '{"name": "test-project", "devDependencies": {"typescript": "^5.0.0"}}'
    )
    (temp_project_dir / "tsconfig.json").write_text(
        '{"compilerOptions": {"target": "ES2020"}}'
    )

    return temp_project_dir


@pytest.fixture
def sample_skill_metadata() -> dict:
    """Sample skill metadata for testing.

    Returns:
        Dictionary with skill metadata
    """
    return {
        "name": "test-skill",
        "description": "A test skill for unit testing",
        "category": "testing",
        "tags": ["test", "pytest"],
        "dependencies": [],
        "version": "1.0.0",
        "author": "Test Author",
    }
