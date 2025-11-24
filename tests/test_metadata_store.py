"""Tests for SQLite metadata store."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mcp_skills.models.repository import Repository
from mcp_skills.services.metadata_store import MetadataStore


class TestMetadataStore:
    """Test suite for MetadataStore."""

    def test_store_initialization(self, tmp_path: Path) -> None:
        """Test metadata store can be initialized."""
        store = MetadataStore(db_path=tmp_path / "test.db")
        assert store is not None
        assert (tmp_path / "test.db").exists()

    def test_add_and_get_repository(self, tmp_path: Path) -> None:
        """Test adding and retrieving repository."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        repo = Repository(
            id="test/repo",
            url="https://github.com/test/repo.git",
            local_path=tmp_path / "repos" / "test/repo",
            priority=50,
            last_updated=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            skill_count=5,
            license="MIT",
        )

        store.add_repository(repo)
        retrieved = store.get_repository("test/repo")

        assert retrieved is not None
        assert retrieved.id == "test/repo"
        assert retrieved.url == "https://github.com/test/repo.git"
        assert retrieved.priority == 50
        assert retrieved.skill_count == 5
        assert retrieved.license == "MIT"

    def test_get_nonexistent_repository(self, tmp_path: Path) -> None:
        """Test getting non-existent repository returns None."""
        store = MetadataStore(db_path=tmp_path / "test.db")
        result = store.get_repository("nonexistent")
        assert result is None

    def test_list_repositories_sorted(self, tmp_path: Path) -> None:
        """Test listing repositories sorted by priority."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        # Add repositories with different priorities
        for name, priority in [("repo1", 30), ("repo2", 90), ("repo3", 50)]:
            repo = Repository(
                id=f"test/{name}",
                url=f"https://github.com/test/{name}.git",
                local_path=tmp_path / "repos" / f"test/{name}",
                priority=priority,
                last_updated=datetime.now(UTC),
                skill_count=0,
                license="MIT",
            )
            store.add_repository(repo)

        repos = store.list_repositories()

        assert len(repos) == 3
        assert repos[0].priority == 90
        assert repos[1].priority == 50
        assert repos[2].priority == 30

    def test_update_repository(self, tmp_path: Path) -> None:
        """Test updating repository metadata."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        repo = Repository(
            id="test/repo",
            url="https://github.com/test/repo.git",
            local_path=tmp_path / "repos" / "test/repo",
            priority=50,
            last_updated=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            skill_count=5,
            license="MIT",
        )

        store.add_repository(repo)

        # Update repository
        repo.skill_count = 10
        repo.priority = 80
        store.update_repository(repo)

        # Verify update
        updated = store.get_repository("test/repo")
        assert updated is not None
        assert updated.skill_count == 10
        assert updated.priority == 80

    def test_update_nonexistent_repository(self, tmp_path: Path) -> None:
        """Test updating non-existent repository raises error."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        repo = Repository(
            id="nonexistent",
            url="https://github.com/test/repo.git",
            local_path=tmp_path / "repos" / "test/repo",
            priority=50,
            last_updated=datetime.now(UTC),
            skill_count=5,
            license="MIT",
        )

        with pytest.raises(ValueError, match="Repository not found"):
            store.update_repository(repo)

    def test_delete_repository(self, tmp_path: Path) -> None:
        """Test deleting repository."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        repo = Repository(
            id="test/repo",
            url="https://github.com/test/repo.git",
            local_path=tmp_path / "repos" / "test/repo",
            priority=50,
            last_updated=datetime.now(UTC),
            skill_count=5,
            license="MIT",
        )

        store.add_repository(repo)
        assert store.get_repository("test/repo") is not None

        store.delete_repository("test/repo")
        assert store.get_repository("test/repo") is None

    def test_delete_nonexistent_repository(self, tmp_path: Path) -> None:
        """Test deleting non-existent repository raises error."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        with pytest.raises(ValueError, match="Repository not found"):
            store.delete_repository("nonexistent")

    def test_has_data(self, tmp_path: Path) -> None:
        """Test checking if database has data."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        assert not store.has_data()

        repo = Repository(
            id="test/repo",
            url="https://github.com/test/repo.git",
            local_path=tmp_path / "repos" / "test/repo",
            priority=50,
            last_updated=datetime.now(UTC),
            skill_count=5,
            license="MIT",
        )

        store.add_repository(repo)
        assert store.has_data()

    def test_migrate_from_json(self, tmp_path: Path) -> None:
        """Test migrating repositories from JSON to SQLite."""
        # Create JSON file with repository data
        json_file = tmp_path / "repos.json"
        json_data = {
            "repositories": [
                {
                    "id": "test/repo1",
                    "url": "https://github.com/test/repo1.git",
                    "local_path": str(tmp_path / "repos" / "test/repo1"),
                    "priority": 50,
                    "last_updated": "2024-01-01T12:00:00",
                    "skill_count": 5,
                    "license": "MIT",
                },
                {
                    "id": "test/repo2",
                    "url": "https://github.com/test/repo2.git",
                    "local_path": str(tmp_path / "repos" / "test/repo2"),
                    "priority": 80,
                    "last_updated": "2024-01-02T12:00:00",
                    "skill_count": 10,
                    "license": "Apache-2.0",
                },
            ]
        }

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Migrate to SQLite
        store = MetadataStore(db_path=tmp_path / "test.db")
        count = store.migrate_from_json(json_file)

        assert count == 2

        # Verify migration
        repos = store.list_repositories()
        assert len(repos) == 2
        assert repos[0].id == "test/repo2"  # Sorted by priority
        assert repos[0].priority == 80
        assert repos[1].id == "test/repo1"
        assert repos[1].priority == 50

    def test_migrate_from_nonexistent_json(self, tmp_path: Path) -> None:
        """Test migration from non-existent JSON file."""
        store = MetadataStore(db_path=tmp_path / "test.db")
        count = store.migrate_from_json(tmp_path / "nonexistent.json")
        assert count == 0

    def test_migrate_skips_duplicates(self, tmp_path: Path) -> None:
        """Test migration skips duplicate entries."""
        json_file = tmp_path / "repos.json"
        json_data = {
            "repositories": [
                {
                    "id": "test/repo1",
                    "url": "https://github.com/test/repo1.git",
                    "local_path": str(tmp_path / "repos" / "test/repo1"),
                    "priority": 50,
                    "last_updated": "2024-01-01T12:00:00",
                    "skill_count": 5,
                    "license": "MIT",
                },
            ]
        }

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        store = MetadataStore(db_path=tmp_path / "test.db")

        # First migration
        count1 = store.migrate_from_json(json_file)
        assert count1 == 1

        # Second migration should skip duplicate
        count2 = store.migrate_from_json(json_file)
        assert count2 == 0

        # Verify only one repository exists
        repos = store.list_repositories()
        assert len(repos) == 1

    def test_duplicate_add_raises_error(self, tmp_path: Path) -> None:
        """Test adding duplicate repository raises error."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        repo = Repository(
            id="test/repo",
            url="https://github.com/test/repo.git",
            local_path=tmp_path / "repos" / "test/repo",
            priority=50,
            last_updated=datetime.now(UTC),
            skill_count=5,
            license="MIT",
        )

        store.add_repository(repo)

        # Try to add duplicate
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            store.add_repository(repo)

    def test_skill_methods_not_implemented(self, tmp_path: Path) -> None:
        """Test skill methods raise NotImplementedError."""
        store = MetadataStore(db_path=tmp_path / "test.db")

        with pytest.raises(NotImplementedError):
            store.add_skill("skill-id", {})

        with pytest.raises(NotImplementedError):
            store.get_skill("skill-id")

        with pytest.raises(NotImplementedError):
            store.list_skills()
