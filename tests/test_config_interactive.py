"""Tests for interactive configuration menu."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml

from mcp_skills.cli.config_menu import ConfigMenu
from mcp_skills.models.config import MCPSkillsConfig


class TestConfigMenu:
    """Tests for ConfigMenu class.

    Tests interactive menu navigation, configuration changes,
    and persistence logic.
    """

    @pytest.fixture
    def temp_config_path(self, tmp_path: Path) -> Path:
        """Create temporary config path for testing.

        Args:
            tmp_path: Pytest temporary directory

        Returns:
            Temporary config file path
        """
        config_dir = tmp_path / ".mcp-skillset"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"

    @pytest.fixture
    def config_menu(self, temp_config_path: Path) -> ConfigMenu:
        """Create ConfigMenu instance with temporary config path.

        Args:
            temp_config_path: Temporary config file path

        Returns:
            ConfigMenu instance
        """
        with patch.object(ConfigMenu, "CONFIG_PATH", temp_config_path):
            return ConfigMenu()

    def test_menu_initialization(self, config_menu: ConfigMenu) -> None:
        """Test menu initializes with default configuration."""
        assert config_menu.config is not None
        assert config_menu.running is True
        assert isinstance(config_menu.config, MCPSkillsConfig)

    @patch("mcp_skills.cli.config_menu.questionary.select")
    def test_menu_exit(
        self,
        mock_select: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test menu exits when user selects Exit."""
        mock_select.return_value.ask.return_value = "Exit"

        config_menu.run()

        assert config_menu.running is False
        mock_select.assert_called_once()

    @patch("mcp_skills.cli.config_menu.questionary.select")
    def test_menu_keyboard_interrupt(
        self,
        mock_select: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test menu handles Ctrl+C gracefully."""
        mock_select.return_value.ask.return_value = None  # Ctrl+C returns None

        config_menu.run()

        assert config_menu.running is False

    @patch("mcp_skills.cli.config_menu.questionary.path")
    def test_configure_base_directory(
        self,
        mock_path: MagicMock,
        config_menu: ConfigMenu,
        tmp_path: Path,
    ) -> None:
        """Test base directory configuration."""
        new_dir = tmp_path / "custom_base"
        mock_path.return_value.ask.return_value = str(new_dir)

        config_menu._configure_base_directory()

        # Verify directory was created
        assert new_dir.exists()

        # Verify config was saved
        assert config_menu.CONFIG_PATH.exists()
        with open(config_menu.CONFIG_PATH) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["base_dir"] == str(new_dir)

    @patch("mcp_skills.cli.config_menu.questionary.path")
    def test_configure_base_directory_cancelled(
        self,
        mock_path: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test base directory configuration cancellation."""
        mock_path.return_value.ask.return_value = None  # User cancelled

        original_base_dir = config_menu.config.base_dir

        config_menu._configure_base_directory()

        # Verify config unchanged
        assert config_menu.config.base_dir == original_base_dir

    @patch("mcp_skills.cli.config_menu.questionary.select")
    def test_configure_search_settings_preset(
        self,
        mock_select: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test search settings configuration with preset."""
        mock_select.return_value.ask.return_value = "balanced"

        config_menu._configure_search_settings()

        # Verify preset was applied
        assert config_menu.config.hybrid_search.preset == "balanced"
        assert config_menu.config.hybrid_search.vector_weight == 0.5
        assert config_menu.config.hybrid_search.graph_weight == 0.5

        # Verify config was saved
        assert config_menu.CONFIG_PATH.exists()
        with open(config_menu.CONFIG_PATH) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["hybrid_search"]["preset"] == "balanced"
            assert saved_config["hybrid_search"]["vector_weight"] == 0.5
            assert saved_config["hybrid_search"]["graph_weight"] == 0.5

    @patch("mcp_skills.cli.config_menu.questionary.confirm")
    @patch("mcp_skills.cli.config_menu.questionary.text")
    @patch("mcp_skills.cli.config_menu.questionary.select")
    def test_configure_custom_weights(
        self,
        mock_select: MagicMock,
        mock_text: MagicMock,
        mock_confirm: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test custom weight configuration."""
        # User selects custom mode
        mock_select.return_value.ask.return_value = "custom"

        # User enters vector weight
        mock_text.return_value.ask.return_value = "0.8"

        # User confirms weights
        mock_confirm.return_value.ask.return_value = True

        config_menu._configure_search_settings()

        # Verify weights were set (use approximate comparison for floating point)
        assert abs(config_menu.config.hybrid_search.vector_weight - 0.8) < 1e-6
        assert abs(config_menu.config.hybrid_search.graph_weight - 0.2) < 1e-6

        # Verify config was saved
        assert config_menu.CONFIG_PATH.exists()
        with open(config_menu.CONFIG_PATH) as f:
            saved_config = yaml.safe_load(f)
            assert abs(saved_config["hybrid_search"]["vector_weight"] - 0.8) < 1e-6
            assert abs(saved_config["hybrid_search"]["graph_weight"] - 0.2) < 1e-6

    def test_validate_weight_valid(self) -> None:
        """Test weight validation with valid values."""
        assert ConfigMenu._validate_weight("0.5") is True
        assert ConfigMenu._validate_weight("0.0") is True
        assert ConfigMenu._validate_weight("1.0") is True

    def test_validate_weight_invalid(self) -> None:
        """Test weight validation with invalid values."""
        result = ConfigMenu._validate_weight("1.5")
        assert isinstance(result, str)
        assert "between 0.0 and 1.0" in result

        result = ConfigMenu._validate_weight("-0.1")
        assert isinstance(result, str)

        result = ConfigMenu._validate_weight("invalid")
        assert isinstance(result, str)
        assert "valid number" in result

    def test_validate_priority_valid(self) -> None:
        """Test priority validation with valid values."""
        assert ConfigMenu._validate_priority("50") is True
        assert ConfigMenu._validate_priority("0") is True
        assert ConfigMenu._validate_priority("100") is True

    def test_validate_priority_invalid(self) -> None:
        """Test priority validation with invalid values."""
        result = ConfigMenu._validate_priority("101")
        assert isinstance(result, str)
        assert "between 0 and 100" in result

        result = ConfigMenu._validate_priority("-1")
        assert isinstance(result, str)

        result = ConfigMenu._validate_priority("invalid")
        assert isinstance(result, str)
        assert "valid integer" in result

    @patch("mcp_skills.cli.config_menu.RepositoryManager")
    @patch("mcp_skills.cli.config_menu.questionary.text")
    def test_add_repository(
        self,
        mock_text: MagicMock,
        mock_repo_manager_class: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test adding a new repository."""
        # Mock repository manager
        mock_repo_manager = MagicMock()
        mock_repo_manager_class.return_value = mock_repo_manager

        # Mock repository object
        mock_repo = Mock()
        mock_repo.id = "test-repo"
        mock_repo.skill_count = 10
        mock_repo.priority = 50
        mock_repo_manager.add_repository.return_value = mock_repo

        # Mock user inputs
        mock_text.return_value.ask.side_effect = [
            "https://github.com/test/repo.git",  # URL
            "50",  # Priority
        ]

        config_menu._add_repository()

        # Verify repository was added
        mock_repo_manager.add_repository.assert_called_once_with(
            "https://github.com/test/repo.git",
            priority=50,
        )

    @patch("mcp_skills.cli.config_menu.RepositoryManager")
    @patch("mcp_skills.cli.config_menu.questionary.confirm")
    @patch("mcp_skills.cli.config_menu.questionary.select")
    def test_remove_repository(
        self,
        mock_select: MagicMock,
        mock_confirm: MagicMock,
        mock_repo_manager_class: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test removing a repository."""
        # Mock repository manager
        mock_repo_manager = MagicMock()
        mock_repo_manager_class.return_value = mock_repo_manager

        # Mock existing repositories
        mock_repo = Mock()
        mock_repo.id = "test-repo"
        mock_repo.skill_count = 10
        mock_repo.priority = 50
        mock_repo_manager.list_repositories.return_value = [mock_repo]

        # User selects repository to remove
        mock_select.return_value.ask.return_value = "test-repo"

        # User confirms removal
        mock_confirm.return_value.ask.return_value = True

        config_menu._remove_repository()

        # Verify repository was removed
        mock_repo_manager.remove_repository.assert_called_once_with("test-repo")

    @patch("mcp_skills.cli.config_menu.questionary.confirm")
    def test_reset_to_defaults(
        self,
        mock_confirm: MagicMock,
        config_menu: ConfigMenu,
    ) -> None:
        """Test resetting configuration to defaults."""
        # Create existing config file
        with open(config_menu.CONFIG_PATH, "w") as f:
            yaml.dump({"base_dir": "/custom/path"}, f)

        # User confirms reset
        mock_confirm.return_value.ask.return_value = True

        config_menu._reset_to_defaults()

        # Verify config file was deleted
        assert not config_menu.CONFIG_PATH.exists()

        # Verify config was reloaded with defaults
        assert isinstance(config_menu.config, MCPSkillsConfig)

    def test_save_config_creates_file(
        self,
        config_menu: ConfigMenu,
    ) -> None:
        """Test config save creates file if it doesn't exist."""
        config_data = {"test_key": "test_value"}

        config_menu._save_config(config_data)

        # Verify file was created
        assert config_menu.CONFIG_PATH.exists()

        # Verify content was saved
        with open(config_menu.CONFIG_PATH) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["test_key"] == "test_value"

    def test_save_config_merges_existing(
        self,
        config_menu: ConfigMenu,
    ) -> None:
        """Test config save merges with existing configuration."""
        # Create existing config
        existing_config = {"existing_key": "existing_value"}
        with open(config_menu.CONFIG_PATH, "w") as f:
            yaml.dump(existing_config, f)

        # Save new config
        new_config = {"new_key": "new_value"}
        config_menu._save_config(new_config)

        # Verify merge
        with open(config_menu.CONFIG_PATH) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["existing_key"] == "existing_value"
            assert saved_config["new_key"] == "new_value"

    def test_save_config_deep_merge_nested_dicts(
        self,
        config_menu: ConfigMenu,
    ) -> None:
        """Test config save performs deep merge for nested dictionaries."""
        # Create existing config with nested dict
        existing_config = {
            "hybrid_search": {
                "preset": "current",
                "vector_weight": 0.7,
            }
        }
        with open(config_menu.CONFIG_PATH, "w") as f:
            yaml.dump(existing_config, f)

        # Update only graph_weight
        new_config = {
            "hybrid_search": {
                "graph_weight": 0.3,
            }
        }
        config_menu._save_config(new_config)

        # Verify deep merge preserved existing keys
        with open(config_menu.CONFIG_PATH) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["hybrid_search"]["preset"] == "current"
            assert saved_config["hybrid_search"]["vector_weight"] == 0.7
            assert saved_config["hybrid_search"]["graph_weight"] == 0.3


class TestConfigCommandFlags:
    """Tests for config command with CLI flags.

    Tests --show and --set flags for non-interactive configuration.
    """

    @pytest.fixture
    def temp_config_path(self, tmp_path: Path) -> Path:
        """Create temporary config path for testing.

        Args:
            tmp_path: Pytest temporary directory

        Returns:
            Temporary config file path
        """
        config_dir = tmp_path / ".mcp-skillset"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"

    def test_set_base_dir(self, temp_config_path: Path, tmp_path: Path) -> None:
        """Test --set flag with base_dir key."""
        from mcp_skills.cli.main import _handle_set_config

        new_base_dir = tmp_path / "custom_base"

        with patch("mcp_skills.cli.main.Path.home") as mock_home:
            mock_home.return_value = temp_config_path.parent.parent
            _handle_set_config(f"base_dir={new_base_dir}")

        # Verify directory was created
        assert new_base_dir.exists()

        # Verify config was saved
        assert temp_config_path.exists()
        with open(temp_config_path) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["base_dir"] == str(new_base_dir)

    def test_set_search_mode(self, temp_config_path: Path) -> None:
        """Test --set flag with search_mode key."""
        from mcp_skills.cli.main import _handle_set_config

        with patch("mcp_skills.cli.main.Path.home") as mock_home:
            mock_home.return_value = temp_config_path.parent.parent
            _handle_set_config("search_mode=balanced")

        # Verify config was saved
        assert temp_config_path.exists()
        with open(temp_config_path) as f:
            saved_config = yaml.safe_load(f)
            assert saved_config["hybrid_search"]["preset"] == "balanced"
            assert saved_config["hybrid_search"]["vector_weight"] == 0.5
            assert saved_config["hybrid_search"]["graph_weight"] == 0.5

    def test_set_invalid_format(self, temp_config_path: Path) -> None:
        """Test --set flag with invalid format raises error."""
        from mcp_skills.cli.main import _handle_set_config

        with patch("mcp_skills.cli.main.Path.home") as mock_home:
            mock_home.return_value = temp_config_path.parent.parent
            with pytest.raises(SystemExit):
                _handle_set_config("invalid_format")

    def test_set_unknown_key(self, temp_config_path: Path) -> None:
        """Test --set flag with unknown key raises error."""
        from mcp_skills.cli.main import _handle_set_config

        with patch("mcp_skills.cli.main.Path.home") as mock_home:
            mock_home.return_value = temp_config_path.parent.parent
            with pytest.raises(SystemExit):
                _handle_set_config("unknown_key=value")

    def test_set_invalid_search_mode(self, temp_config_path: Path) -> None:
        """Test --set flag with invalid search mode raises error."""
        from mcp_skills.cli.main import _handle_set_config

        with patch("mcp_skills.cli.main.Path.home") as mock_home:
            mock_home.return_value = temp_config_path.parent.parent
            with pytest.raises(SystemExit):
                _handle_set_config("search_mode=invalid_mode")
