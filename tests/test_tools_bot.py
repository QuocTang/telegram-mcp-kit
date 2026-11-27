"""Tests for telegram_mcp_kit.tools.bot."""

from telegram_mcp_kit.tools.bot import get_bot_info


async def test_get_bot_info(mock_client):
    mock_client.get_me.return_value = {"id": 123, "is_bot": True, "username": "test_bot"}
    result = await get_bot_info()
    assert result["is_bot"] is True
    assert result["username"] == "test_bot"
