"""Approval request transitions and decision payload construction."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from labquorum.domain.canonical import canonical_json
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import utc_timestamp


class RequestStatus(StrEnum):
    PENDING = "pending"
    COMMITTED = "committed"
    DECLINED = "declined"
    EXPIRED = "expired"


def transition_status(current: RequestStatus, target: RequestStatus) -> RequestStatus:
    if current is not RequestStatus.PENDING:
        raise LabQuorumError(
            ErrorCode.ALREADY_DECIDED,
            f"A {current.value} request cannot transition to {target.value}.",
        )
    if target not in {RequestStatus.COMMITTED, RequestStatus.DECLINED, RequestStatus.EXPIRED}:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Pending requests need a terminal status.")
    return target


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
    if not action or not requester or not resource or not request_id or revision < 1:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Decision fields must be non-empty and revision positive."
        )
    if (
        start_utc.tzinfo is None
        or start_utc.utcoffset() is None
        or end_utc.tzinfo is None
        or end_utc.utcoffset() is None
    ):
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Decision interval times must be aware.")
    if end_utc.astimezone(UTC) <= start_utc.astimezone(UTC):
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Decision interval end must be after start."
        )
    return {
        "action": action,
        "requester": requester,
        "resource": resource,
        "interval": {
            "start_utc": utc_timestamp(start_utc),
            "end_utc": utc_timestamp(end_utc),
        },
        "project": project,
        "request_id": request_id,
        "revision": revision,
    }


def serialize_decision(decision: dict[str, Any]) -> str:
    rendered = canonical_json(decision)
    if len(rendered) >= 900:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Canonical approval decision exceeds 900 characters.",
            {"characters": len(rendered), "limit": 900},
        )
    return rendered


def next_revision(revision: int) -> int:
    if revision < 1:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Revision must be positive.")
    return revision + 1


def is_expired(now: datetime, expires_utc: datetime) -> bool:
    if now.tzinfo is None or now.utcoffset() is None:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Current time must be time-zone aware.")
    if expires_utc.tzinfo is None or expires_utc.utcoffset() is None:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Expiry time must be time-zone aware.")
    return now >= expires_utc
