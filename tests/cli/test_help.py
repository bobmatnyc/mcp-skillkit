"""Tests for help, info, list, and related commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

from click.testing import CliRunner

from mcp_skills.cli.main import cli


class TestHelpCommands:
    """Test suite for help-related commands."""

    def test_cli_main_help(self, cli_runner: CliRunner) -> None:
        """Test main CLI help."""
        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "MCP Skills" in result.output
        assert "setup" in result.output
        assert "config" in result.output
        assert "index" in result.output

    def test_cli_version(self, cli_runner: CliRunner) -> None:
        """Test CLI version."""
        result = cli_runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.5.0" in result.output or "version" in result.output.lower()

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_list_command(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test list command displays skills."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["list"])

        # Verify
        assert result.exit_code == 0
        assert "Available Skills" in result.output or "Skills" in result.output

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_list_command_with_category(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test list command with category filter."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["list", "--category", "testing"])

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_list_command_compact_mode(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test list command in compact mode."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill] * 10
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["list", "--compact"])

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_list_command_no_skills(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test list command when no skills available."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["list"])

        # Verify
        assert result.exit_code == 0
        assert "No skills" in result.output or "0" in result.output

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_info_command(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test info command displays skill details."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.load_skill.return_value = mock_skill
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["info", "test-skill"])

        # Verify
        assert result.exit_code == 0
        assert "test-skill" in result.output.lower() or "Test Skill" in result.output

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_info_command_skill_not_found(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test info command when skill not found."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.load_skill.return_value = None
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["info", "nonexistent"])

        # Verify
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_show_command_alias(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test show command (alias for info)."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.load_skill.return_value = mock_skill
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["show", "test-skill"])

        # Verify
        assert result.exit_code == 0

    def test_list_help(self, cli_runner: CliRunner) -> None:
        """Test list command help."""
        result = cli_runner.invoke(cli, ["list", "--help"])

        assert result.exit_code == 0
        assert "List available skills" in result.output
        assert "--category" in result.output
        assert "--compact" in result.output

    def test_info_help(self, cli_runner: CliRunner) -> None:
        """Test info command help."""
        result = cli_runner.invoke(cli, ["info", "--help"])

        assert result.exit_code == 0
        assert "Show detailed information" in result.output

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_info_displays_metadata(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test info command displays skill metadata."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.load_skill.return_value = mock_skill
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["info", "test-skill"])

        # Verify metadata is displayed
        assert result.exit_code == 0
        assert "version" in result.output.lower() or "1.0.0" in result.output

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    def test_list_displays_categories(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test list command displays skill categories."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill]
        mock_manager.list_categories.return_value = ["testing", "development"]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["list"])

        # Verify
        assert result.exit_code == 0


class TestStatsCommand:
    """Test suite for stats command."""

    @patch("mcp_skills.cli.commands.list_skills.SkillManager")
    @patch("mcp_skills.cli.commands.stats.IndexingEngine")
    def test_stats_command(
        self,
        mock_engine_cls: Mock,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test stats command displays statistics."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager.discover_skills.return_value = [mock_skill] * 10
        mock_manager_cls.return_value = mock_manager

        mock_engine = Mock()
        mock_engine.get_stats.return_value = {
            "total_skills": 10,
            "total_embeddings": 100,
            "index_size_mb": 5.5,
        }
        mock_engine_cls.return_value = mock_engine

        # Run command
        result = cli_runner.invoke(cli, ["stats"])

        # Verify
        assert result.exit_code == 0
        assert "Statistics" in result.output or "stats" in result.output.lower()
        assert "10" in result.output

    def test_stats_help(self, cli_runner: CliRunner) -> None:
        """Test stats command help."""
        result = cli_runner.invoke(cli, ["stats", "--help"])

        assert result.exit_code == 0
        assert "Display statistics" in result.output or "stats" in result.output.lower()
