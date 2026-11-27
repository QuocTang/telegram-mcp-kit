"""HTTP-level tests: the JSON and multipart bodies TelegramClient sends."""

import json

import httpx

from telegram_mcp_kit.client import TelegramClient


def _recording_client(result=True):
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True, "result": result})

    client = TelegramClient("t")
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return client, requests


def _method(request: httpx.Request) -> str:
    return request.url.path.rsplit("/", 1)[-1]


async def test_send_message_uses_reply_parameters_and_thread():
    client, reqs = _recording_client({"message_id": 1})
    await client.send_message(1, "hi", None, 5, message_thread_id=7)
    assert _method(reqs[0]) == "sendMessage"
    assert json.loads(reqs[0].content) == {
        "chat_id": 1,
        "text": "hi",
        "reply_parameters": {"message_id": 5},
        "message_thread_id": 7,
    }


async def test_set_message_reaction_body():
    client, reqs = _recording_client()
    await client.set_message_reaction(1, 2, ["🔥"])
    assert json.loads(reqs[0].content) == {
        "chat_id": 1,
        "message_id": 2,
        "reaction": [{"type": "emoji", "emoji": "🔥"}],
    }


async def test_send_chat_action_body():
    client, reqs = _recording_client()
    await client.send_chat_action(1, "typing")
    assert _method(reqs[0]) == "sendChatAction"
    assert json.loads(reqs[0].content) == {"chat_id": 1, "action": "typing"}


async def test_send_poll_body_drops_none():
    client, reqs = _recording_client({"message_id": 1})
    await client.send_poll(1, "Q", ["a", "b"], type="regular", is_anonymous=None)
    assert json.loads(reqs[0].content) == {
        "chat_id": 1,
        "question": "Q",
        "options": [{"text": "a"}, {"text": "b"}],
        "type": "regular",
    }


async def test_send_checklist_body():
    client, reqs = _recording_client({"message_id": 1})
    await client.send_checklist("bc", 1, {"title": "T", "tasks": [{"id": 1, "text": "x"}]})
    body = json.loads(reqs[0].content)
    assert _method(reqs[0]) == "sendChecklist"
    assert body["business_connection_id"] == "bc"


async def test_send_rich_message_body():
    client, reqs = _recording_client({"message_id": 1})
    await client.send_rich_message(1, {"markdown": "# H"}, message_thread_id=3)
    assert _method(reqs[0]) == "sendRichMessage"
    assert json.loads(reqs[0].content) == {
        "chat_id": 1,
        "rich_message": {"markdown": "# H"},
        "message_thread_id": 3,
    }


async def test_send_media_by_url():
    client, reqs = _recording_client({"message_id": 1})
    await client.send_media("sendVideo", "video", 1, "https://e/v.mp4", caption="c")
    assert json.loads(reqs[0].content) == {"chat_id": 1, "caption": "c", "video": "https://e/v.mp4"}


async def test_send_media_upload_multipart(tmp_path):
    path = tmp_path / "a.mp3"
    path.write_bytes(b"AUDIO")
    client, reqs = _recording_client({"message_id": 1})
    await client.send_media("sendAudio", "audio", 1, file_path=str(path), message_thread_id=2)
    body = reqs[0].content
    assert b'name="audio"' in body and b"AUDIO" in body
    assert b'name="message_thread_id"' in body


async def test_send_media_group_upload(tmp_path):
    path = tmp_path / "p.jpg"
    path.write_bytes(b"IMG")
    client, reqs = _recording_client([{"message_id": 1}, {"message_id": 2}])
    media = [{"type": "photo", "media": "x"}, {"type": "photo", "media": "attach://file1"}]
    result = await client.send_media_group(1, media, {"file1": str(path)})
    assert len(result) == 2
    body = reqs[0].content
    assert b'name="file1"' in body and b"IMG" in body
    assert b"attach://file1" in body
