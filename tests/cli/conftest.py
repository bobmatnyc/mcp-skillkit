"""Shared fixtures for CLI tests."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Generator
from unittest.mock import MagicMock, Mock

import pytest
from click.testing import CliRunner

from mcp_skills.models.config import HybridSearchConfig, MCPSkillsConfig
from mcp_skills.models.repository import Repository
from mcp_skills.models.skill import Skill, SkillMetadata
from mcp_skills.services.indexing.hybrid_search import ScoredSkill
from mcp_skills.services.toolchain_detector import ToolchainInfo

if TYPE_CHECKING:
    from pytest import FixtureRequest


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_config(tmp_path: Path) -> MCPSkillsConfig:
    """Provide mock configuration."""
    config_dir = tmp_path / ".mcp-skillset"
    config_dir.mkdir(parents=True, exist_ok=True)

    return MCPSkillsConfig(
        base_dir=config_dir,
        repositories=[],  # Empty list to avoid Repository initialization issues
        hybrid_search=HybridSearchConfig(
            vector_weight=0.7,
            graph_weight=0.3,
        ),
    )


@pytest.fixture
def mock_toolchain_info() -> ToolchainInfo:
    """Provide mock toolchain info."""
    return ToolchainInfo(
        primary_language="Python",
        secondary_languages=["TypeScript"],
        frameworks=["FastAPI", "pytest"],
        test_frameworks=["pytest"],
        package_managers=["pip"],
        build_tools=["setuptools"],
        confidence=0.95,
    )


@pytest.fixture
def mock_skill() -> Skill:
    """Provide mock skill."""
    return Skill(
        id="test-skill",
        name="Test Skill",
        description="A test skill for unit testing",
        instructions="Test skill content with detailed instructions for testing purposes.",
        category="testing",
        tags=["testing", "python"],
        dependencies=[],
        examples=["Example 1: Run tests", "Example 2: Debug tests"],
        file_path=Path("/test/skill.md"),
        repo_id="test-repo",
        version="1.0.0",
        author="Test Author",
    )


@pytest.fixture
def mock_repository() -> Repository:
    """Provide mock repository."""
    from datetime import datetime

    return Repository(
        id="example-skills",
        url="https://github.com/example/skills.git",
        local_path=Path("/tmp/repos/example-skills"),
        priority=1,
        last_updated=datetime.now(),
        skill_count=10,
        license="MIT",
    )


@pytest.fixture
def mock_skill_manager(mock_skill: Skill) -> Generator[Mock, None, None]:
    """Provide mocked SkillManager."""
    manager = Mock()
    # Return actual lists, not Mocks, so len() works
    manager.discover_skills.return_value = [mock_skill]
    manager.search_skills.return_value = [(mock_skill, 0.95)]  # Return tuples with scores
    manager.get_skill.return_value = mock_skill
    manager.load_skill.return_value = mock_skill  # Add load_skill method
    manager.list_categories.return_value = ["testing", "development"]
    yield manager


@pytest.fixture
def mock_indexing_engine(mock_skill: Skill) -> Generator[Mock, None, None]:
    """Provide mocked IndexingEngine."""
    engine = Mock()
    engine.index_skills.return_value = None
    # Return list of ScoredSkill objects for search
    scored_skill = ScoredSkill(skill=mock_skill, score=0.95, match_type="hybrid")
    engine.search.return_value = [scored_skill]
    engine.get_stats.return_value = {
        "total_skills": 10,
        "total_embeddings": 100,
        "index_size_mb": 1.5,
    }
    yield engine


@pytest.fixture
def mock_repository_manager(
    mock_repository: Repository,
) -> Generator[Mock, None, None]:
    """Provide mocked RepositoryManager."""
    manager = Mock()
    manager.list_repositories.return_value = [mock_repository]
    manager.add_repository.return_value = mock_repository
    manager.update_repositories.return_value = None
    yield manager


@pytest.fixture
def mock_toolchain_detector(
    mock_toolchain_info: ToolchainInfo,
) -> Generator[Mock, None, None]:
    """Provide mocked ToolchainDetector."""
    detector = Mock()
    detector.detect.return_value = mock_toolchain_info
    yield detector


@pytest.fixture
def mock_agent_installer() -> Generator[Mock, None, None]:
    """Provide mocked AgentInstaller."""
    installer = Mock()
    installer.install_agent.return_value = {"status": "success", "agent": "claude"}
    yield installer


@pytest.fixture
def mock_prompt_enricher() -> Generator[Mock, None, None]:
    """Provide mocked PromptEnricher."""
    enricher = Mock()
    enricher.enrich_prompt.return_value = "Enriched prompt content"
    yield enricher


@pytest.fixture
def isolated_filesystem(cli_runner: CliRunner) -> Generator[str, None, None]:
    """Provide isolated filesystem for CLI tests."""
    with cli_runner.isolated_filesystem():
        yield "."
