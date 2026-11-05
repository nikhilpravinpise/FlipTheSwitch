"""P1 approval lifecycle, audit, seed, and SQLite integration behavior."""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import parse_iso_datetime
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
from tests.conftest import ANCHOR_DATE, BASE_NOW, at


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


def test_U_A01_request_lifecycle_has_only_allowed_terminal_states(
    ledger_factory: Any,
) -> None:
    connection, clock = ledger_factory("lifecycle.sqlite")
    committed = _commit(connection, clock, _propose(connection, clock, start_hour=16))
    declined = _propose(connection, clock, start_hour=18)
    decline_request(connection, declined["request_id"], 1, "No available operator", clock=clock)
    expiring = _propose(connection, clock, start_hour=19)
    clock.set(parse_iso_datetime(expiring["expires_utc"]))
    expired = get_request(connection, expiring["request_id"], clock=clock)
    assert committed["status"] == "committed"
    assert get_request(connection, declined["request_id"], clock=clock)["status"] == "declined"
    assert expired["status"] == "expired"


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
        (BASE_NOW.isoformat(), (BASE_NOW + timedelta(days=120)).isoformat()),
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


def test_U_L02_raw_edit_is_detected_at_the_modified_audit_row(
    seeded_ledger: tuple[sqlite3.Connection, Any],
) -> None:
    connection, _ = seeded_ledger
    assert verify(connection) is None
    sequence = int(connection.execute("SELECT min(seq) FROM audit_event").fetchone()[0])
    connection.execute("UPDATE audit_event SET result_json = '{}' WHERE seq = ?", (sequence,))
    assert verify(connection) == sequence


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
    assert any(row["start_utc"].startswith("2026-11-06T08:30:00") for row in initial_bookings)


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
    mismatch.execute("UPDATE schema_version SET version = 999")
    mismatch.commit()
    mismatch.close()
    with pytest.raises(LabQuorumError) as error:
        open_database(backup_path)
    assert error.value.code is ErrorCode.SCHEMA_VERSION_MISMATCH


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
