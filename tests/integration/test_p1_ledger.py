"""P1 approval lifecycle, audit, seed, and SQLite integration behavior."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule, run_state_machine_as_test

from labquorum.cli.main import main as lq_main
from labquorum.domain.booking import Booking, Interval, nearest_free_slot
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import parse_iso_datetime, utc_timestamp
from labquorum.store.audit import verify
from labquorum.store.db import (
    database_info,
    init_database,
    onedrive_warning,
    open_database,
    select_journal_mode,
)
from labquorum.store.repos import (
    cancel_booking,
    commit_booking,
    decline_request,
    get_request,
    lab_state,
    list_bookings,
    propose_booking,
    revise_request,
)
from labquorum.store.seed import seed_demo
from tests.conftest import ANCHOR_DATE, BASE_NOW, at, make_policy, make_seeded_ledger


def _propose(  # noqa: PLR0913
    connection: sqlite3.Connection,
    clock: Any,
    *,
    start_hour: int = 16,
    start_minute: int = 0,
    end_hour: int | None = None,
    end_minute: int = 0,
) -> dict[str, Any]:
    start = at(ANCHOR_DATE, start_hour, start_minute)
    end = at(ANCHOR_DATE, end_hour if end_hour is not None else start_hour + 1, end_minute)
    return propose_booking(
        connection,
        person_id="maya",
        instrument_id="INS-01",
        project_id="demo-project",
        start=start,
        end=end,
        clock=clock,
    )


def _commit(connection: sqlite3.Connection, clock: Any, proposal: dict[str, Any]) -> dict[str, Any]:
    return commit_booking(
        connection,
        proposal["request_id"],
        proposal["revision"],
        proposal["content_hash"],
        proposal["decision"],
        clock=clock,
    )


def _audit_count(connection: sqlite3.Connection) -> int:
    return int(connection.execute("SELECT count(*) FROM audit_event").fetchone()[0])


class ApprovalLifecycleMachine(RuleBasedStateMachine):
    """Exercise approval transitions through durable repository calls."""

    def __init__(self) -> None:
        super().__init__()
        self._temporary = tempfile.TemporaryDirectory(prefix="labquorum-approval-state-")
        self.database_path = Path(self._temporary.name) / "state.sqlite"
        self.connection, self.clock = make_seeded_ledger(self.database_path)
        self.requests: dict[str, dict[str, Any]] = {}
        self.proposal_counter = 0

    def _pending_ids(self) -> list[str]:
        return [
            request_id
            for request_id, model in self.requests.items()
            if model["status"] == "pending"
        ]

    def _record_expired(self, *, request_id: str | None = None) -> None:
        now = self.clock.now()
        for candidate_id, model in self.requests.items():
            if request_id is not None and candidate_id != request_id:
                continue
            if model["status"] == "pending" and now >= parse_iso_datetime(model["expires_utc"]):
                model["status"] = "expired"

    def _attempt_commit(self, model: dict[str, Any]) -> None:
        proposal = model["proposal"]
        if model["status"] in {"declined", "expired"}:
            expected = ErrorCode.DECLINED if model["status"] == "declined" else ErrorCode.EXPIRED
            with pytest.raises(LabQuorumError) as error:
                _commit(self.connection, self.clock, proposal)
            assert error.value.code is expected
            return
        if model["status"] == "committed":
            assert _commit(self.connection, self.clock, proposal) == model["committed_result"]
            return
        if self.clock.now() >= parse_iso_datetime(model["expires_utc"]):
            with pytest.raises(LabQuorumError) as error:
                _commit(self.connection, self.clock, proposal)
            assert error.value.code is ErrorCode.EXPIRED
            model["status"] = "expired"
            return
        try:
            result = _commit(self.connection, self.clock, proposal)
        except LabQuorumError as error:
            assert error.code is ErrorCode.CONFLICT
        else:
            model["status"] = "committed"
            model["committed_result"] = result

    def _assert_durable_model(self) -> None:
        durable = open_database(self.database_path)
        try:
            for request_id, model in self.requests.items():
                request = durable.execute(
                    "SELECT status, revision FROM approval_request WHERE id = ?", (request_id,)
                ).fetchone()
                booking = durable.execute(
                    "SELECT status FROM booking WHERE request_id = ?", (request_id,)
                ).fetchone()
                assert request is not None
                assert booking is not None
                assert str(request["status"]) == model["status"]
                assert int(request["revision"]) == model["revision"]
                expected_booking_status = {
                    "pending": "proposed",
                    "committed": "committed",
                    "declined": "declined",
                    "expired": "expired",
                }[model["status"]]
                assert str(booking["status"]) == expected_booking_status
                if model["status"] in {"declined", "expired"}:
                    self._attempt_commit(model)
                    durable_state = durable.execute(
                        "SELECT status FROM booking WHERE request_id = ?", (request_id,)
                    ).fetchone()
                    assert durable_state is not None
                    assert str(durable_state["status"]) != "committed"
        finally:
            durable.close()

    @rule(hour=st.integers(min_value=16, max_value=19))
    def propose(self, hour: int) -> None:
        self.proposal_counter += 1
        project = f"state-project-{self.proposal_counter}"
        count_before = int(
            self.connection.execute("SELECT count(*) FROM approval_request").fetchone()[0]
        )
        try:
            proposal = propose_booking(
                self.connection,
                person_id="maya",
                instrument_id="INS-01",
                project_id=project,
                start=at(ANCHOR_DATE, hour),
                end=at(ANCHOR_DATE, hour + 1),
                clock=self.clock,
            )
        except LabQuorumError:
            assert (
                int(self.connection.execute("SELECT count(*) FROM approval_request").fetchone()[0])
                == count_before
            )
            return
        self.requests[proposal["request_id"]] = {
            "status": "pending",
            "revision": proposal["revision"],
            "proposal": proposal,
            "expires_utc": proposal["expires_utc"],
        }

    @rule(
        index=st.integers(min_value=0, max_value=20), hour=st.integers(min_value=16, max_value=19)
    )
    def revise(self, index: int, hour: int) -> None:
        pending = self._pending_ids()
        if not pending:
            return
        request_id = pending[index % len(pending)]
        model = self.requests[request_id]
        start = at(ANCHOR_DATE, hour)
        try:
            revised = revise_request(
                self.connection,
                request_id,
                revision=model["revision"],
                start=start,
                end=start + timedelta(hours=1),
                project_id=f"revised-{request_id}-{model['revision'] + 1}",
                clock=self.clock,
            )
        except LabQuorumError as error:
            if self.clock.now() >= parse_iso_datetime(model["expires_utc"]):
                assert error.code is ErrorCode.EXPIRED
                model["status"] = "expired"
            else:
                assert error.code is ErrorCode.CONFLICT
        else:
            model["revision"] = revised["revision"]
            model["proposal"] = revised

    @rule(index=st.integers(min_value=0, max_value=20))
    def decline(self, index: int) -> None:
        pending = self._pending_ids()
        if not pending:
            return
        request_id = pending[index % len(pending)]
        model = self.requests[request_id]
        try:
            decline_request(
                self.connection,
                request_id,
                model["revision"],
                "State machine decline",
                clock=self.clock,
            )
        except LabQuorumError as error:
            assert error.code is ErrorCode.EXPIRED
            model["status"] = "expired"
        else:
            model["status"] = "declined"

    @rule(index=st.integers(min_value=0, max_value=20))
    def expire(self, index: int) -> None:
        pending = self._pending_ids()
        if not pending:
            return
        request_id = pending[index % len(pending)]
        expiry = parse_iso_datetime(self.requests[request_id]["expires_utc"])
        if self.clock.now() < expiry:
            self.clock.set(expiry)
        result = get_request(self.connection, request_id, clock=self.clock)
        assert result["status"] == "expired"
        self._record_expired()

    @rule(index=st.integers(min_value=0, max_value=20))
    def commit(self, index: int) -> None:
        if not self.requests:
            return
        request_id = list(self.requests)[index % len(self.requests)]
        model = self.requests[request_id]
        self._attempt_commit(model)

    @rule(index=st.integers(min_value=0, max_value=20))
    def retry(self, index: int) -> None:
        if not self.requests:
            return
        request_id = list(self.requests)[index % len(self.requests)]
        self._attempt_commit(self.requests[request_id])

    @invariant()
    def durable_statuses_match_independent_model(self) -> None:
        self._assert_durable_model()

    def teardown(self) -> None:
        self.connection.close()
        self._temporary.cleanup()


def _run_lifecycle_state_machine() -> None:
    run_state_machine_as_test(
        ApprovalLifecycleMachine,
        settings=settings(max_examples=5, stateful_step_count=14, deadline=None),
    )


def test_U_B09_proposal_past_hold_expiry_reads_as_expired(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    clock.set(parse_iso_datetime(proposal["expires_utc"]))
    request = get_request(connection, proposal["request_id"], clock=clock)
    assert request["status"] == "expired"


def test_U_B12_cancellation_releases_slot_exactly_once(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    committed = _commit(connection, clock, proposal)
    before_cancel = _audit_count(connection)
    first = cancel_booking(connection, committed["booking_id"], actor="prof-rao", clock=clock)
    after_first = _audit_count(connection)
    second = cancel_booking(connection, committed["booking_id"], actor="prof-rao", clock=clock)
    assert first["status"] == second["status"] == "cancelled"
    assert after_first == before_cancel + 1
    assert _audit_count(connection) == after_first
    replacement = _propose(connection, clock)
    assert replacement["status"] == "pending"


def test_U_A01_lifecycle_state_machine_matches_durable_repository_state() -> None:
    _run_lifecycle_state_machine()


def test_P_05_no_repository_path_commits_declined_or_expired_requests() -> None:
    _run_lifecycle_state_machine()


def test_U_A02_commit_is_idempotent_without_a_second_audit_effect(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    first = _commit(connection, clock, proposal)
    after_first = _audit_count(connection)
    second = _commit(connection, clock, proposal)
    assert second == first
    assert _audit_count(connection) == after_first


def test_U_A03_commit_rechecks_conflict_inside_transaction(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    first = _propose(connection, clock, start_hour=16)
    second = _propose(connection, clock, start_hour=16)
    _commit(connection, clock, first)
    with pytest.raises(LabQuorumError) as error:
        _commit(connection, clock, second)
    assert error.value.code is ErrorCode.CONFLICT


def test_U_A05_declined_request_records_reason_and_never_commits(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    decline_request(
        connection, proposal["request_id"], 1, "Instrument reserved for maintenance", clock=clock
    )
    request = get_request(connection, proposal["request_id"], clock=clock)
    assert request["status"] == "declined"
    assert request["decline_reason"] == "Instrument reserved for maintenance"
    with pytest.raises(LabQuorumError) as error:
        _commit(connection, clock, proposal)
    assert error.value.code is ErrorCode.DECLINED


def test_U_A06_expiry_at_exact_now_is_expired(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    clock.set(parse_iso_datetime(proposal["expires_utc"]))
    request = get_request(connection, proposal["request_id"], clock=clock)
    assert request["status"] == "expired"
    with pytest.raises(LabQuorumError) as error:
        _commit(connection, clock, proposal)
    assert error.value.code is ErrorCode.EXPIRED


def test_U_A07_revision_or_hash_mismatch_fails_stale(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    with pytest.raises(LabQuorumError) as error:
        commit_booking(
            connection,
            proposal["request_id"],
            proposal["revision"] + 1,
            proposal["content_hash"],
            proposal["decision"],
            clock=clock,
        )
    assert error.value.code is ErrorCode.STALE_REQUEST
    with pytest.raises(LabQuorumError) as hash_error:
        commit_booking(
            connection,
            proposal["request_id"],
            proposal["revision"],
            "0" * 64,
            proposal["decision"],
            clock=clock,
        )
    assert hash_error.value.code is ErrorCode.STALE_REQUEST


def test_U_A08_editing_request_bumps_revision_and_invalidates_old_decision(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    revised = revise_request(
        connection,
        proposal["request_id"],
        revision=1,
        start=at(ANCHOR_DATE, 17),
        end=at(ANCHOR_DATE, 18),
        project_id="revised-project",
        clock=clock,
    )
    assert revised["revision"] == 2
    assert revised["content_hash"] != proposal["content_hash"]
    with pytest.raises(LabQuorumError) as error:
        _commit(connection, clock, proposal)
    assert error.value.code is ErrorCode.STALE_REQUEST


def test_U_A09_commit_rechecks_training_and_instrument_status(
    ledger_factory: Any,
) -> None:
    connection, clock = ledger_factory("commit-policy.sqlite")
    no_training = _propose(connection, clock, start_hour=16)
    connection.execute("DELETE FROM training WHERE person_id = 'maya' AND instrument_id = 'INS-01'")
    with pytest.raises(LabQuorumError) as training_error:
        _commit(connection, clock, no_training)
    assert training_error.value.code is ErrorCode.TRAINING_REQUIRED
    connection.execute(
        "INSERT INTO training(person_id, instrument_id, granted_at_utc, expires_at_utc) "
        "VALUES ('maya', 'INS-01', ?, ?)",
        (utc_timestamp(BASE_NOW), utc_timestamp(BASE_NOW + timedelta(days=120))),
    )
    down = _propose(connection, clock, start_hour=17)
    connection.execute("UPDATE instrument SET status = 'down' WHERE id = 'INS-01'")
    with pytest.raises(LabQuorumError) as instrument_error:
        _commit(connection, clock, down)
    assert instrument_error.value.code is ErrorCode.INSTRUMENT_DOWN


def test_U_A10_get_request_returns_exact_commit_echo_fields(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    request = get_request(connection, proposal["request_id"], clock=clock)
    assert request["request_id"] == proposal["request_id"]
    assert request["revision"] == proposal["revision"]
    assert request["content_hash"] == proposal["content_hash"]
    assert request["decision"] == proposal["decision"]
    assert set(request["decision"]) == {
        "action",
        "requester",
        "resource",
        "interval",
        "project",
        "request_id",
        "revision",
    }


def test_U_L01_audit_hash_chain_verifies_clean_log(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, _ = seeded_ledger
    assert verify(connection) is None


def test_U_L02_every_audit_field_and_middle_insertion_or_deletion_is_detected(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    committed = _commit(connection, clock, _propose(connection, clock))
    _propose(connection, clock, start_hour=18)
    assert verify(connection) is None
    second_sequence = 2
    last_sequence = int(connection.execute("SELECT max(seq) FROM audit_event").fetchone()[0])
    assert last_sequence >= 4
    edits = {
        "ts_utc": "2026-11-05T06:30:00.000001Z",
        "actor_agent": "tampered",
        "tool": "tampered",
        "args_json": "{}",
        "result_json": "{}",
        "prev_hash": "a" * 64,
        "hash": "b" * 64,
    }
    for column, replacement in edits.items():
        connection.execute("SAVEPOINT audit_field_edit")
        connection.execute(
            f"UPDATE audit_event SET {column} = ? WHERE seq = ?",
            (replacement, second_sequence),
        )
        assert verify(connection) == second_sequence
        connection.execute("ROLLBACK TO audit_field_edit")
        connection.execute("RELEASE audit_field_edit")

    connection.execute("SAVEPOINT audit_sequence_edit")
    connection.execute(
        "UPDATE audit_event SET seq = ? WHERE seq = ?", (last_sequence + 1, last_sequence)
    )
    assert verify(connection) == last_sequence + 1
    connection.execute("ROLLBACK TO audit_sequence_edit")
    connection.execute("RELEASE audit_sequence_edit")

    first = connection.execute("SELECT * FROM audit_event WHERE seq = 1").fetchone()
    assert first is not None
    connection.execute("SAVEPOINT audit_middle_insert")
    connection.execute("UPDATE audit_event SET seq = 20 WHERE seq = 2")
    connection.execute(
        "INSERT INTO audit_event(seq, ts_utc, actor_agent, tool, args_json, result_json, prev_hash, hash) "
        "VALUES (2, ?, 'inserted', 'inserted', '{}', '{}', ?, ?)",
        (utc_timestamp(clock.now()), first["hash"], "c" * 64),
    )
    assert verify(connection) == 2
    connection.execute("ROLLBACK TO audit_middle_insert")
    connection.execute("RELEASE audit_middle_insert")

    connection.execute("SAVEPOINT audit_middle_delete")
    connection.execute("DELETE FROM audit_event WHERE seq = 2")
    assert verify(connection) == 3
    connection.execute("ROLLBACK TO audit_middle_delete")
    connection.execute("RELEASE audit_middle_delete")
    assert verify(connection) is None
    assert committed["status"] == "committed"


def test_U_L04_injected_clock_drives_timestamped_repository_operations(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    assert connection.execute("SELECT ts_utc FROM audit_event WHERE seq = 1").fetchone()[
        0
    ] == utc_timestamp(clock.now())
    proposal = _propose(connection, clock)
    assert connection.execute(
        "SELECT created_utc FROM approval_request WHERE id = ?", (proposal["request_id"],)
    ).fetchone()[0] == utc_timestamp(clock.now())
    assert connection.execute(
        "SELECT ts_utc FROM audit_event ORDER BY seq DESC LIMIT 1"
    ).fetchone()[0] == utc_timestamp(clock.now())

    clock.advance(timedelta(minutes=1))
    revised = revise_request(
        connection,
        proposal["request_id"],
        revision=1,
        start=at(ANCHOR_DATE, 17),
        end=at(ANCHOR_DATE, 18),
        project_id="clock-revised",
        clock=clock,
    )
    assert connection.execute(
        "SELECT ts_utc FROM audit_event ORDER BY seq DESC LIMIT 1"
    ).fetchone()[0] == utc_timestamp(clock.now())

    clock.advance(timedelta(minutes=1))
    committed = _commit(connection, clock, revised)
    assert connection.execute(
        "SELECT decided_utc FROM approval_request WHERE id = ?", (proposal["request_id"],)
    ).fetchone()[0] == utc_timestamp(clock.now())
    assert connection.execute(
        "SELECT ts_utc FROM audit_event ORDER BY seq DESC LIMIT 1"
    ).fetchone()[0] == utc_timestamp(clock.now())

    clock.advance(timedelta(minutes=1))
    cancel_booking(connection, committed["booking_id"], actor="prof-rao", clock=clock)
    assert connection.execute(
        "SELECT ts_utc FROM audit_event ORDER BY seq DESC LIMIT 1"
    ).fetchone()[0] == utc_timestamp(clock.now())

    declined = _propose(connection, clock, start_hour=19)
    decline_request(connection, declined["request_id"], 1, "No longer needed", clock=clock)
    assert connection.execute(
        "SELECT decided_utc FROM approval_request WHERE id = ?", (declined["request_id"],)
    ).fetchone()[0] == utc_timestamp(clock.now())

    expiring = propose_booking(
        connection,
        person_id="maya",
        instrument_id="INS-01",
        project_id="clock-expiry",
        start=at(ANCHOR_DATE, 18, 15),
        end=at(ANCHOR_DATE, 19, 15),
        clock=clock,
    )
    clock.set(parse_iso_datetime(expiring["expires_utc"]))
    assert get_request(connection, expiring["request_id"], clock=clock)["status"] == "expired"
    assert connection.execute(
        "SELECT decided_utc FROM approval_request WHERE id = ?", (expiring["request_id"],)
    ).fetchone()[0] == utc_timestamp(clock.now())
    assert connection.execute(
        "SELECT ts_utc FROM audit_event ORDER BY seq DESC LIMIT 1"
    ).fetchone()[0] == utc_timestamp(clock.now())


def test_I_10_demo_seed_is_idempotent_and_anchor_date_relative(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    seed_demo(connection, date(2026, 11, 6), clock=clock)
    initial_count = _audit_count(connection)
    initial_bookings = list_bookings(connection, clock=clock)
    seed_demo(connection, date(2026, 11, 6), clock=clock)
    assert _audit_count(connection) == initial_count
    assert list_bookings(connection, clock=clock) == initial_bookings
    assert any(row["start_utc"] == "2026-11-07T08:30:00.000000Z" for row in initial_bookings)


def test_I_10_demo_seed_backfills_a_new_person_and_training_at_the_same_anchor(
    tmp_path: Path,
) -> None:
    anchor_date = date(2026, 11, 6)
    connection, clock = make_seeded_ledger(
        tmp_path / "seed-backfill.sqlite", anchor_date=anchor_date
    )
    connection.execute("DELETE FROM training WHERE person_id = ?", ("darved2305",))
    connection.execute("DELETE FROM person WHERE id = ?", ("darved2305",))
    connection.commit()
    initial_audit_count = _audit_count(connection)

    result = seed_demo(connection, anchor_date, clock=clock)

    person = connection.execute(
        "SELECT display_name, role FROM person WHERE id = ?", ("darved2305",)
    ).fetchone()
    training = connection.execute(
        "SELECT expires_at_utc FROM training WHERE person_id = ? AND instrument_id = ?",
        ("darved2305", "INS-01"),
    ).fetchone()
    assert result["seeded"] is False
    assert result["people"] == 1
    assert person is not None
    assert person["display_name"] == "Darshan Ved (student)"
    assert person["role"] == "student"
    assert training is not None
    assert verify(connection) is None
    assert _audit_count(connection) == initial_audit_count + 1
    connection.close()


def _assert_seeded_alternative_for_anchor(
    database_path: Path, anchor_date: date, expected_open_day: date
) -> None:
    connection, _ = make_seeded_ledger(database_path, anchor_date=anchor_date)
    try:
        row = connection.execute(
            "SELECT start_utc, end_utc FROM booking WHERE id = 'BK-0041'"
        ).fetchone()
        assert row is not None
        assert str(row["start_utc"]) == utc_timestamp(at(expected_open_day, 14))
        assert str(row["end_utc"]) == utc_timestamp(at(expected_open_day, 15, 30))
        existing = Booking(
            "BK-0041",
            Interval(
                parse_iso_datetime(str(row["start_utc"])), parse_iso_datetime(str(row["end_utc"]))
            ),
        )
        alternative = nearest_free_slot(
            make_policy(),
            at(expected_open_day, 14),
            duration_minutes=60,
            now=at(anchor_date, 8),
            existing_bookings=[existing],
        )
        assert alternative == Interval(at(expected_open_day, 15, 45), at(expected_open_day, 16, 45))
    finally:
        connection.close()


def test_I_10_friday_anchor_seeds_saturday_and_demo_alternative(tmp_path: Path) -> None:
    _assert_seeded_alternative_for_anchor(
        tmp_path / "friday.sqlite", date(2026, 11, 6), date(2026, 11, 7)
    )


def test_I_10_sunday_anchor_seeds_monday_and_demo_alternative(tmp_path: Path) -> None:
    _assert_seeded_alternative_for_anchor(
        tmp_path / "sunday.sqlite", date(2026, 11, 8), date(2026, 11, 9)
    )


def test_I_19_backup_restore_and_schema_version_mismatch_are_handled(
    tmp_path: Path,
) -> None:
    source = init_database(tmp_path / "source.sqlite")
    seed_demo(source, ANCHOR_DATE)
    backup_path = tmp_path / "restored.sqlite"
    backup = sqlite3.connect(backup_path)
    source.backup(backup)
    backup.close()
    source.close()
    restored = open_database(backup_path)
    assert verify(restored) is None
    restored.close()
    mismatch = sqlite3.connect(backup_path)
    mismatch.execute("UPDATE schema_version SET version = 1")
    mismatch.commit()
    mismatch.close()
    with pytest.raises(LabQuorumError) as error:
        open_database(backup_path)
    assert error.value.code is ErrorCode.SCHEMA_VERSION_MISMATCH
    with pytest.raises(LabQuorumError) as init_error:
        init_database(backup_path)
    assert init_error.value.code is ErrorCode.SCHEMA_VERSION_MISMATCH
    unchanged = sqlite3.connect(backup_path)
    try:
        assert unchanged.execute("SELECT version FROM schema_version").fetchone()[0] == 1
    finally:
        unchanged.close()


def test_I_19_journal_mode_is_version_gated_and_reported(tmp_path: Path) -> None:
    assert select_journal_mode((3, 51, 2)) == "DELETE"
    assert select_journal_mode((3, 51, 3)) == "WAL"
    connection = init_database(tmp_path / "journal.sqlite")
    info = database_info(connection)
    assert info.sqlite_version == sqlite3.sqlite_version
    assert info.journal_mode in {"delete", "wal"}
    connection.close()


def test_onedrive_path_is_exposed_as_a_doctor_warning() -> None:
    warning = onedrive_warning(Path("C:/Users/test/OneDrive/LabQuorum/ledger.sqlite"))
    assert warning is not None
    assert "OneDrive" in warning


def test_audit_verify_reports_internal_consistency_and_checkpoint_limit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    database_path = tmp_path / "audit-cli.sqlite"
    connection = init_database(database_path)
    connection.close()
    assert lq_main(["audit", "verify", "--db", str(database_path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["scope"] == "internal chain consistency"
    assert "truncation" in output["limitation"].lower()
    assert "recomputed chains" in output["limitation"].lower()
    assert "external checkpoint" in output["limitation"].lower()


def test_I_20_full_demo_scenario_keeps_audit_chain_valid(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    committed = _commit(connection, clock, proposal)
    cancel_booking(connection, committed["booking_id"], actor="prof-rao", clock=clock)
    decline = _propose(connection, clock, start_hour=17)
    decline_request(connection, decline["request_id"], 1, "No longer needed", clock=clock)
    assert verify(connection) is None


def test_lab_state_returns_current_booking_ledger(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    state = lab_state(connection, clock=clock)
    assert any(booking["id"] == "BK-0041" for booking in state["bookings"])


def test_approval_decision_over_900_characters_is_rejected(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    with pytest.raises(LabQuorumError) as error:
        propose_booking(
            connection,
            person_id="maya",
            instrument_id="INS-01",
            project_id="x" * 1000,
            start=at(ANCHOR_DATE, 16),
            end=at(ANCHOR_DATE, 17),
            clock=clock,
        )
    assert error.value.code is ErrorCode.INVALID_ARGUMENT


def test_tampered_decision_bytes_are_rejected(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, clock = seeded_ledger
    proposal = _propose(connection, clock)
    tampered = {**proposal["decision"], "project": "different-project"}
    with pytest.raises(LabQuorumError) as error:
        commit_booking(
            connection,
            proposal["request_id"],
            proposal["revision"],
            proposal["content_hash"],
            tampered,
            clock=clock,
        )
    assert error.value.code is ErrorCode.DECISION_MISMATCH
