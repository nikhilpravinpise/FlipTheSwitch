"""Approval request transitions and decision payload construction."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any


class RequestStatus(StrEnum):
    PENDING = "pending"
    COMMITTED = "committed"
    DECLINED = "declined"
    EXPIRED = "expired"


def transition_status(current: RequestStatus, target: RequestStatus) -> RequestStatus:
    raise NotImplementedError


def approval_decision(  # noqa: PLR0913
    *,
    action: str,
    requester: str,
    resource: str,
    start_utc: datetime,
    end_utc: datetime,
    project: str,
    request_id: str,
    revision: int,
) -> dict[str, Any]:
    raise NotImplementedError


def serialize_decision(decision: dict[str, Any]) -> str:
    raise NotImplementedError


def next_revision(revision: int) -> int:
    raise NotImplementedError


def is_expired(now: datetime, expires_utc: datetime) -> bool:
    raise NotImplementedError
