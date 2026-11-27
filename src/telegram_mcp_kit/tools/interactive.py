"""Interactive tools: reactions, chat actions, polls and checklists."""

from typing import Literal

from telegram_mcp_kit.models import ActionResult, SendResult
from telegram_mcp_kit.tools._base import action_result, get_client, resolve_chat_id, tool

ChatAction = Literal[
    "typing",
    "upload_photo",
    "record_video",
    "upload_video",
    "record_voice",
    "upload_voice",
    "upload_document",
    "choose_sticker",
    "find_location",
    "record_video_note",
    "upload_video_note",
]


@tool("write", idempotent=True)
async def set_reaction(
    message_id: int,
    emoji: str | None = None,
    chat_id: str | None = None,
    is_big: bool = False,
) -> ActionResult:
    """Set the bot's emoji reaction on a message, or remove it when emoji is omitted.

    Bots can set one reaction per message, from the emoji Telegram allows for
    reactions (for example 👍, 👎, ❤, 🔥, 🎉, 👀).

    Args:
        message_id: Target message
        emoji: Reaction emoji; omit to remove the bot's reaction
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        is_big: Show the reaction with a big animation
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().set_message_reaction(
        cid, message_id, [emoji] if emoji else [], is_big
    )
    return action_result(result, f"Reaction {'set to ' + emoji if emoji else 'removed'}.")


@tool("write", idempotent=True)
async def send_chat_action(
    action: ChatAction = "typing",
    chat_id: str | None = None,
    message_thread_id: int | None = None,
) -> ActionResult:
    """Show a status such as "typing…" in the chat for up to 5 seconds.

    Args:
        action: Status to show (typing, upload_photo, upload_document, ...)
        chat_id: Chat ID or @username; channels are not supported
        message_thread_id: Forum topic to show the status in (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_chat_action(cid, action, message_thread_id)
    return action_result(result, f"Chat action {action} sent.")


@tool("write")
async def send_poll(
    question: str,
    options: list[str],
    chat_id: str | None = None,
    is_anonymous: bool | None = None,
    type: Literal["regular", "quiz"] = "regular",
    allows_multiple_answers: bool | None = None,
    correct_option_ids: list[int] | None = None,
    explanation: str | None = None,
    open_period: int | None = None,
    message_thread_id: int | None = None,
) -> SendResult:
    """Send a native poll or quiz.

    Args:
        question: Poll question, 1-300 characters
        options: 1-12 answer options, 1-100 characters each
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        is_anonymous: Anonymous poll (Telegram default True)
        type: "regular" or "quiz"
        allows_multiple_answers: Allow choosing several options
        correct_option_ids: 0-based correct options, required for a quiz
        explanation: Shown after a wrong quiz answer, 0-200 characters
        open_period: Seconds the poll stays open, 5-2628000
        message_thread_id: Forum topic to post in (optional)
    """
    if not 1 <= len(options) <= 12:
        raise ValueError("a poll needs 1-12 options")
    if type == "quiz" and not correct_option_ids:
        raise ValueError("a quiz needs correct_option_ids")
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_poll(
        cid,
        question,
        options,
        is_anonymous=is_anonymous,
        type=type,
        allows_multiple_answers=allows_multiple_answers,
        correct_option_ids=correct_option_ids,
        explanation=explanation,
        open_period=open_period,
        message_thread_id=message_thread_id,
    )
    return SendResult(messages=[result])


@tool("write")
async def send_checklist(
    business_connection_id: str,
    title: str,
    tasks: list[str],
    chat_id: str | None = None,
    others_can_add_tasks: bool = False,
    others_can_mark_tasks_as_done: bool = False,
) -> SendResult:
    """Send a checklist on behalf of a connected business account.

    Telegram accepts sendChecklist only with a business connection; regular bot
    chats cannot receive checklists. For a plain task list use send_rich_message
    with "- [ ] task" lines.

    Args:
        business_connection_id: Business connection the checklist is sent through
        title: Checklist title, 1-255 characters
        tasks: 1-30 task texts, 1-100 characters each
        chat_id: Target chat ID (uses TELEGRAM_CHAT_ID if omitted)
        others_can_add_tasks: Let other users add tasks
        others_can_mark_tasks_as_done: Let other users mark tasks as done
    """
    if not 1 <= len(tasks) <= 30:
        raise ValueError("a checklist needs 1-30 tasks")
    cid = resolve_chat_id(chat_id)
    checklist = {
        "title": title,
        "tasks": [{"id": i, "text": text} for i, text in enumerate(tasks, start=1)],
    }
    if others_can_add_tasks:
        checklist["others_can_add_tasks"] = True
    if others_can_mark_tasks_as_done:
        checklist["others_can_mark_tasks_as_done"] = True
    result = await get_client().send_checklist(business_connection_id, cid, checklist)
    return SendResult(messages=[result])
