.PHONY: help lint-fix quality pre-publish safe-release-build clean test install dev-install

help:
	@echo "MCP Skills - Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install package in development mode"
	@echo "  make dev-install   - Install with dev dependencies"
	@echo "  make lint-fix      - Auto-fix linting issues (ruff + black)"
	@echo "  make test          - Run tests with coverage"
	@echo ""
	@echo "Quality Gates:"
	@echo "  make quality       - Run comprehensive quality checks"
	@echo "  make pre-publish   - Quality checks + secret detection"
	@echo "  make safe-release-build - Full quality gate + build"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Remove build artifacts"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

lint-fix:
	@echo "🔧 Running ruff check with auto-fix..."
	ruff check --fix src/ tests/
	@echo "🎨 Running black formatter..."
	black src/ tests/
	@echo "✅ Linting and formatting complete"

test:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src/mcp_skills --cov-report=term-missing --cov-report=html
	@echo "✅ Tests complete"

quality:
	@echo "📊 Running comprehensive quality checks..."
	@echo ""
	@echo "1️⃣  Checking code formatting..."
	ruff check src/ tests/
	black --check src/ tests/
	@echo ""
	@echo "2️⃣  Running type checks..."
	mypy src/
	@echo ""
	@echo "3️⃣  Running tests with coverage..."
	pytest tests/ --cov=src/mcp_skills --cov-report=term-missing --cov-fail-under=85
	@echo ""
	@echo "✅ All quality checks passed"

pre-publish: quality
	@echo "🔐 Running secret detection..."
	detect-secrets scan
	@echo "✅ Pre-publish checks complete"

safe-release-build: pre-publish
	@echo "📦 Building distribution packages..."
	python -m build
	@echo "✅ Release build complete"
	@echo ""
	@echo "📦 Distribution files created in dist/"
	@ls -lh dist/

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

.DEFAULT_GOAL := help
