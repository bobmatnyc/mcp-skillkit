# Setup Command Integration Analysis

**Date**: 2025-11-29
**Researcher**: Research Agent
**Project**: mcp-skillset
**Objective**: Analyze gap between current `setup` and `install` commands, compare with mcp-ticketer reference implementation

---

## Executive Summary

**GAP IDENTIFIED**: The `mcp-skillset setup` command does NOT automatically call `install` for detected agents, while `mcp-ticketer setup` DOES automatically install for detected platforms. This is a **critical missing integration** that creates a poor first-run user experience.

**Impact**:
- Users must manually run TWO commands: `mcp-skillset setup` then `mcp-skillset install`
- Setup appears "complete" but MCP server is not actually accessible to agents
- Confusing UX: "What's next?" after setup completion is unclear

**Recommendation**: Integrate agent installation into `setup` command to match mcp-ticketer's smart setup behavior.

---

## Current State: mcp-skillset

### Setup Command Implementation

**File**: `src/mcp_skills/cli/main.py`
**Lines**: 48-237

**What it does**:
1. ✅ Detects project toolchain (ToolchainDetector)
2. ✅ Clones skill repositories (RepositoryManager)
3. ✅ Builds vector + KG indices (IndexingEngine)
4. ✅ Configures MCP server paths
5. ✅ Validates setup (repos, skills, indices)
6. ❌ **DOES NOT** install MCP config to agents

**Exit behavior**:
```python
# Line 211-223
if validation_ok:
    console.print("[bold green]✓ Setup complete![/bold green]\n")
    console.print("Next steps:")
    console.print("  1. [cyan]Explore skills:[/cyan] mcp-skillset demo")
    console.print("  2. [cyan]Search skills:[/cyan] mcp-skillset search 'python testing'")
    console.print("  3. [cyan]Show skill:[/cyan] mcp-skillset show <skill-id>")
    console.print("  4. [cyan]Start MCP:[/cyan] mcp-skillset mcp")
```

**Problem**: No mention of `install` command or agent integration. Users don't know they need to run `install` next.

---

### Install Command Implementation

**File**: `src/mcp_skills/cli/main.py`
**Lines**: 240-395

**What it does**:
1. ✅ Detects installed agents (AgentDetector)
2. ✅ Backs up existing configs (AgentInstaller)
3. ✅ Adds mcp-skillset to agent MCP configs
4. ✅ Updates .gitignore if found
5. ✅ Validates installation

**Key features**:
- Agent auto-detection (Claude Desktop, Claude Code, Auggie)
- Atomic config updates with rollback
- Dry-run support
- Force overwrite support
- Per-agent installation with detailed results

**Exit behavior**:
```python
# Line 377-384
if successful and not dry_run:
    console.print("[bold green]✓ Installation complete![/bold green]\n")
    console.print("Next steps:")
    console.print("  1. Restart your AI agent to load the new configuration")
    console.print("  2. The agent will automatically connect to mcp-skillset")
    console.print("  3. Skills will be available through MCP tools\n")
```

---

### AgentInstaller Service

**File**: `src/mcp_skills/services/agent_installer.py`
**Lines**: 1-513

**Key capabilities**:
- Detects agent config paths (cross-platform)
- Creates timestamped backups before modification
- Validates JSON before and after modification
- Automatic rollback on write failure
- Updates .gitignore to exclude `.mcp-skillset/`

**MCP server config**:
```python
# Line 112-116
MCP_SERVER_CONFIG = {
    "command": "mcp-skillset",
    "args": ["mcp"],
    "env": {},
}
```

---

### AgentDetector Service

**File**: `src/mcp_skills/services/agent_detector.py`
**Lines**: 1-230

**Supported agents**:
```python
# Line 71-114
AGENT_CONFIGS = [
    AgentConfig(
        name="Claude Desktop",
        id="claude-desktop",
        config_paths={
            "darwin": Path.home() / "Library" / "Application Support" / "Claude",
            "win32": Path(os.environ.get("APPDATA", "")) / "Claude",
            "linux": Path.home() / ".config" / "Claude",
        },
        config_file="claude_desktop_config.json",
    ),
    AgentConfig(
        name="Claude Code",
        id="claude-code",
        config_paths={
            "darwin": Path.home() / "Library" / "Application Support" / "Code" / "User",
            "win32": Path(os.environ.get("APPDATA", "")) / "Code" / "User",
            "linux": Path.home() / ".config" / "Code" / "User",
        },
        config_file="settings.json",
    ),
    AgentConfig(
        name="Auggie",
        id="auggie",
        config_paths={
            "darwin": Path.home() / "Library" / "Application Support" / "Auggie",
            "win32": Path(os.environ.get("APPDATA", "")) / "Auggie",
            "linux": Path.home() / ".config" / "Auggie",
        },
        config_file="config.json",
    ),
]
```

---

## Reference Implementation: mcp-ticketer

### Setup Command Implementation

**File**: `../mcp-ticketer/src/mcp_ticketer/cli/setup_command.py`
**Lines**: 195-488

**What it does**:
1. ✅ Detects existing configuration (smart state detection)
2. ✅ Auto-discovers adapter from .env files
3. ✅ Initializes adapter configuration
4. ✅ Checks/installs adapter dependencies
5. ✅ **DETECTS AND INSTALLS FOR AI PLATFORMS** ← KEY DIFFERENCE
6. ✅ Shows comprehensive next steps

**Smart setup flow**:
```python
# Line 242-277 - State detection
config_exists = config_path.exists()
config_valid = False
current_adapter = None

if config_exists and not force_reinit:
    try:
        with open(config_path) as f:
            config = json.load(f)
            current_adapter = config.get("default_adapter")
            config_valid = bool(current_adapter and config.get("adapters"))
    except (json.JSONDecodeError, OSError):
        config_valid = False

# Line 351-387 - Platform detection and installation
console.print("[bold]Step 2/2: Platform Installation[/bold]\n")

detector = PlatformDetector()
detected = detector.detect_all(project_path=proj_path)

if not detected:
    console.print("[yellow]No AI platforms detected on this system.[/yellow]")
    return

installed = [p for p in detected if p.is_installed]

console.print(f"[green]✓[/green] Detected {len(installed)} platform(s):\n")
for plat in installed:
    console.print(f"  • {plat.display_name} ({plat.scope})")
```

**Platform installation integration**:
```python
# Line 421-433 - Import configuration functions
from .auggie_configure import configure_auggie_mcp
from .codex_configure import configure_codex_mcp
from .gemini_configure import configure_gemini_mcp
from .mcp_configure import configure_claude_mcp

platform_mapping = {
    "claude-code": lambda: configure_claude_mcp(global_config=False, force=True),
    "claude-desktop": lambda: configure_claude_mcp(global_config=True, force=True),
    "auggie": lambda: configure_auggie_mcp(force=True),
    "gemini": lambda: configure_gemini_mcp(scope="project", force=True),
    "codex": lambda: configure_codex_mcp(force=True),
}

# Line 462-477 - Execute installations
for plat in platforms_to_install:
    config_func = platform_mapping.get(plat.name)
    if not config_func:
        console.print(f"[yellow]⚠[/yellow]  No installer for {plat.display_name}")
        continue

    try:
        console.print(f"[cyan]Installing for {plat.display_name}...[/cyan]")
        config_func()
        console.print(f"[green]✓[/green] {plat.display_name} configured\n")
        success_count += 1
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to configure {plat.display_name}: {e}\n")
        failed.append(plat.display_name)
```

**Exit behavior**:
```python
# Line 615-639
console.print("[bold green]🎉 Setup Complete![/bold green]\n")

console.print("[bold]Quick Start:[/bold]")
console.print("1. Create a test ticket:")
console.print("   [cyan]mcp-ticketer create 'My first ticket'[/cyan]\n")

console.print("2. List tickets:")
console.print("   [cyan]mcp-ticketer list[/cyan]\n")

console.print("[bold]Useful Commands:[/bold]")
console.print("  [cyan]mcp-ticketer doctor[/cyan]        - Validate configuration")
console.print("  [cyan]mcp-ticketer install <platform>[/cyan] - Add more platforms")
console.print("  [cyan]mcp-ticketer --help[/cyan]        - See all commands\n")
```

**Key feature**: `--skip-platforms` flag allows opting out of auto-installation:
```python
# Line 199-202
skip_platforms: bool = typer.Option(
    False,
    "--skip-platforms",
    help="Skip platform installation (only initialize adapter)",
)
```

---

## Gap Analysis

### What mcp-ticketer setup does that ours doesn't:

| Feature | mcp-ticketer | mcp-skillset | Impact |
|---------|--------------|--------------|--------|
| **Platform detection** | ✅ PlatformDetector.detect_all() | ❌ Missing | Cannot auto-install |
| **Platform installation** | ✅ Calls configure_*_mcp() | ❌ Missing | Manual install required |
| **Smart state detection** | ✅ Checks existing config | ❌ Missing | Always full setup |
| **Skip platforms option** | ✅ --skip-platforms flag | ❌ Missing | No way to skip |
| **Installation confirmation** | ✅ Prompts for platforms | ❌ Missing | No user control |
| **Dependency installation** | ✅ Checks/installs deps | ❌ Missing | Manual pip install |
| **Success/failure tracking** | ✅ Per-platform results | ❌ Missing | No installation feedback |
| **Comprehensive next steps** | ✅ Lists actual commands | ✅ Present | Good on both |

### Critical Missing Integration

**Current behavior** (mcp-skillset):
```bash
$ mcp-skillset setup
# ... setup runs ...
✓ Setup complete!

Next steps:
  1. Explore skills: mcp-skillset demo
  2. Search skills: mcp-skillset search 'python testing'
  3. Show skill: mcp-skillset show <skill-id>
  4. Start MCP: mcp-skillset mcp

# USER EXPECTATION: Setup is done, I can use it now
# REALITY: MCP server is NOT configured in any agent
# REQUIRED ACTION: User must ALSO run `mcp-skillset install`
```

**Expected behavior** (matching mcp-ticketer):
```bash
$ mcp-skillset setup
# ... setup runs ...

Step 1/5: Detecting project toolchain...
Step 2/5: Setting up skill repositories...
Step 3/5: Building skill indices...
Step 4/5: Configuring MCP server...
Step 5/5: Installing for AI agents...  ← NEW STEP

✓ Detected 2 agent(s):
  • Claude Code (project)
  • Claude Desktop (global)

Platform Installation Options:
1. Install for all detected agents
2. Select specific agent
3. Skip agent installation

Select option (1-3): 1

Installing for Claude Code...
✓ Claude Code configured

Installing for Claude Desktop...
✓ Claude Desktop configured

🎉 Setup Complete!

Quick Start:
1. Restart your AI agent
2. Ask Claude: "What skills do you have available?"
3. Skills will be accessible via MCP tools

Useful Commands:
  mcp-skillset demo            - Explore skills
  mcp-skillset install --help  - Add more agents
  mcp-skillset doctor          - Validate setup
```

---

## Code Locations Requiring Modification

### 1. Main CLI Setup Command
**File**: `src/mcp_skills/cli/main.py`
**Function**: `setup()` (lines 48-237)

**Required changes**:
- Add Step 5: Agent installation after validation
- Import AgentDetector and AgentInstaller
- Detect installed agents
- Prompt for installation options (all/specific/skip)
- Call installer.install() for selected agents
- Track success/failure per agent
- Update exit message with agent restart instructions

**New imports needed**:
```python
from mcp_skills.services.agent_detector import AgentDetector
from mcp_skills.services.agent_installer import AgentInstaller
```

**Integration point** (after line 207):
```python
console.print()

# 5. Agent installation (NEW STEP)
console.print("[bold cyan]Step 5/5:[/bold cyan] Installing for AI agents...")
detector = AgentDetector()
detected_agents = detector.detect_all()

# ... installation logic ...
```

### 2. Add --skip-agents Flag
**File**: `src/mcp_skills/cli/main.py`
**Function**: `setup()` decorator (line 48)

**Add new option**:
```python
@click.option("--skip-agents", is_flag=True, help="Skip agent installation (only setup skills)")
def setup(project_dir: str, config: str, auto: bool, skip_agents: bool) -> None:
```

### 3. Update AgentDetector (if needed)
**File**: `src/mcp_skills/services/agent_detector.py`

**Verify**:
- detect_all() returns all configured agents ✅ (already implemented)
- DetectedAgent.exists properly detects config files ✅ (already implemented)
- Cross-platform path detection works ✅ (already implemented)

**No changes needed** - service is already complete.

### 4. Update AgentInstaller (if needed)
**File**: `src/mcp_skills/services/agent_installer.py`

**Verify**:
- install() method works with dry_run ✅ (already implemented)
- install() method works with force ✅ (already implemented)
- Backup/rollback mechanism ✅ (already implemented)
- InstallResult provides detailed feedback ✅ (already implemented)

**No changes needed** - service is already complete.

---

## Recommended Implementation Approach

### Phase 1: Core Integration (Minimal Viable)

**Goal**: Get agent installation working in setup with basic UX

1. **Add agent installation step to setup**:
   - After validation (line 207), add Step 5: Agent installation
   - Detect agents with AgentDetector.detect_all()
   - Filter to existing agents only (agent.exists == True)
   - If no agents found, print info message and skip

2. **Basic installation flow**:
   - If `--auto` flag is set: Install for all without prompting
   - If interactive: Prompt "Install for all detected agents? [Y/n]"
   - If yes: Install for all, show per-agent results
   - If no: Show "Run 'mcp-skillset install' to configure agents later"

3. **Update exit message**:
   - If agents installed: Show "Restart your AI agent to load skills"
   - If agents skipped: Show "Run 'mcp-skillset install' to configure agents"

**Code example**:
```python
# After line 207 in setup()
console.print()

# 5. Agent installation
console.print("[bold cyan]Step 5/5:[/bold cyan] Installing for AI agents...")
detector = AgentDetector()
all_agents = detector.detect_all()
found_agents = [a for a in all_agents if a.exists]

if not found_agents:
    console.print("  [yellow]⚠[/yellow] No AI agents detected")
    console.print("  [dim]Run 'mcp-skillset install' after installing Claude Desktop or Claude Code[/dim]\n")
else:
    console.print(f"  ✓ Found {len(found_agents)} agent(s):")
    for agent in found_agents:
        console.print(f"    • {agent.name}")

    # Prompt for installation (unless --auto)
    should_install = auto or click.confirm("\n  Install mcp-skillset for these agents?", default=True)

    if should_install:
        console.print()
        installer = AgentInstaller()
        results = []

        for agent in found_agents:
            result = installer.install(agent, force=False, dry_run=False)
            results.append(result)

            if result.success:
                console.print(f"  [green]✓[/green] {result.agent_name}")
            else:
                console.print(f"  [red]✗[/red] {result.agent_name}: {result.error}")

        successful = [r for r in results if r.success]
        console.print(f"\n  Installed for {len(successful)}/{len(found_agents)} agent(s)")
    else:
        console.print("\n  [dim]Skipped. Run 'mcp-skillset install' to configure agents later[/dim]")

console.print()

# Update exit message based on installation results...
```

### Phase 2: Enhanced UX (Match mcp-ticketer)

**Goal**: Full feature parity with mcp-ticketer setup

1. **Add --skip-agents flag**:
   ```python
   @click.option("--skip-agents", is_flag=True, help="Skip agent installation")
   def setup(project_dir: str, config: str, auto: bool, skip_agents: bool) -> None:
   ```

2. **Add smart state detection**:
   - Check if agents already have mcp-skillset configured
   - Show "Already installed" status
   - Prompt for force reinstall

3. **Add installation options menu**:
   ```
   Platform Installation Options:
   1. Install for all detected agents
   2. Select specific agent
   3. Skip agent installation

   Select option (1-3):
   ```

4. **Add per-agent success tracking**:
   - Show backup paths for successful installations
   - Show detailed errors for failures
   - Provide summary: "2/3 succeeded, 1 failed"

5. **Add comprehensive next steps**:
   - If installed: "Restart {agent_name} to load skills"
   - Show actual usage commands: `mcp-skillset demo`, `mcp-skillset search`
   - Show troubleshooting: `mcp-skillset doctor`

### Phase 3: Advanced Features (Future)

1. **Dependency checking**: Check if mcp-skillset is installed in PATH
2. **Service validation**: Verify MCP server can start with `mcp-skillset mcp --validate`
3. **Health check**: Run doctor after setup to validate end-to-end
4. **Guided tour**: Offer to run `mcp-skillset demo` after setup

---

## Architectural Considerations

### Design Pattern: Composition over Coupling

**Good**: Current design already has perfect separation:
- `AgentDetector` - Pure detection logic, no installation
- `AgentInstaller` - Pure installation logic, no detection
- `setup()` - Orchestrates both services

**Bad**: Don't tightly couple services:
- ❌ AgentDetector should NOT call AgentInstaller
- ❌ AgentInstaller should NOT detect agents itself
- ❌ setup() should NOT duplicate detection/installation logic

**Best Practice**: Keep services focused, orchestrate in CLI command.

### Error Handling Strategy

**Current installer behavior** (already implemented):
- Backup before modify
- Validate before write
- Rollback on failure
- Return detailed InstallResult

**Setup should**:
- Continue even if agent installation fails
- Show partial success: "Installed 2/3 agents"
- Provide clear remediation steps for failures
- Never leave setup in broken state

### User Experience Principles

1. **Progressive disclosure**: Auto-install by default, allow skip with flag
2. **Smart defaults**: Install for all in --auto mode
3. **Clear feedback**: Show per-agent results, not just summary
4. **Actionable errors**: "Failed: permission denied" → "Run as admin or check permissions"
5. **Comprehensive help**: Show next steps based on actual installation outcome

---

## Testing Strategy

### Unit Tests Required

1. **Test setup with no agents**:
   - Should print info message
   - Should complete successfully
   - Should show "install manually" next step

2. **Test setup with --auto**:
   - Should skip installation prompts
   - Should install for all detected agents
   - Should show summary

3. **Test setup with --skip-agents**:
   - Should skip agent detection entirely
   - Should not call AgentInstaller
   - Should show next steps without agent references

4. **Test setup with partial failures**:
   - Mock some agents to fail installation
   - Should continue with other agents
   - Should show partial success message

### Integration Tests Required

1. **Test end-to-end setup + install**:
   - Run setup in clean environment
   - Verify agent configs are updated
   - Verify backups are created
   - Verify MCP server config is correct

2. **Test setup idempotency**:
   - Run setup twice
   - Second run should detect existing config
   - Should offer to reinstall or skip

---

## Migration Path for Existing Users

### Current User Workflow
```bash
$ mcp-skillset setup
$ mcp-skillset install  # Required but not obvious
```

### New User Workflow
```bash
$ mcp-skillset setup  # Does everything
```

### Backward Compatibility
- `install` command remains available
- `install` can be used to add new agents later
- `install` can be used to fix broken configs
- No breaking changes to existing commands

### Communication Plan
1. **Update README**: Highlight new one-command setup
2. **Update docs**: Show setup → install flow is now automatic
3. **Changelog**: Note "setup now auto-installs for agents"
4. **Migration guide**: Not needed (backward compatible)

---

## Success Criteria

### Functional Requirements
- ✅ setup detects installed agents
- ✅ setup offers to install for agents
- ✅ setup shows per-agent results
- ✅ setup handles installation failures gracefully
- ✅ setup updates exit message based on results
- ✅ --skip-agents flag works as expected
- ✅ --auto installs for all without prompting

### User Experience Requirements
- ✅ First-time users can run single command
- ✅ Installation failures don't block setup completion
- ✅ Next steps are clear and actionable
- ✅ Agent restart instructions are prominent
- ✅ Partial success is clearly communicated

### Technical Requirements
- ✅ No code duplication between setup and install
- ✅ Services remain decoupled and testable
- ✅ Error handling is comprehensive
- ✅ Existing install command remains functional
- ✅ Cross-platform compatibility maintained

---

## Conclusion

The gap is clear: **mcp-skillset setup does NOT automatically install for agents**, while **mcp-ticketer setup DOES**. This creates a poor first-run experience where users complete "setup" but the MCP server is not actually accessible to their agents.

**Root cause**: Missing integration between setup command and AgentInstaller service.

**Solution**: Add agent installation as Step 5 in setup, following mcp-ticketer's pattern of smart detection → user confirmation → installation → results summary.

**Implementation complexity**: LOW
- All required services exist (AgentDetector, AgentInstaller)
- All required functionality is implemented
- Just need to orchestrate services in setup command
- No breaking changes required

**User impact**: HIGH
- Eliminates confusing two-step setup process
- Provides clear, actionable next steps
- Matches user expectation that "setup" means "ready to use"

**Recommended approach**: Phase 1 (basic integration) first, then Phase 2 (enhanced UX) to match mcp-ticketer feature parity.

---

## Appendix: Key Code References

### mcp-skillset Files
- `src/mcp_skills/cli/main.py` - setup command (L48-237), install command (L240-395)
- `src/mcp_skills/services/agent_detector.py` - AgentDetector service
- `src/mcp_skills/services/agent_installer.py` - AgentInstaller service

### mcp-ticketer Files (Reference)
- `../mcp-ticketer/src/mcp_ticketer/cli/setup_command.py` - Smart setup with platform installation
- `../mcp-ticketer/src/mcp_ticketer/cli/platform_detection.py` - PlatformDetector (equivalent to AgentDetector)

### Implementation Examples
See code snippets throughout this document for specific implementation patterns from both projects.
