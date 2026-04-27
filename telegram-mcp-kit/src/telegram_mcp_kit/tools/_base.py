"""Shared MCP instance and client accessor.

Every tool module imports ``mcp`` and ``get_client`` from here so there is
exactly one ``FastMCP`` instance across the whole server.
"""

from mcp.server.fastmcp import FastMCP

from telegram_mcp_kit.client import TelegramClient
from telegram_mcp_kit.config import settings

mcp = FastMCP("telegram-mcp-kit", host=settings.mcp_host, port=settings.mcp_port)

_client: TelegramClient | None = None


def get_client() -> TelegramClient:
    global _client
    if _client is None:
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        _client = TelegramClient(settings.telegram_bot_token, timeout=settings.http_timeout)
    return _client


def resolve_chat_id(chat_id: str | None) -> str:
    """Return *chat_id* if given, otherwise fall back to TELEGRAM_CHAT_ID."""
    if chat_id:
        return chat_id
    if settings.telegram_chat_id:
        return settings.telegram_chat_id
    raise ValueError(
        "chat_id is required (pass it explicitly or set TELEGRAM_CHAT_ID)"
    )
