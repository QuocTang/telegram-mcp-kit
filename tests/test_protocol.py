"""End-to-end MCP tests: annotations, outputSchema, elicitation and transports."""

import warnings

import pytest
from mcp import Client
from mcp.types import ElicitResult

from telegram_mcp_kit.server import resolve_transport
from telegram_mcp_kit.tools import discover_tools
from telegram_mcp_kit.tools._base import TOOL_KINDS, mcp

discover_tools()

SETTINGS = "telegram_mcp_kit.config.settings"
MODES = ["legacy", "2026-07-28"]


def _answer(action, confirmed=True):
    calls = []

    async def callback(context, params):
        calls.append(params)
        content = {"confirmed": confirmed} if action == "accept" else None
        return ElicitResult(action=action, content=content)

    return callback, calls


async def test_every_tool_has_annotations_and_output_schema():
    async with Client(mcp) as client:
        tools = (await client.list_tools()).tools
    assert tools
    for t in tools:
        a = t.annotations
        assert a is not None, t.name
        kind = TOOL_KINDS[t.name]
        assert a.read_only_hint is (kind == "read"), t.name
        assert a.destructive_hint is (kind == "destructive"), t.name
        assert a.idempotent_hint is not None, t.name
        assert t.output_schema is not None, t.name
    by_name = {t.name: t for t in tools}
    assert "messages" in by_name["send_message"].output_schema["properties"]
    assert "confirm" in by_name["delete_message"].input_schema["properties"]
    assert "approval" not in by_name["delete_message"].input_schema["properties"]


@pytest.mark.parametrize("mode", MODES)
async def test_delete_asks_and_proceeds_on_accept(mock_client, mode):
    mock_client.delete_message.return_value = True
    callback, calls = _answer("accept")
    async with Client(mcp, mode=mode, elicitation_callback=callback) as client:
        result = await client.call_tool("delete_message", {"message_id": 5, "chat_id": "1"})
    assert not result.is_error, result.content
    assert result.structured_content["ok"] is True
    assert "delete message 5" in calls[0].message
    mock_client.delete_message.assert_awaited_once_with("1", 5)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("action,confirmed", [("decline", True), ("accept", False)])
async def test_delete_aborts_without_consent(mock_client, mode, action, confirmed):
    callback, _ = _answer(action, confirmed)
    async with Client(mcp, mode=mode, elicitation_callback=callback) as client:
        result = await client.call_tool("ban_member", {"user_id": 7, "chat_id": "1"})
    assert result.is_error
    mock_client.ban_chat_member.assert_not_awaited()


async def test_require_mode_without_elicitation_needs_confirm(mock_client, monkeypatch):
    monkeypatch.setattr(f"{SETTINGS}.telegram_confirm_destructive", "require")
    mock_client.delete_message.return_value = True
    async with Client(mcp) as client:
        denied = await client.call_tool("delete_message", {"message_id": 1, "chat_id": "1"})
        allowed = await client.call_tool(
            "delete_message", {"message_id": 1, "chat_id": "1", "confirm": True}
        )
    assert denied.is_error
    assert "confirm=true" in denied.content[0].text
    assert not allowed.is_error
    mock_client.delete_message.assert_awaited_once()


async def test_auto_mode_without_elicitation_proceeds(mock_client):
    mock_client.set_chat_title.return_value = True
    async with Client(mcp) as client:
        result = await client.call_tool("set_chat_title", {"title": "T", "chat_id": "1"})
    assert not result.is_error


async def test_off_mode_skips_elicitation(mock_client, monkeypatch):
    monkeypatch.setattr(f"{SETTINGS}.telegram_confirm_destructive", "off")
    mock_client.delete_message.return_value = True
    callback, calls = _answer("decline")
    async with Client(mcp, elicitation_callback=callback) as client:
        result = await client.call_tool("delete_message", {"message_id": 1, "chat_id": "1"})
    assert not result.is_error
    assert calls == []


async def test_structured_send_result(mock_client):
    mock_client.send_message.return_value = {"message_id": 3, "text": "hi"}
    async with Client(mcp) as client:
        result = await client.call_tool("send_message", {"text": "hi", "chat_id": "1"})
    assert result.structured_content == {"messages": [{"message_id": 3, "text": "hi"}]}


def test_transport_aliases():
    assert resolve_transport("stdio") == "stdio"
    assert resolve_transport("http") == "streamable-http"
    assert resolve_transport("Streamable-HTTP") == "streamable-http"
    with pytest.raises(ValueError):
        resolve_transport("websocket")


def test_sse_warns_deprecated():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert resolve_transport("sse") == "sse"
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


async def test_ask_approval_over_mcp(mock_client, monkeypatch):
    monkeypatch.setattr("telegram_mcp_kit.tools.approval.POLL_SECONDS", 1)
    mock_client.send_message.return_value = {"message_id": 1}
    mock_client.get_updates.return_value = []
    async with Client(mcp) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
        assert "ctx" not in tools["ask_approval"].input_schema["properties"]
        result = await client.call_tool(
            "ask_approval", {"question": "Q", "chat_id": "42", "timeout_seconds": 1}
        )
    assert not result.is_error, result.content
    assert result.structured_content["status"] == "timeout"
