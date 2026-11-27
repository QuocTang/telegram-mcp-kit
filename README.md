# 🚀 telegram-mcp-kit

> *MCP server that exposes the [Telegram Bot API](https://core.telegram.org/bots/api) as tools for Claude Code (or any MCP client).*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

## Table of Contents

- [🚀 Quick Start](#quick-start)
- [🛠️ Installation](#installation)
- [📦 Features](#features)
- [🤝 How to Contribute](#how-to-contribute)
- [💬 Community & Support](#community--support)
- [👥 Repo Contributors](#repo-contributors)
- [⚖️ License](#license)
- [🌟 Star History](#star-history)

---

## 🚀 Quick Start

Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram. Once the server is configured, you can run `/mcp` inside Claude Code to verify it is connected.

## 🛠️ Installation

> Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram first.

### Option 1: From PyPI (recommended)

```bash
claude mcp add telegram-mcp-kit \
  -e TELEGRAM_BOT_TOKEN=your-bot-token-here \
  -e TELEGRAM_CHAT_ID=your-chat-id \
  -- uvx telegram-mcp-kit
```

<details>
<summary>Manual MCP config</summary>

```json
{
  "mcpServers": {
    "telegram-mcp-kit": {
      "command": "uvx",
      "args": ["telegram-mcp-kit"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-bot-token-here",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      }
    }
  }
}
```

</details>

### Option 2: From GitHub

```bash
claude mcp add telegram-mcp-kit \
  -e TELEGRAM_BOT_TOKEN=your-bot-token-here \
  -e TELEGRAM_CHAT_ID=your-chat-id \
  -- uvx --from "git+https://github.com/QuocTang/telegram-mcp-kit.git" telegram-mcp-kit
```

<details>
<summary>Manual MCP config</summary>

```json
{
  "mcpServers": {
    "telegram-mcp-kit": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/QuocTang/telegram-mcp-kit.git",
        "telegram-mcp-kit"
      ],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-bot-token-here",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      }
    }
  }
}
```

</details>

### Option 3: From source

```bash
git clone https://github.com/QuocTang/telegram-mcp-kit.git
cd telegram-mcp-kit
cp .env.example .env   # add your TELEGRAM_BOT_TOKEN
uv sync
```

```bash
claude mcp add telegram-mcp-kit \
  -- uv run --directory /absolute/path/to/telegram-mcp-kit telegram-mcp-kit
```

<details>
<summary>Manual MCP config</summary>

```json
{
  "mcpServers": {
    "telegram-mcp-kit": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/telegram-mcp-kit",
        "telegram-mcp-kit"
      ]
    }
  }
}
```

> With this option, `TELEGRAM_BOT_TOKEN` is read from the `.env` file inside the project directory.

</details>

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Token from BotFather |
| `TELEGRAM_CHAT_ID` | No | Default chat ID (if set, `chat_id` can be omitted in tool calls) |
| `MCP_TRANSPORT` | No | `stdio` (default), `streamable-http` (alias `http`) or the deprecated `sse` |
| `MCP_HOST` | No | Bind host for `streamable-http` and `sse` (default `127.0.0.1`) |
| `MCP_PORT` | No | Bind port for `streamable-http` and `sse` (default `8000`) |
| `HTTP_TIMEOUT` | No | Telegram API timeout in seconds (default `30`) |

#### Safety

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_ALLOWED_CHATS` | empty (all chats) | Comma-separated chat ids or `@usernames`. Tools refuse other chats, and `get_updates` drops their updates. Ids and usernames are compared as written. |
| `TELEGRAM_READ_ONLY` | `false` | Registers only tools with `readOnlyHint=true`; every sending, editing and deleting tool is removed. |
| `TELEGRAM_DRY_RUN` | `false` | Methods that change state are not sent; tools return the request that would have been sent. Read methods still call Telegram. |
| `TELEGRAM_UPLOAD_DIRS` | empty (any path) | Comma-separated directories. Local uploads must resolve (after symlinks and `..`) inside one of them. |
| `TELEGRAM_WRAP_UPDATES` | `false` | Wraps `get_updates` text in `<untrusted_telegram_content nonce="…">` tags with a notice that the content is user data, not instructions. Recommended when the bot reads messages from people you do not control. |
| `TELEGRAM_CONFIRM_DESTRUCTIVE` | `auto` | Confirmation for `delete_message`, `ban_member`, `set_chat_title`, `set_chat_description`. `auto`: ask through an MCP elicitation dialog when the client supports it, otherwise proceed. `require`: same, but a client without elicitation must pass `confirm=true`. `off`: never ask. |
| `TELEGRAM_APPROVER_IDS` | empty | Comma-separated Telegram user ids allowed to answer `ask_approval`. When empty, only the user of a private chat can answer; groups need this variable. |

#### Rate limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_MAX_RETRIES` | `3` | Retries after a `429 Too Many Requests` response, waiting `parameters.retry_after` seconds each time |
| `TELEGRAM_MAX_RETRY_WAIT` | `60` | A 429 asking to wait longer than this many seconds is returned as an error instead of retried |
| `TELEGRAM_CHAT_INTERVAL` | `0` (off) | Minimum seconds between two sending requests to the same chat. The [Bot FAQ](https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this) advises at most 1 message per second per chat and 20 per minute in a group. |
| `TELEGRAM_GLOBAL_INTERVAL` | `0` (off) | Minimum seconds between any two sending requests (the FAQ limit for bulk sending is about 30 messages per second, i.e. `0.034`) |

### Confirmation of destructive actions

Claude Code supports MCP elicitation and shows a confirmation dialog in interactive sessions ([Claude Code docs: Respond to MCP elicitation requests](https://code.claude.com/docs/en/mcp#respond-to-mcp-elicitation-requests)). In `claude -p` (headless) sessions an elicitation is cancelled unless an `Elicitation` hook answers it, so the destructive call is refused. For unattended use set `TELEGRAM_CONFIRM_DESTRUCTIVE=off`, or `TELEGRAM_READ_ONLY=true` when the agent must not change anything.

## 📦 Features

| 🚀 Feature | 📝 Description |
|------------|----------------|
| 🛠️ **31 Tools** | Messages, rich messages, media, polls, reactions, chat management, progress drafts, approval buttons and bot info. |
| 🧾 **Structured output** | Every tool publishes an `outputSchema` and the annotations `readOnlyHint`, `destructiveHint`, `idempotentHint` and `openWorldHint`. |
| 🛡️ **Guards** | Chat allowlist, read-only mode, dry-run, upload directory restriction, untrusted-content tags, confirmation of destructive actions. |
| ⏱️ **Rate limits** | Retries 429 responses after `retry_after`, optional pacing, automatic split of text over 4096 and captions over 1024 characters. |
| 🔍 **Auto-discovery** | A Python file added to the `tools/` folder is registered automatically. |
| 📡 **Transports** | **stdio** for local clients, **Streamable HTTP** for remote and Docker. |

### Tools List

Every send tool accepts `message_thread_id` to post in a forum topic (or a topic of a private chat with the bot).

#### Messages

| Tool | Description |
|------|-------------|
| `send_message` | Send a text message (Markdown/HTML); text over 4096 characters is split into several messages |
| `send_rich_message` | Send a rich message (headings, lists, task lists, tables, quotes, formulas) as rich Markdown, HTML or blocks |
| `edit_message` | Edit an existing message |
| `delete_message` | Delete a message (asks for confirmation) |
| `forward_message` | Forward a message between chats |
| `escape_markdown_v2` | Escape text for `parse_mode="MarkdownV2"` (no API call) |

#### Interaction

| Tool | Description |
|------|-------------|
| `set_reaction` | Set or remove the bot's emoji reaction on a message |
| `send_chat_action` | Show "typing…", "uploading document…" and similar statuses |
| `send_poll` | Send a poll or quiz |
| `send_checklist` | Send a checklist through a business connection |
| `send_progress` | Stream live progress with `sendMessageDraft` (private chats), then persist the final text |
| `ask_approval` | Send approve/reject buttons and wait for an allowed user to press one; returns `approved`, `rejected` or `timeout` |

#### Updates

| Tool | Description |
|------|-------------|
| `get_updates` | Fetch recent messages/updates the bot received |

#### Chat management

| Tool | Description |
|------|-------------|
| `get_chat_info` | Get chat metadata (name, type, description) |
| `get_chat_member_count` | Count members |
| `get_chat_admins` | List administrators |
| `ban_member` | Ban a user (asks for confirmation) |
| `unban_member` | Unban a user |
| `set_chat_title` | Change group/channel title (asks for confirmation) |
| `set_chat_description` | Change group/channel description (asks for confirmation) |
| `pin_message` | Pin a message |
| `unpin_message` | Unpin a message |

#### Files & media

| Tool | Description |
|------|-------------|
| `send_photo` | Send a photo by URL or file_id |
| `send_photo_file` | Send a local photo file |
| `send_document` | Send a document by URL or file_id |
| `send_document_file` | Send a local file as document |
| `send_video` | Send a video by URL/file_id or local file |
| `send_audio` | Send an audio file by URL/file_id or local file |
| `send_media_group` | Send 2-10 photos, videos, documents or audios as an album |
| `get_file_info` | Get file metadata + download link |

Captions over 1024 characters are cut at a line break and the rest is sent as reply messages (except in albums, where a long caption is rejected).

#### Bot

| Tool | Description |
|------|-------------|
| `get_bot_info` | Get bot name, username, etc. |

### Tool results

Tools return structured content. Send tools return `{"messages": [...]}` with the Telegram `Message` objects (several when a text or caption was split). State-changing tools without a message return `{"ok", "detail", "result"}`. `get_updates` returns `{"updates": [...], "notice"}`.

## 🤝 How to Contribute

We welcome contributions! Please follow these steps:

1. **Fork** the repository.
2. **Create a new branch** for your feature.
3. **Submit a Pull Request**.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new tools.

### Development

```bash
uv sync                        # install all deps (including dev)
uv run pytest -v               # run tests
uv run ruff check src/ tests/  # lint
```

## 💬 Community & Support

If this repository saves you time, please star the repository!

## 👥 Repo Contributors

<a href="https://github.com/QuocTang/telegram-mcp-kit/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=QuocTang/telegram-mcp-kit" alt="Repository contributors" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## ⚖️ License

MIT License. See [LICENSE](LICENSE) for details.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=QuocTang/telegram-mcp-kit&type=Date)](https://star-history.com/#QuocTang/telegram-mcp-kit&Date)
