"""Tests for telegram_mcp_kit.tools.bot."""

import json

from telegram_mcp_kit.tools.bot import get_bot_info


async def test_get_bot_info(mock_client):
    mock_client.get_me.return_value = {"id": 123, "is_bot": True, "username": "test_bot"}
    result = await get_bot_info()
    parsed = json.loads(result)
    assert parsed["is_bot"] is True
    assert parsed["username"] == "test_bot"
