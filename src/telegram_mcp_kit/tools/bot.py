"""Bot info tools: get_bot_info."""

from typing import Any

from telegram_mcp_kit.tools._base import get_client, tool


@tool("read")
async def get_bot_info() -> dict[str, Any]:
    """Get information about the bot (name, username, etc.)."""
    return await get_client().get_me()
