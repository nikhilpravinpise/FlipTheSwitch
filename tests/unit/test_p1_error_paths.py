"""Additional boundary coverage for P1 domain and store failure paths."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from labquorum.domain.approvals import (
    RequestStatus,
    approval_decision,
    is_expired,
    next_revision,
    transition_status,
)
from labquorum.domain.booking import (
    InstrumentPolicy,
    Interval,
    Training,
    check_booking,
    intervals_conflict,
    nearest_free_slot,
)
from labquorum.domain.canonical import canonical_json
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.guards import RateGuard
from labquorum.domain.timeutil import FixedClock, format_interval, parse_iso_datetime, utc_timestamp
from labquorum.store import db as db_module
from labquorum.store.audit import append_event, tail
from labquorum.store.db import immediate_transaction, init_database, open_database
from labquorum.store.repos import (
    cancel_booking,
    decline_request,
    get_request,
    list_bookings,
    propose_booking,
)
from labquorum.store.seed import seed_demo
from tests.conftest import ANCHOR_DATE, BASE_NOW, at, make_policy


def _expect_code(code: ErrorCode, operation: Any) -> None:
    with pytest.raises(LabQuorumError) as error:
        operation()
    assert error.value.code is code


def test_p1_domain_rejects_malformed_values_and_rollbacks() -> None:
    naive = datetime(2026, 11, 6, 16)
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: FixedClock(naive))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: utc_timestamp(naive))
    _expect_code(
        ErrorCode.NEEDS_ISO_DATETIME, lambda: parse_iso_datetime("2026-02-30T10:00:00+00:00")
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: parse_iso_datetime("2026-11-06T10:00:00", timezone="No/Such_Zone"),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: format_interval(BASE_NOW, BASE_NOW + timedelta(hours=1), "No/Such_Zone"),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: format_interval(BASE_NOW, BASE_NOW, "Asia/Kolkata"),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: Interval(at(ANCHOR_DATE, 10), at(ANCHOR_DATE, 10)),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: InstrumentPolicy("bad", "No/Such_Zone", {}, 30, 0, 1),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: InstrumentPolicy("bad", "UTC", {}, 0, 0, 1),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: intervals_conflict(
            Interval(at(ANCHOR_DATE, 10), at(ANCHOR_DATE, 11)),
            Interval(at(ANCHOR_DATE, 12), at(ANCHOR_DATE, 13)),
            gap_minutes=-1,
        ),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: nearest_free_slot(
            make_policy(),
            at(ANCHOR_DATE, 10),
            duration_minutes=0,
            now=BASE_NOW,
        ),
    )
    assert (
        nearest_free_slot(
            make_policy(status="down"),
            at(ANCHOR_DATE, 16),
            duration_minutes=60,
            now=BASE_NOW,
        )
        is None
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: check_booking(
            make_policy(status="unexpected"),
            Interval(at(ANCHOR_DATE, 16), at(ANCHOR_DATE, 17)),
            now=BASE_NOW,
            training=Training(at(ANCHOR_DATE, 8), at(ANCHOR_DATE, 20)),
        ),
    )
    _expect_code(
        ErrorCode.TRAINING_REQUIRED,
        lambda: check_booking(
            make_policy(),
            Interval(at(ANCHOR_DATE, 16), at(ANCHOR_DATE, 17)),
            now=BASE_NOW,
            training=Training(at(ANCHOR_DATE, 17), at(ANCHOR_DATE, 20)),
        ),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: approval_decision(
            action="",
            requester="maya",
            resource="INS-01",
            start_utc=at(ANCHOR_DATE, 16),
            end_utc=at(ANCHOR_DATE, 17),
            project="demo",
            request_id="AR-1",
            revision=1,
        ),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: approval_decision(
            action="commit_booking",
            requester="maya",
            resource="INS-01",
            start_utc=naive,
            end_utc=at(ANCHOR_DATE, 17),
            project="demo",
            request_id="AR-1",
            revision=1,
        ),
    )
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: next_revision(0))
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: transition_status(RequestStatus.PENDING, RequestStatus.PENDING),
    )
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: is_expired(naive, BASE_NOW))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: is_expired(BASE_NOW, naive))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: canonical_json({1: "bad-key"}))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: canonical_json({"bad": object()}))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: canonical_json({"time": naive}))

    class NaiveClock:
        def now(self) -> datetime:
            return naive

    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: RateGuard(clock=NaiveClock()).check("labops"))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: RateGuard(clock=FixedClock(BASE_NOW), limit=0))
    guard = RateGuard(clock=FixedClock(BASE_NOW))
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: guard.check(" "))
    rollback_clock = FixedClock(BASE_NOW)
    rollback_guard = RateGuard(clock=rollback_clock)
    rollback_guard.check("labops")
    rollback_clock.set(BASE_NOW - timedelta(seconds=1))
    _expect_code(ErrorCode.RATE_LIMITED, lambda: rollback_guard.check("labops"))


def test_p1_audit_tail_and_append_guards(seeded_ledger: tuple[sqlite3.Connection, Any]) -> None:
    connection, clock = seeded_ledger
    events = tail(connection, limit=1)
    assert len(events) == 1
    assert events[0]["tool"] == "seed_demo"
    _expect_code(ErrorCode.INVALID_ARGUMENT, lambda: tail(connection, limit=0))
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: append_event(
            connection,
            actor="test",
            tool="invalid-outside-transaction",
            args={},
            result={},
            clock=clock,
        ),
    )
    with immediate_transaction(connection):
        _expect_code(
            ErrorCode.INVALID_ARGUMENT,
            lambda: append_event(
                connection,
                actor="",
                tool="invalid-actor",
                args={},
                result={},
                clock=clock,
            ),
        )


def test_p1_database_refuses_incompatible_and_onedrive_ledgers(tmp_path: Path) -> None:
    missing_schema = tmp_path / "missing-schema.sqlite"
    empty = sqlite3.connect(missing_schema)
    empty.close()
    _expect_code(ErrorCode.SCHEMA_VERSION_MISMATCH, lambda: open_database(missing_schema))

    incompatible = init_database(tmp_path / "incompatible.sqlite")
    incompatible.execute("UPDATE schema_version SET version = 999")
    incompatible.close()
    _expect_code(
        ErrorCode.SCHEMA_VERSION_MISMATCH,
        lambda: init_database(tmp_path / "incompatible.sqlite"),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: init_database(Path("C:/Users/test/OneDrive/LabQuorum/ledger.sqlite")),
    )


def test_connect_closes_connection_when_initial_setup_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class BrokenConnection:
        row_factory: Any = None
        closed = False

        def execute(self, *_args: Any, **_kwargs: Any) -> Any:
            raise sqlite3.OperationalError("setup failed")

        def close(self) -> None:
            self.closed = True

    connection = BrokenConnection()

    class SQLiteStub:
        Row = sqlite3.Row

        @staticmethod
        def connect(*_args: Any, **_kwargs: Any) -> BrokenConnection:
            return connection

    monkeypatch.setattr(db_module, "sqlite3", SQLiteStub())
    with pytest.raises(sqlite3.OperationalError, match="setup failed"):
        db_module._connect(tmp_path / "setup-failure.sqlite")
    assert connection.closed


def test_init_database_closes_connection_when_schema_setup_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[sqlite3.Connection] = []
    original_connect = db_module._connect

    def tracked_connect(path: Path) -> sqlite3.Connection:
        connection = original_connect(path)
        opened.append(connection)
        return connection

    class InvalidSchemaFile:
        def joinpath(self, _name: str) -> InvalidSchemaFile:
            return self

        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return "CREATE TABLE invalid_schema ("

    class ResourceStub:
        def files(self, _package: str) -> InvalidSchemaFile:
            return InvalidSchemaFile()

    monkeypatch.setattr(db_module, "_connect", tracked_connect)
    monkeypatch.setattr(db_module, "resources", ResourceStub())
    with pytest.raises(sqlite3.DatabaseError):
        init_database(tmp_path / "schema-failure.sqlite")
    assert len(opened) == 1
    with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
        opened[0].execute("SELECT 1")


def test_p1_repository_not_found_invalid_and_anchor_mismatch_paths(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    _expect_code(ErrorCode.NOT_FOUND, lambda: get_request(connection, "AR-9999", clock=clock))
    _expect_code(
        ErrorCode.NOT_FOUND,
        lambda: propose_booking(
            connection,
            person_id="nobody",
            instrument_id="INS-01",
            project_id="demo",
            start=at(ANCHOR_DATE, 16),
            end=at(ANCHOR_DATE, 17),
            clock=clock,
        ),
    )
    _expect_code(
        ErrorCode.NOT_FOUND,
        lambda: propose_booking(
            connection,
            person_id="maya",
            instrument_id="missing",
            project_id="demo",
            start=at(ANCHOR_DATE, 16),
            end=at(ANCHOR_DATE, 17),
            clock=clock,
        ),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: decline_request(connection, "AR-0041", 1, " ", clock=clock),
    )
    _expect_code(
        ErrorCode.NOT_FOUND,
        lambda: cancel_booking(connection, "BK-9999", actor="prof-rao", clock=clock),
    )
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: cancel_booking(connection, "BK-0041", actor=" ", clock=clock),
    )
    assert len(list_bookings(connection, clock=clock, instrument_id="INS-01")) == 1
    _expect_code(
        ErrorCode.INVALID_ARGUMENT,
        lambda: seed_demo(connection, ANCHOR_DATE + timedelta(days=1), clock=clock),
    )
