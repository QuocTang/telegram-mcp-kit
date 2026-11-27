"""Centralized configuration for Telegram MCP Server."""

from typing import Literal

from pydantic_settings import BaseSettings


def _split_csv(value: str) -> list[str]:
    """Return the non-empty, stripped items of a comma-separated string."""
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """All configuration in one place. Add new fields here to extend."""

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Safety
    telegram_allowed_chats: str = ""
    telegram_read_only: bool = False
    telegram_dry_run: bool = False
    telegram_upload_dirs: str = ""
    telegram_wrap_updates: bool = False
    telegram_confirm_destructive: Literal["auto", "require", "off"] = "auto"
    telegram_approver_ids: str = ""

    # Rate limiting and retries
    telegram_max_retries: int = 3
    telegram_max_retry_wait: float = 60.0
    telegram_chat_interval: float = 0.0
    telegram_global_interval: float = 0.0

    # MCP Server
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000
    mcp_transport: str = "stdio"

    # HTTP Client
    http_timeout: float = 30.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def allowed_chats(self) -> list[str]:
        """Chat ids and @usernames from TELEGRAM_ALLOWED_CHATS; empty means no restriction."""
        return _split_csv(self.telegram_allowed_chats)

    @property
    def approver_ids(self) -> set[int]:
        """User ids from TELEGRAM_APPROVER_IDS allowed to answer ask_approval."""
        return {int(item) for item in _split_csv(self.telegram_approver_ids)}

    @property
    def upload_dirs(self) -> list[str]:
        """Directories from TELEGRAM_UPLOAD_DIRS; empty means no restriction."""
        return _split_csv(self.telegram_upload_dirs)


settings = Settings()
