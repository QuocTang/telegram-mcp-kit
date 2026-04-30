"""File and photo tools: send_photo, send_document, get_file_info."""

import json

from telegram_mcp_kit.config import settings
from telegram_mcp_kit.tools._base import get_client, mcp, resolve_chat_id


@mcp.tool()
async def send_photo(
    photo: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> str:
    """Send a photo to a chat.

    Args:
        photo: Photo URL or file_id
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Photo caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_photo(cid, photo, caption, parse_mode)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def send_photo_file(
    file_path: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> str:
    """Send a local photo file to a chat.

    Args:
        file_path: Absolute path to the photo file on disk
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Photo caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_photo_file(cid, file_path, caption, parse_mode)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def send_document(
    document: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> str:
    """Send a document/file to a chat.

    Args:
        document: Document URL or file_id
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Document caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_document(cid, document, caption, parse_mode)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def send_document_file(
    file_path: str,
    chat_id: str | None = None,
    caption: str | None = None,
    parse_mode: str | None = None,
) -> str:
    """Send a local file as a document to a chat.

    Args:
        file_path: Absolute path to the file on disk
        chat_id: Chat ID or @channel_username (uses TELEGRAM_CHAT_ID if omitted)
        caption: Document caption (optional)
        parse_mode: "Markdown", "MarkdownV2", or "HTML" for caption (optional)
    """
    cid = resolve_chat_id(chat_id)
    result = await get_client().send_document_file(cid, file_path, caption, parse_mode)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_file_info(file_id: str) -> str:
    """Get file info and download link from Telegram.

    Args:
        file_id: Telegram file ID (from received messages)
    """
    result = await get_client().get_file(file_id)
    file_path = result.get("file_path", "")
    result["download_url"] = (
        f"https://api.telegram.org/file/bot{settings.telegram_bot_token}/{file_path}"
    )
    return json.dumps(result, ensure_ascii=False, indent=2)
