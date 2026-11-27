"""Tests for 429 retries, pacing and dry-run in TelegramClient."""

import io
import json

import httpx
import pytest

from telegram_mcp_kit.client import RateLimiter, TelegramClient
from telegram_mcp_kit.exceptions import TelegramAPIError


def _client(handler, **kwargs) -> tuple[TelegramClient, list[float]]:
    client = TelegramClient("t", **kwargs)
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    client._sleep = fake_sleep
    return client, sleeps


def _flood(retry_after: int) -> httpx.Response:
    return httpx.Response(
        429,
        json={
            "ok": False,
            "error_code": 429,
            "description": "Too Many Requests: retry after 2",
            "parameters": {"retry_after": retry_after},
        },
    )


async def test_retries_429_after_retry_after():
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) < 3:
            return _flood(2)
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 7}})

    client, sleeps = _client(handler)
    result = await client._request("sendMessage", json={"chat_id": 1, "text": "x"})
    assert result == {"message_id": 7}
    assert sleeps == [2, 2]
    assert len(calls) == 3


async def test_gives_up_after_max_retries():
    client, sleeps = _client(lambda r: _flood(1), max_retries=2)
    with pytest.raises(TelegramAPIError) as exc:
        await client._request("sendMessage", json={"chat_id": 1, "text": "x"})
    assert exc.value.error_code == 429
    assert exc.value.retry_after == 1
    assert sleeps == [1, 1]


async def test_does_not_retry_when_wait_too_long():
    client, sleeps = _client(lambda r: _flood(120), max_retry_wait=60)
    with pytest.raises(TelegramAPIError):
        await client._request("sendMessage", json={"chat_id": 1, "text": "x"})
    assert sleeps == []


async def test_retry_rewinds_uploaded_file():
    bodies = []

    def handler(request):
        bodies.append(request.read())
        if len(bodies) == 1:
            return _flood(1)
        return httpx.Response(200, json={"ok": True, "result": True})

    client, _ = _client(handler)
    stream = io.BytesIO(b"PAYLOAD")
    stream.name = "a.txt"
    await client._request("sendDocument", data={"chat_id": "1"}, files={"document": stream})
    assert b"PAYLOAD" in bodies[1]


async def test_dry_run_skips_write_methods():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"ok": True, "result": {"id": 1}})

    client, _ = _client(handler, dry_run=True)
    preview = await client._request("sendMessage", json={"chat_id": 5, "text": "hi"})
    assert preview == {
        "dry_run": True,
        "method": "sendMessage",
        "params": {"chat_id": 5, "text": "hi"},
    }
    assert calls == []
    assert await client._request("getMe") == {"id": 1}
    assert len(calls) == 1


async def test_dry_run_lists_files():
    client, _ = _client(lambda r: httpx.Response(500), dry_run=True)
    stream = io.BytesIO(b"x")
    stream.name = "/tmp/a.png"
    preview = await client._request("sendPhoto", data={"chat_id": "1"}, files={"photo": stream})
    assert preview["files"] == {"photo": "/tmp/a.png"}
    json.dumps(preview)


async def test_rate_limiter_spaces_same_chat():
    now = [100.0]
    sleeps = []

    async def sleep(s):
        sleeps.append(s)
        now[0] += s

    limiter = RateLimiter(chat_interval=1.0, global_interval=0.1, clock=lambda: now[0], sleep=sleep)
    await limiter.acquire(1)
    await limiter.acquire(2)
    await limiter.acquire(1)
    assert sleeps[0] == pytest.approx(0.1)
    assert sleeps[1] == pytest.approx(0.9)


async def test_rate_limiter_disabled_by_default():
    limiter = RateLimiter()
    await limiter.acquire(1)
    await limiter.acquire(1)
