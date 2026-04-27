"""Tests for telegram_mcp_kit.tools.files."""

import json

from telegram_mcp_kit.tools.files import (
    get_file_info,
    send_document,
    send_document_file,
    send_photo,
    send_photo_file,
)


async def test_send_photo(mock_client):
    mock_client.send_photo.return_value = {"message_id": 1}
    result = await send_photo("https://example.com/photo.jpg", chat_id="123", caption="nice")
    parsed = json.loads(result)
    assert parsed["message_id"] == 1
    mock_client.send_photo.assert_awaited_once_with(
        "123", "https://example.com/photo.jpg", "nice", None
    )


async def test_send_photo_file(mock_client):
    mock_client.send_photo_file.return_value = {"message_id": 2}
    result = await send_photo_file("/tmp/photo.jpg", chat_id="123")
    assert json.loads(result)["message_id"] == 2


async def test_send_document(mock_client):
    mock_client.send_document.return_value = {"message_id": 3}
    result = await send_document("https://example.com/file.pdf", chat_id="123")
    assert json.loads(result)["message_id"] == 3


async def test_send_document_file(mock_client):
    mock_client.send_document_file.return_value = {"message_id": 4}
    result = await send_document_file("/tmp/file.pdf", chat_id="123")
    assert json.loads(result)["message_id"] == 4


async def test_get_file_info(mock_client):
    mock_client.get_file.return_value = {"file_id": "abc", "file_path": "photos/file.jpg"}
    result = await get_file_info("abc")
    parsed = json.loads(result)
    assert "download_url" in parsed
    assert "photos/file.jpg" in parsed["download_url"]
