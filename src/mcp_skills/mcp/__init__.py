"""MCP Server package for mcp-skillset.

This package provides the FastMCP server implementation for skill
discovery, search, and recommendation via the Model Context Protocol (MCP).
"""

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .server import configure_services, main, mcp

__all__ = ["main", "mcp", "configure_services"]


def __getattr__(name: str) -> Any:
    """Lazy import to avoid premature module loading."""
    if name == "main":
        from .server import main

        return main
    if name == "mcp":
        from .server import mcp

        return mcp
    if name == "configure_services":
        from .server import configure_services

        return configure_services
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
