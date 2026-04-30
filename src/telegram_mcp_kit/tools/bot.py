"""Bot info tools: get_bot_info."""

import json

from telegram_mcp_kit.tools._base import get_client, mcp


@mcp.tool()
async def get_bot_info() -> str:
    """Get information about the bot (name, username, etc.)."""
    result = await get_client().get_me()
    return json.dumps(result, ensure_ascii=False, indent=2)
