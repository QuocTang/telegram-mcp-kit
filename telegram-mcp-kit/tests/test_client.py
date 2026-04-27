"""Tests for telegram_mcp_kit.client — TelegramClient._request error handling."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from telegram_mcp_kit.client import TelegramClient
from telegram_mcp_kit.exceptions import TelegramAPIError, TelegramNetworkError


@pytest.fixture()
def client():
    return TelegramClient("fake-token")


async def test_request_api_error(client):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"ok": False, "description": "Bad Request", "error_code": 400}

    with patch.object(client._client, "post", AsyncMock(return_value=mock_resp)):
        with pytest.raises(TelegramAPIError, match="Bad Request") as exc_info:
            await client._request("sendMessage", json={})
        assert exc_info.value.error_code == 400


async def test_request_network_error(client):
    with patch.object(
        client._client, "post", AsyncMock(side_effect=httpx.ConnectError("connection refused"))
    ):
        with pytest.raises(TelegramNetworkError):
            await client._request("sendMessage", json={})


async def test_request_success(client):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1}}

    with patch.object(client._client, "post", AsyncMock(return_value=mock_resp)):
        result = await client._request("sendMessage", json={})
        assert result == {"message_id": 1}
