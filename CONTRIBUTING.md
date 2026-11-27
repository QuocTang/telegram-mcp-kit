# Contributing

Thanks for your interest in contributing to **telegram-mcp-kit**!

## How to add a new tool

Adding a tool requires **one file** and **zero changes** to existing code.

1. Create a new file under `src/telegram_mcp_kit/tools/` (e.g. `stickers.py`).
2. Import the `tool` decorator and `get_client` helper:

   ```python
   from telegram_mcp_kit.models import SendResult
   from telegram_mcp_kit.tools._base import get_client, resolve_chat_id, tool
   ```

3. Define your tool with the `@tool(kind)` decorator. `kind` is `"read"`, `"write"` or
   `"destructive"`; it sets the MCP annotations and decides whether the tool survives
   `TELEGRAM_READ_ONLY`. Return a Pydantic model or `dict` so the tool publishes an
   `outputSchema`:

   ```python
   @tool("write")
   async def send_sticker(sticker: str, chat_id: str | None = None) -> SendResult:
       """Send a sticker to a chat.

       Args:
           chat_id: Chat ID or @channel_username
           sticker: Sticker file_id or URL
       """
       cid = resolve_chat_id(chat_id)
       result = await get_client()._request(
           "sendSticker", json={"chat_id": cid, "sticker": sticker}
       )
       return SendResult(messages=[result])
   ```

4. Add tests in `tests/test_tools_stickers.py`.
5. Run the checks:

   ```bash
   uv run ruff check src/ tests/
   uv run pytest -v
   ```

That's it! The auto-discovery system (`tools/__init__.py`) will pick up your new module automatically.

## Development setup

```bash
git clone <repo-url> && cd telegram-mcp-kit
cp .env.example .env          # add your TELEGRAM_BOT_TOKEN
uv sync                       # installs all deps including dev
uv run pytest -v              # run tests
uv run ruff check src/ tests/ # lint
```

## Code style

- Python 3.12+
- Formatted & linted with [Ruff](https://docs.astral.sh/ruff/)
- Tests with [pytest](https://docs.pytest.org/) + pytest-asyncio

## Pull requests

- One feature/fix per PR.
- Include tests for new tools.
- Make sure CI passes (`ruff check` + `pytest`).
