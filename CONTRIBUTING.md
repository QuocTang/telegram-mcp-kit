# Contributing

Thanks for your interest in contributing to **telegram-mcp-kit**!

## How to add a new tool

Adding a tool requires **one file** and **zero changes** to existing code.

1. Create a new file under `src/telegram_mcp_kit/tools/` (e.g. `stickers.py`).
2. Import the shared `mcp` instance and `get_client` helper:

   ```python
   from telegram_mcp_kit.tools._base import get_client, mcp
   ```

3. Define your tool with the `@mcp.tool()` decorator:

   ```python
   @mcp.tool()
   async def send_sticker(chat_id: str, sticker: str) -> str:
       """Send a sticker to a chat.

       Args:
           chat_id: Chat ID or @channel_username
           sticker: Sticker file_id or URL
       """
       result = await get_client()._request(
           "sendSticker", json={"chat_id": chat_id, "sticker": sticker}
       )
       return json.dumps(result, ensure_ascii=False, indent=2)
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
