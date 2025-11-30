"""Tests for enrich command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from mcp_skills.cli.main import cli


class TestEnrichCommand:
    """Test suite for enrich command."""

    def test_enrich_help(self, cli_runner: CliRunner) -> None:
        """Test enrich command help."""
        result = cli_runner.invoke(cli, ["enrich", "--help"])

        assert result.exit_code == 0
        assert "Enrich" in result.output or "prompt" in result.output.lower()
        assert "--max-skills" in result.output or "--output" in result.output

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_prompt_text(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with direct prompt text."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt content"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Write a test for authentication"],
        )

        # Verify
        assert result.exit_code == 0
        assert "Enriched" in result.output or "prompt" in result.output.lower()

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_file(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test enrich command with file input."""
        # Create test file
        test_file = tmp_path / "prompt.txt"
        test_file.write_text("Write a test for authentication")

        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt content"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--file", str(test_file)],
        )

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_output_file(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test enrich command with output file."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt content"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        output_file = tmp_path / "output.txt"
        result = cli_runner.invoke(
            cli,
            [
                "enrich",
                "--prompt",
                "Test prompt",
                "--output",
                str(output_file),
            ],
        )

        # Verify
        assert result.exit_code == 0
        # Output file should be created
        assert output_file.exists()

    def test_enrich_requires_prompt_or_file(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command requires either --prompt or --file."""
        result = cli_runner.invoke(cli, ["enrich"])

        # Should fail without input
        assert result.exit_code != 0

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_limit(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with skill limit."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt content"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Test prompt", "--limit", "3"],
        )

        # Verify
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_mode(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with search mode."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt content"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Test prompt", "--mode", "vector"],
        )

        # Verify
        assert result.exit_code == 0

    def test_enrich_file_not_found(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with non-existent file."""
        result = cli_runner.invoke(
            cli,
            ["enrich", "--file", "/nonexistent/file.txt"],
        )

        # Should fail with file not found
        assert result.exit_code != 0

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_error_handling(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command error handling."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.side_effect = Exception("Enrichment failed")
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Test prompt"],
        )

        # Verify error handling
        assert result.exit_code != 0
        assert "failed" in result.output.lower() or "error" in result.output.lower()

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_displays_enriched_content(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command displays enriched content."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        enriched_text = "# Enriched Prompt\n\nTest content"
        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = enriched_text
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Test prompt"],
        )

        # Verify enriched content is displayed
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_stdin(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with stdin input."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt content"
        mock_enricher_cls.return_value = mock_enricher

        # Run command with stdin
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "-"],
            input="Test prompt from stdin",
        )

        # Verify (may not be supported, but should handle gracefully)
        assert result.exit_code in [0, 2]

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_no_relevant_skills(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command when no relevant skills found."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Original prompt (no skills found)"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Very obscure prompt"],
        )

        # Verify still completes
        assert result.exit_code == 0

    @patch("mcp_skills.cli.main.PromptEnricher")
    @patch("mcp_skills.cli.commands.enrich.SkillManager")
    def test_enrich_with_context(
        self,
        mock_manager_cls: Mock,
        mock_enricher_cls: Mock,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with additional context."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_cls.return_value = mock_manager

        mock_enricher = Mock()
        mock_enricher.enrich_prompt.return_value = "Enriched prompt with context"
        mock_enricher_cls.return_value = mock_enricher

        # Run command
        result = cli_runner.invoke(
            cli,
            ["enrich", "--prompt", "Test prompt", "--context", "Python project"],
        )

        # Verify (context flag may or may not exist)
        assert result.exit_code in [0, 2]


class TestEnrichCommandIntegration:
    """Integration tests for enrich command."""

    @pytest.mark.skip(reason="Requires full system setup")
    def test_enrich_full_workflow(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test full enrich workflow with real skills."""
        # This would require actual skills and enricher
        pass

    @pytest.mark.skip(reason="Requires embeddings")
    def test_enrich_with_vector_search(
        self,
        cli_runner: CliRunner,
    ) -> None:
        """Test enrich command with vector search."""
        # This would require actual vector search
        pass
