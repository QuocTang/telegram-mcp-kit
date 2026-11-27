"""Chat management tools: info, members, admins, ban, pin, etc."""

from typing import Annotated, Any

from mcp.server.mcpserver import Context, ElicitationResult, Resolve

from telegram_mcp_kit.models import ActionResult, Confirmation, CountResult
from telegram_mcp_kit.tools._base import (
    action_result,
    confirm_gate,
    ensure_confirmed,
    get_client,
    resolve_chat_id,
    tool,
)


@tool("read")
async def get_chat_info(chat_id: str | None = None) -> dict[str, Any]:
    """Get information about a chat (group, channel, or private chat).

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    return await get_client().get_chat(cid)


@tool("read")
async def get_chat_member_count(chat_id: str | None = None) -> CountResult:
    """Get the number of members in a chat.

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    return CountResult(count=await get_client().get_chat_member_count(cid))


@tool("read")
async def get_chat_admins(chat_id: str | None = None) -> list[dict[str, Any]]:
    """Get list of administrators in a chat.

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    return await get_client().get_chat_administrators(cid)


async def _confirm_ban(user_id: int, chat_id: str | None, confirm: bool, ctx: Context) -> Any:
    target = chat_id or "the default chat"
    return await confirm_gate(ctx, confirm, f"ban user {user_id} from {target}")


@tool("destructive", idempotent=True)
async def ban_member(
    user_id: int,
    chat_id: str | None = None,
    confirm: bool = False,
    approval: Annotated[ElicitationResult[Confirmation], Resolve(_confirm_ban)] = None,
) -> ActionResult:
    """Ban a user from a chat. Asks the user for confirmation first.

    Args:
        user_id: User ID to ban
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        confirm: Explicit confirmation, required when the client cannot show a
            confirmation dialog and TELEGRAM_CONFIRM_DESTRUCTIVE=require
    """
    ensure_confirmed(approval)
    cid = resolve_chat_id(chat_id)
    result = await get_client().ban_chat_member(cid, user_id)
    return action_result(result, f"User {user_id} has been banned.")


@tool("write", idempotent=True)
async def unban_member(user_id: int, chat_id: str | None = None) -> ActionResult:
    """Unban a user from a chat.

    Args:
        user_id: User ID to unban
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().unban_chat_member(cid, user_id)
    return action_result(result, f"User {user_id} has been unbanned.")


async def _confirm_title(title: str, chat_id: str | None, confirm: bool, ctx: Context) -> Any:
    target = chat_id or "the default chat"
    return await confirm_gate(ctx, confirm, f"rename {target} to {title!r}")


@tool("destructive", idempotent=True)
async def set_chat_title(
    title: str,
    chat_id: str | None = None,
    confirm: bool = False,
    approval: Annotated[ElicitationResult[Confirmation], Resolve(_confirm_title)] = None,
) -> ActionResult:
    """Change the title of a chat (group/channel). Asks the user for confirmation first.

    Args:
        title: New chat title (1-128 characters)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        confirm: Explicit confirmation, required when the client cannot show a
            confirmation dialog and TELEGRAM_CONFIRM_DESTRUCTIVE=require
    """
    ensure_confirmed(approval)
    cid = resolve_chat_id(chat_id)
    result = await get_client().set_chat_title(cid, title)
    return action_result(result, f"Chat title changed to: {title}")


async def _confirm_description(
    description: str, chat_id: str | None, confirm: bool, ctx: Context
) -> Any:
    target = chat_id or "the default chat"
    return await confirm_gate(ctx, confirm, f"replace the description of {target}")


@tool("destructive", idempotent=True)
async def set_chat_description(
    description: str,
    chat_id: str | None = None,
    confirm: bool = False,
    approval: Annotated[
        ElicitationResult[Confirmation], Resolve(_confirm_description)
    ] = None,
) -> ActionResult:
    """Change the description of a chat (group/channel). Asks the user for confirmation first.

    Args:
        description: New description (0-255 characters)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        confirm: Explicit confirmation, required when the client cannot show a
            confirmation dialog and TELEGRAM_CONFIRM_DESTRUCTIVE=require
    """
    ensure_confirmed(approval)
    cid = resolve_chat_id(chat_id)
    result = await get_client().set_chat_description(cid, description)
    return action_result(result, "Chat description updated.")


@tool("write", idempotent=True)
async def pin_message(
    message_id: int, chat_id: str | None = None, silent: bool = False
) -> ActionResult:
    """Pin a message in a chat.

    Args:
        message_id: ID of the message to pin
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        silent: Pin without notification (default False)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().pin_chat_message(cid, message_id, silent)
    return action_result(result, "Message pinned.")


@tool("destructive", idempotent=True)
async def unpin_message(
    chat_id: str | None = None, message_id: int | None = None
) -> ActionResult:
    """Unpin a message in a chat.

    Args:
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        message_id: ID of message to unpin (optional, unpins most recent if not specified)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().unpin_chat_message(cid, message_id)
    return action_result(result, "Message unpinned.")
