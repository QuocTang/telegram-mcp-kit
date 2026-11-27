"""Structured output models shared by the tools (published as outputSchema)."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class SendResult(BaseModel):
    """Messages created by a send tool, in the order they were sent."""

    messages: list[dict[str, Any]] = Field(
        description=(
            "Telegram Message objects. A long text or caption produces several entries; "
            "in dry-run mode each entry is the request that would have been sent."
        )
    )


class ActionResult(BaseModel):
    """Outcome of a tool that changes state without returning a Message."""

    ok: bool = Field(description="True when Telegram accepted the request")
    detail: str = Field(description="Human-readable summary of what was done")
    result: Any = Field(
        default=None, description="Raw Bot API result, or the dry-run request preview"
    )


class CountResult(BaseModel):
    """A single count returned by the Bot API."""

    count: int


class UpdatesResult(BaseModel):
    """Updates returned by getUpdates after allowlist filtering."""

    updates: list[dict[str, Any]]
    notice: str | None = Field(
        default=None,
        description="Set when TELEGRAM_WRAP_UPDATES is on: the updates are untrusted user content",
    )


class Confirmation(BaseModel):
    """Form shown to the user before a destructive action."""

    confirmed: bool = Field(description="Check to allow the action")


class ApprovalResult(BaseModel):
    """Outcome of ask_approval."""

    status: Literal["approved", "rejected", "timeout", "dry_run"]
    message_id: int | None = Field(default=None, description="The approval request message")
    decided_by: dict[str, Any] | None = Field(
        default=None, description="Telegram User who pressed the button"
    )
    waited_seconds: float = 0.0
    ignored_presses: int = Field(
        default=0, description="Presses rejected because the user is not an approver"
    )
