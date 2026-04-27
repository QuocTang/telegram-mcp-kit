"""Chat management tools: info, members, admins, ban, pin, etc."""

import json

from telegram_mcp_kit.tools._base import get_client, mcp, resolve_chat_id


@mcp.tool()
async def get_chat_info(chat_id: str | None = None) -> str:
    """Get information about a chat (group, channel, or private chat).

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().get_chat(cid)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_chat_member_count(chat_id: str | None = None) -> str:
    """Get the number of members in a chat.

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    count = await get_client().get_chat_member_count(cid)
    return f"Member count: {count}"


@mcp.tool()
async def get_chat_admins(chat_id: str | None = None) -> str:
    """Get list of administrators in a chat.

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().get_chat_administrators(cid)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def ban_member(user_id: int, chat_id: str | None = None) -> str:
    """Ban a user from a chat.

    Args:
        user_id: User ID to ban
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().ban_chat_member(cid, user_id)
    return f"User {user_id} has been banned."


@mcp.tool()
async def unban_member(user_id: int, chat_id: str | None = None) -> str:
    """Unban a user from a chat.

    Args:
        user_id: User ID to unban
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().unban_chat_member(cid, user_id)
    return f"User {user_id} has been unbanned."


@mcp.tool()
async def set_chat_title(title: str, chat_id: str | None = None) -> str:
    """Change the title of a chat (group/channel).

    Args:
        title: New chat title (1-128 characters)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().set_chat_title(cid, title)
    return f"Chat title changed to: {title}"


@mcp.tool()
async def set_chat_description(description: str, chat_id: str | None = None) -> str:
    """Change the description of a chat (group/channel).

    Args:
        description: New description (0-255 characters)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().set_chat_description(cid, description)
    return "Chat description updated."


@mcp.tool()
async def pin_message(
    message_id: int, chat_id: str | None = None, silent: bool = False
) -> str:
    """Pin a message in a chat.

    Args:
        message_id: ID of the message to pin
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        silent: Pin without notification (default False)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().pin_chat_message(cid, message_id, silent)
    return "Message pinned."


@mcp.tool()
async def unpin_message(
    chat_id: str | None = None, message_id: int | None = None
) -> str:
    """Unpin a message in a chat.

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        message_id: ID of message to unpin (optional, unpins most recent if not specified)
    """
    cid = resolve_chat_id(chat_id)
    await get_client().unpin_chat_message(cid, message_id)
    return "Message unpinned."
