"""Telegram MCP Server - Entrypoint."""

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.tools import discover_tools
from telegram_mcp_kit.tools._base import mcp

discover_tools()


def main():
    mcp.run(transport=settings.mcp_transport)
