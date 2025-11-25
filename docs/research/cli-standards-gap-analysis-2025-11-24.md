# CLI Standards Gap Analysis - Ticket 1M-185

**Research Date:** 2025-11-24
**Ticket:** 1M-185 - CLI Standards
**Status:** High Priority, Open
**Assignee:** claude-mpm@matsuoka.com

## Executive Summary

This analysis compares the current CLI implementation in `src/mcp_skills/cli/main.py` against the required standards defined in ticket 1M-185. The analysis reveals significant alignment in most areas, with some commands requiring modifications and a few new commands needing implementation.

**Key Findings:**
- ✅ **6/9 commands** already implemented (67%)
- ⚠️ **2/9 commands** need modifications (22%)
- ❌ **1/9 commands** missing entirely (11%)
- 🔧 **MCP tool coverage:** 3/9 commands have equivalents (33%)

## Required vs Current Commands Matrix

| Required | Current | Status | MCP Equivalent | Notes |
|----------|---------|--------|----------------|-------|
| `setup` | `setup` | ⚠️ **PARTIAL** | ❌ No | Needs --auto flag behavior refinement |
| `config` | `config` | ⚠️ **NEEDS CHANGE** | ❌ No | Currently display-only, needs menu-based setup |
| `index` | `index` | ✅ **COMPLETE** | ✅ `reindex_skills()` | Fully implements standards |
| `install` | ❌ Missing | ❌ **MISSING** | ❌ No | New command required |
| `mcp` | `mcp` | ✅ **COMPLETE** | N/A (is the server) | Fully implements standards |
| `help` | Built-in | ✅ **COMPLETE** | ❌ No | Click provides --help automatically |
| `doctor` | `health` | ✅ **RENAME ONLY** | ❌ No | Rename `health` → `doctor` |
| `search` | `search` | ✅ **COMPLETE** | ✅ `search_skills()` | Fully implements standards |
| `enrich` | ❌ Missing | ❌ **MISSING** | ❌ No | New command required |

### Additional Current Commands (Not in Requirements)

| Command | Status | Recommendation |
|---------|--------|----------------|
| `list` | ✅ Active | **KEEP** - Useful utility |
| `info` | ✅ Active | **KEEP** - Maps to MCP `get_skill()` |
| `recommend` | ✅ Active | **KEEP** - Maps to MCP `recommend_skills()` |
| `stats` | ✅ Active | **KEEP** - Useful diagnostic |
| `repo add` | ✅ Active | **KEEP** - Essential for management |
| `repo list` | ✅ Active | **KEEP** - Essential for management |
| `repo update` | ✅ Active | **KEEP** - Essential for management |

## Detailed Gap Analysis

### 1. ✅ `setup` - PARTIAL MATCH (Needs Refinement)

**Current Behavior:**
```bash
mcp-skillset setup [--project-dir DIR] [--config PATH] [--auto]
```

**Implementation:** Lines 43-230 in `main.py`

**What It Does:**
1. Detects project toolchain (ToolchainDetector)
2. Clones skill repositories (with user prompts unless --auto)
3. Builds indices (vector + KG)
4. Configures MCP server paths
5. Validates setup completion

**Gap Analysis:**
- ✅ Has automated setup capability
- ✅ Detects and updates skills
- ✅ Downloads and indexes
- ⚠️ **GAP:** `--auto` flag exists but still has minor prompts (line 104)
- ⚠️ **GAP:** Should be more aggressive about "no user interaction"

**Required Changes:**
- Strengthen `--auto` mode to eliminate ALL user prompts
- Make `--auto` the default behavior
- Move interactive prompts to `config` command

**Implementation Complexity:** 🟡 Medium (1-2 hours)

**MCP Equivalent:** ❌ None - should add `setup_project()` tool

---

### 2. ⚠️ `config` - NEEDS MAJOR CHANGES

**Current Behavior:**
```bash
mcp-skillset config
```

**Implementation:** Lines 1115-1197 in `main.py`

**What It Does:**
- Displays current configuration in tree format
- Shows repositories, vector store, knowledge graph status
- Read-only display of environment information

**Gap Analysis:**
- ❌ **CRITICAL GAP:** No menu-based setup
- ❌ **CRITICAL GAP:** No user prompts for configuration
- ❌ **CRITICAL GAP:** Display-only, not interactive

**Required Behavior:**
```
Menu-based setup that prompts users through all setup options:
1. Base directory configuration
2. Repository management
3. MCP server settings
4. Vector store configuration
5. Knowledge graph settings
```

**Required Changes:**
1. Rename current `config` → `status` or `show-config`
2. Create new `config` command with interactive menu
3. Use Click's prompt utilities for user interaction
4. Guide users through all configuration options step-by-step

**Implementation Complexity:** 🔴 High (4-6 hours)

**MCP Equivalent:** ❌ None - configuration is CLI-specific

---

### 3. ✅ `index` - COMPLETE

**Current Behavior:**
```bash
mcp-skillset index [--incremental] [--force]
```

**Implementation:** Lines 1042-1112 in `main.py`

**What It Does:**
1. Rebuilds skill indices (vector + KG)
2. Supports incremental vs. full reindex
3. Displays statistics after completion

**Gap Analysis:**
- ✅ Fully matches requirements
- ✅ Has MCP equivalent: `reindex_skills(force=bool)`

**MCP Tool:** `reindex_skills()` in `skill_tools.py` (lines 457-520)

**No Changes Required**

---

### 4. ❌ `install` - MISSING ENTIRELY

**Required Behavior:**
```
Install MCP for agents (Claude Code, Auggie, etc.) with auto-detection
```

**Current State:** Does not exist

**Expected Functionality:**
1. Auto-detect available AI assistants:
   - Claude Desktop (macOS/Windows/Linux)
   - Claude Code (VSCode extension)
   - Auggie
   - Other MCP-compatible clients
2. Modify their configuration files to add mcp-skillset server
3. Provide installation instructions for detected agents
4. Validate MCP server configuration

**Implementation Strategy:**
```python
@cli.command()
@click.option("--agent", type=click.Choice(["claude-desktop", "claude-code", "auggie", "auto"]), default="auto")
def install(agent: str) -> None:
    """Install MCP server configuration for AI agents.

    Auto-detects installed agents and configures them to use mcp-skillset.

    Supports:
    - Claude Desktop (~/.config/Claude/claude_desktop_config.json)
    - Claude Code (VSCode settings)
    - Auggie
    - Auto-detection of all available agents
    """
    # Detect installed agents
    # Modify configuration files
    # Validate installation
    # Provide restart instructions
```

**Configuration File Locations:**
- **Claude Desktop (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Desktop (Windows):** `%APPDATA%\Claude\claude_desktop_config.json`
- **Claude Desktop (Linux):** `~/.config/Claude/claude_desktop_config.json`
- **Claude Code:** VSCode settings.json + MCP configuration
- **Auggie:** TBD (need to research)

**Implementation Complexity:** 🔴 High (6-8 hours)
- Cross-platform file handling
- JSON configuration manipulation
- Agent detection logic
- Validation and error handling

**MCP Equivalent:** ❌ None - installation is CLI-specific

---

### 5. ✅ `mcp` - COMPLETE

**Current Behavior:**
```bash
mcp-skillset mcp [--dev]
```

**Implementation:** Lines 232-275 in `main.py`

**What It Does:**
1. Starts FastMCP server with stdio transport
2. Configures services (SkillManager, IndexingEngine, etc.)
3. Runs JSON-RPC server for Claude integration

**Gap Analysis:**
- ✅ Fully matches requirements
- ✅ This IS the MCP JSON-RPC command path

**No Changes Required**

---

### 6. ✅ `help` - COMPLETE (Built-in)

**Current Behavior:**
```bash
mcp-skillset --help
mcp-skillset <command> --help
```

**Implementation:** Click framework provides automatic --help

**What It Does:**
- Displays command usage
- Shows available options
- Lists all commands

**Gap Analysis:**
- ✅ Fully matches requirements
- ✅ Click provides comprehensive help automatically

**Enhancement Opportunity:**
- Could add a `help` command that provides more detailed information
- Could add tutorial/getting-started guide

**Implementation Complexity:** 🟢 Low (1 hour for enhanced help)

**MCP Equivalent:** ❌ None - help is CLI-specific

---

### 7. ✅ `doctor` - EXISTS AS `health` (Rename Required)

**Current Behavior:**
```bash
mcp-skillset health
```

**Implementation:** Lines 646-759 in `main.py`

**What It Does:**
1. Checks ChromaDB connection and status
2. Validates knowledge graph health
3. Checks repository status
4. Validates skill index status
5. Provides diagnostic recommendations

**Gap Analysis:**
- ✅ Fully implements required functionality
- ⚠️ **NAMING GAP:** Called `health` instead of `doctor`

**Required Changes:**
- Rename command: `health` → `doctor`
- Keep all existing functionality
- Optionally add `health` as alias for backwards compatibility

**Implementation Complexity:** 🟢 Trivial (5 minutes)

**MCP Equivalent:** ❌ None - should add `health_check()` tool

---

### 8. ✅ `search` - COMPLETE

**Current Behavior:**
```bash
mcp-skillset search QUERY [--limit N] [--category CAT] [--search-mode MODE]
```

**Implementation:** Lines 278-367 in `main.py`

**What It Does:**
1. Performs hybrid RAG search (70% vector, 30% graph)
2. Supports category filtering
3. Configurable search modes
4. Displays results in formatted table

**Gap Analysis:**
- ✅ Fully matches requirements
- ✅ Has MCP equivalent: `search_skills()`

**MCP Tool:** `search_skills()` in `skill_tools.py` (lines 22-138)

**No Changes Required**

---

### 9. ❌ `enrich` - MISSING ENTIRELY

**Required Behavior:**
```
Enrich a prompt (based on keywords)
```

**Current State:** Does not exist

**Expected Functionality:**
1. Accept a user prompt as input
2. Analyze prompt for relevant keywords/concepts
3. Search for relevant skills using hybrid RAG
4. Inject skill instructions into prompt
5. Return enriched prompt for AI assistant

**Use Case Example:**
```bash
# Input prompt
$ mcp-skillset enrich "Write tests for my FastAPI app"

# System behavior:
# 1. Extracts keywords: "tests", "FastAPI"
# 2. Searches for relevant skills (pytest, FastAPI testing patterns)
# 3. Injects skill instructions into prompt

# Output: Enriched prompt
Write tests for my FastAPI app

## Relevant Skills Injected:

### pytest-skill
[Full pytest skill instructions...]

### fastapi-testing
[Full FastAPI testing patterns...]
```

**Implementation Strategy:**
```python
@cli.command()
@click.argument("prompt")
@click.option("--max-skills", type=int, default=3, help="Maximum skills to inject")
@click.option("--output", type=click.Path(), help="Save enriched prompt to file")
def enrich(prompt: str, max_skills: int, output: str | None) -> None:
    """Enrich a prompt with relevant skill instructions.

    Analyzes the prompt, searches for relevant skills, and injects
    their instructions to create a knowledge-enhanced prompt.

    Example:
        mcp-skillset enrich "Write pytest tests" --max-skills 2
    """
    # 1. Parse prompt for keywords
    # 2. Search for relevant skills
    # 3. Load skill instructions
    # 4. Format enriched prompt
    # 5. Display or save to file
```

**Implementation Complexity:** 🟡 Medium (3-4 hours)
- Prompt parsing and keyword extraction
- Skill selection logic
- Template formatting for enriched output
- File I/O for saving enriched prompts

**MCP Equivalent:** ❌ None - should add `enrich_prompt()` tool

---

## MCP Tool Coverage Analysis

**Current MCP Tools:** (from `src/mcp_skills/mcp/tools/skill_tools.py`)

| MCP Tool | CLI Equivalent | Status |
|----------|----------------|--------|
| `search_skills()` | `search` | ✅ Complete |
| `get_skill()` | `info` | ✅ Complete |
| `recommend_skills()` | `recommend` | ✅ Complete |
| `list_categories()` | ❌ None | ⚠️ No CLI equivalent |
| `reindex_skills()` | `index` | ✅ Complete |

**MCP Tools Needed (Per Requirements):**

According to ticket 1M-185: "All commands should have MCP equivalents (except for mcp of course)"

| Required Command | Current MCP Tool | Gap |
|------------------|------------------|-----|
| `setup` | ❌ None | 🔴 **Need `setup_project()` tool** |
| `config` | ❌ None | 🟡 Questionable (config is CLI-specific) |
| `index` | ✅ `reindex_skills()` | ✅ Complete |
| `install` | ❌ None | 🟡 Questionable (install is CLI-specific) |
| `mcp` | N/A (is the server) | N/A |
| `help` | ❌ None | 🟡 Questionable (help is CLI-specific) |
| `doctor` | ❌ None | 🔴 **Need `health_check()` tool** |
| `search` | ✅ `search_skills()` | ✅ Complete |
| `enrich` | ❌ None | 🔴 **Need `enrich_prompt()` tool** |

### MCP Tools to Add

#### 1. `setup_project()` - High Priority
```python
@mcp.tool()
async def setup_project(
    project_path: str,
    auto_clone_repos: bool = True,
    force_reindex: bool = False
) -> dict[str, Any]:
    """Set up mcp-skillset for a project.

    Detects toolchain, clones repositories, and indexes skills.
    """
```

#### 2. `health_check()` - High Priority
```python
@mcp.tool()
async def health_check() -> dict[str, Any]:
    """Check system health and return diagnostic information.

    Returns:
        - chromadb_status
        - knowledge_graph_status
        - repository_status
        - index_status
        - recommendations
    """
```

#### 3. `enrich_prompt()` - High Priority
```python
@mcp.tool()
async def enrich_prompt(
    prompt: str,
    max_skills: int = 3,
    toolchain_filter: str | None = None
) -> dict[str, Any]:
    """Enrich a prompt with relevant skill instructions.

    Args:
        prompt: User's original prompt
        max_skills: Maximum number of skills to inject
        toolchain_filter: Optional toolchain filter

    Returns:
        - enriched_prompt: Full prompt with injected skills
        - injected_skills: List of skill IDs injected
        - relevance_scores: Relevance score for each skill
    """
```

#### 4. `list_skills()` - Medium Priority (Currently missing)
```python
@mcp.tool()
async def list_skills(
    category: str | None = None,
    toolchain: str | None = None,
    limit: int = 50
) -> dict[str, Any]:
    """List all available skills with optional filtering.

    MCP equivalent of CLI `list` command.
    """
```

---

## Implementation Roadmap

### Phase 1: Critical Gaps (High Priority)

**1. Rename `health` → `doctor`** - 🟢 Trivial
- Effort: 5 minutes
- File: `src/mcp_skills/cli/main.py` line 646
- Change: `@cli.command()` → `@cli.command("doctor")`
- Add alias: `@cli.command("health", hidden=True)` for backwards compatibility

**2. Implement `install` command** - 🔴 High
- Effort: 6-8 hours
- New command in `main.py`
- Agent detection logic
- Configuration file manipulation (JSON)
- Cross-platform support (macOS/Windows/Linux)
- Validation and error handling

**3. Implement `enrich` command** - 🟡 Medium
- Effort: 3-4 hours
- New command in `main.py`
- Keyword extraction from prompt
- Skill search and selection
- Template formatting for enriched output

**4. Refactor `config` command** - 🔴 High
- Effort: 4-6 hours
- Rename current `config` → `show-config` or `status`
- Create new interactive `config` command
- Menu-based prompts for all configuration options
- Use Click's prompt utilities

**5. Strengthen `setup --auto` mode** - 🟡 Medium
- Effort: 1-2 hours
- Remove all user prompts when `--auto` is set
- Make `--auto` the default behavior
- Move interactive prompts to `config` command

---

### Phase 2: MCP Tool Additions (Medium Priority)

**1. Add `health_check()` MCP tool** - 🟡 Medium
- Effort: 2-3 hours
- File: `src/mcp_skills/mcp/tools/skill_tools.py`
- Mirrors CLI `doctor` command functionality
- Returns structured health data

**2. Add `enrich_prompt()` MCP tool** - 🟡 Medium
- Effort: 3-4 hours
- File: `src/mcp_skills/mcp/tools/skill_tools.py`
- Mirrors CLI `enrich` command functionality
- Returns enriched prompt as JSON

**3. Add `setup_project()` MCP tool** - 🟡 Medium
- Effort: 3-4 hours
- File: `src/mcp_skills/mcp/tools/skill_tools.py`
- Mirrors CLI `setup` command functionality
- Async implementation required

**4. Add `list_skills()` MCP tool** - 🟢 Low
- Effort: 1-2 hours
- File: `src/mcp_skills/mcp/tools/skill_tools.py`
- Mirrors CLI `list` command functionality
- Simple wrapper around skill_manager.discover_skills()

---

### Phase 3: Enhancements (Low Priority)

**1. Enhanced help command** - 🟢 Low
- Effort: 1 hour
- Add `help` command with detailed guides
- Include getting-started tutorial
- Link to documentation

**2. Configuration file support** - 🟡 Medium
- Effort: 2-3 hours
- Support YAML/TOML configuration files
- CLI flag overrides
- Environment variable support

---

## Effort Summary

| Phase | Item | Complexity | Estimated Hours |
|-------|------|------------|-----------------|
| **Phase 1** | Rename `health` → `doctor` | 🟢 Trivial | 0.1 |
| | Implement `install` command | 🔴 High | 6-8 |
| | Implement `enrich` command | 🟡 Medium | 3-4 |
| | Refactor `config` command | 🔴 High | 4-6 |
| | Strengthen `setup --auto` | 🟡 Medium | 1-2 |
| **Phase 1 Total** | | | **14-20 hours** |
| **Phase 2** | Add `health_check()` tool | 🟡 Medium | 2-3 |
| | Add `enrich_prompt()` tool | 🟡 Medium | 3-4 |
| | Add `setup_project()` tool | 🟡 Medium | 3-4 |
| | Add `list_skills()` tool | 🟢 Low | 1-2 |
| **Phase 2 Total** | | | **9-13 hours** |
| **Phase 3** | Enhanced help command | 🟢 Low | 1 |
| | Configuration file support | 🟡 Medium | 2-3 |
| **Phase 3 Total** | | | **3-4 hours** |
| **GRAND TOTAL** | | | **26-37 hours** |

---

## Recommendations

### Immediate Actions (This Sprint)

1. **Quick Win:** Rename `health` → `doctor` (5 minutes)
2. **High Priority:** Implement `install` command (6-8 hours)
3. **High Priority:** Refactor `config` command (4-6 hours)

### Next Sprint

4. **Medium Priority:** Implement `enrich` command (3-4 hours)
5. **Medium Priority:** Add MCP tools (`health_check`, `enrich_prompt`, `setup_project`) (8-11 hours)
6. **Medium Priority:** Strengthen `setup --auto` (1-2 hours)

### Future Enhancements

7. **Low Priority:** Add `list_skills()` MCP tool (1-2 hours)
8. **Low Priority:** Enhanced help command (1 hour)
9. **Low Priority:** Configuration file support (2-3 hours)

---

## Commands to Deprecate

**None.** All current commands should be retained:
- `list`, `info`, `recommend`, `stats` provide valuable utility
- `repo add/list/update` are essential for repository management
- No conflicts with required command standards

---

## Code References

### Files Modified
1. `src/mcp_skills/cli/main.py` - All CLI command implementations
2. `src/mcp_skills/mcp/tools/skill_tools.py` - MCP tool implementations

### Key Line Numbers
- `setup`: Lines 43-230
- `config`: Lines 1115-1197 (needs major refactor)
- `index`: Lines 1042-1112
- `mcp`: Lines 232-275
- `health` (→ `doctor`): Lines 646-759
- `search`: Lines 278-367

### MCP Tools
- `search_skills()`: Lines 22-138
- `get_skill()`: Lines 141-216
- `recommend_skills()`: Lines 219-394
- `list_categories()`: Lines 397-453
- `reindex_skills()`: Lines 456-520

---

## Compliance Matrix

| Requirement | Status | Compliance |
|-------------|--------|------------|
| Automated setup with no user interaction | ⚠️ Partial | 80% - `--auto` flag exists but needs strengthening |
| Menu-based config prompting through all options | ❌ Missing | 0% - Current `config` is display-only |
| Index/reindex databases | ✅ Complete | 100% |
| Install MCP for agents with auto-detection | ❌ Missing | 0% |
| MCP JSON-RPC command path | ✅ Complete | 100% |
| Detailed help and information | ✅ Complete | 100% - Click provides comprehensive help |
| Check health (doctor) | ✅ Complete | 100% - Exists as `health`, needs rename |
| Vector/search based on keywords | ✅ Complete | 100% |
| Enrich a prompt | ❌ Missing | 0% |
| All commands have MCP equivalents | ⚠️ Partial | 33% - 3/9 commands have tools |

**Overall Compliance: 67%** (6/9 commands complete or near-complete)

---

## Conclusion

The current CLI implementation is **67% compliant** with ticket 1M-185 standards. Most required functionality exists, with the primary gaps being:

1. **Missing `install` command** (high complexity, 6-8 hours)
2. **Missing `enrich` command** (medium complexity, 3-4 hours)
3. **`config` needs major refactor** (high complexity, 4-6 hours)
4. **MCP tool coverage insufficient** (33% vs required 100%)

**Recommended approach:**
- Start with quick win: Rename `health` → `doctor` (5 minutes)
- Focus Phase 1 on critical gaps: `install`, `config`, `enrich` (14-20 hours)
- Add MCP tools in Phase 2 to reach 100% MCP coverage (9-13 hours)
- Total estimated effort: **26-37 hours** across 3 phases

This research provides a clear roadmap to achieve full compliance with CLI standards while maintaining backward compatibility with existing commands.
