"""Tests for CLI commands."""

from click.testing import CliRunner
import pytest

from mcp_skills.cli.main import cli


class TestCLI:
    """Test suite for CLI commands."""

    def test_cli_help(self) -> None:
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "MCP Skills" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_setup_command(self) -> None:
        """Test setup command runs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["setup", "--project-dir", ".", "--auto"])

        assert result.exit_code == 0
        assert "Starting mcp-skills setup" in result.output

    def test_serve_command(self) -> None:
        """Test serve command runs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--dev"])

        assert result.exit_code == 0
        assert "Starting MCP server" in result.output

    def test_search_command(self) -> None:
        """Test search command runs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "testing"])

        assert result.exit_code == 0
        assert "Searching for" in result.output

    def test_list_command(self) -> None:
        """Test list command runs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "Available Skills" in result.output

    def test_health_command(self) -> None:
        """Test health command runs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["health"])

        assert result.exit_code == 0
        assert "Health Check" in result.output

    def test_repo_list_command(self) -> None:
        """Test repo list command runs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["repo", "list"])

        assert result.exit_code == 0
        assert "Repositories" in result.output
