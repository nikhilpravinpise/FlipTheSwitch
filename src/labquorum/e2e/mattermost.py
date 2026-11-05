"""Mattermost REST client placeholders for the P4 harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class MattermostError(RuntimeError):
    """Base exception for sanitized Mattermost API failures."""


class MattermostAuthenticationError(MattermostError):
    """Raised when a persona cannot log in."""


class ReplyTimeout(MattermostError):
    """Raised when no matching agent reply arrives before the timeout."""


@dataclass(frozen=True)
class MattermostPost:
    post_id: str
    channel_id: str
    user_id: str
    message: str
    create_at: int
    root_id: str | None = None
    props: dict[str, Any] | None = None


class MattermostClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("Mattermost REST client is not implemented yet.")
