"""Main CLI entry point for mcp-skills."""

import click
from rich.console import Console

from mcp_skills import __version__


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="mcp-skills")
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
    default="~/.mcp-skills/config.yaml",
    type=click.Path(),
    help="Config file location",
)
@click.option("--auto", is_flag=True, help="Non-interactive setup with defaults")
def setup(project_dir: str, config: str, auto: bool) -> None:
    """Auto-configure mcp-skills for your project.

    This command will:
    1. Detect your project's toolchain
    2. Clone relevant skill repositories
    3. Index skills with vector + KG
    4. Configure MCP server
    5. Validate setup
    """
    console.print("🚀 [bold green]Starting mcp-skills setup...[/bold green]")
    console.print(f"📁 Project directory: {project_dir}")
    console.print(f"⚙️  Config location: {config}")

    # TODO: Implement setup workflow
    # 1. Toolchain detection
    # 2. Repository cloning
    # 3. Indexing
    # 4. MCP configuration
    # 5. Validation

    console.print("\n[yellow]⚠️  Setup implementation coming soon![/yellow]")
    console.print(
        "\n[dim]This will detect toolchain, clone repos, build indices, "
        "and configure MCP.[/dim]"
    )


@cli.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport protocol (stdio for Claude Code, http for web clients)",
)
@click.option("--port", type=int, default=8000, help="Port for HTTP transport")
@click.option("--dev", is_flag=True, help="Development mode (auto-reload)")
def serve(transport: str, port: int, dev: bool) -> None:
    """Start the MCP server.

    Exposes skills to code assistants via Model Context Protocol.
    """
    console.print(f"🚀 [bold green]Starting MCP server ({transport})...[/bold green]")

    if transport == "http":
        console.print(f"🌐 HTTP server on port {port}")
    else:
        console.print("📡 stdio transport (for Claude Code)")

    if dev:
        console.print("🔧 [yellow]Development mode - auto-reload enabled[/yellow]")

    # TODO: Implement MCP server startup
    console.print("\n[yellow]⚠️  Server implementation coming soon![/yellow]")


@cli.command()
@click.argument("query")
@click.option("--limit", type=int, default=10, help="Maximum results")
@click.option("--category", type=str, help="Filter by category")
def search(query: str, limit: int, category: str | None) -> None:
    """Search for skills using natural language query.

    Example: mcp-skills search "testing skills for Python"
    """
    console.print(f"🔍 [bold]Searching for:[/bold] {query}")
    if category:
        console.print(f"📁 [dim]Category filter: {category}[/dim]")

    # TODO: Implement skill search
    console.print("\n[yellow]⚠️  Search implementation coming soon![/yellow]")


@cli.command()
@click.option("--category", type=str, help="Filter by category")
@click.option("--compact", is_flag=True, help="Compact output")
def list(category: str | None, compact: bool) -> None:
    """List all available skills."""
    console.print("📋 [bold]Available Skills[/bold]")
    if category:
        console.print(f"📁 [dim]Category: {category}[/dim]")

    # TODO: Implement skill listing
    console.print("\n[yellow]⚠️  List implementation coming soon![/yellow]")


@cli.command()
@click.argument("skill_id")
def info(skill_id: str) -> None:
    """Show detailed information about a skill.

    Example: mcp-skills info pytest-skill
    """
    console.print(f"ℹ️  [bold]Skill Information:[/bold] {skill_id}")

    # TODO: Implement skill info display
    console.print("\n[yellow]⚠️  Info implementation coming soon![/yellow]")


@cli.command()
def recommend() -> None:
    """Get skill recommendations for current project."""
    console.print("💡 [bold]Recommended Skills[/bold]")

    # TODO: Implement skill recommendations
    console.print("\n[yellow]⚠️  Recommendations implementation coming soon![/yellow]")


@cli.command()
def health() -> None:
    """Check system health and status."""
    console.print("🏥 [bold]System Health Check[/bold]")

    # TODO: Implement health checks
    # - Vector store status
    # - Knowledge graph status
    # - Repository status
    # - Index status

    console.print("\n[yellow]⚠️  Health check implementation coming soon![/yellow]")


@cli.command()
def stats() -> None:
    """Show usage statistics."""
    console.print("📊 [bold]Usage Statistics[/bold]")

    # TODO: Implement statistics display
    console.print("\n[yellow]⚠️  Statistics implementation coming soon![/yellow]")


@cli.group()
def repo() -> None:
    """Manage skill repositories."""
    pass


@repo.command("add")
@click.argument("url")
@click.option("--priority", type=int, default=50, help="Repository priority")
def repo_add(url: str, priority: int) -> None:
    """Add a new skill repository.

    Example: mcp-skills repo add https://github.com/user/skills.git
    """
    console.print(f"➕ [bold]Adding repository:[/bold] {url}")
    console.print(f"📊 Priority: {priority}")

    # TODO: Implement repository addition
    console.print("\n[yellow]⚠️  Repository add implementation coming soon![/yellow]")


@repo.command("list")
def repo_list() -> None:
    """List all configured repositories."""
    console.print("📚 [bold]Configured Repositories[/bold]")

    # TODO: Implement repository listing
    console.print("\n[yellow]⚠️  Repository list implementation coming soon![/yellow]")


@repo.command("update")
@click.argument("repo_id", required=False)
def repo_update(repo_id: str | None) -> None:
    """Update repositories (pull latest changes).

    If repo_id is provided, update only that repository.
    Otherwise, update all repositories.
    """
    if repo_id:
        console.print(f"🔄 [bold]Updating repository:[/bold] {repo_id}")
    else:
        console.print("🔄 [bold]Updating all repositories...[/bold]")

    # TODO: Implement repository update
    console.print("\n[yellow]⚠️  Repository update implementation coming soon![/yellow]")


@cli.command()
@click.option("--incremental", is_flag=True, help="Index only new/changed skills")
@click.option("--force", is_flag=True, help="Force full reindex")
def index(incremental: bool, force: bool) -> None:
    """Rebuild skill indices (vector + knowledge graph).

    By default, performs incremental indexing.
    Use --force for full reindex.
    """
    if force:
        console.print("🔨 [bold]Full reindex (forced)[/bold]")
    elif incremental:
        console.print("🔨 [bold]Incremental indexing[/bold]")
    else:
        console.print("🔨 [bold]Indexing skills...[/bold]")

    # TODO: Implement indexing
    console.print("\n[yellow]⚠️  Indexing implementation coming soon![/yellow]")


@cli.command()
def config() -> None:
    """Show current configuration."""
    console.print("⚙️  [bold]Current Configuration[/bold]")

    # TODO: Implement config display
    console.print("\n[yellow]⚠️  Config display implementation coming soon![/yellow]")


if __name__ == "__main__":
    cli()
