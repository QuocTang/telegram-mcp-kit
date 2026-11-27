"""Tests for telegram_mcp_kit.tools.files."""

import pytest

from telegram_mcp_kit.tools.files import (
    MediaItem,
    get_file_info,
    send_audio,
    send_document,
    send_document_file,
    send_media_group,
    send_photo,
    send_photo_file,
    send_video,
)


def _media_call(mock_client):
    args = mock_client.send_media.await_args
    return args.args, args.kwargs


async def test_send_photo(mock_client):
    mock_client.send_media.return_value = {"message_id": 1}
    result = await send_photo("https://example.com/photo.jpg", chat_id="123", caption="nice")
    assert result.messages[0]["message_id"] == 1
    args, kwargs = _media_call(mock_client)
    assert args == ("sendPhoto", "photo", "123", "https://example.com/photo.jpg", None)
    assert kwargs["caption"] == "nice"


async def test_send_photo_file(mock_client, tmp_path):
    mock_client.send_media.return_value = {"message_id": 2}
    result = await send_photo_file(str(tmp_path / "photo.jpg"), chat_id="123")
    assert result.messages[0]["message_id"] == 2
    args, _ = _media_call(mock_client)
    assert args[3] is None and args[4] == str(tmp_path / "photo.jpg")


async def test_send_document(mock_client):
    mock_client.send_media.return_value = {"message_id": 3}
    result = await send_document("https://example.com/file.pdf", chat_id="123")
    assert result.messages[0]["message_id"] == 3


async def test_send_document_file(mock_client, tmp_path):
    mock_client.send_media.return_value = {"message_id": 4}
    result = await send_document_file(str(tmp_path / "f.pdf"), chat_id="123")
    assert result.messages[0]["message_id"] == 4


async def test_send_video_with_thread(mock_client):
    mock_client.send_media.return_value = {"message_id": 5}
    await send_video(video="vid-id", chat_id="1", message_thread_id=9, supports_streaming=True)
    args, kwargs = _media_call(mock_client)
    assert args[:4] == ("sendVideo", "video", "1", "vid-id")
    assert kwargs["message_thread_id"] == 9
    assert kwargs["supports_streaming"] is True


async def test_send_audio_requires_one_source(mock_client):
    with pytest.raises(ValueError):
        await send_audio(chat_id="1")
    with pytest.raises(ValueError):
        await send_audio(audio="a", file_path="/tmp/a.mp3", chat_id="1")


async def test_send_audio_metadata(mock_client):
    mock_client.send_media.return_value = {"message_id": 6}
    await send_audio(audio="a", chat_id="1", performer="P", title="T")
    _, kwargs = _media_call(mock_client)
    assert kwargs["performer"] == "P" and kwargs["title"] == "T"


async def test_send_media_group(mock_client, tmp_path):
    mock_client.send_media_group.return_value = [{"message_id": 7}, {"message_id": 8}]
    items = [
        MediaItem(type="photo", media="https://e/1.jpg", caption="one"),
        MediaItem(type="photo", file_path=str(tmp_path / "2.jpg")),
    ]
    result = await send_media_group(items, chat_id="1", message_thread_id=3)
    assert [m["message_id"] for m in result.messages] == [7, 8]
    args = mock_client.send_media_group.await_args
    media, files = args.args[1], args.args[2]
    assert media[0] == {"type": "photo", "media": "https://e/1.jpg", "caption": "one"}
    assert media[1] == {"type": "photo", "media": "attach://file1"}
    assert files == {"file1": str(tmp_path / "2.jpg")}
    assert args.kwargs["message_thread_id"] == 3


async def test_send_media_group_validates_count(mock_client):
    with pytest.raises(ValueError):
        await send_media_group([MediaItem(type="photo", media="x")], chat_id="1")


async def test_get_file_info(mock_client):
    mock_client.get_file.return_value = {"file_id": "abc", "file_path": "photos/file.jpg"}
    result = await get_file_info("abc")
    assert "download_url" in result
    assert "photos/file.jpg" in result["download_url"]
