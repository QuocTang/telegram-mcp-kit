"""File and media tools: photos, documents, video, audio, albums, file info."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.formatting import CAPTION_LIMIT, utf16_len
from telegram_mcp_kit.models import SendResult
from telegram_mcp_kit.safety import check_upload_path
from telegram_mcp_kit.tools._base import (
    get_client,
    resolve_chat_id,
    send_caption_overflow,
    split_caption,
    tool,
)


async def _send(
    method: str,
    field: str,
    chat_id: str | None,
    media: str | None,
    file_path: str | None,
    caption: str | None,
    parse_mode: str | None,
    message_thread_id: int | None,
    **extra: Any,
) -> SendResult:
    """Send one media item, checking the upload path and splitting a long caption.

    Raises:
        ValueError: If neither or both of *media* and *file_path* are given.
    """
    if (media is None) == (file_path is None):
        raise ValueError(f"pass exactly one of {field} or file_path")
    cid = resolve_chat_id(chat_id)
    path = str(check_upload_path(file_path)) if file_path is not None else None
    caption, overflow = split_caption(caption)
    result = await get_client().send_media(
        method,
        field,
        cid,
        media,
        path,
        caption=caption,
        parse_mode=parse_mode,
        message_thread_id=message_thread_id,
        **extra,
    )
    return await send_caption_overflow(cid, result, overflow, parse_mode, message_thread_id)


@tool("write")
async def send_photo(
    photo: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
) -> SendResult:
    """Send a photo to a chat.

    A caption over 1024 characters is cut at a line break; the rest is sent as
    reply messages.

    Args:
        photo: Photo URL or file_id
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Photo caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
        message_thread_id: Forum topic to post in (optional)
    """
    return await _send(
        "sendPhoto", "photo", chat_id, photo, None, caption, parse_mode, message_thread_id
    )


@tool("write")
async def send_photo_file(
    file_path: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
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
        message_thread_id: Forum topic to post in (optional)
    """
    return await _send(
        "sendPhoto", "photo", chat_id, None, file_path, caption, parse_mode, message_thread_id
    )


@tool("write")
async def send_document(
    document: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
) -> SendResult:
    """Send a document/file to a chat.

    A caption over 1024 characters is cut at a line break; the rest is sent as
    reply messages.

    Args:
        document: Document URL or file_id
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Document caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
        message_thread_id: Forum topic to post in (optional)
    """
    return await _send(
        "sendDocument", "document", chat_id, document, None, caption, parse_mode,
        message_thread_id,
    )


@tool("write")
async def send_document_file(
    file_path: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
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
        message_thread_id: Forum topic to post in (optional)
    """
    return await _send(
        "sendDocument", "document", chat_id, None, file_path, caption, parse_mode,
        message_thread_id,
    )


@tool("write")
async def send_video(
    video: str | None = None,
    file_path: str | None = None,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
    supports_streaming: bool | None = None,
) -> SendResult:
    """Send a video (MPEG4) by URL/file_id or from a local file.

    Pass exactly one of video or file_path. A caption over 1024 characters is cut
    at a line break; the rest is sent as reply messages.

    Args:
        video: Video URL or file_id
        file_path: Absolute path to a local video (must lie inside TELEGRAM_UPLOAD_DIRS
            when that variable is set)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Video caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
        message_thread_id: Forum topic to post in (optional)
        supports_streaming: Mark an uploaded video as suitable for streaming
    """
    return await _send(
        "sendVideo", "video", chat_id, video, file_path, caption, parse_mode,
        message_thread_id, supports_streaming=supports_streaming,
    )


@tool("write")
async def send_audio(
    audio: str | None = None,
    file_path: str | None = None,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
    message_thread_id: int | None = None,
    performer: str | None = None,
    title: str | None = None,
) -> SendResult:
    """Send an audio file (MP3/M4A) shown in the music player, by URL/file_id or local file.

    Pass exactly one of audio or file_path. A caption over 1024 characters is cut
    at a line break; the rest is sent as reply messages.

    Args:
        audio: Audio URL or file_id
        file_path: Absolute path to a local audio file (must lie inside
            TELEGRAM_UPLOAD_DIRS when that variable is set)
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Audio caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
        message_thread_id: Forum topic to post in (optional)
        performer: Performer (optional)
        title: Track name (optional)
    """
    return await _send(
        "sendAudio", "audio", chat_id, audio, file_path, caption, parse_mode,
        message_thread_id, performer=performer, title=title,
    )


class MediaItem(BaseModel):
    """One item of an album sent with send_media_group."""

    type: Literal["photo", "video", "document", "audio"]
    media: str | None = Field(default=None, description="URL or file_id")
    file_path: str | None = Field(default=None, description="Local file to upload instead")
    caption: str | None = Field(default=None, description="Caption, at most 1024 characters")
    parse_mode: str | None = None


@tool("write")
async def send_media_group(
    items: list[MediaItem],
    chat_id: str | None = None,
    message_thread_id: int | None = None,
) -> SendResult:
    """Send 2-10 photos, videos, documents or audios as one album.

    Documents and audios can only be grouped with items of the same type. Each item
    gives either media (URL/file_id) or file_path.

    Args:
        items: Album items in display order
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        message_thread_id: Forum topic to post in (optional)
    """
    if not 2 <= len(items) <= 10:
        raise ValueError("send_media_group needs 2-10 items")
    cid = resolve_chat_id(chat_id)
    media: list[dict[str, Any]] = []
    files: dict[str, str] = {}
    for i, item in enumerate(items):
        if (item.media is None) == (item.file_path is None):
            raise ValueError(f"item {i}: pass exactly one of media or file_path")
        if item.caption and utf16_len(item.caption) > CAPTION_LIMIT:
            raise ValueError(f"item {i}: caption exceeds {CAPTION_LIMIT} characters")
        entry: dict[str, Any] = {"type": item.type}
        if item.file_path is not None:
            name = f"file{i}"
            files[name] = str(check_upload_path(item.file_path))
            entry["media"] = f"attach://{name}"
        else:
            entry["media"] = item.media
        if item.caption:
            entry["caption"] = item.caption
        if item.parse_mode:
            entry["parse_mode"] = item.parse_mode
        media.append(entry)
    result = await get_client().send_media_group(
        cid, media, files or None, message_thread_id=message_thread_id
    )
    return SendResult(messages=result if isinstance(result, list) else [result])


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
