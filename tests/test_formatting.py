"""Tests for telegram_mcp_kit.formatting and the escape_markdown_v2 tool."""

import pytest

from telegram_mcp_kit.formatting import escape_markdown_v2, split_text, utf16_len
from telegram_mcp_kit.tools.text import escape_markdown_v2 as escape_tool


def test_escape_text_context():
    assert escape_markdown_v2("a_b*c.d!") == r"a\_b\*c\.d\!"
    assert escape_markdown_v2("1+1=2 (ok)") == r"1\+1\=2 \(ok\)"
    assert escape_markdown_v2("back\\slash") == "back\\\\slash"


def test_escape_code_and_link_context():
    assert escape_markdown_v2("a`b\\c.d", "code") == "a\\`b\\\\c.d"
    assert escape_markdown_v2("http://x.y/(a)", "link") == "http://x.y/(a\\)"


def test_escape_rejects_unknown_context():
    with pytest.raises(ValueError):
        escape_markdown_v2("x", "bogus")


async def test_escape_tool():
    assert await escape_tool("v1.2") == r"v1\.2"


def test_utf16_len_counts_surrogate_pairs():
    assert utf16_len("a") == 1
    assert utf16_len("😀") == 2


def test_split_short_text_unchanged():
    assert split_text("hello", 10) == ["hello"]


def test_split_prefers_line_breaks():
    text = "line one\nline two\nline three"
    chunks = split_text(text, 18)
    assert chunks == ["line one\nline two", "line three"]
    assert all(utf16_len(c) <= 18 for c in chunks)


def test_split_hard_cut_without_separators():
    chunks = split_text("x" * 25, 10)
    assert chunks == ["x" * 10, "x" * 10, "x" * 5]


def test_split_respects_utf16_limit_with_emoji():
    chunks = split_text("😀" * 6, 5)
    assert all(utf16_len(c) <= 5 for c in chunks)
    assert "".join(chunks) == "😀" * 6


def test_split_does_not_end_chunk_with_backslash():
    chunks = split_text("abcdefghi\\.jkl", 10)
    assert not chunks[0].endswith("\\")
    assert "".join(chunks) == "abcdefghi\\.jkl"


def test_split_message_limit():
    text = ("word " * 2000).strip()
    chunks = split_text(text)
    assert len(chunks) == 3
    assert all(utf16_len(c) <= 4096 for c in chunks)
