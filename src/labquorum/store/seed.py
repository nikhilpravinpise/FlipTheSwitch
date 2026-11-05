"""Anchor-relative demo seed for the booking-only ledger."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime, time, timedelta
from importlib import resources
from pathlib import Path
from typing import Any, cast
from zoneinfo import ZoneInfo

import yaml

from labquorum.domain.approvals import approval_decision, serialize_decision
from labquorum.domain.canonical import content_hash
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock, SystemClock, utc_timestamp
from labquorum.store.audit import append_event
from labquorum.store.db import immediate_transaction

_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _seed_data() -> dict[str, Any]:
    packaged = resources.files("labquorum.store").joinpath("demo.yaml")
    if packaged.is_file():
        raw = packaged.read_text(encoding="utf-8")
    else:
        seed_path = Path(__file__).resolve().parents[3] / "seed" / "demo.yaml"
        raw = seed_path.read_text(encoding="utf-8")
    try:
        data: Any = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Demo seed YAML is invalid.") from exc
    if not isinstance(data, dict):
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Demo seed has an unsupported format version."
        )
    typed_data = cast(dict[str, Any], data)
    if typed_data.get("version") != 1:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Demo seed has an unsupported format version."
        )
    return typed_data


def _local_instant(anchor_date: date, day_offset: int, clock_text: str, zone: ZoneInfo) -> datetime:
    local_date = anchor_date + timedelta(days=day_offset)
    return datetime.combine(local_date, time.fromisoformat(clock_text), tzinfo=zone)


def _next_open_day(
    anchor_date: date, opening_hours: dict[str, list[str]], open_day_offset: int
) -> date:
    if open_day_offset < 0:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Open-day offset cannot be negative.")
    open_weekdays = {int(weekday) for weekday in opening_hours}
    if not open_weekdays:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Instrument has no open days.")
    selected = anchor_date
    remaining = open_day_offset + 1
    while remaining:
        selected += timedelta(days=1)
        if selected.weekday() in open_weekdays:
            remaining -= 1
    return selected


def _insert_seeded_booking(
    connection: sqlite3.Connection,
    booking: dict[str, Any],
    anchor_date: date,
    now_utc: datetime,
) -> None:
    instrument = connection.execute(
        "SELECT timezone, opening_hours_json FROM instrument WHERE id = ?",
        (booking["instrument_id"],),
    ).fetchone()
    if instrument is None:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Seed booking references unknown instrument {booking['instrument_id']}.",
        )
    zone = ZoneInfo(str(instrument["timezone"]))
    opening_hours = cast(dict[str, list[str]], json.loads(str(instrument["opening_hours_json"])))
    booking_day = _next_open_day(anchor_date, opening_hours, int(booking.get("open_day_offset", 0)))
    start = datetime.combine(booking_day, time.fromisoformat(booking["start_time"]), tzinfo=zone)
    end = datetime.combine(booking_day, time.fromisoformat(booking["end_time"]), tzinfo=zone)
    if end <= start:
        end += timedelta(days=1)
    start_text = utc_timestamp(start)
    end_text = utc_timestamp(end)
    request_id = str(booking["request_id"])
    revision = 1
    decision = approval_decision(
        action="commit_booking",
        requester=str(booking["person_id"]),
        resource=str(booking["instrument_id"]),
        start_utc=start,
        end_utc=end,
        project=str(booking["project_id"]),
        request_id=request_id,
        revision=revision,
    )
    decision_json = serialize_decision(decision)
    connection.execute(
        "INSERT INTO approval_request(id, kind, requester, resource, start_utc, end_utc, project, "
        "revision, content_hash, decision_json, status, created_utc, expires_utc, decided_utc) "
        "VALUES (?, 'booking', ?, ?, ?, ?, ?, ?, ?, ?, 'committed', ?, ?, ?)",
        (
            request_id,
            booking["person_id"],
            booking["instrument_id"],
            start_text,
            end_text,
            booking["project_id"],
            revision,
            content_hash(decision),
            decision_json,
            utc_timestamp(now_utc),
            utc_timestamp(now_utc + timedelta(minutes=10)),
            utc_timestamp(now_utc),
        ),
    )
    connection.execute(
        "INSERT INTO booking(id, instrument_id, person_id, project_id, start_utc, end_utc, status, request_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            booking["id"],
            booking["instrument_id"],
            booking["person_id"],
            booking["project_id"],
            start_text,
            end_text,
            booking["status"],
            request_id,
        ),
    )


def seed_demo(
    connection: sqlite3.Connection,
    anchor_date: date,
    *,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Load the booking-only demo fixtures once for an explicit anchor date."""
    source = _seed_data()
    clock = clock or SystemClock()
    now = clock.now()
    if now.tzinfo is None or now.utcoffset() is None:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Seed clock must return an aware datetime."
        )
    now_utc = now.astimezone(UTC)
    timezone_name = str(source["timezone"])
    zone = ZoneInfo(timezone_name)
    anchor_key = anchor_date.isoformat()

    with immediate_transaction(connection):
        marker = connection.execute(
            "SELECT value FROM app_meta WHERE key = 'demo_seed_anchor'"
        ).fetchone()
        if marker is not None:
            if str(marker["value"]) != anchor_key:
                raise LabQuorumError(
                    ErrorCode.INVALID_ARGUMENT,
                    "Demo seed was already loaded with a different anchor date.",
                    {"loaded_anchor_date": marker["value"], "requested_anchor_date": anchor_key},
                )
            existing_people = {
                str(row["id"]) for row in connection.execute("SELECT id FROM person")
            }
            added_people = [
                person for person in source["people"] if str(person["id"]) not in existing_people
            ]
            for person in added_people:
                connection.execute(
                    "INSERT INTO person(id, display_name, role, timezone) VALUES (?, ?, ?, ?)",
                    (person["id"], person["display_name"], person["role"], person["timezone"]),
                )
            added_ids = {str(person["id"]) for person in added_people}
            added_training = [
                training
                for training in source["training"]
                if str(training["person_id"]) in added_ids
            ]
            for training in added_training:
                granted = _local_instant(
                    anchor_date,
                    int(training["granted_offset_days"]),
                    "00:00",
                    zone,
                )
                expires = _local_instant(
                    anchor_date,
                    int(training["expires_offset_days"]),
                    "00:00",
                    zone,
                )
                connection.execute(
                    "INSERT INTO training(person_id, instrument_id, granted_at_utc, expires_at_utc) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        training["person_id"],
                        training["instrument_id"],
                        utc_timestamp(granted),
                        utc_timestamp(expires),
                    ),
                )
            if added_people:
                append_event(
                    connection,
                    actor="lq",
                    tool="seed_demo",
                    args={"anchor_date": anchor_key, "added_people": sorted(added_ids)},
                    result={
                        "seeded": False,
                        "people": len(added_people),
                        "instruments": 0,
                        "bookings": 0,
                    },
                    clock=clock,
                )
            return {
                "seeded": False,
                "anchor_date": anchor_key,
                "people": len(added_people),
                "instruments": 0,
                "bookings": 0,
            }

        for person in source["people"]:
            connection.execute(
                "INSERT INTO person(id, display_name, role, timezone) VALUES (?, ?, ?, ?)",
                (person["id"], person["display_name"], person["role"], person["timezone"]),
            )

        schedules: dict[str, list[str] | None] = {
            str(name): value for name, value in source["opening_hours"].items()
        }
        for instrument in source["instruments"]:
            instrument_zone = timezone_name
            weekly: dict[str, list[str]] = {}
            for day_name, hours in schedules.items():
                weekday = _WEEKDAYS[day_name]
                if hours is not None:
                    weekly[str(weekday)] = [str(hours[0]), str(hours[1])]
            down_until = None
            if instrument.get("down_until_offset_days") is not None:
                down_date = anchor_date + timedelta(days=int(instrument["down_until_offset_days"]))
                down_until = utc_timestamp(datetime.combine(down_date, time.min, zone))
            connection.execute(
                "INSERT INTO instrument(id, name, aliases_json, location, timezone, requires_training, "
                "max_block_minutes, min_gap_minutes, booking_window_days, opening_hours_json, status, down_until_utc) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    instrument["id"],
                    instrument["name"],
                    json.dumps(instrument["aliases"], ensure_ascii=False, separators=(",", ":")),
                    instrument["location"],
                    instrument_zone,
                    int(instrument["requires_training"]),
                    int(instrument["max_block_minutes"]),
                    int(instrument["min_gap_minutes"]),
                    int(instrument["booking_window_days"]),
                    json.dumps(weekly, sort_keys=True, separators=(",", ":")),
                    instrument["status"],
                    down_until,
                ),
            )

        for training in source["training"]:
            granted = _local_instant(
                anchor_date,
                int(training["granted_offset_days"]),
                "00:00",
                zone,
            )
            expires = _local_instant(
                anchor_date,
                int(training["expires_offset_days"]),
                "00:00",
                zone,
            )
            connection.execute(
                "INSERT INTO training(person_id, instrument_id, granted_at_utc, expires_at_utc) "
                "VALUES (?, ?, ?, ?)",
                (
                    training["person_id"],
                    training["instrument_id"],
                    utc_timestamp(granted),
                    utc_timestamp(expires),
                ),
            )

        for booking in source["bookings"]:
            _insert_seeded_booking(connection, booking, anchor_date, now_utc)

        request_start = int(source["next_request_number"])
        connection.executemany(
            "INSERT INTO counter(name, value) VALUES (?, ?)",
            (("request", request_start), ("booking", request_start)),
        )
        connection.execute(
            "INSERT INTO app_meta(key, value) VALUES ('demo_seed_anchor', ?)",
            (anchor_key,),
        )
        counts = {
            "people": len(source["people"]),
            "instruments": len(source["instruments"]),
            "bookings": len(source["bookings"]),
        }
        append_event(
            connection,
            actor="lq",
            tool="seed_demo",
            args={"anchor_date": anchor_key},
            result={"seeded": True, **counts},
            clock=clock,
        )
    return {"seeded": True, "anchor_date": anchor_key, **counts}
