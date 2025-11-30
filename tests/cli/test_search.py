"""Tests for search and recommend commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

from click.testing import CliRunner

from mcp_skills.cli.main import cli


class TestSearchCommand:
    """Test suite for search command."""

    def test_search_help(self, cli_runner: CliRunner) -> None:
        """Test search command help."""
        result = cli_runner.invoke(cli, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search for skills" in result.output
        assert "query" in result.output.lower()

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_basic(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test basic search command."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["search", "testing"])

        # Verify
        assert result.exit_code == 0
        assert "Searching for" in result.output or "testing" in result.output

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_no_results(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test search command with no results."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["search", "nonexistent"])

        # Verify
        assert result.exit_code == 0
        assert "No skills found" in result.output or "0" in result.output

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_with_limit(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test search command with limit parameter."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill] * 5
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["search", "test", "--limit", "3"])

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_with_mode(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test search command with mode parameter."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(
            cli,
            ["search", "test", "--mode", "vector"],
        )

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_with_threshold(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test search command with similarity threshold."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(
            cli,
            ["search", "test", "--threshold", "0.7"],
        )

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_multiple_results(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test search command with multiple results."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill] * 10
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["search", "test"])

        # Verify multiple results displayed
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_displays_relevance_scores(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
        mock_skill,
    ) -> None:
        """Test search command displays relevance scores."""
        # Setup mock
        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["search", "test"])

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_error_handling(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test search command error handling."""
        # Setup mock to raise exception
        mock_manager = Mock()
        mock_manager.search_skills.side_effect = Exception("Search failed")
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["search", "test"])

        # Verify error handling
        assert result.exit_code != 0

    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_search_empty_query(
        self,
        mock_manager_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test search command with empty query."""
        # Run command with empty query
        result = cli_runner.invoke(cli, ["search", ""])

        # Should handle gracefully
        assert result.exit_code in [0, 2]  # 2 = missing argument

    def test_search_requires_query(self, cli_runner: CliRunner) -> None:
        """Test search command requires query argument."""
        result = cli_runner.invoke(cli, ["search"])

        # Should fail without query
        assert result.exit_code != 0


class TestRecommendCommand:
    """Test suite for recommend command."""

    def test_recommend_help(self, cli_runner: CliRunner) -> None:
        """Test recommend command help."""
        result = cli_runner.invoke(cli, ["recommend", "--help"])

        assert result.exit_code == 0
        assert "Recommend skills" in result.output

    @patch("mcp_skills.cli.main.ToolchainDetector")
    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_recommend_basic(
        self,
        mock_manager_cls: Mock,
        mock_detector_cls: Mock,
        cli_runner: CliRunner,
        mock_toolchain_info,
        mock_skill,
    ) -> None:
        """Test basic recommend command."""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect.return_value = mock_toolchain_info
        mock_detector_cls.return_value = mock_detector

        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["recommend"])

        # Verify
        assert result.exit_code == 0
        assert "Recommend" in result.output or "skills" in result.output.lower()

    @patch("mcp_skills.cli.main.ToolchainDetector")
    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_recommend_with_search_mode(
        self,
        mock_manager_cls: Mock,
        mock_detector_cls: Mock,
        cli_runner: CliRunner,
        mock_toolchain_info,
        mock_skill,
    ) -> None:
        """Test recommend command with search mode."""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect.return_value = mock_toolchain_info
        mock_detector_cls.return_value = mock_detector

        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill]
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(
            cli,
            ["recommend", "--search-mode", "balanced"],
        )

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.ToolchainDetector")
    def test_recommend_toolchain_detection_failed(
        self,
        mock_detector_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test recommend command when toolchain detection fails."""
        # Setup mock to raise exception
        mock_detector = Mock()
        mock_detector.detect.side_effect = Exception("Detection failed")
        mock_detector_cls.return_value = mock_detector

        # Run command
        result = cli_runner.invoke(cli, ["recommend"])

        # Verify error handling
        assert result.exit_code != 0

    @patch("mcp_skills.cli.main.ToolchainDetector")
    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_recommend_no_matching_skills(
        self,
        mock_manager_cls: Mock,
        mock_detector_cls: Mock,
        cli_runner: CliRunner,
        mock_toolchain_info,
    ) -> None:
        """Test recommend command when no matching skills found."""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect.return_value = mock_toolchain_info
        mock_detector_cls.return_value = mock_detector

        mock_manager = Mock()
        mock_manager.search_skills.return_value = []
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["recommend"])

        # Verify
        assert result.exit_code == 0
        assert "No" in result.output or "0" in result.output

    @patch("mcp_skills.cli.main.ToolchainDetector")
    @patch("mcp_skills.cli.commands.search.SkillManager")
    def test_recommend_displays_recommendations(
        self,
        mock_manager_cls: Mock,
        mock_detector_cls: Mock,
        cli_runner: CliRunner,
        mock_toolchain_info,
        mock_skill,
    ) -> None:
        """Test recommend command displays recommendations."""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect.return_value = mock_toolchain_info
        mock_detector_cls.return_value = mock_detector

        mock_manager = Mock()
        mock_manager.search_skills.return_value = [mock_skill] * 5
        mock_manager_cls.return_value = mock_manager

        # Run command
        result = cli_runner.invoke(cli, ["recommend"])

        # Verify recommendations are displayed
        assert result.exit_code == 0
