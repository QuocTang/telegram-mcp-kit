"""Telegram MCP Server - Entrypoint."""

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.tools import discover_tools
from telegram_mcp_kit.tools._base import mcp

discover_tools()


def main():
    """Start the MCP server with the transport chosen by MCP_TRANSPORT.

    ``host`` and ``port`` (MCP_HOST, MCP_PORT) apply only to the HTTP transports
    ``sse`` and ``streamable-http``; ``stdio`` accepts no transport options.
    """
    if settings.mcp_transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=settings.mcp_transport,
            host=settings.mcp_host,
            port=settings.mcp_port,
        )
