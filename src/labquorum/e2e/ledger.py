"""Read-only views over LabQuorum's SQLite ledger and audit chain."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote

from labquorum.store.audit import tail, verify


@dataclass(frozen=True)
class RequestRecord:
    request_id: str
    status: str
    revision: int
    content_hash: str
    decision: dict[str, Any]
    requester: str
    resource: str
    resource_timezone: str | None
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
    schema_version: int | None = None
    ledger_identity: str = ""

    def request(self, request_id: str) -> RequestRecord | None:
        return next(
            (request for request in self.requests if request.request_id == request_id), None
        )

    def bookings_for(self, request_id: str) -> tuple[BookingRecord, ...]:
        return tuple(booking for booking in self.bookings if booking.request_id == request_id)

    def commit_events_for(self, request_id: str) -> tuple[AuditEvent, ...]:
        return tuple(
            event
            for event in self.audit_events
            if event.tool == "commit_booking" and event.args.get("request_id") == request_id
        )


class LedgerInspector:
    """Read ledger rows without opening a write transaction or lazy-expiring rows."""

    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().resolve(strict=False)
        encoded = quote(self.path.as_posix(), safe="/:\\")
        self.read_only_uri = f"file:{encoded}?mode=ro"

    def snapshot(self) -> LedgerSnapshot:
        try:
            connection = sqlite3.connect(self.read_only_uri, uri=True, timeout=5.0)
        except sqlite3.Error as exc:
            raise RuntimeError("Could not open the configured ledger read-only.") from exc
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA query_only = ON")
            schema_row = connection.execute("SELECT version FROM schema_version").fetchone()
            schema_version = int(schema_row["version"]) if schema_row is not None else None
            requests = tuple(
                _request_record(row)
                for row in connection.execute(
                    "SELECT request.id, request.status, request.revision, request.content_hash, "
                    "request.decision_json, request.requester, request.resource, "
                    "instrument.timezone AS resource_timezone, request.start_utc, request.end_utc, "
                    "request.project FROM approval_request AS request LEFT JOIN instrument "
                    "ON instrument.id = request.resource ORDER BY request.id"
                ).fetchall()
            )
            bookings = tuple(
                _booking_record(row)
                for row in connection.execute(
                    "SELECT id, request_id, status, person_id, instrument_id, start_utc, end_utc "
                    "FROM booking ORDER BY id"
                ).fetchall()
            )
            bad_sequence = verify(connection)
            event_count_row = connection.execute(
                "SELECT COUNT(*) AS count FROM audit_event"
            ).fetchone()
            event_count = int(event_count_row["count"]) if event_count_row is not None else 0
            raw_events = tail(connection, limit=max(event_count, 1)) if event_count else []
            events = tuple(_audit_event(event) for event in raw_events)
            return LedgerSnapshot(
                requests=requests,
                bookings=bookings,
                audit_events=events,
                audit_valid=bad_sequence is None,
                bad_audit_sequence=bad_sequence,
                schema_version=schema_version,
                ledger_identity=str(self.path),
            )
        except sqlite3.Error as exc:
            raise RuntimeError("The configured ledger does not have the expected schema.") from exc
        finally:
            connection.close()


def _request_record(row: sqlite3.Row) -> RequestRecord:
    decision = json.loads(str(row["decision_json"]))
    if not isinstance(decision, dict):
        raise RuntimeError("Ledger request decision is not a JSON object.")
    raw_timezone = row["resource_timezone"]
    return RequestRecord(
        request_id=str(row["id"]),
        status=str(row["status"]),
        revision=int(row["revision"]),
        content_hash=str(row["content_hash"]),
        decision=cast(dict[str, Any], decision),
        requester=str(row["requester"]),
        resource=str(row["resource"]),
        resource_timezone=str(raw_timezone) if raw_timezone is not None else None,
        start_utc=str(row["start_utc"]),
        end_utc=str(row["end_utc"]),
        project=str(row["project"]),
    )


def _booking_record(row: sqlite3.Row) -> BookingRecord:
    request_id = row["request_id"]
    return BookingRecord(
        booking_id=str(row["id"]),
        request_id=str(request_id) if request_id is not None else None,
        status=str(row["status"]),
        person_id=str(row["person_id"]),
        instrument_id=str(row["instrument_id"]),
        start_utc=str(row["start_utc"]),
        end_utc=str(row["end_utc"]),
    )


def _audit_event(event: dict[str, Any]) -> AuditEvent:
    return AuditEvent(
        seq=int(event["seq"]),
        actor_agent=str(event["actor_agent"]),
        tool=str(event["tool"]),
        args=cast(dict[str, Any], event["args"]),
        result=cast(dict[str, Any], event["result"]),
        hash=str(event["hash"]),
    )
