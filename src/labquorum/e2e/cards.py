"""Approval card placeholders for the P4 harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApprovalCard:
    handle: str
    post_id: str
    channel_id: str
    user_id: str
    message: str
    root_id: str | None = None
    options: tuple[tuple[int, str], ...] = ()


def find_approval_cards(posts: list[Any]) -> list[ApprovalCard]:
    raise NotImplementedError("Approval card discovery is not implemented yet.")
