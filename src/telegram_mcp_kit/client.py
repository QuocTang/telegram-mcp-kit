"""Telegram Bot API client using httpx."""

import httpx

from telegram_mcp_kit.exceptions import TelegramAPIError, TelegramNetworkError


class TelegramClient:
    """Lightweight Telegram Bot API client."""

    def __init__(self, token: str, timeout: float = 30.0):
        self.base_url = f"https://api.telegram.org/bot{token}"
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _request(self, method: str, **kwargs) -> dict:
        """Make a request to the Telegram Bot API."""
        try:
            resp = await self._client.post(f"{self.base_url}/{method}", **kwargs)
        except httpx.HTTPError as exc:
            raise TelegramNetworkError(exc) from exc
        data = resp.json()
        if not data.get("ok"):
            raise TelegramAPIError(
                data.get("description", "Unknown error"),
                data.get("error_code"),
            )
        return data["result"]

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
