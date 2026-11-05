"""Process-level P1 races using Windows-compatible spawn workers."""

from __future__ import annotations

import contextlib
import multiprocessing
import sqlite3
import tempfile
from datetime import UTC, timedelta
from pathlib import Path
from typing import Any

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    rule,
    run_state_machine_as_test,
)

from labquorum.domain.booking import Interval, intervals_conflict
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import FixedClock, parse_iso_datetime, utc_timestamp
from labquorum.store.db import database_info, open_database
from labquorum.store.repos import (
    cancel_booking,
    commit_booking,
    decline_request,
    get_request,
    propose_booking,
)
from tests.conftest import ANCHOR_DATE, at, make_seeded_ledger

RACE_REPETITIONS = 50


def _commit_process(  # noqa: PLR0913, PLR0917
    database_path: str,
    barrier: Any,
    output: Any,
    now_text: str,
    request_id: str,
    revision: int,
    content_hash: str,
    decision: dict[str, Any],
) -> None:
    connection = open_database(Path(database_path))
    clock = FixedClock(parse_iso_datetime(now_text))
    try:
        barrier.wait(timeout=20)
        result = commit_booking(
            connection,
            request_id,
            revision,
            content_hash,
            decision,
            clock=clock,
        )
        output.put(("ok", result["booking_id"]))
    except LabQuorumError as error:
        output.put((error.code.value, ""))
    except Exception as error:  # pragma: no cover - only reported if a child crashes
        output.put(("ERROR", repr(error)))
        raise
    finally:
        connection.close()


def _unsafe_read_before_lock_worker(  # noqa: PLR0913, PLR0917
    database_path: str,
    barrier: Any,
    output: Any,
    booking_id: str,
    start_text: str,
    end_text: str,
) -> None:
    connection = sqlite3.connect(database_path, timeout=5.0, isolation_level=None)
    try:
        start = parse_iso_datetime(start_text)
        end = parse_iso_datetime(end_text)
        # This test-only path makes its conflict decision before taking a write lock.
        existing = connection.execute(
            "SELECT start_utc, end_utc FROM unsafe_probe WHERE status = 'committed'"
        ).fetchall()
        saw_conflict = any(
            intervals_conflict(
                Interval(start, end),
                Interval(parse_iso_datetime(row[0]), parse_iso_datetime(row[1])),
                gap_minutes=15,
            )
            for row in existing
        )
        barrier.wait(timeout=20)
        if saw_conflict:
            output.put("CONFLICT")
            return
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO unsafe_probe(booking_id, start_utc, end_utc, status) "
            "VALUES (?, ?, ?, 'committed')",
            (booking_id, start_text, end_text),
        )
        connection.commit()
        output.put("committed")
    finally:
        connection.close()


def _commit_args(proposal: dict[str, Any]) -> tuple[str, int, str, dict[str, Any]]:
    return (
        proposal["request_id"],
        proposal["revision"],
        proposal["content_hash"],
        proposal["decision"],
    )


def _race_pair(
    context: Any,
    database_path: Path,
    left: dict[str, Any],
    right: dict[str, Any],
    now: Any,
) -> list[tuple[str, str]]:
    barrier = context.Barrier(2)
    output = context.Queue()
    workers = [
        context.Process(
            target=_commit_process,
            args=(
                str(database_path),
                barrier,
                output,
                utc_timestamp(now),
                *_commit_args(proposal),
            ),
        )
        for proposal in (left, right)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=30)
    for worker in workers:
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
        assert worker.exitcode == 0
    results = [output.get(timeout=5), output.get(timeout=5)]
    output.close()
    return results


def _unsafe_race(context: Any, database_path: Path, now: Any) -> list[str]:
    connection = sqlite3.connect(database_path, timeout=5.0, isolation_level=None)
    connection.execute(
        "CREATE TABLE unsafe_probe(booking_id TEXT PRIMARY KEY, start_utc TEXT, "
        "end_utc TEXT, status TEXT NOT NULL)"
    )
    connection.close()
    barrier = context.Barrier(2)
    output = context.Queue()
    start = utc_timestamp(at(ANCHOR_DATE, 10))
    end = utc_timestamp(at(ANCHOR_DATE, 11))
    workers = [
        context.Process(
            target=_unsafe_read_before_lock_worker,
            args=(str(database_path), barrier, output, f"unsafe-{index}", start, end),
        )
        for index in range(2)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=20)
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
        assert worker.exitcode == 0
    results = [output.get(timeout=5), output.get(timeout=5)]
    output.close()
    return results


def test_I_01_two_processes_race_fifty_times_and_unsafe_variant_is_detected(
    tmp_path: Path,
) -> None:
    context = multiprocessing.get_context("spawn")
    database_path = tmp_path / "race.sqlite"
    connection, clock = make_seeded_ledger(database_path)
    info = database_info(connection)
    print(f"SQLite {info.sqlite_version}; journal mode {info.journal_mode}")
    committed_before = int(
        connection.execute("SELECT count(*) FROM booking WHERE status = 'committed'").fetchone()[0]
    )
    proposals: list[dict[str, Any]] = []
    current_day = ANCHOR_DATE
    for _ in range(30):
        if current_day.weekday() < 6:
            for start_hour in (9, 11):
                start = at(current_day, start_hour)
                proposals.extend(
                    [
                        propose_booking(
                            connection,
                            person_id="maya",
                            instrument_id="INS-01",
                            project_id="race-a",
                            start=start,
                            end=start + timedelta(hours=1),
                            clock=clock,
                        ),
                        propose_booking(
                            connection,
                            person_id="maya",
                            instrument_id="INS-01",
                            project_id="race-b",
                            start=start,
                            end=start + timedelta(hours=1),
                            clock=clock,
                        ),
                    ]
                )
                if len(proposals) >= RACE_REPETITIONS * 2:
                    break
        if len(proposals) >= RACE_REPETITIONS * 2:
            break
        current_day += timedelta(days=1)
    assert len(proposals) == RACE_REPETITIONS * 2

    for repetition in range(RACE_REPETITIONS):
        outcomes = _race_pair(
            context,
            database_path,
            proposals[2 * repetition],
            proposals[2 * repetition + 1],
            clock.now(),
        )
        assert sorted(result[0] for result in outcomes) == ["CONFLICT", "ok"]

    committed_after = int(
        connection.execute("SELECT count(*) FROM booking WHERE status = 'committed'").fetchone()[0]
    )
    assert committed_after == committed_before + RACE_REPETITIONS
    unsafe = _unsafe_race(context, database_path, clock.now())
    unsafe_commits = int(
        connection.execute(
            "SELECT count(*) FROM unsafe_probe WHERE status = 'committed'"
        ).fetchone()[0]
    )
    assert unsafe.count("committed") == 2
    assert unsafe_commits == 2
    connection.close()


def test_I_25_five_writers_are_exactly_once_and_clock_rollback_expires_closed(
    tmp_path: Path,
) -> None:
    context = multiprocessing.get_context("spawn")
    database_path = tmp_path / "five-writers.sqlite"
    connection, clock = make_seeded_ledger(database_path)
    info = database_info(connection)
    print(f"SQLite {info.sqlite_version}; journal mode {info.journal_mode}")
    proposal = propose_booking(
        connection,
        person_id="maya",
        instrument_id="INS-01",
        project_id="five-writers",
        start=at(ANCHOR_DATE, 16),
        end=at(ANCHOR_DATE, 17),
        clock=clock,
    )
    barrier = context.Barrier(5)
    output = context.Queue()
    workers = [
        context.Process(
            target=_commit_process,
            args=(
                str(database_path),
                barrier,
                output,
                utc_timestamp(clock.now()),
                *_commit_args(proposal),
            ),
        )
        for _ in range(5)
    ]
    audit_before = int(connection.execute("SELECT count(*) FROM audit_event").fetchone()[0])
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=30)
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
        assert worker.exitcode == 0
    results = [output.get(timeout=5) for _ in workers]
    output.close()
    assert all(result[0] == "ok" for result in results)
    assert len({result[1] for result in results}) == 1
    assert (
        int(connection.execute("SELECT count(*) FROM audit_event").fetchone()[0])
        == audit_before + 1
    )

    rollback_proposal = propose_booking(
        connection,
        person_id="maya",
        instrument_id="INS-01",
        project_id="clock-rollback",
        start=at(ANCHOR_DATE, 18),
        end=at(ANCHOR_DATE, 19),
        clock=clock,
    )
    rollback_clock = FixedClock(clock.now() - timedelta(minutes=1))
    with pytest.raises(LabQuorumError) as error:
        commit_booking(
            connection,
            rollback_proposal["request_id"],
            rollback_proposal["revision"],
            rollback_proposal["content_hash"],
            rollback_proposal["decision"],
            clock=rollback_clock,
        )
    assert error.value.code is ErrorCode.EXPIRED
    assert (
        get_request(connection, rollback_proposal["request_id"], clock=clock)["status"] == "expired"
    )
    connection.close()


class LedgerBookingMachine(RuleBasedStateMachine):
    """Stateful booking operations against a temporary SQLite ledger."""

    def __init__(self) -> None:
        super().__init__()
        self._temporary = tempfile.TemporaryDirectory(prefix="labquorum-state-")
        path = Path(self._temporary.name) / "state.sqlite"
        self.connection, self.clock = make_seeded_ledger(path)
        self.proposals: list[dict[str, Any]] = []
        self.committed: dict[str, dict[str, Any]] = {}

    @rule(slot=st.integers(min_value=9, max_value=18))
    def propose(self, slot: int) -> None:
        start = at(ANCHOR_DATE, slot)
        try:
            proposal = propose_booking(
                self.connection,
                person_id="maya",
                instrument_id="INS-01",
                project_id="state-machine",
                start=start,
                end=start + timedelta(minutes=30),
                clock=self.clock,
            )
            self.proposals.append(proposal)
        except LabQuorumError:
            pass

    @rule(index=st.integers(min_value=0, max_value=30))
    def commit_pending(self, index: int) -> None:
        if not self.proposals:
            return
        proposal = self.proposals[index % len(self.proposals)]
        try:
            result = commit_booking(
                self.connection,
                proposal["request_id"],
                proposal["revision"],
                proposal["content_hash"],
                proposal["decision"],
                clock=self.clock,
            )
            self.committed[result["booking_id"]] = result
        except LabQuorumError:
            pass

    @rule(index=st.integers(min_value=0, max_value=30))
    def cancel_committed(self, index: int) -> None:
        if self.committed:
            booking = list(self.committed.values())[index % len(self.committed)]
            cancel_booking(
                self.connection, booking["booking_id"], actor="prof-rao", clock=self.clock
            )

    @rule(index=st.integers(min_value=0, max_value=30))
    def decline_pending(self, index: int) -> None:
        if self.proposals:
            proposal = self.proposals[index % len(self.proposals)]
            with contextlib.suppress(LabQuorumError):
                decline_request(
                    self.connection,
                    proposal["request_id"],
                    proposal["revision"],
                    "State machine decline",
                    clock=self.clock,
                )

    @rule(minutes=st.integers(min_value=1, max_value=20))
    def advance_to_expiry(self, minutes: int) -> None:
        self.clock.set(self.clock.now() + timedelta(minutes=minutes))
        for proposal in self.proposals:
            with contextlib.suppress(LabQuorumError):
                get_request(self.connection, proposal["request_id"], clock=self.clock)

    @invariant()
    def invariant_no_committed_gap_violation(self) -> None:
        rows = self.connection.execute(
            "SELECT id, instrument_id, start_utc, end_utc FROM booking "
            "WHERE status = 'committed' ORDER BY instrument_id, start_utc"
        ).fetchall()
        for index, first in enumerate(rows):
            for second in rows[index + 1 :]:
                if first["instrument_id"] == second["instrument_id"]:
                    first_start = parse_iso_datetime(first["start_utc"]).astimezone(UTC)
                    first_end = parse_iso_datetime(first["end_utc"]).astimezone(UTC)
                    second_start = parse_iso_datetime(second["start_utc"]).astimezone(UTC)
                    second_end = parse_iso_datetime(second["end_utc"]).astimezone(UTC)
                    gap = timedelta(minutes=15)
                    assert not (first_start < second_end + gap and first_end + gap > second_start)

    def teardown(self) -> None:
        self.connection.close()
        self._temporary.cleanup()


def test_P_01_state_machine_preserves_committed_gap_invariant() -> None:
    run_state_machine_as_test(
        LedgerBookingMachine,
        settings=settings(max_examples=8, stateful_step_count=12, deadline=None),
    )
