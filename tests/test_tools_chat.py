"""Tests for telegram_mcp_kit.tools.chat."""

from telegram_mcp_kit.tools.chat import (
    ban_member,
    get_chat_admins,
    get_chat_info,
    get_chat_member_count,
    pin_message,
    set_chat_description,
    set_chat_title,
    unban_member,
    unpin_message,
)


async def test_get_chat_info(mock_client):
    mock_client.get_chat.return_value = {"id": 123, "type": "group"}
    result = await get_chat_info(chat_id="123")
    assert result["type"] == "group"


async def test_get_chat_member_count(mock_client):
    mock_client.get_chat_member_count.return_value = 42
    result = await get_chat_member_count(chat_id="123")
    assert result.count == 42


async def test_get_chat_admins(mock_client):
    mock_client.get_chat_administrators.return_value = [{"user": {"id": 1}}]
    result = await get_chat_admins(chat_id="123")
    assert len(result) == 1


async def test_ban_member(mock_client, approved):
    mock_client.ban_chat_member.return_value = True
    result = await ban_member(456, chat_id="123", approval=approved)
    assert result.ok and "banned" in result.detail.lower()


async def test_unban_member(mock_client):
    mock_client.unban_chat_member.return_value = True
    result = await unban_member(456, chat_id="123")
    assert "unbanned" in result.detail.lower()


async def test_set_chat_title(mock_client, approved):
    mock_client.set_chat_title.return_value = True
    result = await set_chat_title("New Title", chat_id="123", approval=approved)
    assert "New Title" in result.detail


async def test_set_chat_description(mock_client, approved):
    mock_client.set_chat_description.return_value = True
    result = await set_chat_description("desc", chat_id="123", approval=approved)
    assert "updated" in result.detail.lower()


async def test_pin_message(mock_client):
    mock_client.pin_chat_message.return_value = True
    result = await pin_message(1, chat_id="123")
    assert "pinned" in result.detail.lower()


async def test_unpin_message(mock_client):
    mock_client.unpin_chat_message.return_value = True
    result = await unpin_message(chat_id="123", message_id=1)
    assert "unpinned" in result.detail.lower()
