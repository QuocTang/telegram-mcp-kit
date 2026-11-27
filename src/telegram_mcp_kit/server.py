"""Telegram MCP Server - Entrypoint."""

import logging
import warnings

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.tools import discover_tools
from telegram_mcp_kit.tools._base import mcp

discover_tools()

logger = logging.getLogger(__name__)

_ALIASES = {"http": "streamable-http", "streamable_http": "streamable-http"}
SSE_DEPRECATION = (
    "MCP_TRANSPORT=sse uses the HTTP+SSE transport, which the MCP specification marks as "
    "deprecated (2026-07-28, SEP-2596). Use MCP_TRANSPORT=streamable-http instead."
)


def resolve_transport(value: str) -> str:
    """Normalize MCP_TRANSPORT to a transport name accepted by ``MCPServer.run``.

    ``http`` is accepted as an alias of ``streamable-http``. ``sse`` is kept for
    existing deployments and emits a ``DeprecationWarning``.

    Raises:
        ValueError: If the value is not a known transport.
    """
    name = _ALIASES.get(value.strip().lower(), value.strip().lower())
    if name not in ("stdio", "sse", "streamable-http"):
        raise ValueError(f"Unknown MCP_TRANSPORT {value!r}; use stdio or streamable-http")
    if name == "sse":
        warnings.warn(SSE_DEPRECATION, DeprecationWarning, stacklevel=2)
        logger.warning(SSE_DEPRECATION)
    return name


def main():
    """Start the MCP server with the transport chosen by MCP_TRANSPORT.

    ``stdio`` (default) serves a local client. ``streamable-http`` is the network
    transport; ``host`` and ``port`` (MCP_HOST, MCP_PORT) apply to it and to the
    deprecated ``sse`` transport.
    """
    transport = resolve_transport(settings.mcp_transport)
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=transport,
            host=settings.mcp_host,
            port=settings.mcp_port,
        )
