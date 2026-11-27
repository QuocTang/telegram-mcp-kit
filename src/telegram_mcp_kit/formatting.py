"""Text helpers for Telegram length limits and MarkdownV2 escaping."""

import re

MESSAGE_LIMIT = 4096
CAPTION_LIMIT = 1024

_MDV2_SPECIAL = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")
_MDV2_CODE_SPECIAL = re.compile(r"([`\\])")
_MDV2_LINK_SPECIAL = re.compile(r"([)\\])")


def utf16_len(text: str) -> int:
    """Return the length of *text* in UTF-16 code units (the unit Telegram counts)."""
    return len(text.encode("utf-16-le")) // 2


def escape_markdown_v2(text: str, context: str = "text") -> str:
    """Escape *text* for parse_mode=MarkdownV2.

    Args:
        text: Raw text to escape.
        context: ``"text"`` for ordinary text, ``"code"`` for the inside of pre/code
            entities, ``"link"`` for the (...) part of an inline link or custom emoji.

    Returns:
        The escaped text.

    Raises:
        ValueError: If *context* is not one of the supported values.
    """
    patterns = {"text": _MDV2_SPECIAL, "code": _MDV2_CODE_SPECIAL, "link": _MDV2_LINK_SPECIAL}
    if context not in patterns:
        raise ValueError(f"context must be one of {sorted(patterns)}")
    return patterns[context].sub(r"\\\1", text)


def _prefix_within(text: str, limit: int) -> int:
    """Return the largest index ``i`` such that ``utf16_len(text[:i]) <= limit``."""
    units = 0
    for i, ch in enumerate(text):
        units += 2 if ord(ch) > 0xFFFF else 1
        if units > limit:
            return i
    return len(text)


def split_text(text: str, limit: int = MESSAGE_LIMIT) -> list[str]:
    """Split *text* into chunks of at most *limit* UTF-16 code units.

    Chunks break at the last paragraph break, line break or space inside the limit
    when one exists in the second half of the window; otherwise the chunk is cut at
    the limit. A cut never leaves a trailing backslash, so MarkdownV2 escapes stay
    intact. Markup spanning a chunk boundary is not repaired.

    Args:
        text: Text to split.
        limit: Maximum chunk length in UTF-16 code units (must be positive).

    Returns:
        A list with at least one chunk; ``[text]`` when it already fits.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")
    chunks: list[str] = []
    rest = text
    while utf16_len(rest) > limit:
        hard = _prefix_within(rest, limit)
        cut = hard
        for sep in ("\n\n", "\n", " "):
            pos = rest.rfind(sep, 0, hard)
            if pos >= hard // 2 and pos > 0:
                cut = pos
                break
        while cut > 1 and rest[cut - 1] == "\\":
            cut -= 1
        chunks.append(rest[:cut])
        rest = rest[cut:].lstrip("\n ") if cut != hard else rest[cut:]
    chunks.append(rest)
    return chunks
