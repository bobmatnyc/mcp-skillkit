"""Tests for VectorStore error handling and edge cases."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mcp_skills.models.skill import Skill
from mcp_skills.services.indexing.vector_store import VectorStore


@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_skill():
    """Create a sample skill for testing."""
    return Skill(
        id="test-repo/test-skill",
        name="test-skill",
        description="Test skill description",
        instructions="Test instructions for skill",
        category="testing",
        tags=["test", "python"],
        dependencies=[],
        examples=["test example"],
        file_path=Path("/tmp/test/SKILL.md"),
        repo_id="test-repo",
        version="1.0.0",
        author="Test Author",
    )


class TestVectorStoreInitializationErrors:
    """Test VectorStore initialization error handling."""

    def test_chromadb_initialization_failure_raises_runtime_error(self):
        """Test that ChromaDB init failure raises RuntimeError."""
        with patch("mcp_skills.services.indexing.vector_store.chromadb.PersistentClient") as mock_client:
            mock_client.side_effect = Exception("ChromaDB connection failed")

            with pytest.raises(RuntimeError, match="ChromaDB initialization failed"):
                VectorStore()

    def test_embedding_model_initialization_failure_raises_runtime_error(self):
        """Test that embedding model init failure raises RuntimeError."""
        with patch("mcp_skills.services.indexing.vector_store.SentenceTransformer") as mock_model:
            mock_model.side_effect = Exception("Model download failed")

            with pytest.raises(RuntimeError, match="Embedding model initialization failed"):
                VectorStore()

    def test_vector_store_creates_persist_directory(self, temp_storage):
        """Test that persist directory is created if it doesn't exist."""
        nested_dir = temp_storage / "nested" / "chroma"

        # Directory doesn't exist yet
        assert not nested_dir.exists()

        # Should create it during initialization
        vector_store = VectorStore(persist_directory=nested_dir)
        assert nested_dir.exists()
        assert vector_store.persist_directory == nested_dir


class TestVectorStoreIndexSkillErrors:
    """Test index_skill error handling."""

    def test_index_skill_with_empty_embeddable_text_skips_indexing(self, temp_storage):
        """Test that skill with empty embeddable text is skipped."""
        skill = Skill(
            id="test/empty",
            name="",  # Empty name
            description="",  # Empty description
            instructions="",  # Empty instructions
            category="testing",
            tags=[],  # No tags
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test/SKILL.md"),
            repo_id="test-repo",
        )

        vector_store = VectorStore(persist_directory=temp_storage)
        initial_count = vector_store.count()

        # Should log warning and skip
        vector_store.index_skill(skill)

        # Count should not increase
        assert vector_store.count() == initial_count

    def test_index_skill_handles_chromadb_add_failure_gracefully(self, temp_storage, sample_skill):
        """Test that ChromaDB add failure is handled gracefully."""
        vector_store = VectorStore(persist_directory=temp_storage)

        # Mock collection.add to raise exception
        with patch.object(vector_store.collection, 'add', side_effect=Exception("DB write failed")):
            # Should not raise exception (logs error instead)
            vector_store.index_skill(sample_skill)

            # Verify skill was not added
            assert vector_store.count() == 0


class TestVectorStoreBuildEmbeddingsErrors:
    """Test build_embeddings error handling."""

    def test_build_embeddings_with_empty_text_returns_empty_list(self, temp_storage):
        """Test that empty embeddable text returns empty embedding list."""
        skill = Skill(
            id="test/empty",
            name="",
            description="",
            instructions="",
            category="testing",
            tags=[],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test/SKILL.md"),
            repo_id="test-repo",
        )

        vector_store = VectorStore(persist_directory=temp_storage)
        embeddings = vector_store.build_embeddings(skill)

        assert embeddings == []

    def test_build_embeddings_handles_encoding_error_gracefully(self, temp_storage, sample_skill):
        """Test that encoding errors are handled gracefully."""
        vector_store = VectorStore(persist_directory=temp_storage)

        # Mock embedding model to raise exception
        with patch.object(vector_store.embedding_model, 'encode', side_effect=Exception("Encoding failed")):
            embeddings = vector_store.build_embeddings(sample_skill)

            # Should return empty list instead of raising
            assert embeddings == []


class TestVectorStoreSearchErrors:
    """Test search error handling."""

    def test_search_with_empty_query_returns_empty_results(self, temp_storage):
        """Test that empty query returns empty results."""
        vector_store = VectorStore(persist_directory=temp_storage)
        results = vector_store.search("", top_k=5)

        assert results == []

    def test_search_with_chromadb_query_failure_returns_empty_list(self, temp_storage, sample_skill):
        """Test that ChromaDB query failure returns empty list."""
        vector_store = VectorStore(persist_directory=temp_storage)
        vector_store.index_skill(sample_skill)

        # Mock collection.query to raise exception
        with patch.object(vector_store.collection, 'query', side_effect=Exception("Query failed")):
            results = vector_store.search("test query", top_k=5)

            # Should return empty list instead of raising
            assert results == []

    def test_search_with_no_results_returns_empty_list(self, temp_storage):
        """Test search with no indexed skills returns empty list."""
        vector_store = VectorStore(persist_directory=temp_storage)
        results = vector_store.search("nonexistent query", top_k=5)

        assert results == []

    def test_search_respects_top_k_limit(self, temp_storage):
        """Test that search respects top_k parameter."""
        vector_store = VectorStore(persist_directory=temp_storage)

        # Index multiple skills
        for i in range(10):
            skill = Skill(
                id=f"test-repo/skill-{i}",
                name=f"skill-{i}",
                description=f"Test skill {i} description",
                instructions=f"Test instructions {i}",
                category="testing",
                tags=["test"],
                dependencies=[],
                examples=[],
                file_path=Path(f"/tmp/test/SKILL-{i}.md"),
                repo_id="test-repo",
            )
            vector_store.index_skill(skill)

        # Search with top_k=3
        results = vector_store.search("test", top_k=3)

        # Should return at most 3 results
        assert len(results) <= 3


class TestVectorStoreClearErrors:
    """Test clear error handling."""

    def test_clear_with_chromadb_delete_failure_raises_exception(self, temp_storage, sample_skill):
        """Test that ChromaDB delete failure raises exception."""
        vector_store = VectorStore(persist_directory=temp_storage)
        vector_store.index_skill(sample_skill)

        # Mock collection.delete to raise exception
        with patch.object(vector_store.collection, 'delete', side_effect=Exception("Delete failed")):
            with pytest.raises(Exception, match="Delete failed"):
                vector_store.clear()

    def test_clear_empty_store_handles_gracefully(self, temp_storage):
        """Test that clearing empty store handles gracefully."""
        vector_store = VectorStore(persist_directory=temp_storage)

        # Should not raise exception
        vector_store.clear()

        assert vector_store.count() == 0


class TestVectorStoreCountErrors:
    """Test count error handling."""

    def test_count_with_chromadb_count_failure_returns_zero(self, temp_storage, sample_skill):
        """Test that ChromaDB count failure returns 0."""
        vector_store = VectorStore(persist_directory=temp_storage)
        vector_store.index_skill(sample_skill)

        # Mock collection.count to raise exception
        with patch.object(vector_store.collection, 'count', side_effect=Exception("Count failed")):
            count = vector_store.count()

            # Should return 0 instead of raising
            assert count == 0


class TestVectorStoreEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_index_skill_with_very_long_instructions(self, temp_storage):
        """Test that very long instructions are truncated properly."""
        long_instructions = "x" * 10000  # Much longer than 500 char limit

        skill = Skill(
            id="test/long",
            name="long-skill",
            description="Test skill",
            instructions=long_instructions,
            category="testing",
            tags=["test"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test/SKILL.md"),
            repo_id="test-repo",
        )

        vector_store = VectorStore(persist_directory=temp_storage)
        vector_store.index_skill(skill)

        # Should index successfully (instructions truncated)
        assert vector_store.count() == 1

    def test_index_skill_with_unicode_characters(self, temp_storage):
        """Test that unicode characters in skills are handled."""
        skill = Skill(
            id="test/unicode",
            name="unicode-skill 你好",
            description="Test with émojis 🎉 and accènts",
            instructions="Unicode test: 日本語 العربية",
            category="testing",
            tags=["test", "国际化"],
            dependencies=[],
            examples=[],
            file_path=Path("/tmp/test/SKILL.md"),
            repo_id="test-repo",
        )

        vector_store = VectorStore(persist_directory=temp_storage)
        vector_store.index_skill(skill)

        # Should index successfully
        assert vector_store.count() == 1

        # Should be searchable
        results = vector_store.search("unicode", top_k=5)
        assert len(results) > 0

    def test_search_with_filters_applies_correctly(self, temp_storage):
        """Test that metadata filters are applied correctly."""
        # Index skills with different categories
        for category in ["testing", "deployment", "debugging"]:
            skill = Skill(
                id=f"test-repo/{category}-skill",
                name=f"{category}-skill",
                description=f"Skill for {category}",
                instructions=f"Instructions for {category}",
                category=category,
                tags=[category],
                dependencies=[],
                examples=[],
                file_path=Path(f"/tmp/test/{category}/SKILL.md"),
                repo_id="test-repo",
            )
            vector_store = VectorStore(persist_directory=temp_storage)
            vector_store.index_skill(skill)

        # Search with category filter
        results = vector_store.search("skill", top_k=10, filters={"category": "testing"})

        # All results should have testing category
        for result in results:
            assert result["metadata"]["category"] == "testing"

    def test_build_embeddings_creates_consistent_dimensions(self, temp_storage, sample_skill):
        """Test that embeddings have consistent dimensions."""
        vector_store = VectorStore(persist_directory=temp_storage)

        # Generate embeddings multiple times
        embedding1 = vector_store.build_embeddings(sample_skill)
        embedding2 = vector_store.build_embeddings(sample_skill)

        # Should have same dimension (384 for all-MiniLM-L6-v2)
        assert len(embedding1) == len(embedding2) == 384

        # Should be deterministic (same input = same output)
        assert embedding1 == embedding2
