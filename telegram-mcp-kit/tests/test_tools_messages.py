"""Tests for telegram_mcp_kit.tools.messages."""

import json

from telegram_mcp_kit.tools.messages import (
    delete_message,
    edit_message,
    forward_message,
    send_message,
)


async def test_send_message(mock_client):
    mock_client.send_message.return_value = {"message_id": 1, "text": "hi"}
    result = await send_message("hi", chat_id="123")
    parsed = json.loads(result)
    assert parsed["message_id"] == 1
    mock_client.send_message.assert_awaited_once_with("123", "hi", None, None)


async def test_send_message_with_options(mock_client):
    mock_client.send_message.return_value = {"message_id": 2}
    await send_message("bold", chat_id="123", parse_mode="HTML", reply_to_message_id=5)
    mock_client.send_message.assert_awaited_once_with("123", "bold", "HTML", 5)


async def test_edit_message(mock_client):
    mock_client.edit_message_text.return_value = {"message_id": 1, "text": "edited"}
    result = await edit_message(1, "edited", chat_id="123")
    parsed = json.loads(result)
    assert parsed["text"] == "edited"
    mock_client.edit_message_text.assert_awaited_once_with("123", 1, "edited", None)


async def test_delete_message(mock_client):
    mock_client.delete_message.return_value = True
    result = await delete_message(1, chat_id="123")
    assert "deleted" in result.lower()
    mock_client.delete_message.assert_awaited_once_with("123", 1)


async def test_forward_message(mock_client):
    mock_client.forward_message.return_value = {"message_id": 10}
    result = await forward_message("123", 1, chat_id="456")
    parsed = json.loads(result)
    assert parsed["message_id"] == 10
    mock_client.forward_message.assert_awaited_once_with("456", "123", 1)


async def test_send_message_default_chat_id(mock_client, monkeypatch):
    monkeypatch.setattr("telegram_mcp_kit.tools._base.settings.telegram_chat_id", "999")
    mock_client.send_message.return_value = {"message_id": 3}
    result = await send_message("hello")
    parsed = json.loads(result)
    assert parsed["message_id"] == 3
    mock_client.send_message.assert_awaited_once_with("999", "hello", None, None)
