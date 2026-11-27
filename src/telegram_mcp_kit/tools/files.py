"""File and photo tools: send_photo, send_document, get_file_info."""

from typing import Any

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.models import SendResult
from telegram_mcp_kit.safety import check_upload_path
from telegram_mcp_kit.tools._base import (
    get_client,
    resolve_chat_id,
    send_caption_overflow,
    split_caption,
    tool,
)


@tool("write")
async def send_photo(
    photo: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> SendResult:
    """Send a photo to a chat.

    A caption over 1024 characters is cut at a line break; the rest is sent as
    reply messages.

    Args:
        photo: Photo URL or file_id
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Photo caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    caption, overflow = split_caption(caption)
    result = await get_client().send_photo(cid, photo, caption, parse_mode)
    return await send_caption_overflow(cid, result, overflow, parse_mode)


@tool("write")
async def send_photo_file(
    file_path: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> SendResult:
    """Send a local photo file to a chat.

    A caption over 1024 characters is cut at a line break; the rest is sent as
    reply messages.

    Args:
        file_path: Absolute path to the photo file on disk (must lie inside
            TELEGRAM_UPLOAD_DIRS when that variable is set)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Photo caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    path = str(check_upload_path(file_path))
    caption, overflow = split_caption(caption)
    result = await get_client().send_photo_file(cid, path, caption, parse_mode)
    return await send_caption_overflow(cid, result, overflow, parse_mode)


@tool("write")
async def send_document(
    document: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> SendResult:
    """Send a document/file to a chat.

    A caption over 1024 characters is cut at a line break; the rest is sent as
    reply messages.

    Args:
        document: Document URL or file_id
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Document caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    caption, overflow = split_caption(caption)
    result = await get_client().send_document(cid, document, caption, parse_mode)
    return await send_caption_overflow(cid, result, overflow, parse_mode)


@tool("write")
async def send_document_file(
    file_path: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> SendResult:
    """Send a local file as a document to a chat.

    A caption over 1024 characters is cut at a line break; the rest is sent as
    reply messages.

    Args:
        file_path: Absolute path to the file on disk (must lie inside
            TELEGRAM_UPLOAD_DIRS when that variable is set)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Document caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    path = str(check_upload_path(file_path))
    caption, overflow = split_caption(caption)
    result = await get_client().send_document_file(cid, path, caption, parse_mode)
    return await send_caption_overflow(cid, result, overflow, parse_mode)


@tool("read")
async def get_file_info(file_id: str) -> dict[str, Any]:
    """Get file info and download link from Telegram.

    Args:
        file_id: Telegram file ID (from received messages)
    """
    result = await get_client().get_file(file_id)
    file_path = result.get("file_path", "")
    result["download_url"] = (
        f"https://api.telegram.org/file/bot{settings.telegram_bot_token}/{file_path}"
    )
    return result
