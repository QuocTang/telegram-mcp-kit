"""Tests for telegram_mcp_kit.tools.updates."""

import json

from telegram_mcp_kit.tools.updates import get_updates


async def test_get_updates(mock_client):
    mock_client.get_updates.return_value = [{"update_id": 1, "message": {"text": "hello"}}]
    result = await get_updates()
    assert result.structured_content["updates"][0]["update_id"] == 1
    assert json.loads(result.content[0].text)[0]["update_id"] == 1


async def test_get_updates_with_offset(mock_client):
    mock_client.get_updates.return_value = []
    result = await get_updates(offset=100, limit=10)
    assert result.structured_content["updates"] == []
    mock_client.get_updates.assert_awaited_once_with(100, 10, ["message"])
