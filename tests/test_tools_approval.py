"""Tests for send_progress, ask_approval and the shared update buffer."""

from unittest.mock import AsyncMock

import pytest

from telegram_mcp_kit import update_buffer
from telegram_mcp_kit.tools import approval
from telegram_mcp_kit.tools.approval import ask_approval, send_progress
from telegram_mcp_kit.tools.updates import get_updates

SETTINGS = "telegram_mcp_kit.config.settings"


@pytest.fixture(autouse=True)
def fresh_buffer(monkeypatch):
    buf = update_buffer.UpdateBuffer()
    monkeypatch.setattr(approval, "buffer", buf)
    monkeypatch.setattr("telegram_mcp_kit.tools.updates.buffer", buf)
    return buf


@pytest.fixture()
def ctx():
    c = AsyncMock()
    c.report_progress = AsyncMock()
    return c


@pytest.fixture()
def clock(monkeypatch):
    now = [1000.0]

    def monotonic():
        now[0] += 1
        return now[0]

    monkeypatch.setattr(approval.time, "monotonic", monotonic)
    return now


def _press(uid, user_id, data):
    return {
        "update_id": uid,
        "callback_query": {
            "id": f"cb{uid}",
            "from": {"id": user_id, "username": "boss"},
            "data": data,
        },
    }


def _token(mock_client):
    markup = mock_client.send_message.await_args.kwargs["reply_markup"]
    return markup["inline_keyboard"][0][0]["callback_data"].split(":")[1]


async def test_send_progress_draft(mock_client):
    mock_client.send_message_draft.return_value = True
    result = await send_progress("Step 1/3", chat_id="42", draft_id=7, can_stop=True)
    assert result.ok
    mock_client.send_message_draft.assert_awaited_once_with(42, 7, "Step 1/3", None, None, True)


async def test_send_progress_final_sends_message(mock_client):
    mock_client.send_message.return_value = {"message_id": 3}
    result = await send_progress("Done", chat_id="42", final=True)
    assert result.messages[0]["message_id"] == 3
    mock_client.send_message_draft.assert_not_awaited()


async def test_send_progress_rejects_username_and_zero_draft(mock_client):
    with pytest.raises(ValueError):
        await send_progress("x", chat_id="@chan")
    with pytest.raises(ValueError):
        await send_progress("x", chat_id="42", draft_id=0)


async def test_approval_approved_by_private_chat_user(mock_client, ctx, clock):
    mock_client.send_message.return_value = {"message_id": 50}

    async def updates(offset, limit, allowed, timeout):
        token = _token(mock_client)
        assert allowed == ["message", "callback_query"] and timeout > 0
        return [
            {"update_id": 10, "message": {"chat": {"id": 42}, "text": "hello"}},
            _press(11, 42, f"apv:{token}:y"),
        ]

    mock_client.get_updates.side_effect = updates
    result = await ask_approval("Deploy v1?", ctx, chat_id="42", timeout_seconds=60)
    assert result.status == "approved"
    assert result.decided_by["id"] == 42
    assert result.message_id == 50
    mock_client.answer_callback_query.assert_awaited_once_with("cb11", "Approved")
    edit = mock_client.edit_message_text.await_args
    assert "Approved by @boss" in edit.args[2]
    assert edit.kwargs["reply_markup"] == {"inline_keyboard": []}


async def test_approval_ignores_non_approver(mock_client, ctx, clock, monkeypatch):
    monkeypatch.setattr(f"{SETTINGS}.telegram_approver_ids", "7, 8")
    mock_client.send_message.return_value = {"message_id": 1}
    batches = []

    async def updates(offset, limit, allowed, timeout):
        token = _token(mock_client)
        if not batches:
            batches.append(1)
            return [_press(1, 999, f"apv:{token}:y"), _press(2, 8, f"apv:{token}:n")]
        return []

    mock_client.get_updates.side_effect = updates
    result = await ask_approval("Drop table?", ctx, chat_id="-100", timeout_seconds=60)
    assert result.status == "rejected"
    assert result.ignored_presses == 1
    first, second = mock_client.answer_callback_query.await_args_list
    assert first.args[0] == "cb1" and first.kwargs["show_alert"] is True
    assert second.args == ("cb2", "Rejected")


async def test_approval_timeout(mock_client, ctx, clock):
    mock_client.send_message.return_value = {"message_id": 1}
    mock_client.get_updates.return_value = []
    result = await ask_approval("Q", ctx, chat_id="42", timeout_seconds=5)
    assert result.status == "timeout"
    assert "timed out" in mock_client.edit_message_text.await_args.args[2]


async def test_approval_requires_approvers_for_groups(mock_client, ctx):
    with pytest.raises(ValueError):
        await ask_approval("Q", ctx, chat_id="-100123")
    mock_client.send_message.assert_not_awaited()


async def test_approval_dry_run(mock_client, ctx):
    mock_client.send_message.return_value = {"dry_run": True, "method": "sendMessage"}
    result = await ask_approval("Q", ctx, chat_id="42")
    assert result.status == "dry_run"
    mock_client.get_updates.assert_not_awaited()


async def test_approval_escapes_outcome_for_markdown_v2(mock_client, ctx, clock):
    mock_client.send_message.return_value = {"message_id": 1}
    mock_client.get_updates.return_value = []
    await ask_approval("Q", ctx, chat_id="42", timeout_seconds=2, parse_mode="MarkdownV2")
    assert r"\(timed out\)" in mock_client.edit_message_text.await_args.args[2]


async def test_get_updates_returns_buffered_messages(mock_client, fresh_buffer):
    fresh_buffer.pending = [{"update_id": 10, "message": {"text": "kept"}}]
    mock_client.get_updates.return_value = [{"update_id": 11, "message": {"text": "new"}}]
    result = await get_updates()
    assert [u["update_id"] for u in result.structured_content["updates"]] == [10, 11]
    assert fresh_buffer.pending == []


async def test_buffer_advances_offset(mock_client):
    buf = update_buffer.UpdateBuffer()
    mock_client.get_updates.return_value = [{"update_id": 5}, {"update_id": 6}]
    await buf.fetch(mock_client, ["message"], 1)
    assert buf.next_offset == 7
    await buf.fetch(mock_client, ["message"], 1)
    assert mock_client.get_updates.await_args.args[0] == 7
    assert [u["update_id"] for u in buf.pending] == [5, 6]
