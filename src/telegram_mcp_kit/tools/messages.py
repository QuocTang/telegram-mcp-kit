"""Message tools: send, edit, delete, forward."""

import json

from telegram_mcp_kit.tools._base import get_client, mcp, resolve_chat_id


@mcp.tool()
async def send_message(
    text: str,
    chat_id: str | None = None,
    parse_mode: str | None = None,
    reply_to_message_id: int | None = None,
) -> str:
    """Send a text message to a Telegram chat.

    Args:
        text: Message text (supports Markdown/HTML based on parse_mode)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" (optional)
        reply_to_message_id: ID of message to reply to (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_message(cid, text, parse_mode, reply_to_message_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def edit_message(
    message_id: int,
    text: str,
    chat_id: str | None = None,
    parse_mode: str | None = None,
) -> str:
    """Edit an existing message.

    Args:
        message_id: ID of the message to edit
        text: New text for the message
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().edit_message_text(cid, message_id, text, parse_mode)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def delete_message(message_id: int, chat_id: str | None = None) -> str:
    """Delete a message from a chat.

    Args:
        message_id: ID of the message to delete
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().delete_message(cid, message_id)
    return "Message deleted successfully."


@mcp.tool()
async def forward_message(
    from_chat_id: str, message_id: int, chat_id: str | None = None
) -> str:
    """Forward a message from one chat to another.

    Args:
        from_chat_id: Source chat ID
        message_id: ID of the message to forward
        chat_id: Target chat ID (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().forward_message(cid, from_chat_id, message_id)
    return json.dumps(result, ensure_ascii=False, indent=2)
