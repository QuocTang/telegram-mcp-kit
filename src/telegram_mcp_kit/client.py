"""Telegram Bot API client using httpx."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

import httpx

from telegram_mcp_kit.exceptions import TelegramAPIError, TelegramNetworkError

# httpx and httpcore log the full request URL at INFO/DEBUG level, and the Bot API URL
# embeds the bot token, so these loggers are capped at WARNING.
for _name in ("httpx", "httpcore"):
    logging.getLogger(_name).setLevel(logging.WARNING)


# Methods that only read state. They bypass pacing and dry-run.
READ_METHODS = frozenset(
    {
        "getMe",
        "getUpdates",
        "getChat",
        "getChatMemberCount",
        "getChatMember",
        "getChatAdministrators",
        "getFile",
    }
)


class RateLimiter:
    """Spaces out outgoing requests per chat and across all chats.

    Args:
        chat_interval: Minimum seconds between two requests to the same chat.
        global_interval: Minimum seconds between any two requests.
        clock: Monotonic clock, injectable for tests.
        sleep: Async sleep, injectable for tests.
    """

    def __init__(
        self,
        chat_interval: float = 0.0,
        global_interval: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self.chat_interval = chat_interval
        self.global_interval = global_interval
        self._clock = clock
        self._sleep = sleep
        self._lock = asyncio.Lock()
        self._next_global = 0.0
        self._next_chat: dict[str, float] = {}

    async def acquire(self, chat_id: str | int | None) -> None:
        """Wait until a request to *chat_id* is allowed, then reserve the slot."""
        if self.chat_interval <= 0 and self.global_interval <= 0:
            return
        key = str(chat_id) if chat_id is not None else ""
        async with self._lock:
            now = self._clock()
            wait = max(self._next_global - now, self._next_chat.get(key, 0.0) - now, 0.0)
            if wait > 0:
                await self._sleep(wait)
                now = self._clock()
            self._next_global = now + self.global_interval
            if key:
                self._next_chat[key] = now + self.chat_interval


class TelegramClient:
    """Lightweight Telegram Bot API client.

    Args:
        token: Bot token.
        timeout: HTTP timeout in seconds.
        max_retries: Times a request rejected with 429 is repeated after ``retry_after``.
        max_retry_wait: A 429 asking to wait longer than this many seconds is not retried.
        rate_limiter: Pacing applied to methods outside ``READ_METHODS``.
        dry_run: When True, methods outside ``READ_METHODS`` are not sent; the request
            that would have been sent is returned instead.
    """

    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        max_retry_wait: float = 60.0,
        rate_limiter: RateLimiter | None = None,
        dry_run: bool = False,
    ):
        self._token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self._client = httpx.AsyncClient(timeout=timeout)
        self.max_retries = max_retries
        self.max_retry_wait = max_retry_wait
        self.rate_limiter = rate_limiter or RateLimiter()
        self.dry_run = dry_run
        self._sleep: Callable[[float], Awaitable[None]] = asyncio.sleep

    @staticmethod
    def _params_of(kwargs: dict) -> dict:
        return dict(kwargs.get("json") or kwargs.get("data") or {})

    async def _request(self, method: str, **kwargs) -> dict:
        """Call *method* on the Bot API and return its ``result``.

        A 429 response carrying ``parameters.retry_after`` is retried up to
        ``max_retries`` times. Write methods are paced and honour ``dry_run``.

        Raises:
            TelegramAPIError: The API answered ``ok=false``.
            TelegramNetworkError: The HTTP request failed.
        """
        params = self._params_of(kwargs)
        is_write = method not in READ_METHODS
        if is_write and self.dry_run:
            preview: dict = {"dry_run": True, "method": method, "params": params}
            if kwargs.get("files"):
                preview["files"] = {
                    name: getattr(f, "name", "<stream>") for name, f in kwargs["files"].items()
                }
            return preview
        attempt = 0
        while True:
            if is_write:
                await self.rate_limiter.acquire(params.get("chat_id"))
            try:
                resp = await self._client.post(f"{self.base_url}/{method}", **kwargs)
            except httpx.HTTPError as exc:
                raise TelegramNetworkError(exc, secret=self._token) from exc
            data = resp.json()
            if data.get("ok"):
                return data["result"]
            retry_after = (data.get("parameters") or {}).get("retry_after")
            if (
                data.get("error_code") == 429
                and retry_after is not None
                and attempt < self.max_retries
                and retry_after <= self.max_retry_wait
            ):
                attempt += 1
                for f in (kwargs.get("files") or {}).values():
                    if hasattr(f, "seek"):
                        f.seek(0)
                await self._sleep(retry_after)
                continue
            raise TelegramAPIError(
                data.get("description", "Unknown error"),
                data.get("error_code"),
                retry_after,
            )

    # ── Messages ──

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str | None = None,
        reply_to_message_id: int | None = None,
    ) -> dict:
        params = {"chat_id": chat_id, "text": text}
        if parse_mode:
            params["parse_mode"] = parse_mode
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        return await self._request("sendMessage", json=params)

    async def forward_message(
        self, chat_id: str | int, from_chat_id: str | int, message_id: int
    ) -> dict:
        return await self._request(
            "forwardMessage",
            json={"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id},
        )

    async def delete_message(self, chat_id: str | int, message_id: int) -> bool:
        return await self._request(
            "deleteMessage", json={"chat_id": chat_id, "message_id": message_id}
        )

    async def edit_message_text(
        self,
        chat_id: str | int,
        message_id: int,
        text: str,
        parse_mode: str | None = None,
    ) -> dict:
        params = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if parse_mode:
            params["parse_mode"] = parse_mode
        return await self._request("editMessageText", json=params)

    # ── History / Updates ──

    async def get_updates(
        self,
        offset: int | None = None,
        limit: int = 100,
        allowed_updates: list[str] | None = None,
    ) -> list[dict]:
        params: dict = {"limit": limit}
        if offset is not None:
            params["offset"] = offset
        if allowed_updates:
            params["allowed_updates"] = allowed_updates
        return await self._request("getUpdates", json=params)

    # ── Chat / Channel / Group Management ──

    async def get_chat(self, chat_id: str | int) -> dict:
        return await self._request("getChat", json={"chat_id": chat_id})

    async def get_chat_member_count(self, chat_id: str | int) -> int:
        return await self._request("getChatMemberCount", json={"chat_id": chat_id})

    async def get_chat_member(self, chat_id: str | int, user_id: int) -> dict:
        return await self._request(
            "getChatMember", json={"chat_id": chat_id, "user_id": user_id}
        )

    async def get_chat_administrators(self, chat_id: str | int) -> list[dict]:
        return await self._request("getChatAdministrators", json={"chat_id": chat_id})

    async def ban_chat_member(self, chat_id: str | int, user_id: int) -> bool:
        return await self._request(
            "banChatMember", json={"chat_id": chat_id, "user_id": user_id}
        )

    async def unban_chat_member(self, chat_id: str | int, user_id: int) -> bool:
        return await self._request(
            "unbanChatMember",
            json={"chat_id": chat_id, "user_id": user_id, "only_if_banned": True},
        )

    async def set_chat_title(self, chat_id: str | int, title: str) -> bool:
        return await self._request(
            "setChatTitle", json={"chat_id": chat_id, "title": title}
        )

    async def set_chat_description(self, chat_id: str | int, description: str) -> bool:
        return await self._request(
            "setChatDescription", json={"chat_id": chat_id, "description": description}
        )

    async def pin_chat_message(
        self, chat_id: str | int, message_id: int, disable_notification: bool = False
    ) -> bool:
        return await self._request(
            "pinChatMessage",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "disable_notification": disable_notification,
            },
        )

    async def unpin_chat_message(self, chat_id: str | int, message_id: int | None = None) -> bool:
        params: dict = {"chat_id": chat_id}
        if message_id is not None:
            params["message_id"] = message_id
        return await self._request("unpinChatMessage", json=params)

    # ── Files / Photos ──

    async def send_photo(
        self,
        chat_id: str | int,
        photo: str,
        caption: str | None = None,
        parse_mode: str | None = None,
    ) -> dict:
        """Send photo by file_id or URL."""
        params = {"chat_id": chat_id, "photo": photo}
        if caption:
            params["caption"] = caption
        if parse_mode:
            params["parse_mode"] = parse_mode
        return await self._request("sendPhoto", json=params)

    async def send_photo_file(
        self,
        chat_id: str | int,
        file_path: str,
        caption: str | None = None,
        parse_mode: str | None = None,
    ) -> dict:
        """Send photo from local file."""
        data = {"chat_id": str(chat_id)}
        if caption:
            data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
        with open(file_path, "rb") as f:
            return await self._request("sendPhoto", data=data, files={"photo": f})

    async def send_document(
        self,
        chat_id: str | int,
        document: str,
        caption: str | None = None,
        parse_mode: str | None = None,
    ) -> dict:
        """Send document by file_id or URL."""
        params = {"chat_id": chat_id, "document": document}
        if caption:
            params["caption"] = caption
        if parse_mode:
            params["parse_mode"] = parse_mode
        return await self._request("sendDocument", json=params)

    async def send_document_file(
        self,
        chat_id: str | int,
        file_path: str,
        caption: str | None = None,
        parse_mode: str | None = None,
    ) -> dict:
        """Send document from local file."""
        data = {"chat_id": str(chat_id)}
        if caption:
            data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
        with open(file_path, "rb") as f:
            return await self._request("sendDocument", data=data, files={"document": f})

    async def get_file(self, file_id: str) -> dict:
        return await self._request("getFile", json={"file_id": file_id})

    # ── Bot Info ──

    async def get_me(self) -> dict:
        return await self._request("getMe")

    async def close(self):
        await self._client.aclose()
