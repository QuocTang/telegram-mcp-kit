"""Shared MCP instance and client accessor.

Every tool module imports ``mcp`` and ``get_client`` from here so there is
exactly one ``MCPServer`` instance across the whole server.
"""

import json
from collections.abc import Callable
from importlib.metadata import version
from typing import Any, Literal, TypeVar

from mcp.server.mcpserver import MCPServer

from telegram_mcp_kit.client import RateLimiter, TelegramClient
from telegram_mcp_kit.config import settings
from telegram_mcp_kit.formatting import CAPTION_LIMIT, MESSAGE_LIMIT, split_text
from telegram_mcp_kit.safety import check_chat_allowed

mcp = MCPServer("telegram-mcp-kit", version=version("telegram-mcp-kit"))

ToolKind = Literal["read", "write", "destructive"]

# Kind of every registered tool, used by read-only mode.
TOOL_KINDS: dict[str, ToolKind] = {}

_F = TypeVar("_F", bound=Callable[..., Any])


def tool(kind: ToolKind, **kwargs: Any) -> Callable[[_F], _F]:
    """Register a tool on the shared server and record its kind.

    Args:
        kind: ``"read"`` for tools without side effects, ``"write"`` for tools that
            add state (send, pin), ``"destructive"`` for tools that remove or
            overwrite state (delete, ban, edit).
        **kwargs: Passed to ``MCPServer.tool``.

    Returns:
        A decorator that returns the function unchanged.
    """

    def decorator(fn: _F) -> _F:
        name = kwargs.get("name") or fn.__name__
        TOOL_KINDS[name] = kind
        return mcp.tool(**kwargs)(fn)

    return decorator


def apply_read_only(server: MCPServer = mcp) -> list[str]:
    """Remove every tool that is not of kind ``"read"`` when TELEGRAM_READ_ONLY is set.

    Returns:
        Names of the removed tools (empty when read-only mode is off).
    """
    if not settings.telegram_read_only:
        return []
    registered = {t.name for t in server._tool_manager.list_tools()}
    removed = [n for n, k in TOOL_KINDS.items() if k != "read" and n in registered]
    for name in removed:
        server.remove_tool(name)
    return removed

_client: TelegramClient | None = None


def get_client() -> TelegramClient:
    global _client
    if _client is None:
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        _client = TelegramClient(
            settings.telegram_bot_token,
            timeout=settings.http_timeout,
            max_retries=settings.telegram_max_retries,
            max_retry_wait=settings.telegram_max_retry_wait,
            rate_limiter=RateLimiter(
                settings.telegram_chat_interval, settings.telegram_global_interval
            ),
            dry_run=settings.telegram_dry_run,
        )
    return _client


def resolve_chat_id(chat_id: str | None) -> str:
    """Return *chat_id* if given, otherwise TELEGRAM_CHAT_ID, checked against the allowlist.

    Raises:
        ValueError: If neither *chat_id* nor TELEGRAM_CHAT_ID is set.
        TelegramGuardError: If the chat is outside TELEGRAM_ALLOWED_CHATS.
    """
    if chat_id:
        return check_chat_allowed(chat_id)
    if settings.telegram_chat_id:
        return check_chat_allowed(settings.telegram_chat_id)
    raise ValueError(
        "chat_id is required (pass it explicitly or set TELEGRAM_CHAT_ID)"
    )


def to_json(result: Any) -> str:
    """Serialize a Bot API result for a tool response."""
    return json.dumps(result, ensure_ascii=False, indent=2)


async def send_long_text(
    send: Callable[..., Any], cid: str, text: str, parse_mode: str | None, *args: Any
) -> dict | list[dict]:
    """Send *text* through *send*, split into chunks of at most 4096 characters.

    Args:
        send: Client method called as ``send(cid, chunk, parse_mode, *args)``; extra
            positional *args* are passed with the first chunk only.

    Returns:
        The sent message when the text fits in one message, otherwise the list of
        sent messages in order.
    """
    chunks = split_text(text, MESSAGE_LIMIT)
    if len(chunks) == 1:
        return await send(cid, text, parse_mode, *args)
    sent = [await send(cid, chunks[0], parse_mode, *args)]
    for chunk in chunks[1:]:
        sent.append(await send(cid, chunk, parse_mode, *[None] * len(args)))
    return sent


def split_caption(caption: str | None) -> tuple[str | None, list[str]]:
    """Split *caption* into a 1024-character caption and the overflow text.

    Returns:
        The caption to attach to the media and the remaining chunks (each at most
        4096 characters) to send as follow-up messages.
    """
    if not caption:
        return caption, []
    parts = split_text(caption, CAPTION_LIMIT)
    if len(parts) == 1:
        return caption, []
    return parts[0], split_text("\n".join(parts[1:]), MESSAGE_LIMIT)


async def send_caption_overflow(
    cid: str, media_result: dict, overflow: list[str], parse_mode: str | None
) -> dict:
    """Send caption overflow as replies to the media message.

    Returns:
        *media_result* unchanged when there is no overflow, otherwise
        ``{"message": media_result, "caption_overflow_messages": [...]}``.
    """
    if not overflow:
        return media_result
    client = get_client()
    reply_to = media_result.get("message_id") if isinstance(media_result, dict) else None
    extra = [await client.send_message(cid, chunk, parse_mode, reply_to) for chunk in overflow]
    return {"message": media_result, "caption_overflow_messages": extra}
