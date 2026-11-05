"""Read-only ledger inspector placeholders for the P4 harness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RequestRecord:
    request_id: str
    status: str
    revision: int
    content_hash: str
    decision: dict[str, Any]
    requester: str
    resource: str
    start_utc: str
    end_utc: str
    project: str


@dataclass(frozen=True)
class BookingRecord:
    booking_id: str
    request_id: str | None
    status: str
    person_id: str
    instrument_id: str
    start_utc: str
    end_utc: str


@dataclass(frozen=True)
class AuditEvent:
    seq: int
    actor_agent: str
    tool: str
    args: dict[str, Any]
    result: dict[str, Any]
    hash: str


@dataclass(frozen=True)
class LedgerSnapshot:
    requests: tuple[RequestRecord, ...]
    bookings: tuple[BookingRecord, ...]
    audit_events: tuple[AuditEvent, ...]
    audit_valid: bool
    bad_audit_sequence: int | None = None


class LedgerInspector:
    def __init__(self, path: Path) -> None:
        self.path = path

    def snapshot(self) -> LedgerSnapshot:
        raise NotImplementedError("Read-only ledger inspection is not implemented yet.")
