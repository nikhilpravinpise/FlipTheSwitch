"""Append-only audit event hashing and verification."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any

from labquorum.domain.canonical import canonical_json
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock, utc_timestamp


def _row_hash(row_without_hash: dict[str, Any]) -> str:
    previous = str(row_without_hash["prev_hash"])
    payload = canonical_json(row_without_hash).encode("utf-8")
    return hashlib.sha256(previous.encode("ascii") + payload).hexdigest()


def append_event(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    actor: str,
    tool: str,
    args: dict[str, Any],
    result: dict[str, Any],
    clock: Clock,
) -> int:
    """Append a hash-linked event inside the caller's active transaction."""
    if not connection.in_transaction:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Audit events must be appended inside the mutation transaction.",
        )
    if not actor or not tool:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Audit actor and tool are required.")
    latest = connection.execute(
        "SELECT seq, hash FROM audit_event ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    sequence = int(latest["seq"]) + 1 if latest is not None else 1
    previous_hash = str(latest["hash"]) if latest is not None else ""
    row_without_hash: dict[str, Any] = {
        "seq": sequence,
        "ts_utc": utc_timestamp(clock.now()),
        "actor_agent": actor,
        "tool": tool,
        "args_json": canonical_json(args),
        "result_json": canonical_json(result),
        "prev_hash": previous_hash,
    }
    event_hash = _row_hash(row_without_hash)
    connection.execute(
        "INSERT INTO audit_event(seq, ts_utc, actor_agent, tool, args_json, result_json, prev_hash, hash) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            sequence,
            row_without_hash["ts_utc"],
            actor,
            tool,
            row_without_hash["args_json"],
            row_without_hash["result_json"],
            previous_hash,
            event_hash,
        ),
    )
    return sequence


def verify(connection: sqlite3.Connection) -> int | None:
    """Return the first bad sequence number, or None for a valid stored chain."""
    rows = connection.execute(
        "SELECT seq, ts_utc, actor_agent, tool, args_json, result_json, prev_hash, hash "
        "FROM audit_event ORDER BY seq"
    ).fetchall()
    previous_hash = ""
    expected_sequence = 1
    for row in rows:
        sequence = int(row["seq"])
        if sequence != expected_sequence or str(row["prev_hash"]) != previous_hash:
            return sequence
        body = {
            "seq": sequence,
            "ts_utc": str(row["ts_utc"]),
            "actor_agent": str(row["actor_agent"]),
            "tool": str(row["tool"]),
            "args_json": str(row["args_json"]),
            "result_json": str(row["result_json"]),
            "prev_hash": previous_hash,
        }
        if _row_hash(body) != str(row["hash"]):
            return sequence
        previous_hash = str(row["hash"])
        expected_sequence += 1
    return None


def tail(connection: sqlite3.Connection, *, limit: int = 20) -> list[dict[str, Any]]:
    """Return recent events in chronological order with parsed JSON payloads."""
    if limit <= 0:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Audit tail limit must be positive.")
    rows = connection.execute(
        "SELECT seq, ts_utc, actor_agent, tool, args_json, result_json, prev_hash, hash "
        "FROM audit_event ORDER BY seq DESC LIMIT ?",
        (limit,),
    ).fetchall()
    events: list[dict[str, Any]] = []
    for row in reversed(rows):
        events.append(
            {
                "seq": int(row["seq"]),
                "ts_utc": str(row["ts_utc"]),
                "actor_agent": str(row["actor_agent"]),
                "tool": str(row["tool"]),
                "args": json.loads(str(row["args_json"])),
                "result": json.loads(str(row["result_json"])),
                "prev_hash": str(row["prev_hash"]),
                "hash": str(row["hash"]),
            }
        )
    return events
