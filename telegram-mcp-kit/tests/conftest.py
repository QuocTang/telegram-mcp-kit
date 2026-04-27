"""Shared fixtures for all tool tests."""

from unittest.mock import AsyncMock, patch

import pytest

from telegram_mcp_kit.client import TelegramClient


@pytest.fixture()
def mock_client():
    """Return an AsyncMock that quacks like TelegramClient.

    Patches the module-level ``_client`` in ``_base`` so that
    ``get_client()`` returns this mock (since ``_client is not None``).
    """
    client = AsyncMock(spec=TelegramClient)
    with patch("telegram_mcp_kit.tools._base._client", client):
        yield client
