# Changelog

## 0.4.0

### Added

- Tools `send_rich_message`, `set_reaction`, `send_chat_action`, `send_poll`, `send_checklist`, `send_video`, `send_audio`, `send_media_group`, `send_progress`, `ask_approval` and `escape_markdown_v2`.
- `message_thread_id` on every send tool and on `forward_message`.
- Retry of `429 Too Many Requests` after `parameters.retry_after` (`TELEGRAM_MAX_RETRIES`, `TELEGRAM_MAX_RETRY_WAIT`) and optional pacing (`TELEGRAM_CHAT_INTERVAL`, `TELEGRAM_GLOBAL_INTERVAL`).
- Text over 4096 characters is sent as several messages; captions over 1024 characters are cut and the rest is sent as replies.
- Guards: `TELEGRAM_ALLOWED_CHATS`, `TELEGRAM_READ_ONLY`, `TELEGRAM_DRY_RUN`, `TELEGRAM_UPLOAD_DIRS`, `TELEGRAM_WRAP_UPDATES`.
- MCP tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) and `outputSchema` on every tool.
- Confirmation of `delete_message`, `ban_member`, `set_chat_title` and `set_chat_description` through MCP elicitation, with a `confirm=true` fallback (`TELEGRAM_CONFIRM_DESTRUCTIVE`).
- `MCP_TRANSPORT=http` as an alias of `streamable-http`.

### Changed

- Tool results are structured: send tools return `{"messages": [...]}`, state-changing tools return `{"ok", "detail", "result"}`, `get_chat_member_count` returns `{"count"}`, `get_updates` returns `{"updates", "notice"}`. The text content is the JSON of the structured result.
- Replies use `reply_parameters` instead of the undocumented `reply_to_message_id` parameter.
- The Docker image uses `MCP_TRANSPORT=streamable-http`.

### Deprecated

- `MCP_TRANSPORT=sse` logs a deprecation warning; the MCP specification 2026-07-28 marks HTTP+SSE as deprecated (SEP-2596).

## 0.3.0

- Migrate to MCP Python SDK 2.x (`MCPServer`), report the package version in `serverInfo`, mask the bot token in logs and errors.
