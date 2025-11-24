"""Tests for utils module (logger and utilities)."""

import logging
import tempfile
from pathlib import Path

from mcp_skills.utils import get_logger, setup_logger


class TestSetupLogger:
    """Test logger setup functionality."""

    def test_setup_logger_default_creates_logger(self):
        """Test that setup_logger creates a logger with defaults."""
        logger = setup_logger()

        assert isinstance(logger, logging.Logger)
        assert logger.name == "mcp_skills"
        assert logger.level == logging.INFO

    def test_setup_logger_with_custom_name(self):
        """Test logger creation with custom name."""
        logger = setup_logger(name="test_logger")

        assert logger.name == "test_logger"

    def test_setup_logger_with_debug_level(self):
        """Test logger with DEBUG level."""
        logger = setup_logger(level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_setup_logger_with_warning_level(self):
        """Test logger with WARNING level."""
        logger = setup_logger(level="WARNING")

        assert logger.level == logging.WARNING

    def test_setup_logger_with_error_level(self):
        """Test logger with ERROR level."""
        logger = setup_logger(level="ERROR")

        assert logger.level == logging.ERROR

    def test_setup_logger_level_case_insensitive(self):
        """Test that log level is case-insensitive."""
        logger = setup_logger(level="debug")
        assert logger.level == logging.DEBUG

        logger = setup_logger(level="InFo")
        assert logger.level == logging.INFO

    def test_setup_logger_creates_console_handler(self):
        """Test that console handler is added."""
        logger = setup_logger(name="test_console")

        # Should have at least one handler (console)
        assert len(logger.handlers) >= 1

        # Check that at least one handler is StreamHandler
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_setup_logger_with_file_handler(self):
        """Test logger with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger(name="test_file", log_file=str(log_file))

            # Should have both console and file handlers
            assert len(logger.handlers) >= 2

            # Write log message
            logger.info("Test message")

            # Verify file was created and contains message
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

    def test_setup_logger_handler_formatting(self):
        """Test that handlers have proper formatting."""
        logger = setup_logger(name="test_format")

        # All handlers should have formatter
        for handler in logger.handlers:
            assert handler.formatter is not None

            # Check format string includes expected fields
            format_str = handler.formatter._fmt
            assert "%(asctime)s" in format_str
            assert "%(name)s" in format_str
            assert "%(levelname)s" in format_str
            assert "%(message)s" in format_str

    def test_setup_logger_clears_existing_handlers(self):
        """Test that calling setup_logger again clears old handlers."""
        logger_name = "test_clear_handlers"

        # Setup logger with file handler
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file_1 = Path(tmpdir) / "test1.log"
            logger1 = setup_logger(name=logger_name, log_file=str(log_file_1))
            initial_count = len(logger1.handlers)

            # Setup again without file handler
            logger2 = setup_logger(name=logger_name)

            # Should have fewer handlers (no file handler)
            assert len(logger2.handlers) < initial_count

    def test_setup_logger_file_handler_level(self):
        """Test that file handler respects log level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test_level.log"
            logger = setup_logger(
                name="test_file_level", level="WARNING", log_file=str(log_file)
            )

            # Both console and file handlers should have WARNING level
            for handler in logger.handlers:
                assert handler.level == logging.WARNING


class TestGetLogger:
    """Test logger retrieval functionality."""

    def test_get_logger_default_name(self):
        """Test getting logger with default name."""
        logger = get_logger()

        assert isinstance(logger, logging.Logger)
        assert logger.name == "mcp_skills"

    def test_get_logger_custom_name(self):
        """Test getting logger with custom name."""
        logger = get_logger(name="custom_logger")

        assert logger.name == "custom_logger"

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns same instance for same name."""
        logger1 = get_logger(name="shared_logger")
        logger2 = get_logger(name="shared_logger")

        # Should be the exact same object
        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self):
        """Test that different names return different loggers."""
        logger1 = get_logger(name="logger_a")
        logger2 = get_logger(name="logger_b")

        assert logger1 is not logger2
        assert logger1.name != logger2.name


class TestUtilsModuleImports:
    """Test that utils module exports are correct."""

    def test_utils_exports_setup_logger(self):
        """Test that setup_logger is exported."""
        from mcp_skills.utils import setup_logger as imported_setup

        assert imported_setup is setup_logger

    def test_utils_exports_get_logger(self):
        """Test that get_logger is exported."""
        from mcp_skills.utils import get_logger as imported_get

        assert imported_get is get_logger

    def test_utils_all_contains_expected_exports(self):
        """Test that __all__ contains expected functions."""
        import mcp_skills.utils

        assert hasattr(mcp_skills.utils, "__all__")
        assert "setup_logger" in mcp_skills.utils.__all__
        assert "get_logger" in mcp_skills.utils.__all__


class TestLoggerEdgeCases:
    """Test edge cases and error handling."""

    def test_setup_logger_with_nonexistent_directory_creates_parent(self):
        """Test that log file parent directories need to be created manually."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use nested directory that doesn't exist
            log_file = Path(tmpdir) / "nested" / "dir" / "test.log"

            # Create parent directories first (FileHandler doesn't auto-create)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            logger = setup_logger(name="test_nested", log_file=str(log_file))
            logger.info("Test message")

            # File should exist
            assert log_file.exists()

    def test_logger_handles_unicode_messages(self):
        """Test that logger handles unicode characters."""
        logger = setup_logger(name="test_unicode")

        # Should not raise exception
        logger.info("Unicode test: 你好世界 🎉")
        logger.debug("Emoji: 🔥 🚀 ✨")

    def test_multiple_loggers_independent(self):
        """Test that multiple loggers maintain independence."""
        logger1 = setup_logger(name="independent_1", level="DEBUG")
        logger2 = setup_logger(name="independent_2", level="ERROR")

        assert logger1.level == logging.DEBUG
        assert logger2.level == logging.ERROR
        assert logger1.name != logger2.name
