"""Tests for telegram_mcp_kit.tools.interactive."""

import pytest

from telegram_mcp_kit.tools.interactive import (
    send_chat_action,
    send_checklist,
    send_poll,
    set_reaction,
)


async def test_set_reaction(mock_client):
    mock_client.set_message_reaction.return_value = True
    result = await set_reaction(5, "👍", chat_id="1", is_big=True)
    assert result.ok
    mock_client.set_message_reaction.assert_awaited_once_with("1", 5, ["👍"], True)


async def test_remove_reaction(mock_client):
    mock_client.set_message_reaction.return_value = True
    await set_reaction(5, chat_id="1")
    mock_client.set_message_reaction.assert_awaited_once_with("1", 5, [], False)


async def test_send_chat_action(mock_client):
    mock_client.send_chat_action.return_value = True
    result = await send_chat_action("upload_document", chat_id="1", message_thread_id=4)
    assert result.ok
    mock_client.send_chat_action.assert_awaited_once_with("1", "upload_document", 4)


async def test_send_poll(mock_client):
    mock_client.send_poll.return_value = {"message_id": 9, "poll": {"id": "p"}}
    result = await send_poll("Deploy?", ["Yes", "No"], chat_id="1", is_anonymous=False)
    assert result.messages[0]["poll"]["id"] == "p"
    args = mock_client.send_poll.await_args
    assert args.args == ("1", "Deploy?", ["Yes", "No"])
    assert args.kwargs["is_anonymous"] is False
    assert args.kwargs["type"] == "regular"


async def test_send_quiz_requires_answer(mock_client):
    with pytest.raises(ValueError):
        await send_poll("Q", ["a", "b"], chat_id="1", type="quiz")


async def test_send_poll_option_count(mock_client):
    with pytest.raises(ValueError):
        await send_poll("Q", [], chat_id="1")


async def test_send_checklist(mock_client):
    mock_client.send_checklist.return_value = {"message_id": 3}
    await send_checklist("bc1", "Release", ["Build", "Tag"], chat_id="1", others_can_add_tasks=True)
    mock_client.send_checklist.assert_awaited_once_with(
        "bc1",
        "1",
        {
            "title": "Release",
            "tasks": [{"id": 1, "text": "Build"}, {"id": 2, "text": "Tag"}],
            "others_can_add_tasks": True,
        },
    )
