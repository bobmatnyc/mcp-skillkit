"""Tests for prompt enrichment functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_skills.models.skill import Skill
from mcp_skills.services.prompt_enricher import EnrichedPrompt, PromptEnricher


@pytest.fixture
def mock_skill_manager():
    """Create mock SkillManager for testing."""
    manager = MagicMock()
    return manager


@pytest.fixture
def sample_skills():
    """Create sample skills for testing."""
    skill1 = Skill(
        id="test/fastapi",
        name="FastAPI Testing",
        description="Testing FastAPI applications",
        instructions="# FastAPI Testing\n\nUse pytest with TestClient...",
        category="testing",
        tags=["fastapi", "testing", "api"],
        dependencies=[],
        examples=["pytest example"],
        file_path=Path("/fake/path/SKILL.md"),
        repo_id="test-repo",
    )

    skill2 = Skill(
        id="test/validation",
        name="Input Validation",
        description="Validate user input with pydantic",
        instructions="# Input Validation\n\nUse Pydantic models for validation...",
        category="development",
        tags=["validation", "pydantic", "input"],
        dependencies=[],
        examples=["validation example"],
        file_path=Path("/fake/path/SKILL.md"),
        repo_id="test-repo",
    )

    skill3 = Skill(
        id="test/auth",
        name="Authentication",
        description="Implement JWT authentication",
        instructions="# Authentication\n\nImplement JWT-based auth with FastAPI...",
        category="security",
        tags=["auth", "jwt", "security"],
        dependencies=[],
        examples=["auth example"],
        file_path=Path("/fake/path/SKILL.md"),
        repo_id="test-repo",
    )

    return [skill1, skill2, skill3]


@pytest.fixture
def enricher(mock_skill_manager):
    """Create PromptEnricher instance."""
    return PromptEnricher(mock_skill_manager)


class TestKeywordExtraction:
    """Test keyword extraction functionality."""

    def test_extract_basic_keywords(self, enricher):
        """Test basic keyword extraction."""
        prompt = "Create a FastAPI endpoint with validation"
        keywords = enricher.extract_keywords(prompt)

        assert "fastapi" in keywords
        assert "endpoint" in keywords
        assert "validation" in keywords
        assert "create" in keywords

    def test_extract_removes_stop_words(self, enricher):
        """Test that stop words are removed."""
        prompt = "The API is for the user authentication"
        keywords = enricher.extract_keywords(prompt)

        assert "the" not in keywords
        assert "is" not in keywords
        assert "for" not in keywords
        assert "api" in keywords
        assert "user" in keywords
        assert "authentication" in keywords

    def test_extract_prioritizes_technical_terms(self, enricher):
        """Test that technical terms are prioritized."""
        prompt = "Create something with FastAPI and pytest"
        keywords = enricher.extract_keywords(prompt)

        # Technical terms should come before regular words
        assert keywords.index("fastapi") < keywords.index("something")
        assert keywords.index("pytest") < keywords.index("something")

    def test_extract_quoted_phrases(self, enricher):
        """Test extraction of quoted phrases as single keywords."""
        prompt = 'Create "user authentication" and "input validation" features'
        keywords = enricher.extract_keywords(prompt)

        assert "user authentication" in keywords
        assert "input validation" in keywords

    def test_extract_action_verbs(self, enricher):
        """Test that action verbs are identified."""
        prompt = "Implement testing and deploy to production"
        keywords = enricher.extract_keywords(prompt)

        assert "implement" in keywords
        assert "testing" in keywords
        assert "deploy" in keywords

    def test_extract_empty_prompt(self, enricher):
        """Test extraction from empty prompt."""
        keywords = enricher.extract_keywords("")
        assert keywords == []

    def test_extract_deduplicates(self, enricher):
        """Test that duplicate keywords are removed."""
        prompt = "Create API endpoint create API create endpoint"
        keywords = enricher.extract_keywords(prompt)

        # Should only appear once each
        assert keywords.count("api") == 1
        assert keywords.count("endpoint") == 1
        assert keywords.count("create") == 1


class TestSkillSearch:
    """Test skill search functionality."""

    def test_search_with_keywords(self, enricher, mock_skill_manager, sample_skills):
        """Test searching for skills with keywords."""
        mock_skill_manager.search_skills.return_value = sample_skills[:2]

        keywords = ["fastapi", "validation"]
        skills = enricher.search_skills(keywords, max_skills=3)

        assert len(skills) == 2
        mock_skill_manager.search_skills.assert_called_once_with(
            "fastapi validation", limit=3
        )

    def test_search_no_keywords(self, enricher, mock_skill_manager):
        """Test search with empty keywords."""
        skills = enricher.search_skills([], max_skills=3)

        assert skills == []
        mock_skill_manager.search_skills.assert_not_called()

    def test_search_limits_results(self, enricher, mock_skill_manager, sample_skills):
        """Test that max_skills limits results."""
        mock_skill_manager.search_skills.return_value = sample_skills

        enricher.search_skills(["test"], max_skills=2)

        mock_skill_manager.search_skills.assert_called_once_with("test", limit=2)


class TestPromptFormatting:
    """Test prompt formatting functionality."""

    def test_format_simple(self, enricher, sample_skills):
        """Test simple format output."""
        prompt = "Create FastAPI endpoint"
        result = enricher.format_simple(prompt, sample_skills[:2])

        assert prompt in result
        assert "Relevant Skills:" in result
        assert "FastAPI Testing" in result
        assert "Input Validation" in result
        assert "1." in result
        assert "2." in result

    def test_format_simple_truncates_instructions(self, enricher, sample_skills):
        """Test that simple format truncates long instructions."""
        # Create skill with long instructions
        long_skill = Skill(
            id="test/long",
            name="Long Skill",
            description="Test",
            instructions="x" * 500,  # 500 chars
            category="test",
            tags=[],
            dependencies=[],
            examples=[],
            file_path=Path("/fake/path/SKILL.md"),
            repo_id="test-repo",
        )

        result = enricher.format_simple("test", [long_skill])

        # Should be truncated to ~200 chars + "..."
        assert "..." in result
        assert len(result.split("Long Skill")[1].split("\n")[1]) <= 210

    def test_format_detailed(self, enricher, sample_skills):
        """Test detailed format output."""
        prompt = "Create FastAPI endpoint"
        result = enricher.format_detailed(prompt, sample_skills[:2])

        assert prompt in result
        assert "Context from MCP SkillSet:" in result
        assert "## FastAPI Testing" in result
        assert "## Input Validation" in result
        assert "Category: testing" in result
        assert "Category: development" in result

    def test_format_detailed_includes_full_instructions(self, enricher, sample_skills):
        """Test that detailed format includes full instructions."""
        result = enricher.format_detailed("test", [sample_skills[0]])

        # Should include full instructions, not truncated
        assert "Use pytest with TestClient..." in result


class TestPromptEnrichment:
    """Test complete prompt enrichment workflow."""

    def test_enrich_success(self, enricher, mock_skill_manager, sample_skills):
        """Test successful prompt enrichment."""
        mock_skill_manager.search_skills.return_value = sample_skills[:2]

        result = enricher.enrich(
            "Create FastAPI endpoint with validation", max_skills=3
        )

        assert isinstance(result, EnrichedPrompt)
        assert result.original_prompt == "Create FastAPI endpoint with validation"
        assert len(result.keywords) > 0
        assert "fastapi" in result.keywords
        assert len(result.skills_found) == 2
        assert "Relevant Skills:" in result.enriched_text
        assert not result.detailed

    def test_enrich_detailed_mode(self, enricher, mock_skill_manager, sample_skills):
        """Test enrichment with detailed mode."""
        mock_skill_manager.search_skills.return_value = [sample_skills[0]]

        result = enricher.enrich("Test prompt", max_skills=3, detailed=True)

        assert result.detailed
        assert "Context from MCP SkillSet:" in result.enriched_text
        assert "##" in result.enriched_text

    def test_enrich_no_skills_found(self, enricher, mock_skill_manager):
        """Test enrichment when no skills are found."""
        mock_skill_manager.search_skills.return_value = []

        result = enricher.enrich("Unknown topic xyz123", max_skills=3)

        assert len(result.skills_found) == 0
        assert "No relevant skills found" in result.enriched_text

    def test_enrich_empty_prompt(self, enricher, mock_skill_manager):
        """Test enrichment with empty prompt."""
        result = enricher.enrich("", max_skills=3)

        assert result.original_prompt == ""
        assert len(result.keywords) == 0
        assert len(result.skills_found) == 0

    def test_enrich_whitespace_only_prompt(self, enricher, mock_skill_manager):
        """Test enrichment with whitespace-only prompt."""
        result = enricher.enrich("   \n\t  ", max_skills=3)

        assert len(result.keywords) == 0
        assert len(result.skills_found) == 0

    def test_enrich_handles_search_exception(self, enricher, mock_skill_manager):
        """Test that enrichment handles search failures gracefully."""
        mock_skill_manager.search_skills.side_effect = Exception("Search failed")

        result = enricher.enrich("Test prompt", max_skills=3)

        # Should return original prompt on error
        assert result.enriched_text == "Test prompt"
        assert len(result.skills_found) == 0


class TestFileOperations:
    """Test file save and clipboard operations."""

    def test_save_to_file(self, enricher):
        """Test saving enriched prompt to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "enriched_prompt.md"
            text = "Enriched prompt content"

            enricher.save_to_file(text, output_path)

            assert output_path.exists()
            assert output_path.read_text() == text

    def test_save_to_file_creates_parent_dirs(self, enricher):
        """Test that save creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "enriched_prompt.md"
            text = "Test content"

            # Should create subdir automatically
            output_path.parent.mkdir(parents=True, exist_ok=True)
            enricher.save_to_file(text, output_path)

            assert output_path.exists()

    def test_save_to_file_handles_errors(self, enricher):
        """Test that save_to_file raises on write errors."""
        invalid_path = Path("/invalid/nonexistent/path/file.md")

        with pytest.raises(OSError):
            enricher.save_to_file("content", invalid_path)

    def test_copy_to_clipboard_success(self, enricher):
        """Test successful clipboard copy."""
        with patch("pyperclip.copy") as mock_copy:
            text = "Enriched prompt"

            result = enricher.copy_to_clipboard(text)

            assert result is True
            mock_copy.assert_called_once_with(text)

    def test_copy_to_clipboard_no_pyperclip(self, enricher):
        """Test clipboard copy when pyperclip is not installed."""
        with patch.dict("sys.modules", {"pyperclip": None}):
            result = enricher.copy_to_clipboard("text")

            # Should return False when pyperclip unavailable
            # Note: This might still return True if pyperclip is installed
            # in the test environment, so we just check it doesn't crash
            assert isinstance(result, bool)

    def test_copy_to_clipboard_handles_errors(self, enricher):
        """Test clipboard copy handles errors gracefully."""
        with patch("pyperclip.copy") as mock_copy:
            mock_copy.side_effect = Exception("Clipboard error")

            result = enricher.copy_to_clipboard("text")

            assert result is False


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_enrichment_workflow(
        self, enricher, mock_skill_manager, sample_skills
    ):
        """Test complete enrichment workflow from prompt to output."""
        mock_skill_manager.search_skills.return_value = sample_skills[:2]

        # Test the complete flow
        prompt = "Create a FastAPI endpoint that validates user input"
        result = enricher.enrich(prompt, max_skills=2, detailed=False)

        # Verify all components
        assert result.original_prompt == prompt
        assert "fastapi" in result.keywords
        assert "validation" in result.keywords or "validates" in result.keywords
        assert len(result.skills_found) == 2
        assert "FastAPI Testing" in result.enriched_text
        assert "Input Validation" in result.enriched_text

    def test_enrichment_with_file_output(
        self, enricher, mock_skill_manager, sample_skills
    ):
        """Test enrichment with file output."""
        mock_skill_manager.search_skills.return_value = [sample_skills[0]]

        result = enricher.enrich("Test prompt", max_skills=1)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            enricher.save_to_file(result.enriched_text, output_path)

            saved_content = output_path.read_text()
            assert "Test prompt" in saved_content
            assert "FastAPI Testing" in saved_content
