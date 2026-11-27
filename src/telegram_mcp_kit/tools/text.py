"""Text helper tools that do not call the Telegram API."""

from typing import Literal

from telegram_mcp_kit.formatting import escape_markdown_v2 as _escape
from telegram_mcp_kit.tools._base import tool


@tool("read")
async def escape_markdown_v2(
    text: str, context: Literal["text", "code", "link"] = "text"
) -> str:
    """Escape text so it can be embedded in a message sent with parse_mode="MarkdownV2".

    Args:
        text: Raw text to escape
        context: "text" for ordinary text, "code" for the inside of a code/pre entity,
            "link" for the URL part of an inline link
    """
    return _escape(text, context)
