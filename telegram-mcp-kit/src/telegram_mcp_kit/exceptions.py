"""Custom exceptions for Telegram API interactions."""

import httpx


class TelegramError(Exception):
    """Base exception for all Telegram-related errors."""


class TelegramAPIError(TelegramError):
    """Telegram API returned an error response (ok=false)."""

    def __init__(self, description: str, error_code: int | None = None):
        self.description = description
        self.error_code = error_code
        msg = f"[{error_code}] {description}" if error_code else description
        super().__init__(msg)


class TelegramNetworkError(TelegramError):
    """Network-level failure when calling the Telegram API."""

    def __init__(self, cause: httpx.HTTPError):
        self.cause = cause
        super().__init__(str(cause))
