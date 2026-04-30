"""Tests for tool auto-discovery."""

from telegram_mcp_kit.tools import discover_tools
from telegram_mcp_kit.tools._base import mcp


def test_discover_tools_registers_all():
    """After discover_tools(), all 20 tools should be registered on the mcp instance."""
    discover_tools()
    tools = list(mcp._tool_manager._tools.keys())

    expected = [
        "send_message",
        "edit_message",
        "delete_message",
        "forward_message",
        "get_updates",
        "get_chat_info",
        "get_chat_member_count",
        "get_chat_admins",
        "ban_member",
        "unban_member",
        "set_chat_title",
        "set_chat_description",
        "pin_message",
        "unpin_message",
        "send_photo",
        "send_photo_file",
        "send_document",
        "send_document_file",
        "get_file_info",
        "get_bot_info",
    ]
    for name in expected:
        assert name in tools, f"Tool {name!r} not found after discover_tools()"
