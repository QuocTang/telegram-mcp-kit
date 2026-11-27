"""Message tools: send, edit, delete, forward."""

from typing import Annotated, Any

from mcp.server.mcpserver import Context, ElicitationResult, Resolve

from telegram_mcp_kit.models import ActionResult, Confirmation, SendResult
from telegram_mcp_kit.safety import check_chat_allowed
from telegram_mcp_kit.tools._base import (
    action_result,
    confirm_gate,
    ensure_confirmed,
    get_client,
    resolve_chat_id,
    send_long_text,
    tool,
)


@tool("write")
async def send_message(
    text: str,
    chat_id: str | None = None,
    parse_mode: str | None = None,
    reply_to_message_id: int | None = None,
    message_thread_id: int | None = None,
) -> SendResult:
    """Send a text message to a Telegram chat.

    Text longer than 4096 characters is sent as several messages, split at line
    breaks where possible.

    Args:
        text: Message text (supports Markdown/HTML based on parse_mode)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" (optional)
        reply_to_message_id: ID of message to reply to (optional)
        message_thread_id: Forum topic to post in (optional)
    """
    cid = resolve_chat_id(chat_id)
    return await send_long_text(cid, text, parse_mode, reply_to_message_id, message_thread_id)


@tool("destructive", idempotent=True)
async def edit_message(
    message_id: int,
    text: str,
    chat_id: str | None = None,
    parse_mode: str | None = None,
) -> dict[str, Any]:
    """Edit the text of an existing message. Returns the edited Message.

    Args:
        message_id: ID of the message to edit
        text: New text for the message
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" (optional)
    """
    cid = resolve_chat_id(chat_id)
    return await get_client().edit_message_text(cid, message_id, text, parse_mode)


async def _confirm_delete(
    message_id: int, chat_id: str | None, confirm: bool, ctx: Context
) -> Any:
    target = chat_id or "the default chat"
    return await confirm_gate(ctx, confirm, f"delete message {message_id} in {target}")


@tool("destructive", idempotent=True)
async def delete_message(
    message_id: int,
    chat_id: str | None = None,
    confirm: bool = False,
    approval: Annotated[ElicitationResult[Confirmation], Resolve(_confirm_delete)] = None,
) -> ActionResult:
    """Delete a message from a chat. Asks the user for confirmation first.

    Args:
        message_id: ID of the message to delete
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        confirm: Explicit confirmation, required when the client cannot show a
            confirmation dialog and TELEGRAM_CONFIRM_DESTRUCTIVE=require
    """
    ensure_confirmed(approval)
    cid = resolve_chat_id(chat_id)
    result = await get_client().delete_message(cid, message_id)
    return action_result(result, f"Message {message_id} deleted.")


@tool("write")
async def forward_message(
    from_chat_id: str,
    message_id: int,
    chat_id: str | None = None,
    message_thread_id: int | None = None,
) -> SendResult:
    """Forward a message from one chat to another.

    Args:
        from_chat_id: Source chat ID
        message_id: ID of the message to forward
        chat_id: Target chat ID (uses TELEGRAM_CHAT_ID if omitted)
        message_thread_id: Forum topic of the target chat (optional)
    """
    cid = resolve_chat_id(chat_id)
    check_chat_allowed(from_chat_id)
    result = await get_client().forward_message(
        cid, from_chat_id, message_id, message_thread_id=message_thread_id
    )
    return SendResult(messages=[result])


@tool("write")
async def send_rich_message(
    markdown: str | None = None,
    html: str | None = None,
    blocks: list[dict[str, Any]] | None = None,
    chat_id: str | None = None,
    message_thread_id: int | None = None,
    reply_to_message_id: int | None = None,
    skip_entity_detection: bool = False,
) -> SendResult:
    """Send a rich message (headings, lists, tables, task lists, quotes, formulas).

    Pass exactly one of markdown, html or blocks. Rich Markdown supports "# Heading",
    "- item", "- [x] task", "| a | b |" tables, ">" quotes, "**bold**", "==marked==",
    "$x^2$" and fenced code. Limit: 32768 characters, 500 blocks, 20 table columns.

    Args:
        markdown: Content in rich Markdown
        html: Content in rich HTML
        blocks: Content as a list of InputRichBlock objects
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        message_thread_id: Forum topic to post in (optional)
        reply_to_message_id: ID of message to reply to (optional)
        skip_entity_detection: Do not auto-detect URLs, mentions, hashtags, etc.
    """
    given = [v for v in (markdown, html, blocks) if v is not None]
    if len(given) != 1:
        raise ValueError("pass exactly one of markdown, html or blocks")
    cid = resolve_chat_id(chat_id)
    rich: dict[str, Any] = {}
    if markdown is not None:
        rich["markdown"] = markdown
    elif html is not None:
        rich["html"] = html
    else:
        rich["blocks"] = blocks
    if skip_entity_detection:
        rich["skip_entity_detection"] = True
    result = await get_client().send_rich_message(
        cid, rich, message_thread_id=message_thread_id, reply_to_message_id=reply_to_message_id
    )
    return SendResult(messages=[result])
