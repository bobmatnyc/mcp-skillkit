"""Main CLI entry point for mcp-skillset."""

from __future__ import annotations

import builtins
import logging
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from mcp_skills import __version__
from mcp_skills.models.config import MCPSkillsConfig
from mcp_skills.models.repository import Repository
from mcp_skills.services.agent_detector import AgentDetector
from mcp_skills.services.agent_installer import AgentInstaller
from mcp_skills.services.indexing import IndexingEngine
from mcp_skills.services.prompt_enricher import PromptEnricher
from mcp_skills.services.repository_manager import RepositoryManager
from mcp_skills.services.skill_manager import SkillManager
from mcp_skills.services.toolchain_detector import ToolchainDetector


console = Console()
logger = logging.getLogger(__name__)

# Store builtin list to avoid shadowing in annotations
ListType = builtins.list


@click.group()
@click.version_option(version=__version__, prog_name="mcp-skillset")
def cli() -> None:
    """MCP Skills - Dynamic RAG-powered skills for code assistants.

    Provides intelligent, context-aware skills via Model Context Protocol
    using hybrid RAG (vector + knowledge graph).
    """
    pass


@cli.command()
@click.option(
    "--project-dir",
    default=".",
    type=click.Path(exists=True),
    help="Project directory to analyze",
)
@click.option(
    "--config",
    default="~/.mcp-skillset/config.yaml",
    type=click.Path(),
    help="Config file location",
)
@click.option("--auto", is_flag=True, help="Non-interactive setup with defaults")
def setup(project_dir: str, config: str, auto: bool) -> None:
    """Auto-configure mcp-skillset for your project.

    This command will:
    1. Detect your project's toolchain
    2. Clone relevant skill repositories
    3. Index skills with vector + KG
    4. Configure MCP server
    5. Validate setup
    """
    console.print("🚀 [bold green]Starting mcp-skillset setup...[/bold green]")
    console.print(f"📁 Project directory: {project_dir}")
    console.print(f"⚙️  Config location: {config}\n")

    try:
        # 1. Toolchain detection
        console.print("[bold cyan]Step 1/5:[/bold cyan] Detecting project toolchain...")
        detector = ToolchainDetector()
        project_path = Path(project_dir).resolve()
        toolchain = detector.detect(project_path)

        console.print(
            f"  ✓ Primary language: [bold]{toolchain.primary_language}[/bold]"
        )
        if toolchain.frameworks:
            console.print(f"  ✓ Frameworks: {', '.join(toolchain.frameworks)}")
        if toolchain.test_frameworks:
            console.print(
                f"  ✓ Test frameworks: {', '.join(toolchain.test_frameworks)}"
            )
        console.print(f"  ✓ Confidence: {toolchain.confidence:.0%}\n")

        # 2. Repository cloning
        console.print(
            "[bold cyan]Step 2/5:[/bold cyan] Setting up skill repositories..."
        )
        repo_manager = RepositoryManager()

        # Get default repos or prompt user
        if auto:
            repos_to_add = RepositoryManager.DEFAULT_REPOS
            console.print("  Using default repositories (--auto mode)")
        else:
            console.print("\n  Available default repositories:")
            for i, repo in enumerate(RepositoryManager.DEFAULT_REPOS, 1):
                console.print(f"    {i}. {repo['url']} (priority: {repo['priority']})")

            if click.confirm("\n  Clone default repositories?", default=True):
                repos_to_add = RepositoryManager.DEFAULT_REPOS
            else:
                repos_to_add = []
                console.print(
                    "  [dim]You can add repositories later with: mcp-skillset repo add <url>[/dim]"
                )

        # Clone repositories
        added_repos: ListType[Repository] = []
        for repo_config in repos_to_add:
            try:
                # Check if already exists
                repo_id = repo_manager._generate_repo_id(repo_config["url"])
                existing = repo_manager.get_repository(repo_id)

                if existing:
                    console.print(
                        f"  ⊙ Repository already exists: {repo_config['url']}"
                    )
                    added_repos.append(existing)
                else:
                    console.print(f"  + Cloning: {repo_config['url']}")
                    new_repo = repo_manager.add_repository(
                        url=repo_config["url"],
                        priority=repo_config["priority"],
                        license=repo_config["license"],
                    )
                    added_repos.append(new_repo)
                    console.print(f"    ✓ Cloned {new_repo.skill_count} skills")
            except Exception as e:
                console.print(
                    f"    [red]✗ Failed to clone {repo_config['url']}: {e}[/red]"
                )
                logger.error(f"Repository clone failed: {e}")

        if not added_repos:
            console.print(
                "\n  [yellow]No repositories configured. Add some with: mcp-skillset repo add <url>[/yellow]"
            )

        console.print()

        # 3. Indexing
        console.print("[bold cyan]Step 3/5:[/bold cyan] Building skill indices...")
        skill_manager = SkillManager()
        indexing_engine = IndexingEngine(skill_manager=skill_manager)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("  Indexing skills...", total=None)
            try:
                stats = indexing_engine.reindex_all(force=True)
                progress.update(task, completed=True)
                console.print(f"  ✓ Indexed {stats.total_skills} skills")
                console.print(f"  ✓ Vector store: {stats.vector_store_size // 1024} KB")
                console.print(
                    f"  ✓ Knowledge graph: {stats.graph_nodes} nodes, {stats.graph_edges} edges\n"
                )
            except Exception as e:
                progress.stop()
                console.print(f"  [red]✗ Indexing failed: {e}[/red]")
                logger.error(f"Indexing failed: {e}")

        # 4. MCP configuration
        console.print("[bold cyan]Step 4/5:[/bold cyan] Configuring MCP server...")
        base_dir = Path.home() / ".mcp-skillset"
        console.print(f"  ✓ Base directory: {base_dir}")
        console.print(f"  ✓ ChromaDB: {base_dir / 'chromadb'}")
        console.print(f"  ✓ Repositories: {base_dir / 'repos'}\n")

        # 5. Validation
        console.print("[bold cyan]Step 5/5:[/bold cyan] Validating setup...")
        repos = repo_manager.list_repositories()
        skills = skill_manager.discover_skills()

        validation_ok = True
        if not repos:
            console.print("  [red]✗ No repositories configured[/red]")
            validation_ok = False
        else:
            console.print(f"  ✓ {len(repos)} repositories configured")

        if not skills:
            console.print("  [red]✗ No skills discovered[/red]")
            validation_ok = False
        else:
            console.print(f"  ✓ {len(skills)} skills available")

        if stats.total_skills == 0:
            console.print("  [red]✗ No skills indexed[/red]")
            validation_ok = False
        else:
            console.print(f"  ✓ {stats.total_skills} skills indexed")

        console.print()

        # Summary
        if validation_ok:
            console.print("[bold green]✓ Setup complete![/bold green]\n")
            console.print("Next steps:")
            console.print("  1. Start MCP server: [cyan]mcp-skillset mcp[/cyan]")
            console.print(
                "  2. Search skills: [cyan]mcp-skillset search 'python testing'[/cyan]"
            )
            console.print(
                "  3. Get recommendations: [cyan]mcp-skillset recommend[/cyan]"
            )
        else:
            console.print(
                "[bold yellow]⚠ Setup completed with warnings[/bold yellow]\n"
            )
            console.print(
                "Please check the errors above and run setup again if needed."
            )

    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"\n[red]Setup failed: {e}[/red]")
        logger.exception("Setup failed")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--agent",
    type=click.Choice(["claude-desktop", "claude-code", "auggie", "all"]),
    default="all",
    help="Which agent to install for",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be installed without making changes",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing mcp-skillset configuration",
)
def install(agent: str, dry_run: bool, force: bool) -> None:
    """Install MCP SkillSet for AI agents with auto-detection.

    Automatically detects installed AI agents (Claude Desktop, Claude Code, Auggie)
    and configures them to use mcp-skillset as an MCP server.

    The command will:
    1. Scan for installed AI agents on your system
    2. Backup existing configuration files
    3. Add mcp-skillset to the agent's MCP server configuration
    4. Validate the changes

    Use --dry-run to preview changes without modifying files.
    Use --force to overwrite existing mcp-skillset configuration.

    Examples:
        mcp-skillset install                    # Install for all detected agents
        mcp-skillset install --agent claude-desktop  # Install for specific agent
        mcp-skillset install --dry-run          # Preview changes
        mcp-skillset install --force            # Overwrite existing config
    """
    console.print("🔍 [bold green]MCP SkillSet Agent Installer[/bold green]\n")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    try:
        # Detect agents
        console.print("[bold cyan]Step 1/3:[/bold cyan] Detecting AI agents...")
        detector = AgentDetector()

        if agent == "all":
            detected_agents = detector.detect_all()
        else:
            single_agent = detector.detect_agent(agent)
            detected_agents = [single_agent] if single_agent else []

        if not detected_agents:
            console.print(f"[red]No agents found for: {agent}[/red]")
            console.print("\nSupported agents:")
            console.print("  • Claude Desktop - https://claude.ai/download")
            console.print(
                "  • Claude Code (VS Code) - Install from VS Code marketplace"
            )
            console.print("  • Auggie - https://auggie.app")
            return

        # Display detected agents
        found_agents = [a for a in detected_agents if a.exists]
        not_found = [a for a in detected_agents if not a.exists]

        if found_agents:
            console.print(f"\n[green]✓[/green] Found {len(found_agents)} agent(s):")
            for a in found_agents:
                console.print(f"  • {a.name}: {a.config_path}")
        else:
            console.print("\n[yellow]No installed agents found[/yellow]")

        if not_found:
            console.print(f"\n[dim]Not found ({len(not_found)}):[/dim]")
            for a in not_found:
                console.print(f"  • {a.name}")

        if not found_agents:
            console.print(
                "\nPlease install an AI agent first, then run this command again."
            )
            return

        console.print()

        # Confirmation (unless --force or --dry-run)
        if (
            not force
            and not dry_run
            and not click.confirm(
                f"Install mcp-skillset for {len(found_agents)} agent(s)?",
                default=True,
            )
        ):
            console.print("[yellow]Installation cancelled[/yellow]")
            return

        # Install for each agent
        console.print("[bold cyan]Step 2/3:[/bold cyan] Installing mcp-skillset...")
        installer = AgentInstaller()
        results = []

        for detected_agent in found_agents:
            result = installer.install(detected_agent, force=force, dry_run=dry_run)
            results.append(result)

            if result.success:
                console.print(f"  [green]✓[/green] {result.agent_name}")
                if result.backup_path:
                    console.print(f"    [dim]Backup: {result.backup_path}[/dim]")
                if result.changes_made and not dry_run:
                    console.print(f"    [dim]{result.changes_made}[/dim]")
            else:
                console.print(f"  [red]✗[/red] {result.agent_name}: {result.error}")

        console.print()

        # Summary
        console.print("[bold cyan]Step 3/3:[/bold cyan] Summary")
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        if successful:
            console.print(
                f"  [green]✓[/green] Successfully installed for {len(successful)} agent(s)"
            )

        if failed:
            console.print(f"  [red]✗[/red] Failed for {len(failed)} agent(s)")

        console.print()

        # Next steps
        if successful and not dry_run:
            console.print("[bold green]✓ Installation complete![/bold green]\n")
            console.print("Next steps:")
            console.print("  1. Restart your AI agent to load the new configuration")
            console.print("  2. The agent will automatically connect to mcp-skillset")
            console.print("  3. Skills will be available through MCP tools\n")
            console.print(
                "[dim]Note: If using Claude Desktop, quit and restart the app completely.[/dim]"
            )
        elif dry_run:
            console.print("[yellow]Dry run complete - no changes were made[/yellow]\n")
            console.print("Run without --dry-run to apply these changes.")

    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"\n[red]Installation failed: {e}[/red]")
        logger.exception("Installation failed")
        raise SystemExit(1)


@cli.command()
@click.option("--dev", is_flag=True, help="Development mode")
def mcp(dev: bool) -> None:
    """Start MCP server for Claude Code integration.

    Starts the FastMCP server using stdio transport, making skills
    available to Claude Code via Model Context Protocol.

    Usage:
        mcp-skillset mcp

    The server will run in stdio mode and communicate with Claude Code.
    """
    console.print("🚀 [bold green]Starting MCP server for Claude Code...[/bold green]")
    console.print("📡 stdio transport")

    if dev:
        console.print("🔧 [yellow]Development mode enabled[/yellow]")

    # Import and configure MCP server
    from mcp_skills.mcp.server import configure_services
    from mcp_skills.mcp.server import main as mcp_main

    try:
        # Initialize services (SkillManager, IndexingEngine, ToolchainDetector, RepositoryManager)
        console.print("⚙️  Configuring services...")
        configure_services()

        console.print("✅ Services configured")
        console.print("📡 stdio transport active")
        console.print("🎯 Ready for Claude Code connection\n")

        # Start FastMCP server (blocks until terminated)
        mcp_main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Server stopped by user[/yellow]")
        raise SystemExit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Server failed to start: {e}[/red]")
        import traceback

        if dev:
            traceback.print_exc()
        raise SystemExit(1)


@cli.command()
@click.argument("query")
@click.option("--limit", type=int, default=10, help="Maximum results")
@click.option("--category", type=str, help="Filter by category")
@click.option(
    "--search-mode",
    type=click.Choice(
        ["semantic_focused", "graph_focused", "balanced", "current"],
        case_sensitive=False,
    ),
    help="Hybrid search weighting preset (overrides config file)",
)
def search(
    query: str, limit: int, category: str | None, search_mode: str | None
) -> None:
    """Search for skills using natural language query.

    Example: mcp-skillset search "testing skills for Python"

    Search Modes:
      - semantic_focused: Optimize for semantic similarity (90% vector, 10% graph)
      - graph_focused: Optimize for relationships (30% vector, 70% graph)
      - balanced: Equal weighting (50% vector, 50% graph)
      - current: Default optimized preset (70% vector, 30% graph)

    If --search-mode is not specified, loads from config.yaml or uses default.
    """
    console.print(f"🔍 [bold]Searching for:[/bold] {query}")
    if category:
        console.print(f"📁 [dim]Category filter: {category}[/dim]")
    if search_mode:
        console.print(f"⚖️  [dim]Search mode: {search_mode}[/dim]")
    console.print()

    try:
        # Initialize services with config
        skill_manager = SkillManager()

        # Load config and optionally override with CLI flag
        config = MCPSkillsConfig()
        if search_mode:
            # Override config with CLI flag
            config.hybrid_search = config._get_preset(search_mode)
            console.print(
                f"[dim]Using {search_mode} preset: "
                f"vector={config.hybrid_search.vector_weight:.1f}, "
                f"graph={config.hybrid_search.graph_weight:.1f}[/dim]\n"
            )

        indexing_engine = IndexingEngine(skill_manager=skill_manager, config=config)

        # Perform search
        results = indexing_engine.search(query, category=category, top_k=limit)

        if not results:
            console.print("[yellow]No results found[/yellow]")
            console.print("\nTry:")
            console.print("  • Using different keywords")
            console.print("  • Removing category filter")
            console.print("  • Running: mcp-skillset index --force")
            return

        # Display results in table
        table = Table(title=f"Search Results ({len(results)} found)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Tags", style="dim")

        for result in results:
            skill = result.skill
            score_str = f"{result.score:.2f}"
            tags_str = ", ".join(skill.tags[:3])  # Show first 3 tags
            if len(skill.tags) > 3:
                tags_str += f" +{len(skill.tags) - 3}"

            table.add_row(
                skill.name,
                skill.category,
                score_str,
                tags_str,
            )

        console.print(table)
        console.print("\n[dim]Use 'mcp-skillset info <skill-id>' for details[/dim]")

    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
        logger.exception("Search failed")
        raise SystemExit(1)


@cli.command()
@click.option("--category", type=str, help="Filter by category")
@click.option("--compact", is_flag=True, help="Compact output")
def list(category: str | None, compact: bool) -> None:
    """List all available skills."""
    console.print("📋 [bold]Available Skills[/bold]")
    if category:
        console.print(f"📁 [dim]Category: {category}[/dim]\n")
    else:
        console.print()

    try:
        # Initialize skill manager
        skill_manager = SkillManager()

        # Discover skills
        skills = skill_manager.discover_skills()

        # Apply category filter
        if category:
            skills = [s for s in skills if s.category == category]

        if not skills:
            console.print("[yellow]No skills found[/yellow]")
            if category:
                console.print(f"\nNo skills in category: {category}")
                console.print(
                    "Available categories: testing, debugging, refactoring, etc."
                )
            return

        # Display skills
        if compact:
            # Compact output: just names
            for skill in sorted(skills, key=lambda s: s.name):
                console.print(f"  • {skill.name} [dim]({skill.category})[/dim]")
            console.print(f"\n[dim]Total: {len(skills)} skills[/dim]")
        else:
            # Detailed table
            table = Table(title=f"Skills ({len(skills)} found)")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="bold")
            table.add_column("Category", style="magenta")
            table.add_column("Description", style="dim")
            table.add_column("Tags", style="yellow")

            for skill in sorted(skills, key=lambda s: (s.category, s.name)):
                # Truncate description
                desc = skill.description[:60]
                if len(skill.description) > 60:
                    desc += "..."

                # Show first 2 tags
                tags_str = ", ".join(skill.tags[:2])
                if len(skill.tags) > 2:
                    tags_str += f" +{len(skill.tags) - 2}"

                table.add_row(
                    skill.id,
                    skill.name,
                    skill.category,
                    desc,
                    tags_str,
                )

            console.print(table)

        console.print("\n[dim]Use 'mcp-skillset info <skill-id>' for details[/dim]")

    except Exception as e:
        console.print(f"[red]List failed: {e}[/red]")
        logger.exception("List failed")
        raise SystemExit(1)


@cli.command()
@click.argument("skill_id")
def info(skill_id: str) -> None:
    """Show detailed information about a skill.

    Example: mcp-skillset info pytest-skill
    """
    console.print(f"ℹ️  [bold]Skill Information:[/bold] {skill_id}\n")

    try:
        # Initialize skill manager
        skill_manager = SkillManager()

        # Load skill
        skill = skill_manager.load_skill(skill_id)

        if not skill:
            console.print(f"[red]Skill not found: {skill_id}[/red]")
            console.print("\nTry:")
            console.print("  • mcp-skillset list - to see all available skills")
            console.print("  • mcp-skillset search <query> - to search for skills")
            return

        # Metadata panel
        metadata_content = f"[bold cyan]Name:[/bold cyan] {skill.name}\n"
        metadata_content += f"[bold cyan]ID:[/bold cyan] {skill.id}\n"
        metadata_content += f"[bold cyan]Category:[/bold cyan] {skill.category}\n"
        metadata_content += f"[bold cyan]Repository:[/bold cyan] {skill.repo_id}\n"

        if skill.version:
            metadata_content += f"[bold cyan]Version:[/bold cyan] {skill.version}\n"
        if skill.author:
            metadata_content += f"[bold cyan]Author:[/bold cyan] {skill.author}\n"

        if skill.tags:
            metadata_content += (
                f"[bold cyan]Tags:[/bold cyan] {', '.join(skill.tags)}\n"
            )

        metadata_panel = Panel(
            metadata_content.rstrip(),
            title="Metadata",
            border_style="cyan",
        )
        console.print(metadata_panel)

        # Description panel
        desc_panel = Panel(
            skill.description,
            title="Description",
            border_style="green",
        )
        console.print(desc_panel)

        # Instructions panel (truncated)
        instructions_preview = skill.instructions[:500]
        if len(skill.instructions) > 500:
            instructions_preview += "\n\n[dim]... (truncated, see full file for complete instructions)[/dim]"

        instructions_panel = Panel(
            instructions_preview,
            title="Instructions (Preview)",
            border_style="yellow",
        )
        console.print(instructions_panel)

        # Dependencies panel (if any)
        if skill.dependencies:
            deps_content = "\n".join(f"  • {dep}" for dep in skill.dependencies)
            deps_panel = Panel(
                deps_content,
                title="Dependencies",
                border_style="magenta",
            )
            console.print(deps_panel)

        # Examples panel (if any)
        if skill.examples:
            examples_content = (
                f"\n{len(skill.examples)} example(s) available in full instructions"
            )
            examples_panel = Panel(
                examples_content,
                title="Examples",
                border_style="blue",
            )
            console.print(examples_panel)

        # File path
        console.print(f"\n[dim]File: {skill.file_path}[/dim]")

    except Exception as e:
        console.print(f"[red]Info failed: {e}[/red]")
        logger.exception("Info failed")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--search-mode",
    type=click.Choice(
        ["semantic_focused", "graph_focused", "balanced", "current"],
        case_sensitive=False,
    ),
    help="Hybrid search weighting preset (overrides config file)",
)
def recommend(search_mode: str | None) -> None:
    """Get skill recommendations for current project.

    Search Modes:
      - semantic_focused: Optimize for semantic similarity (90% vector, 10% graph)
      - graph_focused: Optimize for relationships (30% vector, 70% graph)
      - balanced: Equal weighting (50% vector, 50% graph)
      - current: Default optimized preset (70% vector, 30% graph)

    If --search-mode is not specified, loads from config.yaml or uses default.
    """
    console.print("💡 [bold]Skill Recommendations[/bold]")
    if search_mode:
        console.print(f"⚖️  [dim]Search mode: {search_mode}[/dim]")
    console.print()

    try:
        # Detect current directory toolchain
        detector = ToolchainDetector()
        current_dir = Path.cwd()
        toolchain = detector.detect(current_dir)

        # Display detected toolchain
        console.print("[bold cyan]Detected Toolchain:[/bold cyan]")
        console.print(f"  • Language: {toolchain.primary_language}")
        if toolchain.frameworks:
            console.print(f"  • Frameworks: {', '.join(toolchain.frameworks)}")
        if toolchain.test_frameworks:
            console.print(f"  • Testing: {', '.join(toolchain.test_frameworks)}")
        console.print(f"  • Confidence: {toolchain.confidence:.0%}\n")

        # Get recommendations with config
        skill_manager = SkillManager()

        # Load config and optionally override with CLI flag
        config = MCPSkillsConfig()
        if search_mode:
            # Override config with CLI flag
            config.hybrid_search = config._get_preset(search_mode)
            console.print(
                f"[dim]Using {search_mode} preset: "
                f"vector={config.hybrid_search.vector_weight:.1f}, "
                f"graph={config.hybrid_search.graph_weight:.1f}[/dim]\n"
            )

        indexing_engine = IndexingEngine(skill_manager=skill_manager, config=config)

        # Build query from toolchain
        query_parts = [toolchain.primary_language]
        query_parts.extend(toolchain.frameworks[:2])  # Add top 2 frameworks
        query = " ".join(query_parts)

        # Search for relevant skills
        results = indexing_engine.search(query, top_k=10)

        if not results:
            console.print("[yellow]No recommendations available[/yellow]")
            console.print("\nTry:")
            console.print("  • Running: mcp-skillset setup")
            console.print("  • Adding repositories: mcp-skillset repo add <url>")
            console.print("  • Rebuilding index: mcp-skillset index --force")
            return

        # Display recommendations
        table = Table(title=f"Recommended Skills ({len(results)} found)")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Relevance", justify="right", style="green")
        table.add_column("Description", style="dim")

        for result in results:
            skill = result.skill
            relevance_str = f"{result.score:.2f}"

            # Truncate description
            desc = skill.description[:50]
            if len(skill.description) > 50:
                desc += "..."

            table.add_row(
                skill.name,
                skill.category,
                relevance_str,
                desc,
            )

        console.print(table)
        console.print("\n[dim]Use 'mcp-skillset info <skill-id>' for details[/dim]")

    except Exception as e:
        console.print(f"[red]Recommendations failed: {e}[/red]")
        logger.exception("Recommendations failed")
        raise SystemExit(1)


@cli.command(name="doctor")
def doctor() -> None:
    """Check system health and status.

    Diagnoses the health of your MCP Skills installation, including:
    - ChromaDB vector store connectivity
    - Knowledge graph status
    - Repository configuration
    - Skill index status
    """
    console.print("🏥 [bold]System Health Check[/bold]\n")

    all_healthy = True

    try:
        # 1. Check ChromaDB connection
        console.print("[bold cyan]ChromaDB Vector Store:[/bold cyan]")
        try:
            skill_manager = SkillManager()
            indexing_engine = IndexingEngine(skill_manager=skill_manager)
            stats = indexing_engine.get_stats()

            if stats.total_skills > 0:
                console.print(
                    f"  [green]✓[/green] Connected ({stats.total_skills} skills indexed)"
                )
                console.print(
                    f"  [green]✓[/green] Storage: {stats.vector_store_size // 1024} KB"
                )
            else:
                console.print(
                    "  [yellow]⚠[/yellow] Connected but empty (run: mcp-skillset index)"
                )
                all_healthy = False
        except Exception as e:
            console.print(f"  [red]✗[/red] Connection failed: {e}")
            all_healthy = False

        console.print()

        # 2. Check knowledge graph
        console.print("[bold cyan]Knowledge Graph:[/bold cyan]")
        try:
            if stats.graph_nodes > 0:
                console.print(
                    f"  [green]✓[/green] {stats.graph_nodes} nodes, {stats.graph_edges} edges"
                )
            else:
                console.print(
                    "  [yellow]⚠[/yellow] Empty graph (run: mcp-skillset index)"
                )
                all_healthy = False
        except Exception as e:
            console.print(f"  [red]✗[/red] Graph check failed: {e}")
            all_healthy = False

        console.print()

        # 3. Check repository status
        console.print("[bold cyan]Repositories:[/bold cyan]")
        try:
            repo_manager = RepositoryManager()
            repos = repo_manager.list_repositories()

            if repos:
                console.print(
                    f"  [green]✓[/green] {len(repos)} repositories configured"
                )
                total_skills = sum(repo.skill_count for repo in repos)
                console.print(
                    f"  [green]✓[/green] {total_skills} total skills available"
                )
            else:
                console.print(
                    "  [yellow]⚠[/yellow] No repositories configured (run: mcp-skillset setup)"
                )
                all_healthy = False
        except Exception as e:
            console.print(f"  [red]✗[/red] Repository check failed: {e}")
            all_healthy = False

        console.print()

        # 4. Check skill index status
        console.print("[bold cyan]Skill Index:[/bold cyan]")
        try:
            skills = skill_manager.discover_skills()

            if skills:
                console.print(f"  [green]✓[/green] {len(skills)} skills discovered")
                if stats.last_indexed != "never":
                    console.print(
                        f"  [green]✓[/green] Last indexed: {stats.last_indexed}"
                    )
                else:
                    console.print(
                        "  [yellow]⚠[/yellow] Never indexed (run: mcp-skillset index)"
                    )
                    all_healthy = False
            else:
                console.print("  [yellow]⚠[/yellow] No skills discovered")
                all_healthy = False
        except Exception as e:
            console.print(f"  [red]✗[/red] Index check failed: {e}")
            all_healthy = False

        console.print()

        # Summary
        if all_healthy:
            console.print("[bold green]✓ All systems healthy[/bold green]")
        else:
            console.print("[bold yellow]⚠ Some systems need attention[/bold yellow]")
            console.print("\nRecommended actions:")
            console.print("  • Run: mcp-skillset setup")
            console.print("  • Run: mcp-skillset index --force")

    except Exception as e:
        console.print(f"\n[red]Health check failed: {e}[/red]")
        logger.exception("Health check failed")
        raise SystemExit(1)


@cli.command(name="health", hidden=True)
def health() -> None:
    """Check system health and status (deprecated: use 'doctor' instead)."""
    console.print(
        "[yellow]Warning: 'health' is deprecated, use 'doctor' instead[/yellow]\n"
    )
    # Invoke the doctor command directly
    ctx = click.get_current_context()
    ctx.invoke(doctor)


@cli.command()
def stats() -> None:
    """Show usage statistics."""
    console.print("📊 [bold]Usage Statistics[/bold]\n")

    try:
        # Get index statistics
        skill_manager = SkillManager()
        indexing_engine = IndexingEngine(skill_manager=skill_manager)
        index_stats = indexing_engine.get_stats()

        # Get repository statistics
        repo_manager = RepositoryManager()
        repos = repo_manager.list_repositories()

        # Create statistics table
        table = Table(title="System Statistics", show_header=False)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold")

        # Index metrics
        table.add_row("Total Skills Indexed", str(index_stats.total_skills))
        table.add_row(
            "Vector Store Size", f"{index_stats.vector_store_size // 1024} KB"
        )
        table.add_row("Graph Nodes", str(index_stats.graph_nodes))
        table.add_row("Graph Edges", str(index_stats.graph_edges))

        if index_stats.last_indexed != "never":
            table.add_row("Last Indexed", index_stats.last_indexed)
        else:
            table.add_row("Last Indexed", "[yellow]Never[/yellow]")

        # Repository metrics
        table.add_row("", "")  # Separator
        table.add_row("Repositories", str(len(repos)))

        if repos:
            total_skills = sum(repo.skill_count for repo in repos)
            table.add_row("Total Skills Available", str(total_skills))

            # Repository breakdown
            console.print(table)
            console.print()

            # Repositories details
            repo_table = Table(title="Repository Details")
            repo_table.add_column("Repository", style="cyan")
            repo_table.add_column("Priority", justify="right", style="magenta")
            repo_table.add_column("Skills", justify="right", style="green")
            repo_table.add_column("Last Updated", style="dim")

            for repo in sorted(repos, key=lambda r: r.priority, reverse=True):
                repo_table.add_row(
                    repo.id,
                    str(repo.priority),
                    str(repo.skill_count),
                    repo.last_updated.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(repo_table)
        else:
            console.print(table)
            console.print("\n[yellow]No repositories configured[/yellow]")

    except Exception as e:
        console.print(f"[red]Stats failed: {e}[/red]")
        logger.exception("Stats failed")
        raise SystemExit(1)


@cli.group()
def repo() -> None:
    """Manage skill repositories."""
    pass


@repo.command("add")
@click.argument("url")
@click.option("--priority", type=int, default=50, help="Repository priority")
def repo_add(url: str, priority: int) -> None:
    """Add a new skill repository.

    Example: mcp-skillset repo add https://github.com/user/skills.git
    """
    console.print(f"➕ [bold]Adding repository:[/bold] {url}")
    console.print(f"📊 Priority: {priority}\n")

    try:
        repo_manager = RepositoryManager()

        # Add repository
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Cloning repository...", total=None)
            try:
                repo = repo_manager.add_repository(url, priority=priority)
                progress.update(task, completed=True)

                console.print("[green]✓[/green] Repository added successfully")
                console.print(f"  • ID: {repo.id}")
                console.print(f"  • Skills: {repo.skill_count}")
                console.print(f"  • License: {repo.license}")
                console.print(f"  • Path: {repo.local_path}")

                # Suggest reindexing
                console.print(
                    "\n[dim]Tip: Run 'mcp-skillset index' to index new skills[/dim]"
                )

            except ValueError as e:
                progress.stop()
                console.print(f"[red]✗ Failed to add repository: {e}[/red]")
                raise SystemExit(1)

    except Exception as e:
        console.print(f"[red]Failed to add repository: {e}[/red]")
        logger.exception("Repository add failed")
        raise SystemExit(1)


@repo.command("list")
def repo_list() -> None:
    """List all configured repositories."""
    console.print("📚 [bold]Configured Repositories[/bold]\n")

    try:
        repo_manager = RepositoryManager()
        repos = repo_manager.list_repositories()

        if not repos:
            console.print("[yellow]No repositories configured[/yellow]")
            console.print("\nAdd repositories with:")
            console.print("  mcp-skillset repo add <url>")
            console.print("\nOr run setup:")
            console.print("  mcp-skillset setup")
            return

        # Display repositories in table
        table = Table(title=f"Repositories ({len(repos)} configured)")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("URL", style="blue")
        table.add_column("Priority", justify="right", style="magenta")
        table.add_column("Skills", justify="right", style="green")
        table.add_column("Last Updated", style="dim")

        for repo in repos:
            table.add_row(
                repo.id,
                repo.url,
                str(repo.priority),
                str(repo.skill_count),
                repo.last_updated.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

        # Summary
        total_skills = sum(repo.skill_count for repo in repos)
        console.print(
            f"\n[dim]Total: {len(repos)} repositories, {total_skills} skills[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Failed to list repositories: {e}[/red]")
        logger.exception("Repository list failed")
        raise SystemExit(1)


@repo.command("update")
@click.argument("repo_id", required=False)
def repo_update(repo_id: str | None) -> None:
    """Update repositories (pull latest changes).

    If repo_id is provided, update only that repository.
    Otherwise, update all repositories.
    """
    try:
        repo_manager = RepositoryManager()

        if repo_id:
            # Update single repository
            console.print(f"🔄 [bold]Updating repository:[/bold] {repo_id}\n")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Pulling latest changes...", total=None)
                try:
                    repo = repo_manager.update_repository(repo_id)
                    progress.update(task, completed=True)

                    console.print("[green]✓[/green] Repository updated successfully")
                    console.print(f"  • ID: {repo.id}")
                    console.print(f"  • Skills: {repo.skill_count}")
                    console.print(
                        f"  • Last updated: {repo.last_updated.strftime('%Y-%m-%d %H:%M')}"
                    )

                except ValueError as e:
                    progress.stop()
                    console.print(f"[red]✗ Update failed: {e}[/red]")
                    raise SystemExit(1)

        else:
            # Update all repositories
            console.print("🔄 [bold]Updating all repositories...[/bold]\n")

            repos = repo_manager.list_repositories()

            if not repos:
                console.print("[yellow]No repositories configured[/yellow]")
                return

            updated_count = 0
            failed_count = 0
            new_skills = 0

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                for repo in repos:
                    task = progress.add_task(f"Updating {repo.id}...", total=None)
                    try:
                        old_skill_count = repo.skill_count
                        updated_repo = repo_manager.update_repository(repo.id)
                        progress.update(task, completed=True)

                        updated_count += 1
                        skill_diff = updated_repo.skill_count - old_skill_count
                        new_skills += skill_diff

                        if skill_diff > 0:
                            console.print(
                                f"  [green]✓[/green] {repo.id}: +{skill_diff} new skills"
                            )
                        elif skill_diff < 0:
                            console.print(
                                f"  [yellow]✓[/yellow] {repo.id}: {skill_diff} skills removed"
                            )
                        else:
                            console.print(f"  [green]✓[/green] {repo.id}: up to date")

                    except Exception as e:
                        progress.stop()
                        console.print(f"  [red]✗[/red] {repo.id}: {e}")
                        failed_count += 1
                        progress = Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console,
                        )
                        progress.start()

            console.print()
            console.print("[bold]Summary:[/bold]")
            console.print(f"  • Updated: {updated_count}/{len(repos)} repositories")
            if failed_count > 0:
                console.print(f"  • Failed: {failed_count}")
            if new_skills != 0:
                console.print(f"  • New skills: {new_skills}")

            if updated_count > 0:
                console.print(
                    "\n[dim]Tip: Run 'mcp-skillset index' to reindex updated skills[/dim]"
                )

    except Exception as e:
        console.print(f"[red]Update failed: {e}[/red]")
        logger.exception("Repository update failed")
        raise SystemExit(1)


@cli.command()
@click.option("--incremental", is_flag=True, help="Index only new/changed skills")
@click.option("--force", is_flag=True, help="Force full reindex")
def index(incremental: bool, force: bool) -> None:
    """Rebuild skill indices (vector + knowledge graph).

    By default, performs incremental indexing.
    Use --force for full reindex.
    """
    if force:
        console.print("🔨 [bold]Full reindex (forced)[/bold]\n")
    elif incremental:
        console.print("🔨 [bold]Incremental indexing[/bold]\n")
    else:
        console.print("🔨 [bold]Indexing skills...[/bold]\n")

    try:
        # Initialize services
        skill_manager = SkillManager()
        indexing_engine = IndexingEngine(skill_manager=skill_manager)

        # Perform indexing with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Building indices...", total=None)

            try:
                # Reindex (force=True clears existing indices first)
                stats = indexing_engine.reindex_all(force=force)
                progress.update(task, completed=True)

                # Display results
                console.print("[green]✓[/green] Indexing complete\n")

                # Statistics table
                table = Table(title="Indexing Statistics", show_header=False)
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="bold")

                table.add_row("Skills Indexed", str(stats.total_skills))
                table.add_row(
                    "Vector Store Size", f"{stats.vector_store_size // 1024} KB"
                )
                table.add_row("Graph Nodes", str(stats.graph_nodes))
                table.add_row("Graph Edges", str(stats.graph_edges))
                table.add_row("Last Indexed", stats.last_indexed)

                console.print(table)

                if stats.total_skills == 0:
                    console.print("\n[yellow]No skills were indexed[/yellow]")
                    console.print("\nPossible reasons:")
                    console.print(
                        "  • No repositories configured (run: mcp-skillset setup)"
                    )
                    console.print("  • Repositories are empty")
                    console.print("  • No SKILL.md files found")

            except Exception as e:
                progress.stop()
                console.print(f"[red]✗ Indexing failed: {e}[/red]")
                logger.exception("Indexing failed")
                raise SystemExit(1)

    except Exception as e:
        console.print(f"[red]Indexing failed: {e}[/red]")
        logger.exception("Indexing failed")
        raise SystemExit(1)


@cli.command()
@click.argument("prompt", nargs=-1, required=True)
@click.option(
    "--max-skills",
    default=3,
    type=int,
    help="Maximum number of skills to include (default: 3)",
)
@click.option(
    "--detailed",
    is_flag=True,
    help="Include full skill instructions (default: brief summaries)",
)
@click.option(
    "--threshold",
    default=0.7,
    type=float,
    help="Relevance threshold 0.0-1.0 (default: 0.7)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Save enriched prompt to file",
)
@click.option(
    "--copy",
    is_flag=True,
    help="Copy enriched prompt to clipboard (requires pyperclip)",
)
def enrich(
    prompt: tuple[str, ...],
    max_skills: int,
    detailed: bool,
    threshold: float,
    output: str | None,
    copy: bool,
) -> None:
    """Enrich a prompt with relevant skill instructions.

    Automatically finds and injects relevant skill knowledge into your prompt
    to provide better context for AI assistants.

    The command extracts keywords from your prompt, searches for relevant skills,
    and formats an enriched prompt with skill instructions.

    Examples:

        # Basic enrichment with top 3 skills
        mcp-skillset enrich "Create a REST API with authentication"

        # Include more skills and full details
        mcp-skillset enrich "Write tests for user service" --max-skills 5 --detailed

        # Save to file
        mcp-skillset enrich "Deploy to AWS" --output prompt.md

        # Copy to clipboard
        mcp-skillset enrich "Optimize database queries" --copy

        # Quoted prompts for complex sentences
        mcp-skillset enrich "Create a FastAPI endpoint that validates user input and returns JSON"
    """
    # Join prompt tuple into single string
    prompt_text = " ".join(prompt)

    console.print("🔍 [bold]Enriching prompt...[/bold]\n")
    console.print(f"[dim]Prompt: {prompt_text}[/dim]\n")

    try:
        # Initialize services
        skill_manager = SkillManager()
        enricher = PromptEnricher(skill_manager)

        # Step 1: Extract keywords
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Extracting keywords...", total=None)
            keywords = enricher.extract_keywords(prompt_text)
            progress.update(task, completed=True)

        console.print(
            f"  [green]✓[/green] Extracted keywords: {', '.join(keywords[:5])}"
        )
        if len(keywords) > 5:
            console.print(f"    [dim]... and {len(keywords) - 5} more[/dim]")

        # Step 2: Search for skills
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching skills...", total=None)
            skills = enricher.search_skills(keywords, max_skills)
            progress.update(task, completed=True)

        console.print(f"  [green]✓[/green] Found {len(skills)} relevant skill(s)")

        if not skills:
            console.print(
                "\n[yellow]No relevant skills found. Try different keywords or lower the threshold.[/yellow]"
            )
            console.print("\nSuggestions:")
            console.print("  • Use more specific technical terms")
            console.print("  • Try --threshold 0.5 for broader results")
            console.print("  • Run: mcp-skillset search <keywords> to test")
            return

        # Step 3: Enrich prompt
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Enriching prompt...", total=None)
            result = enricher.enrich(
                prompt_text,
                max_skills=max_skills,
                detailed=detailed,
            )
            progress.update(task, completed=True)

        console.print("  [green]✓[/green] Enrichment complete\n")

        # Display enriched prompt
        console.print("─" * 80)
        console.print(result.enriched_text)
        console.print("─" * 80)

        # Handle output options
        saved_to_file = False
        copied_to_clipboard = False

        if output:
            try:
                output_path = Path(output)
                enricher.save_to_file(result.enriched_text, output_path)
                console.print(f"\n[green]✓[/green] Saved to: {output_path}")
                saved_to_file = True
            except OSError as e:
                console.print(f"\n[red]✗ Failed to save file: {e}[/red]")

        if copy:
            if enricher.copy_to_clipboard(result.enriched_text):
                console.print("\n[green]✓[/green] Copied to clipboard")
                copied_to_clipboard = True
            else:
                console.print(
                    "\n[yellow]⚠ Clipboard copy failed (install pyperclip: pip install pyperclip)[/yellow]"
                )

        # Summary
        console.print(
            f"\n[dim]Enriched with {len(result.skills_found)} skill(s) "
            f"({len(skills)} candidates, threshold: {threshold})[/dim]"
        )
        console.print(f"[dim]Keywords: {', '.join(result.keywords[:10])}[/dim]")

        if not saved_to_file and not copied_to_clipboard:
            console.print(
                "\n[dim]Tip: Use --output FILE to save or --copy to clipboard[/dim]"
            )

    except Exception as e:
        console.print(f"\n[red]Enrichment failed: {e}[/red]")
        logger.exception("Enrichment failed")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--show",
    is_flag=True,
    help="Display current configuration (read-only)",
)
@click.option(
    "--set",
    "set_value",
    type=str,
    help="Set configuration value (format: key=value)",
)
def config(show: bool, set_value: str | None) -> None:
    """Configure mcp-skillset settings interactively.

    By default, opens an interactive menu for configuration.
    Use --show to display current configuration (backward compatible).
    Use --set to change values non-interactively.

    Examples:
        mcp-skillset config                    # Interactive menu
        mcp-skillset config --show            # Display configuration
        mcp-skillset config --set base_dir=/custom/path
        mcp-skillset config --set search_mode=balanced
    """
    # Handle --set flag (non-interactive)
    if set_value:
        _handle_set_config(set_value)
        return

    # Handle --show flag (read-only display)
    if show:
        _display_configuration()
        return

    # Default: Interactive menu
    try:
        from mcp_skills.cli.config_menu import ConfigMenu

        menu = ConfigMenu()
        menu.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration cancelled by user[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"\n[red]Configuration failed: {e}[/red]")
        logger.exception("Configuration failed")
        raise SystemExit(1)


def _display_configuration() -> None:
    """Display current configuration (--show flag).

    This is the original config command behavior, preserved for
    backward compatibility.
    """
    console.print("⚙️  [bold]Current Configuration[/bold]\n")

    try:
        from mcp_skills.models.config import MCPSkillsConfig

        config = MCPSkillsConfig()
        base_dir = config.base_dir

        # Create configuration tree
        tree = Tree("[bold cyan]mcp-skillset Configuration[/bold cyan]")

        # Base directory
        base_node = tree.add(f"📁 Base Directory: [yellow]{base_dir}[/yellow]")

        # Repositories
        repos_dir = config.repos_dir
        repos_node = base_node.add(f"📚 Repositories: [yellow]{repos_dir}[/yellow]")

        try:
            repo_manager = RepositoryManager()
            repos = repo_manager.list_repositories()

            if repos:
                for repo in sorted(repos, key=lambda r: r.priority, reverse=True):
                    repo_info = f"{repo.id} (priority: {repo.priority}, skills: {repo.skill_count})"
                    repos_node.add(f"[green]✓[/green] {repo_info}")
            else:
                repos_node.add("[dim]No repositories configured[/dim]")
        except Exception as e:
            repos_node.add(f"[red]Error loading repositories: {e}[/red]")

        # Vector store
        chromadb_dir = base_dir / "chromadb"
        vector_node = base_node.add(f"🔍 Vector Store: [yellow]{chromadb_dir}[/yellow]")

        try:
            skill_manager = SkillManager()
            indexing_engine = IndexingEngine(skill_manager=skill_manager)
            stats = indexing_engine.get_stats()

            if stats.total_skills > 0:
                vector_node.add(f"[green]✓[/green] {stats.total_skills} skills indexed")
                vector_node.add(
                    f"[green]✓[/green] Size: {stats.vector_store_size // 1024} KB"
                )
            else:
                vector_node.add("[dim]Empty (run: mcp-skillset index)[/dim]")
        except Exception as e:
            vector_node.add(f"[red]Error: {e}[/red]")

        # Knowledge graph
        graph_node = base_node.add("🕸️  Knowledge Graph")

        try:
            if stats.graph_nodes > 0:
                graph_node.add(f"[green]✓[/green] {stats.graph_nodes} nodes")
                graph_node.add(f"[green]✓[/green] {stats.graph_edges} edges")
            else:
                graph_node.add("[dim]Empty (run: mcp-skillset index)[/dim]")
        except Exception as e:
            graph_node.add(f"[red]Error: {e}[/red]")

        # Hybrid search settings
        search_node = base_node.add("⚖️  Hybrid Search")
        preset = config.hybrid_search.preset or "custom"
        search_node.add(f"[green]✓[/green] Mode: {preset}")
        search_node.add(
            f"[green]✓[/green] Vector weight: {config.hybrid_search.vector_weight:.1f}"
        )
        search_node.add(
            f"[green]✓[/green] Graph weight: {config.hybrid_search.graph_weight:.1f}"
        )

        # Metadata file
        metadata_file = base_dir / "repos.json"
        metadata_node = base_node.add(f"📄 Metadata: [yellow]{metadata_file}[/yellow]")

        if metadata_file.exists():
            metadata_node.add("[green]✓[/green] Exists")
        else:
            metadata_node.add("[dim]Not created yet[/dim]")

        console.print(tree)

        # Additional info
        console.print()
        console.print("[bold]Environment:[/bold]")
        console.print(f"  • Python: [cyan]{Path.home()}[/cyan]")
        console.print(f"  • Working directory: [cyan]{Path.cwd()}[/cyan]")

    except Exception as e:
        console.print(f"[red]Failed to display configuration: {e}[/red]")
        logger.exception("Config display failed")
        raise SystemExit(1)


def _handle_set_config(set_value: str) -> None:
    """Handle --set flag for non-interactive configuration changes.

    Args:
        set_value: Configuration key=value pair

    Supported keys:
        - base_dir: Base directory path
        - search_mode: Search mode preset (semantic_focused, graph_focused, balanced, current)
    """
    import yaml

    try:
        # Parse key=value
        if "=" not in set_value:
            console.print("[red]Invalid format. Use: key=value[/red]")
            console.print("\nExamples:")
            console.print("  --set base_dir=/custom/path")
            console.print("  --set search_mode=balanced")
            raise SystemExit(1)

        key, value = set_value.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Load existing config
        config_path = Path.home() / ".mcp-skillset" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        existing_config: dict = {}
        if config_path.exists():
            with open(config_path) as f:
                existing_config = yaml.safe_load(f) or {}

        # Handle different keys
        if key == "base_dir":
            base_path = Path(value).expanduser()
            base_path.mkdir(parents=True, exist_ok=True)
            existing_config["base_dir"] = str(base_path)
            console.print(f"[green]✓[/green] Base directory set to: {base_path}")

        elif key == "search_mode":
            from mcp_skills.models.config import MCPSkillsConfig

            # Validate preset
            try:
                preset_config = MCPSkillsConfig._get_preset(value)
                existing_config["hybrid_search"] = {
                    "preset": value,
                    "vector_weight": preset_config.vector_weight,
                    "graph_weight": preset_config.graph_weight,
                }
                console.print(
                    f"[green]✓[/green] Search mode set to: {value} "
                    f"(vector={preset_config.vector_weight:.1f}, "
                    f"graph={preset_config.graph_weight:.1f})"
                )
            except ValueError as e:
                console.print(f"[red]Invalid search mode: {e}[/red]")
                raise SystemExit(1)

        else:
            console.print(f"[red]Unknown configuration key: {key}[/red]")
            console.print("\nSupported keys:")
            console.print("  • base_dir - Base directory path")
            console.print("  • search_mode - Search mode preset")
            raise SystemExit(1)

        # Save updated config
        with open(config_path, "w") as f:
            yaml.dump(existing_config, f, default_flow_style=False, sort_keys=False)

        console.print(f"\n[dim]Configuration saved to {config_path}[/dim]")

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Failed to set configuration: {e}[/red]")
        logger.exception("Config set failed")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
