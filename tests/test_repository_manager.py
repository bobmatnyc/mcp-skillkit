"""Tests for repository management service."""

from pathlib import Path

import pytest

from mcp_skills.services.repository_manager import RepositoryManager, Repository


class TestRepositoryManager:
    """Test suite for RepositoryManager."""

    def test_manager_initialization(self, tmp_path: Path) -> None:
        """Test repository manager can be initialized."""
        manager = RepositoryManager(base_dir=tmp_path / "repos")
        assert manager is not None
        assert manager.base_dir.exists()

    def test_default_repos_defined(self) -> None:
        """Test default repositories are defined."""
        assert hasattr(RepositoryManager, "DEFAULT_REPOS")
        assert isinstance(RepositoryManager.DEFAULT_REPOS, list)
        assert len(RepositoryManager.DEFAULT_REPOS) > 0

    @pytest.mark.skip(reason="Implementation pending")
    def test_add_repository(self, tmp_path: Path) -> None:
        """Test adding a new repository."""
        manager = RepositoryManager(base_dir=tmp_path / "repos")

        # This will be implemented later
        with pytest.raises(NotImplementedError):
            manager.add_repository(
                url="https://github.com/test/repo.git", priority=50
            )

    def test_list_repositories_returns_list(self, tmp_path: Path) -> None:
        """Test list_repositories returns list."""
        manager = RepositoryManager(base_dir=tmp_path / "repos")
        repos = manager.list_repositories()

        assert isinstance(repos, list)

    def test_get_repository_returns_optional(self, tmp_path: Path) -> None:
        """Test get_repository returns None for non-existent repo."""
        manager = RepositoryManager(base_dir=tmp_path / "repos")
        repo = manager.get_repository("non-existent")

        assert repo is None
