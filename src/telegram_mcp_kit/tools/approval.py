"""Human-in-the-loop tools: live progress drafts and approval buttons."""

import html
import secrets
import time
from collections.abc import Callable

from mcp.server.mcpserver import Context

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.exceptions import TelegramError
from telegram_mcp_kit.formatting import escape_markdown_v2
from telegram_mcp_kit.models import ActionResult, ApprovalResult, SendResult
from telegram_mcp_kit.tools._base import (
    action_result,
    get_client,
    resolve_chat_id,
    send_long_text,
    tool,
)
from telegram_mcp_kit.update_buffer import buffer

MAX_APPROVAL_TIMEOUT = 3600
POLL_SECONDS = 20


@tool("write")
async def send_progress(
    text: str,
    chat_id: str | None = None,
    draft_id: int = 1,
    final: bool = False,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
    can_stop: bool = False,
) -> ActionResult | SendResult:
    """Show live progress in a private chat, then persist the final text.

    While final is false the text is streamed with sendMessageDraft: it replaces
    the previous draft with the same draft_id and disappears after about 30
    seconds unless updated. Call again with final=true to send the finished text
    as a normal message. Drafts work only in private chats with the bot.

    Args:
        text: Progress text, 0-4096 characters (empty shows "Thinking…")
        chat_id: Private chat ID (uses TELEGRAM_CHAT_ID if omitted)
        draft_id: Non-zero id; reuse it to update the same draft
        final: Send text as a persistent message instead of a draft
        parse_mode: "Markdown", "MarkdownV2", or "HTML" (optional)
        message_thread_id: Topic in a private chat with topics enabled (optional)
        can_stop: Show the user a button to stop the drafts
    """
    cid = resolve_chat_id(chat_id)
    if final:
        return await send_long_text(cid, text, parse_mode, None, message_thread_id)
    if draft_id == 0:
        raise ValueError("draft_id must be non-zero")
    try:
        private_id = int(cid)
    except ValueError:
        raise ValueError("send_progress drafts need a numeric private chat id") from None
    result = await get_client().send_message_draft(
        private_id, draft_id, text, parse_mode, message_thread_id, can_stop
    )
    return action_result(result, f"Draft {draft_id} updated.")


def _escape(text: str, parse_mode: str | None) -> str:
    """Escape *text* for appending to a message sent with *parse_mode*."""
    if parse_mode == "MarkdownV2":
        return escape_markdown_v2(text)
    if parse_mode == "HTML":
        return html.escape(text)
    return text


def _user_label(user: dict) -> str:
    if user.get("username"):
        return "@" + user["username"]
    return " ".join(p for p in (user.get("first_name"), user.get("last_name")) if p) or str(
        user.get("id")
    )


def _approvers_for(cid: str) -> set[int]:
    """Return the user ids allowed to answer, from TELEGRAM_APPROVER_IDS.

    Without TELEGRAM_APPROVER_IDS a private chat (positive numeric id) accepts its
    own user only.

    Raises:
        ValueError: If no approver can be determined for a group or channel.
    """
    approvers = settings.approver_ids
    if approvers:
        return approvers
    if cid.lstrip("-").isdigit() and int(cid) > 0:
        return {int(cid)}
    raise ValueError("set TELEGRAM_APPROVER_IDS to use ask_approval outside a private chat")


def _is_press(token: str) -> Callable[[dict], bool]:
    def match(update: dict) -> bool:
        data = (update.get("callback_query") or {}).get("data") or ""
        return data.startswith(f"apv:{token}:")

    return match


@tool("write")
async def ask_approval(
    question: str,
    ctx: Context,
    chat_id: str | None = None,
    timeout_seconds: int = 300,
    approve_label: str = "✅ Approve",
    reject_label: str = "❌ Reject",
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
) -> ApprovalResult:
    """Ask a person in Telegram to approve or reject, and wait for the button press.

    Sends the question with two inline buttons and long-polls getUpdates for the
    callback. Only users in TELEGRAM_APPROVER_IDS (or, when unset, the user of a
    private chat) can decide; other presses are answered with a refusal and
    ignored. The message is edited to show the outcome. Not usable while a webhook
    is set for the bot.

    Args:
        question: Text of the request, 1-4096 characters
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        timeout_seconds: How long to wait, 1-3600 seconds (default 300)
        approve_label: Text of the approve button
        reject_label: Text of the reject button
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for the question (optional)
        message_thread_id: Forum topic to post in (optional)
    """
    if not 1 <= timeout_seconds <= MAX_APPROVAL_TIMEOUT:
        raise ValueError(f"timeout_seconds must be 1-{MAX_APPROVAL_TIMEOUT}")
    cid = resolve_chat_id(chat_id)
    approvers = _approvers_for(cid)
    client = get_client()
    token = secrets.token_hex(6)
    markup = {
        "inline_keyboard": [
            [
                {"text": approve_label, "callback_data": f"apv:{token}:y"},
                {"text": reject_label, "callback_data": f"apv:{token}:n"},
            ]
        ]
    }
    sent = await client.send_message(
        cid, question, parse_mode, None, message_thread_id=message_thread_id, reply_markup=markup
    )
    if sent.get("dry_run"):
        return ApprovalResult(status="dry_run")
    message_id = sent.get("message_id")

    started = time.monotonic()
    deadline = started + timeout_seconds
    ignored = 0
    match = _is_press(token)
    while True:
        update = buffer.take(match)
        if update is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            await ctx.report_progress(
                time.monotonic() - started, timeout_seconds, "Waiting for approval"
            )
            await buffer.fetch(
                client, ["message", "callback_query"], min(POLL_SECONDS, max(1, int(remaining)))
            )
            continue
        press = update["callback_query"]
        user = press.get("from") or {}
        if user.get("id") not in approvers:
            ignored += 1
            await client.answer_callback_query(
                press["id"], "You are not allowed to answer this request.", show_alert=True
            )
            continue
        approved = press.get("data", "").endswith(":y")
        status = "approved" if approved else "rejected"
        await client.answer_callback_query(press["id"], status.capitalize())
        label = f"{'Approved' if approved else 'Rejected'} by {_user_label(user)}"
        await _close(client, cid, message_id, question, label, parse_mode)
        return ApprovalResult(
            status=status,
            message_id=message_id,
            decided_by=user,
            waited_seconds=round(time.monotonic() - started, 1),
            ignored_presses=ignored,
        )

    await _close(client, cid, message_id, question, "No answer (timed out)", parse_mode)
    return ApprovalResult(
        status="timeout",
        message_id=message_id,
        waited_seconds=round(time.monotonic() - started, 1),
        ignored_presses=ignored,
    )


async def _close(client, cid, message_id, question, label, parse_mode) -> None:
    """Replace the buttons of the approval message with the outcome line."""
    if message_id is None:
        return
    text = f"{question}\n\n{_escape(label, parse_mode)}"
    try:
        await client.edit_message_text(
            cid, message_id, text, parse_mode, reply_markup={"inline_keyboard": []}
        )
    except TelegramError:
        # The outcome is already decided; a failed edit of the message must not hide it.
        pass
