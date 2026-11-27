"""Tests for telegram_mcp_kit.tools.messages."""

import pytest

from telegram_mcp_kit.tools.messages import (
    delete_message,
    edit_message,
    forward_message,
    send_message,
    send_rich_message,
)


async def test_send_message(mock_client):
    mock_client.send_message.return_value = {"message_id": 1, "text": "hi"}
    result = await send_message("hi", chat_id="123")
    assert result.messages[0]["message_id"] == 1
    mock_client.send_message.assert_awaited_once_with(
        "123", "hi", None, None, message_thread_id=None, reply_markup=None
    )


async def test_send_message_with_options(mock_client):
    mock_client.send_message.return_value = {"message_id": 2}
    await send_message(
        "bold", chat_id="123", parse_mode="HTML", reply_to_message_id=5, message_thread_id=8
    )
    mock_client.send_message.assert_awaited_once_with(
        "123", "bold", "HTML", 5, message_thread_id=8, reply_markup=None
    )


async def test_edit_message(mock_client):
    mock_client.edit_message_text.return_value = {"message_id": 1, "text": "edited"}
    result = await edit_message(1, "edited", chat_id="123")
    assert result["text"] == "edited"
    mock_client.edit_message_text.assert_awaited_once_with("123", 1, "edited", None)


async def test_delete_message(mock_client, approved):
    mock_client.delete_message.return_value = True
    result = await delete_message(1, chat_id="123", approval=approved)
    assert "deleted" in result.detail.lower()
    mock_client.delete_message.assert_awaited_once_with("123", 1)


async def test_forward_message(mock_client):
    mock_client.forward_message.return_value = {"message_id": 10}
    result = await forward_message("123", 1, chat_id="456")
    assert result.messages[0]["message_id"] == 10
    mock_client.forward_message.assert_awaited_once_with(
        "456", "123", 1, message_thread_id=None
    )


async def test_send_message_default_chat_id(mock_client, monkeypatch):
    monkeypatch.setattr("telegram_mcp_kit.tools._base.settings.telegram_chat_id", "999")
    mock_client.send_message.return_value = {"message_id": 3}
    result = await send_message("hello")
    assert result.messages[0]["message_id"] == 3
    mock_client.send_message.assert_awaited_once_with(
        "999", "hello", None, None, message_thread_id=None, reply_markup=None
    )


async def test_send_rich_message_markdown(mock_client):
    mock_client.send_rich_message.return_value = {"message_id": 4}
    result = await send_rich_message(markdown="# Report\n- [x] tests", chat_id="1")
    assert result.messages[0]["message_id"] == 4
    mock_client.send_rich_message.assert_awaited_once_with(
        "1", {"markdown": "# Report\n- [x] tests"}, message_thread_id=None,
        reply_to_message_id=None,
    )


async def test_send_rich_message_requires_exactly_one_body(mock_client):
    with pytest.raises(ValueError):
        await send_rich_message(chat_id="1")
    with pytest.raises(ValueError):
        await send_rich_message(markdown="a", html="<b>a</b>", chat_id="1")
