"""MCP server implementation for exposing skills to code assistants.

DEPRECATED: This module is kept for backward compatibility.
Use mcp_skills.mcp.server instead for the FastMCP-based implementation.
"""

from pathlib import Path
from typing import Any

from ..mcp.server import configure_services, main, mcp


class MCPSkillsServer:
    """Main MCP server implementation (DEPRECATED).

    This class is deprecated and maintained only for backward compatibility.
    New code should use the FastMCP-based implementation in mcp_skills.mcp.server.

    The new implementation provides:
    - FastMCP SDK integration
    - 5 MCP tools: search_skills, get_skill, recommend_skills,
      list_categories, reindex_skills
    - Hybrid RAG search (70% vector + 30% knowledge graph)
    - Global service management pattern
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize MCP server (DEPRECATED).

        Args:
            config: Server configuration dictionary (ignored)

        Note:
            This constructor is deprecated. Use configure_services()
            from mcp_skills.mcp.server instead.
        """
        self.config = config or {}

        # Configure services using default paths
        base_dir = Path.home() / ".mcp-skillset"
        configure_services(base_dir=base_dir)

    async def start(self, transport: str = "stdio") -> None:
        """Start MCP server (DEPRECATED).

        Args:
            transport: Transport protocol (stdio only supported)

        Note:
            This method is deprecated. Use main() from
            mcp_skills.mcp.server instead.
        """
        if transport != "stdio":
            raise ValueError("Only stdio transport is supported")

        # Start the FastMCP server
        main()


# Export new implementation for direct import
__all__ = ["MCPSkillsServer", "configure_services", "main", "mcp"]
