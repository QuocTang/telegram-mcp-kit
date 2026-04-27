"""Update tools: get_updates."""

import json

from telegram_mcp_kit.tools._base import get_client, mcp


@mcp.tool()
async def get_updates(
    offset: int | None = None,
    limit: int = 100,
) -> str:
    """Get recent messages/updates received by the bot.

    Args:
        offset: Update ID offset (to get updates after a specific ID)
        limit: Maximum number of updates to return (1-100, default 100)
    """
    results = await get_client().get_updates(offset, limit, ["message"])
    return json.dumps(results, ensure_ascii=False, indent=2)
