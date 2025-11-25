# Contributing to mcp-skillset

Thank you for your interest in contributing to mcp-skillset!

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- pip

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-skillset.git
cd mcp-skillset

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -m mcp_skills.cli.main --version
```

## Development Workflow

### 1. Auto-Fix Linting Issues

Before every commit, run:

```bash
make lint-fix
```

This will:
- Auto-fix ruff linting issues
- Format code with black

### 2. Run Quality Checks

Before submitting a PR:

```bash
make quality
```

This runs:
- Code linting (ruff)
- Code formatting check (black)
- Type checking (mypy)
- Tests with coverage (pytest)

### 3. Run Tests

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/test_toolchain_detector.py

# Run with verbose output
pytest tests/ -v
```

## Code Quality Standards

### Type Hints

All functions must have type hints:

```python
def process_skill(skill_id: str) -> Optional[Skill]:
    """Process a skill by ID."""
    ...
```

### Docstrings

All public functions and classes need docstrings (Google style):

```python
def search_skills(query: str, limit: int = 10) -> list[Skill]:
    """Search for skills using natural language query.

    Args:
        query: Search query text
        limit: Maximum number of results

    Returns:
        List of matching Skill objects

    Raises:
        ValueError: If query is empty
    """
    ...
```

### Test Coverage

- Minimum 85% test coverage required
- All new features need tests
- Use pytest fixtures from `tests/conftest.py`

## Project Structure

```
mcp-skillset/
├── src/mcp_skills/       # Main package
│   ├── cli/              # CLI commands
│   ├── services/         # Core services
│   ├── models/           # Pydantic models
│   └── utils/            # Utilities
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── pyproject.toml        # Package configuration
```

## Commit Guidelines

Follow conventional commits:

```
feat: add skill recommendation engine
fix: resolve vector search timeout
docs: update installation guide
test: add toolchain detector tests
chore: bump version to 0.2.0
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run `make quality` to ensure all checks pass
5. Commit with conventional commits format
6. Push and create a pull request

## Release Process

Releases are managed through version bumping:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
python scripts/manage_version.py bump patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/manage_version.py bump minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/manage_version.py bump major

# Build release
make safe-release-build
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
