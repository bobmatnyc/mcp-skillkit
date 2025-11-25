# CLI Test Suite for mcp-skillset

Comprehensive test coverage for all CLI commands using Click's CliRunner and mocked services.

## Test Structure

```
tests/cli/
├── __init__.py                 # Package marker
├── conftest.py                 # Shared fixtures (159 lines)
├── test_config.py             # Config command tests (12 tests, 222 lines)
├── test_doctor.py             # Health check tests (15 tests, 275 lines)
├── test_enrich.py             # Prompt enrichment tests (15 tests, 273 lines)
├── test_help.py               # Help/info/list tests (15 tests, 215 lines)
├── test_index.py              # Indexing tests (10 tests, 220 lines)
├── test_install.py            # Agent installation tests (11 tests, 246 lines)
├── test_mcp.py                # MCP server tests (10 tests, 182 lines)
├── test_search.py             # Search/recommend tests (17 tests, 272 lines)
└── test_setup.py              # Setup command tests (7 tests, 195 lines)
```

**Total: 112 tests across 2,613 lines of code**

## Commands Covered

1. **setup** - Auto-configuration with toolchain detection
2. **config** - Interactive and command-line configuration
3. **index** - Skill indexing operations
4. **install** - Agent installation for Claude, Cursor, etc.
5. **mcp** - MCP server startup
6. **list/info/show** - Skill listing and information display
7. **doctor/health** - Health checks and diagnostics
8. **search/recommend** - Skill search and recommendations
9. **enrich** - Prompt enrichment

## Running Tests

```bash
# Run all CLI tests
uv run pytest tests/cli/ -v

# Run specific test file
uv run pytest tests/cli/test_setup.py -v

# Run specific test
uv run pytest tests/cli/test_setup.py::TestSetupCommand::test_setup_help -v

# Run with coverage
uv run pytest tests/cli/ --cov=src/mcp_skills/cli --cov-report=html
```

## Test Patterns

### Mocking Strategy

All tests use comprehensive mocking to isolate CLI logic:

- **SkillManager**: Mocked for skill operations
- **IndexingEngine**: Mocked for indexing operations
- **RepositoryManager**: Mocked for repository management
- **ToolchainDetector**: Mocked for project detection
- **AgentInstaller**: Mocked for agent installation
- **PromptEnricher**: Mocked for prompt enrichment
- **MCPSkillsConfig**: Mocked configuration

### Test Categories

1. **Help Tests**: Verify command help text and options
2. **Success Scenarios**: Test successful command execution
3. **Error Handling**: Test graceful failure and error messages
4. **Edge Cases**: Test boundary conditions and unusual inputs
5. **Integration Points**: Test interaction between components

## Fixtures (conftest.py)

### Core Fixtures

- `cli_runner`: Click's CliRunner for command invocation
- `mock_config`: Mocked MCPSkillsConfig instance
- `mock_skill`: Sample skill for testing
- `mock_repository`: Sample repository metadata
- `mock_toolchain_info`: Sample toolchain detection result

### Service Mocks

- `mock_skill_manager`: Mocked SkillManager
- `mock_indexing_engine`: Mocked IndexingEngine
- `mock_repository_manager`: Mocked RepositoryManager
- `mock_toolchain_detector`: Mocked ToolchainDetector
- `mock_agent_installer`: Mocked AgentInstaller
- `mock_prompt_enricher`: Mocked PromptEnricher

### Utilities

- `isolated_filesystem`: Temporary filesystem for file operations

## Test Coverage by Command

| Command | Total Tests | Passing | Failing | Skipped | Pass Rate | Status |
|---------|-------------|---------|---------|---------|-----------|--------|
| config  | 12 | 12 | 0 | 0 | 100% | ✅ All passing |
| doctor  | 15 | 12 | 1 | 2 | 92% | ✅ Nearly complete |
| help    | 15 | 12 | 3 | 0 | 80% | ✅ Good coverage |
| enrich  | 15 | 6 | 7 | 2 | 46% | ⚠️ Needs mocking fixes |
| search  | 17 | 5 | 12 | 0 | 29% | ⚠️ Needs IndexingEngine mocks |
| setup   | 7 | 3 | 4 | 0 | 43% | ⚠️ Needs toolchain mocks |
| install | 11 | 3 | 8 | 0 | 27% | ⚠️ Needs agent mocks |
| index   | 10 | 1 | 9 | 0 | 10% | ❌ Needs IndexingEngine mocks |
| mcp     | 10 | 0 | 0 | 5 | N/A | ⏭️ Skipped (integration tests) |
| **Total** | **112** | **54** | **49** | **9** | **52.4%** | **In Progress** |

## Fixture Field Mappings

### Skill Model Structure (FIXED)

The `Skill` dataclass uses **flat attributes**, not nested metadata:

```python
Skill(
    id="test-skill",                    # Required
    name="Test Skill",                   # Required
    description="A test skill...",       # Required (min 10 chars)
    instructions="Full content...",      # Required (min 50 chars)
    category="testing",                  # Required
    tags=["python", "testing"],          # Optional (default: [])
    dependencies=[],                     # Optional (default: [])
    examples=["Example 1", "Example 2"], # Optional (default: [])
    file_path=Path("/path/to/skill.md"), # Required (Path object)
    repo_id="test-repo",                 # Required
    version="1.0.0",                     # Optional
    author="Test Author",                # Optional
)
```

**Common mistakes:**
- ❌ Using `metadata=SkillMetadata(...)` - SkillMetadata is separate, not nested
- ❌ Using `content=` instead of `instructions=`
- ❌ Missing required fields like `id`, `repo_id`, `examples`

### Repository Model Structure (FIXED)

The `Repository` dataclass requires all these fields:

```python
Repository(
    id="example-skills",                           # Required
    url="https://github.com/example/skills.git",   # Required
    local_path=Path("/tmp/repos/example-skills"),  # Required (Path object)
    priority=1,                                    # Required (int)
    last_updated=datetime.now(),                   # Required (datetime)
    skill_count=10,                                # Required (int)
    license="MIT",                                 # Required (str)
)
```

**Common mistakes:**
- ❌ Using Mock() with attributes instead of real Repository instance
- ❌ Missing required fields like `last_updated`, `skill_count`, `license`

### MCPSkillsConfig Structure (FIXED)

The config uses `hybrid_search` not `search`:

```python
MCPSkillsConfig(
    base_dir=Path("/path/to/.mcp-skillset"),
    repositories=[],  # Empty list OK
    hybrid_search=HybridSearchConfig(  # NOT 'search'!
        vector_weight=0.7,
        graph_weight=0.3,
    ),
)
```

**Common mistakes:**
- ❌ Using `search=` instead of `hybrid_search=`
- ❌ Using `kg_weight=` instead of `graph_weight=`

## Test Status

**Current Results (After December 2024 Fix Session):**
- **54 passing** (up from 38)
- **49 failing** (down from 65)
- **9 skipped** (unchanged)
- **0 errors** (maintained) ✅
- **Pass rate: 52.4%** (up from 34%)

**Progress Summary:**
- Fixed 16 additional tests
- All fixture errors remain resolved (44 → 0)
- Major fixes: discover_skills method names, ConfigMenu imports, Pydantic config.save issues, load_skill vs get_skill

## Known Issues and TODOs

### Remaining Test Implementation Issues

The 49 remaining failures fall into these categories:

1. **IndexingEngine mocking** (25+ tests): Search and index tests patch SkillManager but should patch IndexingEngine.search()
   - Affects: test_search.py (12 failures), test_index.py (9 failures), some test_enrich.py failures
   - Fix: Patch `@patch("mcp_skills.cli.main.IndexingEngine")` and return ScoredSkill objects

2. **Help text assertions** (5-8 tests): Tests expect specific option names that changed
   - Affects: test_help.py (3 failures), test_enrich.py (some failures), test_doctor.py (1 failure)
   - Fix: Update assertions to match actual CLI help text

3. **PromptEnricher mocking** (3-5 tests): Tests don't properly mock enrichment results
   - Affects: test_enrich.py (remaining failures)
   - Fix: Mock PromptEnricher.enrich_prompt() with proper return structure

4. **AgentInstaller mocking** (8 tests): Tests need better agent detection mocking
   - Affects: test_install.py (8 failures)
   - Fix: Mock AgentDetector and installer methods properly

5. **ToolchainDetector integration** (4 tests): Setup tests need better toolchain detection mocks
   - Affects: test_setup.py (4 failures)
   - Fix: Mock detect() method with proper ToolchainInfo return

### Skipped Tests

- MCP server tests with I/O issues (marked with `@pytest.mark.skip`)
- Integration tests requiring full system setup
- Tests requiring actual network connections

### Improvements Needed

1. Fix remaining fixture initialization issues
2. Add more integration tests for command combinations
3. Improve mock assertions to verify call arguments
4. Add tests for concurrent command execution
5. Add tests for signal handling (SIGINT, SIGTERM)

## Design Decisions

### Click CliRunner

All tests use Click's `CliRunner` which provides:
- Isolated invocation context
- Captured stdout/stderr
- Exit code verification
- Input simulation
- Temporary filesystem support

### Comprehensive Mocking

External services are fully mocked because:
- Tests run quickly without I/O
- No external dependencies required
- Predictable test behavior
- Easy to test error conditions

### Test Organization

Tests are organized by command rather than by functionality:
- Easy to find tests for specific commands
- Clear test coverage per command
- Mirrors CLI command structure

## Contributing

When adding new CLI commands:

1. Create new test file: `test_<command>.py`
2. Add fixtures to `conftest.py` if needed
3. Include help, success, and error tests
4. Mock all external dependencies
5. Use descriptive test names
6. Document skipped tests

## Example Test

```python
@patch("mcp_skills.cli.main.SkillManager")
def test_search_basic(
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
    assert "Searching for" in result.output
    mock_manager.search_skills.assert_called_once()
```

## License

Same as mcp-skillset project license.
