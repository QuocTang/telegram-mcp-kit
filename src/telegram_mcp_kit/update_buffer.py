"""Shared getUpdates cursor so ask_approval and get_updates do not lose each other's updates."""

from telegram_mcp_kit.client import TelegramClient


class UpdateBuffer:
    """Fetches updates with a moving offset and keeps those no consumer has taken yet.

    getUpdates confirms every update below the offset it is called with, so a
    consumer that only wants callback queries would otherwise discard messages.
    """

    def __init__(self) -> None:
        self.next_offset: int | None = None
        self.pending: list[dict] = []

    async def fetch(
        self, client: TelegramClient, allowed_updates: list[str], timeout: int = 0
    ) -> None:
        """Fetch new updates into the buffer, long-polling up to *timeout* seconds."""
        updates = await client.get_updates(self.next_offset, 100, allowed_updates, timeout)
        if not isinstance(updates, list):
            return
        known = {u.get("update_id") for u in self.pending}
        for update in updates:
            uid = update.get("update_id")
            if isinstance(uid, int):
                self.next_offset = max(self.next_offset or 0, uid + 1)
            if uid not in known:
                self.pending.append(update)

    def take(self, predicate) -> dict | None:
        """Remove and return the first buffered update matching *predicate*."""
        for i, update in enumerate(self.pending):
            if predicate(update):
                return self.pending.pop(i)
        return None

    def drain(self, offset: int | None = None) -> list[dict]:
        """Remove and return buffered updates with ``update_id >= offset`` (all when None)."""
        if offset is not None and offset >= 0:
            kept = [u for u in self.pending if u.get("update_id", 0) >= offset]
        else:
            kept = list(self.pending)
        self.pending.clear()
        return kept


buffer = UpdateBuffer()
