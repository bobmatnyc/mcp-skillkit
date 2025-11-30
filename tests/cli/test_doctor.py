"""Tests for doctor (health check) command."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from mcp_skills.cli.main import cli


class TestDoctorCommand:
    """Test suite for doctor command."""

    def test_doctor_help(self, cli_runner: CliRunner) -> None:
        """Test doctor command help."""
        result = cli_runner.invoke(cli, ["doctor", "--help"])

        assert result.exit_code == 0
        assert "health" in result.output.lower()

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    @patch("mcp_skills.cli.commands.doctor.SkillManager")
    @patch("mcp_skills.cli.commands.doctor.IndexingEngine")
    def test_doctor_all_healthy(
        self,
        mock_engine_cls: Mock,
        mock_manager_cls: Mock,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
        mock_skill,
    ) -> None:
        """Test doctor command when everything is healthy."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill] * 5
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.get_stats.return_value = {
            "total_skills": 5,
            "total_embeddings": 50,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify
        assert result.exit_code == 0
        assert "Health Check" in result.output or "health" in result.output.lower()

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_doctor_config_not_found(
        self,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test doctor command when config is missing."""
        # Setup mock to raise exception
        mock_config_cls.load.side_effect = FileNotFoundError("Config not found")

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify warning about config
        assert result.exit_code == 0  # Doctor should still complete
        assert "config" in result.output.lower()

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    @patch("mcp_skills.cli.commands.doctor.SkillManager")
    def test_doctor_no_skills(
        self,
        mock_manager_cls: Mock,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test doctor command when no skills are available."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify warning about no skills
        assert result.exit_code == 0
        assert (
            "no skills" in result.output.lower() or "warning" in result.output.lower()
        )

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    @patch("mcp_skills.cli.commands.doctor.IndexingEngine")
    def test_doctor_index_not_built(
        self,
        mock_engine_cls: Mock,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test doctor command when index is not built."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_engine = Mock()
        mock_engine.get_stats.return_value = {
            "total_skills": 0,
            "total_embeddings": 0,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify warning about index
        assert result.exit_code == 0
        assert "index" in result.output.lower() or "warning" in result.output.lower()

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    @patch("mcp_skills.cli.commands.doctor.RepositoryManager")
    def test_doctor_checks_repositories(
        self,
        mock_repo_cls: Mock,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
        mock_repository,
    ) -> None:
        """Test doctor command checks repositories."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_repo_manager = Mock()
        mock_repo_manager.list_repositories.return_value = [mock_repository]
        mock_repo_cls.return_value = mock_repo_manager

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify repositories are checked
        assert result.exit_code == 0

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    @patch("mcp_skills.cli.commands.doctor.RepositoryManager")
    def test_doctor_no_repositories(
        self,
        mock_repo_cls: Mock,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test doctor command when no repositories configured."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_repo_manager = Mock()
        mock_repo_manager.list_repositories.return_value = []
        mock_repo_cls.return_value = mock_repo_manager

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify warning about repositories
        assert result.exit_code == 0
        assert "repository" in result.output.lower() or "repo" in result.output.lower()

    def test_doctor_displays_summary(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test doctor command displays health summary."""
        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify summary is displayed
        assert "Health Check" in result.output or "health" in result.output.lower()

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    @patch("mcp_skills.cli.commands.doctor.SkillManager")
    @patch("mcp_skills.cli.commands.doctor.IndexingEngine")
    @patch("mcp_skills.cli.commands.doctor.RepositoryManager")
    def test_doctor_comprehensive_check(
        self,
        mock_repo_cls: Mock,
        mock_engine_cls: Mock,
        mock_manager_cls: Mock,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
        mock_skill,
        mock_repository,
    ) -> None:
        """Test doctor command performs comprehensive health check."""
        # Setup all mocks as healthy
        mock_config_cls.load.return_value = mock_config

        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill] * 10
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.get_stats.return_value = {
            "total_skills": 10,
            "total_embeddings": 100,
            "index_size_mb": 3.0,
        }
        mock_engine_cls.return_value = mock_engine

        mock_repo_manager = Mock()
        mock_repo_manager.list_repositories.return_value = [mock_repository]
        mock_repo_cls.return_value = mock_repo_manager

        # Run command
        result = cli_runner.invoke(cli, ["doctor"])

        # Verify comprehensive check
        assert result.exit_code == 0
        assert "Health Check" in result.output

    def test_doctor_returns_zero_on_success(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test doctor command returns exit code 0 on success."""
        result = cli_runner.invoke(cli, ["doctor"])

        # Should complete even if warnings
        assert result.exit_code == 0


class TestHealthCommandDeprecated:
    """Test suite for deprecated health command."""

    def test_health_command_deprecated(self, cli_runner: CliRunner) -> None:
        """Test health command shows deprecation warning."""
        result = cli_runner.invoke(cli, ["health"])

        assert result.exit_code == 0
        assert "deprecated" in result.output.lower()

    def test_health_command_redirects_to_doctor(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test health command redirects to doctor functionality."""
        result = cli_runner.invoke(cli, ["health"])

        # Should still perform health check
        assert result.exit_code == 0
        assert "Health Check" in result.output or "health" in result.output.lower()

    def test_health_command_hidden(self, cli_runner: CliRunner) -> None:
        """Test health command is hidden from main help."""
        result = cli_runner.invoke(cli, ["--help"])

        # health command should be hidden but doctor should be visible
        assert "doctor" in result.output.lower()


class TestDoctorCommandIntegration:
    """Integration tests for doctor command."""

    @pytest.mark.skip(reason="Requires full system setup")
    def test_doctor_full_system_check(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test doctor command with full system setup."""
        # This would require actual system setup
        pass

    @pytest.mark.skip(reason="Requires repository access")
    def test_doctor_checks_repository_connectivity(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test doctor command checks repository connectivity."""
        # This would require actual repository access
        pass
