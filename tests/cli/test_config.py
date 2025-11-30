"""Tests for config command."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from click.testing import CliRunner

from mcp_skills.cli.main import cli


if TYPE_CHECKING:
    from mcp_skills.models.config import MCPSkillsConfig


class TestConfigCommand:
    """Test suite for config command."""

    def test_config_help(self, cli_runner: CliRunner) -> None:
        """Test config command help."""
        result = cli_runner.invoke(cli, ["config", "--help"])

        assert result.exit_code == 0
        assert "Configure mcp-skillset settings" in result.output
        assert "--show" in result.output
        assert "--set" in result.output

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_config_show(
        self,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config: MCPSkillsConfig,
    ) -> None:
        """Test config --show displays configuration."""
        # Setup mock
        mock_config_cls.load.return_value = mock_config

        # Run command
        result = cli_runner.invoke(cli, ["config", "--show"])

        # Verify
        assert result.exit_code == 0
        assert "Current Configuration" in result.output

    def test_config_set_valid_value(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test config --set with valid key=value."""
        # Run command
        result = cli_runner.invoke(
            cli,
            ["config", "--set", f"base_dir={tmp_path}"],
        )

        # Verify
        assert result.exit_code == 0
        assert "Base directory set to" in result.output or "✓" in result.output

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_config_set_invalid_format(
        self,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config: MCPSkillsConfig,
    ) -> None:
        """Test config --set with invalid format."""
        # Setup mock
        mock_config_cls.load.return_value = mock_config

        # Run command with invalid format (no =)
        result = cli_runner.invoke(
            cli,
            ["config", "--set", "invalid_format"],
        )

        # Verify error
        assert result.exit_code != 0
        assert "format" in result.output.lower() or "=" in result.output

    def test_config_set_search_mode(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test config --set for search_mode."""
        # Run command
        result = cli_runner.invoke(
            cli,
            ["config", "--set", "search_mode=balanced"],
        )

        # Verify
        assert result.exit_code == 0
        assert "Search mode set to" in result.output or "balanced" in result.output

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_config_set_invalid_key(
        self,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config: MCPSkillsConfig,
    ) -> None:
        """Test config --set with invalid configuration key."""
        # Setup mock
        mock_config_cls.load.return_value = mock_config

        # Run command with invalid key
        result = cli_runner.invoke(
            cli,
            ["config", "--set", "nonexistent_key=value"],
        )

        # Verify error
        assert result.exit_code != 0

    @patch("mcp_skills.cli.config_menu.ConfigMenu")
    def test_config_interactive_mode(
        self,
        mock_menu_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test config command in interactive mode (default)."""
        # Setup mock
        mock_menu = Mock()
        mock_menu.run.return_value = None
        mock_menu_cls.return_value = mock_menu

        # Run command (no flags = interactive)
        cli_runner.invoke(cli, ["config"], input="\n")

        # Verify interactive menu was invoked
        mock_menu_cls.assert_called_once()

    @patch("mcp_skills.cli.config_menu.ConfigMenu")
    def test_config_interactive_keyboard_interrupt(
        self,
        mock_menu_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test config command handles keyboard interrupt in interactive mode."""
        # Setup mock to raise KeyboardInterrupt
        mock_menu = Mock()
        mock_menu.run.side_effect = KeyboardInterrupt()
        mock_menu_cls.return_value = mock_menu

        # Run command
        result = cli_runner.invoke(cli, ["config"])

        # Verify graceful exit
        assert result.exit_code == 1
        assert "cancelled" in result.output.lower()

    @patch("mcp_skills.cli.config_menu.ConfigMenu")
    def test_config_interactive_error(
        self,
        mock_menu_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test config command handles errors in interactive mode."""
        # Setup mock to raise exception
        mock_menu = Mock()
        mock_menu.run.side_effect = Exception("Configuration error")
        mock_menu_cls.return_value = mock_menu

        # Run command
        result = cli_runner.invoke(cli, ["config"])

        # Verify error handling
        assert result.exit_code == 1
        assert "failed" in result.output.lower()

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_config_show_with_repositories(
        self,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config: MCPSkillsConfig,
    ) -> None:
        """Test config --show displays repositories."""
        # Setup mock with repositories
        mock_config_cls.load.return_value = mock_config

        # Run command
        result = cli_runner.invoke(cli, ["config", "--show"])

        # Verify repositories are shown
        assert result.exit_code == 0
        assert (
            "Repositories" in result.output or "repositories" in result.output.lower()
        )

    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_config_show_with_search_settings(
        self,
        mock_config_cls: Mock,
        cli_runner: CliRunner,
        mock_config: MCPSkillsConfig,
    ) -> None:
        """Test config --show displays search settings."""
        # Setup mock
        mock_config_cls.load.return_value = mock_config

        # Run command
        result = cli_runner.invoke(cli, ["config", "--show"])

        # Verify search settings are shown
        assert result.exit_code == 0
        assert "Search" in result.output or "search" in result.output.lower()

    def test_config_set_multiple_values(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test config --set can be called multiple times."""
        # Run first command
        result1 = cli_runner.invoke(
            cli,
            ["config", "--set", "search_mode=semantic_focused"],
        )

        # Run second command
        result2 = cli_runner.invoke(
            cli,
            ["config", "--set", "search_mode=balanced"],
        )

        # Verify both succeed
        assert result1.exit_code == 0
        assert result2.exit_code == 0
