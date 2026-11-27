"""Tests ensuring the bot token never appears in log output or error messages."""

import logging

import httpx
import pytest

from telegram_mcp_kit.client import TelegramClient
from telegram_mcp_kit.exceptions import TelegramNetworkError

TOKEN = "123456789:SECRET-token-for-tests"


def _ok_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"ok": True, "result": {"id": 1}})


def _failing_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError(f"cannot reach {request.url}", request=request)


def _client_with(handler) -> TelegramClient:
    client = TelegramClient(TOKEN)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return client


@pytest.mark.parametrize("root_level", [logging.DEBUG, logging.INFO])
async def test_request_does_not_log_token(caplog, root_level):
    caplog.set_level(root_level)
    client = _client_with(_ok_handler)

    await client._request("getMe")

    assert TOKEN not in caplog.text
    for record in caplog.records:
        assert TOKEN not in record.getMessage()


async def test_network_error_masks_token(caplog):
    caplog.set_level(logging.DEBUG)
    client = _client_with(_failing_handler)

    with pytest.raises(TelegramNetworkError) as exc_info:
        await client._request("getMe")

    assert TOKEN not in str(exc_info.value)
    assert TOKEN not in caplog.text
