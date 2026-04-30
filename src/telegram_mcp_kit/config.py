"""Centralized configuration for Telegram MCP Server."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration in one place. Add new fields here to extend."""

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # MCP Server
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000
    mcp_transport: str = "stdio"

    # HTTP Client
    http_timeout: float = 30.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
