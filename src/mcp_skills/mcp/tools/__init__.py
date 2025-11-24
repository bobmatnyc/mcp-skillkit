"""MCP tools for skill management.

This package contains all MCP tool implementations for the
mcp-skills server. Tools are automatically registered with
FastMCP when imported.
"""

# Import all tool modules to register them with FastMCP
from . import skill_tools  # noqa: F401


__all__ = ["skill_tools"]
