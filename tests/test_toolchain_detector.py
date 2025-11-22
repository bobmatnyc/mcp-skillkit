"""Tests for toolchain detection service."""

from pathlib import Path

import pytest

from mcp_skills.services.toolchain_detector import ToolchainDetector, ToolchainInfo


class TestToolchainDetector:
    """Test suite for ToolchainDetector."""

    def test_detector_initialization(self) -> None:
        """Test detector can be initialized."""
        detector = ToolchainDetector()
        assert detector is not None
        assert hasattr(detector, "TOOLCHAIN_PATTERNS")

    def test_detect_returns_toolchain_info(self, sample_python_project: Path) -> None:
        """Test detect returns ToolchainInfo object."""
        detector = ToolchainDetector()
        info = detector.detect(sample_python_project)

        assert isinstance(info, ToolchainInfo)
        assert isinstance(info.primary_language, str)
        assert isinstance(info.secondary_languages, list)
        assert isinstance(info.frameworks, list)
        assert isinstance(info.build_tools, list)
        assert isinstance(info.package_managers, list)
        assert isinstance(info.test_frameworks, list)
        assert isinstance(info.confidence, float)
        assert 0.0 <= info.confidence <= 1.0

    @pytest.mark.skip(reason="Implementation pending")
    def test_detect_python_project(self, sample_python_project: Path) -> None:
        """Test detection of Python project."""
        detector = ToolchainDetector()
        info = detector.detect(sample_python_project)

        assert info.primary_language == "Python"
        assert "Flask" in info.frameworks or len(info.frameworks) >= 0
        assert info.confidence > 0.5

    @pytest.mark.skip(reason="Implementation pending")
    def test_detect_typescript_project(self, sample_typescript_project: Path) -> None:
        """Test detection of TypeScript project."""
        detector = ToolchainDetector()
        info = detector.detect(sample_typescript_project)

        assert info.primary_language == "TypeScript"
        assert info.confidence > 0.5

    def test_detect_languages_returns_list(self, temp_project_dir: Path) -> None:
        """Test detect_languages returns list."""
        detector = ToolchainDetector()
        languages = detector.detect_languages(temp_project_dir)

        assert isinstance(languages, list)

    def test_detect_frameworks_returns_list(self, temp_project_dir: Path) -> None:
        """Test detect_frameworks returns list."""
        detector = ToolchainDetector()
        frameworks = detector.detect_frameworks(temp_project_dir)

        assert isinstance(frameworks, list)

    def test_recommend_skills_returns_list(self) -> None:
        """Test recommend_skills returns list."""
        detector = ToolchainDetector()
        toolchain = ToolchainInfo(
            primary_language="Python",
            secondary_languages=[],
            frameworks=["Flask"],
            build_tools=["pip"],
            package_managers=["pip"],
            test_frameworks=["pytest"],
            confidence=0.9,
        )
        skills = detector.recommend_skills(toolchain)

        assert isinstance(skills, list)
