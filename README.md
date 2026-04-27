# 🚀 telegram-mcp-kit

> _MCP server that exposes the [Telegram Bot API](https://core.telegram.org/bots/api) as tools for Claude Code (or any MCP client)._

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
  -- uvx --from "git+https://github.com/QuocTang/telegram-bot.git#subdirectory=telegram-mcp-kit" telegram-mcp-kit
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
        "git+https://github.com/QuocTang/telegram-bot.git#subdirectory=telegram-mcp-kit",
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
git clone https://github.com/QuocTang/telegram-bot.git
cd telegram-bot/telegram-mcp-kit
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

| Variable             | Required | Description                                                      |
| -------------------- | -------- | ---------------------------------------------------------------- |
| `TELEGRAM_BOT_TOKEN` | Yes      | Token from BotFather                                             |
| `TELEGRAM_CHAT_ID`   | No       | Default chat ID (if set, `chat_id` can be omitted in tool calls) |
| `MCP_TRANSPORT`      | No       | `stdio` (default) or `sse`                                       |
| `MCP_HOST`           | No       | Bind host (default `127.0.0.1`)                                  |
| `MCP_PORT`           | No       | Bind port (default `8000`)                                       |
| `HTTP_TIMEOUT`       | No       | Telegram API timeout in seconds (default `30`)                   |

## 📦 Features

| 🚀 Feature                | 📝 Description                                                                    |
| ------------------------- | --------------------------------------------------------------------------------- |
| 🛠️ **20+ Tools**          | Comprehensive coverage for messages, chat management, files/photos, and bot info. |
| 🔍 **Auto-discovery**     | Simply add a Python file to the `tools/` folder and it registers automatically.   |
| 📡 **Flexible Transport** | Works seamlessly over **stdio** (for local clients) or **SSE** (remote/Docker).   |

### Tools List

#### Messages

| Tool              | Description                         |
| ----------------- | ----------------------------------- |
| `send_message`    | Send a text message (Markdown/HTML) |
| `edit_message`    | Edit an existing message            |
| `delete_message`  | Delete a message                    |
| `forward_message` | Forward a message between chats     |

#### Updates

| Tool          | Description                                    |
| ------------- | ---------------------------------------------- |
| `get_updates` | Fetch recent messages/updates the bot received |

#### Chat management

| Tool                    | Description                                 |
| ----------------------- | ------------------------------------------- |
| `get_chat_info`         | Get chat metadata (name, type, description) |
| `get_chat_member_count` | Count members                               |
| `get_chat_admins`       | List administrators                         |
| `ban_member`            | Ban a user                                  |
| `unban_member`          | Unban a user                                |
| `set_chat_title`        | Change group/channel title                  |
| `set_chat_description`  | Change group/channel description            |
| `pin_message`           | Pin a message                               |
| `unpin_message`         | Unpin a message                             |

#### Files & photos

| Tool                 | Description                       |
| -------------------- | --------------------------------- |
| `send_photo`         | Send a photo by URL or file_id    |
| `send_photo_file`    | Send a local photo file           |
| `send_document`      | Send a document by URL or file_id |
| `send_document_file` | Send a local file as document     |
| `get_file_info`      | Get file metadata + download link |

#### Bot

| Tool           | Description                  |
| -------------- | ---------------------------- |
| `get_bot_info` | Get bot name, username, etc. |

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

<a href="https://github.com/QuocTang/telegram-bot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=QuocTang/telegram-bot" alt="Repository contributors" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## ⚖️ License

MIT License. See [LICENSE](LICENSE) for details.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=QuocTang/telegram-bot&type=Date)](https://star-history.com/#QuocTang/telegram-bot&Date)
