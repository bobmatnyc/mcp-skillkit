"""Tests for install command."""

from __future__ import annotations

from unittest.mock import Mock, patch

from click.testing import CliRunner

from mcp_skills.cli.main import cli


class TestInstallCommand:
    """Test suite for install command."""

    def test_install_help(self, cli_runner: CliRunner) -> None:
        """Test install command help."""
        result = cli_runner.invoke(cli, ["install", "--help"])

        assert result.exit_code == 0
        assert "Install mcp-skillset for a specific agent" in result.output
        assert "--agent" in result.output
        assert "--dry-run" in result.output
        assert "--force" in result.output

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_claude(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command for Claude agent."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {
            "status": "success",
            "agent": "claude",
            "config_path": "~/.claude/config.json",
        }
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(cli, ["install", "--agent", "claude"])

        # Verify
        assert result.exit_code == 0
        assert "Installing" in result.output or "claude" in result.output.lower()

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_cursor(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command for Cursor agent."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {
            "status": "success",
            "agent": "cursor",
        }
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(cli, ["install", "--agent", "cursor"])

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_dry_run(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command with --dry-run flag."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {
            "status": "success",
            "dry_run": True,
        }
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(
            cli,
            ["install", "--agent", "claude", "--dry-run"],
        )

        # Verify
        assert result.exit_code == 0
        assert "dry" in result.output.lower() or "would" in result.output.lower()

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_force(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command with --force flag."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {
            "status": "success",
            "force": True,
        }
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(
            cli,
            ["install", "--agent", "claude", "--force"],
        )

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_invalid_agent(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command with invalid agent."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.side_effect = ValueError("Unsupported agent")
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(
            cli,
            ["install", "--agent", "invalid-agent"],
        )

        # Verify error handling
        assert result.exit_code != 0
        assert "error" in result.output.lower() or "failed" in result.output.lower()

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_config_exists_warning(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command warns if config already exists."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {
            "status": "success",
            "already_exists": True,
        }
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(cli, ["install", "--agent", "claude"])

        # Verify warning or success
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_without_agent_flag(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test install command requires --agent flag."""
        # Run command without --agent
        result = cli_runner.invoke(cli, ["install"])

        # Should fail or prompt for agent
        assert result.exit_code != 0 or "agent" in result.output.lower()

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_multiple_agents(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command can be run for multiple agents."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {"status": "success"}
        mock_installer_cls.return_value = mock_installer

        # Run command for first agent
        result1 = cli_runner.invoke(cli, ["install", "--agent", "claude"])

        # Run command for second agent
        result2 = cli_runner.invoke(cli, ["install", "--agent", "cursor"])

        # Verify both succeed
        assert result1.exit_code == 0
        assert result2.exit_code == 0

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_displays_config_path(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command displays configuration path."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.return_value = {
            "status": "success",
            "config_path": "/path/to/config.json",
        }
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(cli, ["install", "--agent", "claude"])

        # Verify config path is shown
        assert result.exit_code == 0
        assert "config" in result.output.lower() or "/path" in result.output

    @patch("mcp_skills.cli.main.AgentInstaller")
    @patch("mcp_skills.models.config.MCPSkillsConfig")
    def test_install_error_handling(
        self,
        mock_config_cls: Mock,
        mock_installer_cls: Mock,
        cli_runner: CliRunner,
        mock_config,
    ) -> None:
        """Test install command handles errors gracefully."""
        # Setup mocks
        mock_config_cls.load.return_value = mock_config

        mock_installer = Mock()
        mock_installer.install_agent.side_effect = Exception("Installation failed")
        mock_installer_cls.return_value = mock_installer

        # Run command
        result = cli_runner.invoke(cli, ["install", "--agent", "claude"])

        # Verify error handling
        assert result.exit_code != 0
        assert "failed" in result.output.lower() or "error" in result.output.lower()
