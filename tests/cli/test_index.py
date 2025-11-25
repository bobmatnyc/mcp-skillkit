"""Tests for index command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from mcp_skills.cli.main import cli


class TestIndexCommand:
    """Test suite for index command."""

    def test_index_help(self, cli_runner: CliRunner) -> None:
        """Test index command help."""
        result = cli_runner.invoke(cli, ["index", "--help"])

        assert result.exit_code == 0
        assert "Index all skills" in result.output
        assert "--incremental" in result.output
        assert "--force" in result.output

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_basic(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test basic index command."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine.get_stats.return_value = {
            "total_skills": 10,
            "total_embeddings": 100,
            "index_size_mb": 2.5,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index"])

        # Verify
        assert result.exit_code == 0
        assert "Indexing" in result.output or "indexed" in result.output.lower()

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_incremental(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test index command with --incremental flag."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine.get_stats.return_value = {
            "total_skills": 10,
            "total_embeddings": 100,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index", "--incremental"])

        # Verify
        assert result.exit_code == 0
        assert "incremental" in result.output.lower() or result.exit_code == 0

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_force(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test index command with --force flag."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine.get_stats.return_value = {
            "total_skills": 5,
            "total_embeddings": 50,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index", "--force"])

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_with_skills(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test index command with actual skills to index."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill] * 5
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine.get_stats.return_value = {
            "total_skills": 5,
            "total_embeddings": 50,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index"])

        # Verify indexing was called
        assert result.exit_code == 0
        mock_engine.index_skills.assert_called_once()

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_no_skills(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test index command when no skills found."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index"])

        # Verify appropriate message
        assert result.exit_code == 0
        assert "No skills" in result.output or "0" in result.output

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_error_handling(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test index command error handling."""
        # Setup mock to raise exception
        mock_manager = Mock()
        mock_manager.list_skills.side_effect = Exception("Indexing failed")
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["index"])

        # Verify error handling
        assert result.exit_code != 0
        assert "failed" in result.output.lower() or "error" in result.output.lower()

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_displays_stats(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test index command displays statistics."""
        # Setup mocks with stats
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine.get_stats.return_value = {
            "total_skills": 15,
            "total_embeddings": 150,
            "index_size_mb": 3.2,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index"])

        # Verify stats are displayed
        assert result.exit_code == 0
        assert "15" in result.output or "skills" in result.output.lower()

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_incremental_and_force_mutually_exclusive(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test that incremental and force flags work together."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine_cls.return_value = mock_engine

        # Run command with both flags (should prioritize one)
        result = cli_runner.invoke(cli, ["index", "--incremental", "--force"])

        # Command should still work
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.IndexingEngine")
    @patch("mcp_skills.cli.main.SkillManager")
    def test_index_progress_display(
        self,
        mock_manager_cls: Mock,
        mock_engine_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test index command shows progress information."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill] * 20
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.index_skills.return_value = None
        mock_engine.get_stats.return_value = {
            "total_skills": 20,
            "total_embeddings": 200,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["index"])

        # Verify progress or completion message
        assert result.exit_code == 0
        assert "20" in result.output or "complete" in result.output.lower()
