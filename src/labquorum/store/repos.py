"""Transactional booking and approval request repository operations."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime, time, timedelta
from typing import Any

from labquorum.domain.approvals import (
    RequestStatus,
    approval_decision,
    is_expired,
    next_revision,
    serialize_decision,
    transition_status,
)
from labquorum.domain.booking import (
    Booking,
    InstrumentPolicy,
    Interval,
    Training,
    check_booking,
)
from labquorum.domain.canonical import content_hash as canonical_hash
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock, parse_iso_datetime, utc_timestamp
from labquorum.store.audit import append_event
from labquorum.store.db import immediate_transaction


def _now(clock: Clock) -> datetime:
    value = clock.now()
    if value.tzinfo is None or value.utcoffset() is None:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Ledger clock must return an aware datetime."
        )
    return value.astimezone(UTC)


def _request_row(connection: sqlite3.Connection, request_id: str) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM approval_request WHERE id = ?", (request_id,)
    ).fetchone()
    if row is None:
        raise LabQuorumError(ErrorCode.NOT_FOUND, f"Approval request {request_id} was not found.")
    return row


def _request_result(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "request_id": str(row["id"]),
        "kind": str(row["kind"]),
        "requester": str(row["requester"]),
        "resource": str(row["resource"]),
        "start_utc": str(row["start_utc"]),
        "end_utc": str(row["end_utc"]),
        "project": str(row["project"]),
        "revision": int(row["revision"]),
        "content_hash": str(row["content_hash"]),
        "decision": json.loads(str(row["decision_json"])),
        "status": str(row["status"]),
        "created_utc": str(row["created_utc"]),
        "expires_utc": str(row["expires_utc"]),
        "decided_utc": str(row["decided_utc"]) if row["decided_utc"] is not None else None,
        "decline_reason": str(row["decline_reason"]) if row["decline_reason"] is not None else None,
    }


def _instrument_policy(connection: sqlite3.Connection, instrument_id: str) -> InstrumentPolicy:
    row = connection.execute("SELECT * FROM instrument WHERE id = ?", (instrument_id,)).fetchone()
    if row is None:
        raise LabQuorumError(ErrorCode.NOT_FOUND, f"Instrument {instrument_id} was not found.")
    weekly_raw = json.loads(str(row["opening_hours_json"]))
    weekly = {
        int(day): (time.fromisoformat(hours[0]), time.fromisoformat(hours[1]))
        for day, hours in weekly_raw.items()
    }
    down_until = (
        parse_iso_datetime(str(row["down_until_utc"]))
        if row["down_until_utc"] is not None
        else None
    )
    return InstrumentPolicy(
        instrument_id=str(row["id"]),
        timezone=str(row["timezone"]),
        opening_hours=weekly,
        max_block_minutes=int(row["max_block_minutes"]),
        min_gap_minutes=int(row["min_gap_minutes"]),
        booking_window_days=int(row["booking_window_days"]),
        status=str(row["status"]),
        down_until=down_until,
        requires_training=bool(row["requires_training"]),
    )


def _training(
    connection: sqlite3.Connection,
    person_id: str,
    instrument_id: str,
) -> Training | None:
    row = connection.execute(
        "SELECT granted_at_utc, expires_at_utc FROM training "
        "WHERE person_id = ? AND instrument_id = ?",
        (person_id, instrument_id),
    ).fetchone()
    if row is None:
        return None
    return Training(
        granted_at=parse_iso_datetime(str(row["granted_at_utc"])),
        expires_at=parse_iso_datetime(str(row["expires_at_utc"])),
    )


def _committed_bookings(connection: sqlite3.Connection, instrument_id: str) -> list[Booking]:
    rows = connection.execute(
        "SELECT id, start_utc, end_utc, status FROM booking "
        "WHERE instrument_id = ? AND status = 'committed' ORDER BY start_utc",
        (instrument_id,),
    ).fetchall()
    return [
        Booking(
            booking_id=str(row["id"]),
            interval=Interval(
                parse_iso_datetime(str(row["start_utc"])),
                parse_iso_datetime(str(row["end_utc"])),
            ),
            status=str(row["status"]),
        )
        for row in rows
    ]


def _validate_booking(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    person_id: str,
    instrument_id: str,
    interval: Interval,
    now: datetime,
    exclude_request_id: str | None = None,
) -> None:
    if connection.execute("SELECT 1 FROM person WHERE id = ?", (person_id,)).fetchone() is None:
        raise LabQuorumError(ErrorCode.NOT_FOUND, f"Person {person_id} was not found.")
    policy = _instrument_policy(connection, instrument_id)
    bookings = _committed_bookings(connection, instrument_id)
    if exclude_request_id is not None:
        booking_row = connection.execute(
            "SELECT id FROM booking WHERE request_id = ?",
            (exclude_request_id,),
        ).fetchone()
        if booking_row is not None:
            excluded_id = str(booking_row["id"])
            bookings = [booking for booking in bookings if booking.booking_id != excluded_id]
    check_booking(
        policy,
        interval,
        now=now,
        training=_training(connection, person_id, instrument_id),
        existing_bookings=bookings,
    )


def _next_number(connection: sqlite3.Connection, counter_name: str) -> int:
    row = connection.execute("SELECT value FROM counter WHERE name = ?", (counter_name,)).fetchone()
    number = int(row["value"]) if row is not None else 1
    if row is None:
        connection.execute(
            "INSERT INTO counter(name, value) VALUES (?, ?)", (counter_name, number + 1)
        )
    else:
        connection.execute(
            "UPDATE counter SET value = ? WHERE name = ?", (number + 1, counter_name)
        )
    return number


def _request_decision(  # noqa: PLR0913
    *,
    request_id: str,
    revision: int,
    requester: str,
    resource: str,
    start: datetime,
    end: datetime,
    project: str,
) -> tuple[dict[str, Any], str, str]:
    decision = approval_decision(
        action="commit_booking",
        requester=requester,
        resource=resource,
        start_utc=start,
        end_utc=end,
        project=project,
        request_id=request_id,
        revision=revision,
    )
    serialized = serialize_decision(decision)
    return decision, serialized, canonical_hash(decision)


def _insert_request(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    request_id: str,
    person_id: str,
    instrument_id: str,
    project_id: str,
    interval: Interval,
    revision: int,
    created: datetime,
    expires: datetime,
) -> tuple[dict[str, Any], str, str]:
    decision, decision_json, digest = _request_decision(
        request_id=request_id,
        revision=revision,
        requester=person_id,
        resource=instrument_id,
        start=interval.start,
        end=interval.end,
        project=project_id,
    )
    connection.execute(
        "INSERT INTO approval_request(id, kind, requester, resource, start_utc, end_utc, project, "
        "revision, content_hash, decision_json, status, created_utc, expires_utc) "
        "VALUES (?, 'booking', ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)",
        (
            request_id,
            person_id,
            instrument_id,
            utc_timestamp(interval.start),
            utc_timestamp(interval.end),
            project_id,
            revision,
            digest,
            decision_json,
            utc_timestamp(created),
            utc_timestamp(expires),
        ),
    )
    return decision, decision_json, digest


def _proposal_result(  # noqa: PLR0913, PLR0917
    request_id: str,
    booking_id: str,
    revision: int,
    digest: str,
    decision: dict[str, Any],
    expires: datetime,
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "booking_id": booking_id,
        "revision": revision,
        "content_hash": digest,
        "decision": decision,
        "status": RequestStatus.PENDING.value,
        "expires_utc": utc_timestamp(expires),
    }


def propose_booking(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    person_id: str,
    instrument_id: str,
    project_id: str,
    start: datetime,
    end: datetime,
    clock: Clock,
    hold_minutes: int = 10,
) -> dict[str, Any]:
    """Recheck current booking policy and create a pending revision-one request."""
    if not project_id.strip() or hold_minutes <= 0:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Project and positive hold duration are required."
        )
    interval = Interval(start, end)
    result: dict[str, Any] | None = None
    with immediate_transaction(connection):
        now = _now(clock)
        _validate_booking(
            connection,
            person_id=person_id,
            instrument_id=instrument_id,
            interval=interval,
            now=now,
        )
        request_number = _next_number(connection, "request")
        booking_number = _next_number(connection, "booking")
        request_id = f"AR-{request_number:04d}"
        booking_id = f"BK-{booking_number:04d}"
        expires = now + timedelta(minutes=hold_minutes)
        decision, _, digest = _insert_request(
            connection,
            request_id=request_id,
            person_id=person_id,
            instrument_id=instrument_id,
            project_id=project_id,
            interval=interval,
            revision=1,
            created=now,
            expires=expires,
        )
        connection.execute(
            "INSERT INTO booking(id, instrument_id, person_id, project_id, start_utc, end_utc, status, request_id) "
            "VALUES (?, ?, ?, ?, ?, ?, 'proposed', ?)",
            (
                booking_id,
                instrument_id,
                person_id,
                project_id,
                utc_timestamp(start),
                utc_timestamp(end),
                request_id,
            ),
        )
        result = _proposal_result(request_id, booking_id, 1, digest, decision, expires)
        append_event(
            connection,
            actor="labops",
            tool="propose_booking",
            args={
                "person_id": person_id,
                "instrument_id": instrument_id,
                "project_id": project_id,
                "start_utc": utc_timestamp(start),
                "end_utc": utc_timestamp(end),
            },
            result=result,
            clock=clock,
        )
    assert result is not None
    return result


def _terminal_error(status: str) -> LabQuorumError:
    if status == RequestStatus.DECLINED.value:
        return LabQuorumError(ErrorCode.DECLINED, "Declined requests cannot be committed.")
    if status == RequestStatus.EXPIRED.value:
        return LabQuorumError(ErrorCode.EXPIRED, "Expired requests cannot be committed.")
    return LabQuorumError(ErrorCode.ALREADY_DECIDED, f"Request is already {status}.")


def _expiry_reason(row: sqlite3.Row, now: datetime) -> str | None:
    created = parse_iso_datetime(str(row["created_utc"]))
    expiry = parse_iso_datetime(str(row["expires_utc"]))
    if now < created.astimezone(UTC):
        return "clock_rollback"
    if is_expired(now, expiry):
        return "hold_expired"
    return None


def _expire_request(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
    *,
    reason: str,
    clock: Clock,
) -> None:
    request_id = str(row["id"])
    decided = utc_timestamp(_now(clock))
    transition_status(RequestStatus.PENDING, RequestStatus.EXPIRED)
    connection.execute(
        "UPDATE approval_request SET status = 'expired', decided_utc = ? WHERE id = ?",
        (decided, request_id),
    )
    connection.execute(
        "UPDATE booking SET status = 'expired' WHERE request_id = ? AND status = 'proposed'",
        (request_id,),
    )
    append_event(
        connection,
        actor="system",
        tool="expire_request",
        args={"request_id": request_id, "reason": reason},
        result={"status": RequestStatus.EXPIRED.value},
        clock=clock,
    )


def _expire_due_requests(connection: sqlite3.Connection, *, now: datetime, clock: Clock) -> int:
    rows = connection.execute(
        "SELECT * FROM approval_request WHERE status = 'pending' ORDER BY id"
    ).fetchall()
    expired = 0
    for row in rows:
        reason = _expiry_reason(row, now)
        if reason is not None:
            _expire_request(connection, row, reason=reason, clock=clock)
            expired += 1
    return expired


def revise_request(  # noqa: PLR0913
    connection: sqlite3.Connection,
    request_id: str,
    *,
    revision: int,
    start: datetime,
    end: datetime,
    project_id: str,
    clock: Clock,
) -> dict[str, Any]:
    """Edit a pending booking request, bumping its revision and decision hash."""
    interval = Interval(start, end)
    result: dict[str, Any] | None = None
    expired = False
    with immediate_transaction(connection):
        row = _request_row(connection, request_id)
        if str(row["status"]) != RequestStatus.PENDING.value:
            raise _terminal_error(str(row["status"]))
        if int(row["revision"]) != revision:
            raise LabQuorumError(ErrorCode.STALE_REQUEST, "Request revision changed before edit.")
        now = _now(clock)
        reason = _expiry_reason(row, now)
        if reason is not None:
            _expire_request(connection, row, reason=reason, clock=clock)
            expired = True
        else:
            person_id = str(row["requester"])
            instrument_id = str(row["resource"])
            if not project_id.strip():
                raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Project cannot be empty.")
            _validate_booking(
                connection,
                person_id=person_id,
                instrument_id=instrument_id,
                interval=interval,
                now=now,
                exclude_request_id=request_id,
            )
            next_rev = next_revision(revision)
            decision, decision_json, digest = _request_decision(
                request_id=request_id,
                revision=next_rev,
                requester=person_id,
                resource=instrument_id,
                start=start,
                end=end,
                project=project_id,
            )
            connection.execute(
                "UPDATE approval_request SET start_utc = ?, end_utc = ?, project = ?, revision = ?, "
                "content_hash = ?, decision_json = ? WHERE id = ? AND status = 'pending'",
                (
                    utc_timestamp(start),
                    utc_timestamp(end),
                    project_id,
                    next_rev,
                    digest,
                    decision_json,
                    request_id,
                ),
            )
            connection.execute(
                "UPDATE booking SET start_utc = ?, end_utc = ?, project_id = ? "
                "WHERE request_id = ? AND status = 'proposed'",
                (utc_timestamp(start), utc_timestamp(end), project_id, request_id),
            )
            expires = parse_iso_datetime(str(row["expires_utc"]))
            result = _proposal_result(
                request_id,
                str(
                    connection.execute(
                        "SELECT id FROM booking WHERE request_id = ?", (request_id,)
                    ).fetchone()["id"]
                ),
                next_rev,
                digest,
                decision,
                expires,
            )
            append_event(
                connection,
                actor="labops",
                tool="revise_request",
                args={"request_id": request_id, "revision": revision, "new_revision": next_rev},
                result=result,
                clock=clock,
            )
    if expired:
        raise LabQuorumError(
            ErrorCode.EXPIRED, "Expired or clock-skewed requests cannot be revised."
        )
    assert result is not None
    return result


def _stored_booking_result(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    booking = connection.execute(
        "SELECT id, status FROM booking WHERE request_id = ?",
        (row["id"],),
    ).fetchone()
    if booking is None:
        raise LabQuorumError(ErrorCode.NOT_FOUND, f"Booking for request {row['id']} was not found.")
    return {
        "request_id": str(row["id"]),
        "booking_id": str(booking["id"]),
        "revision": int(row["revision"]),
        "content_hash": str(row["content_hash"]),
        "decision": json.loads(str(row["decision_json"])),
        "status": str(booking["status"]),
    }


def commit_booking(  # noqa: PLR0913
    connection: sqlite3.Connection,
    request_id: str,
    revision: int,
    content_hash: str,
    decision: Mapping[str, Any],
    *,
    clock: Clock,
) -> dict[str, Any]:
    """Commit only the exact current decision after policy is rechecked under the write lock."""
    incoming_json = serialize_decision(dict(decision))
    result: dict[str, Any] | None = None
    expired = False
    with immediate_transaction(connection):
        row = _request_row(connection, request_id)
        status = str(row["status"])
        stored_json = str(row["decision_json"])
        if status == RequestStatus.COMMITTED.value:
            if revision != int(row["revision"]) or content_hash != str(row["content_hash"]):
                raise LabQuorumError(
                    ErrorCode.STALE_REQUEST,
                    "Committed request does not match the supplied revision and hash.",
                )
            if incoming_json.encode("utf-8") != stored_json.encode("utf-8"):
                raise LabQuorumError(
                    ErrorCode.DECISION_MISMATCH, "Decision differs from the stored canonical bytes."
                )
            result = _stored_booking_result(connection, row)
            if result["status"] != "committed":
                raise LabQuorumError(
                    ErrorCode.ALREADY_DECIDED, "The committed booking was later cancelled."
                )
        elif status != RequestStatus.PENDING.value:
            raise _terminal_error(status)
        elif revision != int(row["revision"]) or content_hash != str(row["content_hash"]):
            raise LabQuorumError(
                ErrorCode.STALE_REQUEST, "Request revision or content hash changed."
            )
        elif incoming_json.encode("utf-8") != stored_json.encode("utf-8"):
            raise LabQuorumError(
                ErrorCode.DECISION_MISMATCH, "Decision differs from the stored canonical bytes."
            )
        else:
            stored_decision = json.loads(stored_json)
            if canonical_hash(stored_decision) != str(row["content_hash"]):
                raise LabQuorumError(
                    ErrorCode.DECISION_MISMATCH,
                    "Stored decision hash does not match its canonical content.",
                )
            now = _now(clock)
            reason = _expiry_reason(row, now)
            if reason is not None:
                _expire_request(connection, row, reason=reason, clock=clock)
                expired = True
            else:
                start = parse_iso_datetime(str(row["start_utc"]))
                end = parse_iso_datetime(str(row["end_utc"]))
                interval = Interval(start, end)
                _validate_booking(
                    connection,
                    person_id=str(row["requester"]),
                    instrument_id=str(row["resource"]),
                    interval=interval,
                    now=now,
                    exclude_request_id=request_id,
                )
                transition_status(RequestStatus.PENDING, RequestStatus.COMMITTED)
                decided = utc_timestamp(now)
                connection.execute(
                    "UPDATE approval_request SET status = 'committed', decided_utc = ? WHERE id = ?",
                    (decided, request_id),
                )
                connection.execute(
                    "UPDATE booking SET status = 'committed' WHERE request_id = ? AND status = 'proposed'",
                    (request_id,),
                )
                result = _stored_booking_result(connection, _request_row(connection, request_id))
                append_event(
                    connection,
                    actor="pi-desk",
                    tool="commit_booking",
                    args={
                        "request_id": request_id,
                        "revision": revision,
                        "content_hash": content_hash,
                        "decision": stored_decision,
                    },
                    result=result,
                    clock=clock,
                )
    if expired:
        raise LabQuorumError(
            ErrorCode.EXPIRED, "Expired or clock-skewed requests cannot be committed."
        )
    assert result is not None
    return result


def decline_request(
    connection: sqlite3.Connection,
    request_id: str,
    revision: int,
    reason: str,
    *,
    clock: Clock,
) -> dict[str, Any]:
    """Decline a pending request and preserve the reason in the ledger."""
    if not reason.strip():
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "A decline reason is required.")
    expired = False
    result: dict[str, Any] | None = None
    with immediate_transaction(connection):
        row = _request_row(connection, request_id)
        if str(row["status"]) != RequestStatus.PENDING.value:
            raise _terminal_error(str(row["status"]))
        if revision != int(row["revision"]):
            raise LabQuorumError(
                ErrorCode.STALE_REQUEST, "Request revision changed before decline."
            )
        now = _now(clock)
        expiry_reason = _expiry_reason(row, now)
        if expiry_reason is not None:
            _expire_request(connection, row, reason=expiry_reason, clock=clock)
            expired = True
        else:
            transition_status(RequestStatus.PENDING, RequestStatus.DECLINED)
            connection.execute(
                "UPDATE approval_request SET status = 'declined', decided_utc = ?, decline_reason = ? "
                "WHERE id = ?",
                (utc_timestamp(now), reason.strip(), request_id),
            )
            connection.execute(
                "UPDATE booking SET status = 'declined' WHERE request_id = ? AND status = 'proposed'",
                (request_id,),
            )
            result = _request_result(_request_row(connection, request_id))
            append_event(
                connection,
                actor="pi-desk",
                tool="decline_request",
                args={"request_id": request_id, "revision": revision, "reason": reason.strip()},
                result={"status": RequestStatus.DECLINED.value},
                clock=clock,
            )
    if expired:
        raise LabQuorumError(
            ErrorCode.EXPIRED, "Expired or clock-skewed requests cannot be declined."
        )
    assert result is not None
    return result


def cancel_booking(
    connection: sqlite3.Connection,
    booking_id: str,
    *,
    actor: str,
    clock: Clock,
) -> dict[str, Any]:
    """Cancel a committed booking once; repeated cancellation has no second effect."""
    if not actor.strip():
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Cancellation actor is required.")
    result: dict[str, Any] | None = None
    with immediate_transaction(connection):
        row = connection.execute("SELECT * FROM booking WHERE id = ?", (booking_id,)).fetchone()
        if row is None:
            raise LabQuorumError(ErrorCode.NOT_FOUND, f"Booking {booking_id} was not found.")
        status = str(row["status"])
        if status == "cancelled":
            result = {"booking_id": booking_id, "status": status}
        elif status != "committed":
            raise LabQuorumError(ErrorCode.ALREADY_DECIDED, f"Booking is already {status}.")
        else:
            connection.execute(
                "UPDATE booking SET status = 'cancelled' WHERE id = ?", (booking_id,)
            )
            result = {"booking_id": booking_id, "status": "cancelled"}
            append_event(
                connection,
                actor=actor,
                tool="cancel_booking",
                args={"booking_id": booking_id},
                result=result,
                clock=clock,
            )
    assert result is not None
    return result


def get_request(
    connection: sqlite3.Connection,
    request_id: str,
    *,
    clock: Clock,
) -> dict[str, Any]:
    """Read one request and lazily expire an overdue or clock-rollback hold."""
    with immediate_transaction(connection):
        row = _request_row(connection, request_id)
        if str(row["status"]) == RequestStatus.PENDING.value:
            _expire_due_requests(connection, now=_now(clock), clock=clock)
            row = _request_row(connection, request_id)
        return _request_result(row)


def _booking_rows(
    connection: sqlite3.Connection,
    instrument_id: str | None,
) -> list[dict[str, Any]]:
    if instrument_id is None:
        rows = connection.execute("SELECT * FROM booking ORDER BY start_utc, id").fetchall()
    else:
        rows = connection.execute(
            "SELECT * FROM booking WHERE instrument_id = ? ORDER BY start_utc, id",
            (instrument_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_bookings(
    connection: sqlite3.Connection,
    *,
    clock: Clock,
    instrument_id: str | None = None,
) -> list[dict[str, Any]]:
    """List bookings, applying lazy expiry to pending requests first."""
    with immediate_transaction(connection):
        _expire_due_requests(connection, now=_now(clock), clock=clock)
        return _booking_rows(connection, instrument_id)


def lab_state(connection: sqlite3.Connection, *, clock: Clock) -> dict[str, Any]:
    """Return a compact current snapshot of instruments and bookings."""
    with immediate_transaction(connection):
        _expire_due_requests(connection, now=_now(clock), clock=clock)
        instruments = [
            dict(row)
            for row in connection.execute("SELECT * FROM instrument ORDER BY id").fetchall()
        ]
        bookings = _booking_rows(connection, None)
        return {"instruments": instruments, "bookings": bookings}
