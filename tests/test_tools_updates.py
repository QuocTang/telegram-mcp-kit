"""Tests for telegram_mcp_kit.tools.updates."""

import json

from telegram_mcp_kit.tools.updates import get_updates


async def test_get_updates(mock_client):
    mock_client.get_updates.return_value = [{"update_id": 1, "message": {"text": "hello"}}]
    result = await get_updates()
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["update_id"] == 1


async def test_get_updates_with_offset(mock_client):
    mock_client.get_updates.return_value = []
    result = await get_updates(offset=100, limit=10)
    assert json.loads(result) == []
    mock_client.get_updates.assert_awaited_once_with(100, 10, ["message"])
