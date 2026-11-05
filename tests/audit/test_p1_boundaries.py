"""Independent regressions for P1 boundary defects."""

from datetime import timedelta

import pytest

from labquorum.domain.approvals import serialize_decision
from labquorum.domain.canonical import canonical_json
from labquorum.domain.errors import LabQuorumError
from labquorum.store.repos import propose_booking
from tests.conftest import ANCHOR_DATE, at


def test_exactly_900_character_decision_is_rejected() -> None:
    decision = {"project": ""}
    decision["project"] = "x" * (900 - len(canonical_json(decision)))
    assert len(canonical_json(decision)) == 900
    with pytest.raises(LabQuorumError):
        serialize_decision(decision)


def test_positive_subsecond_booking_can_be_proposed(seeded_ledger) -> None:
    connection, clock = seeded_ledger
    start = at(ANCHOR_DATE, 16)
    proposal = propose_booking(
        connection,
        person_id="maya",
        instrument_id="INS-01",
        project_id="subsecond",
        start=start,
        end=start + timedelta(microseconds=1),
        clock=clock,
    )
    assert proposal["status"] == "pending"


def test_seed_bookings_fall_on_next_open_day(tmp_path) -> None:
    from datetime import date

    from labquorum.store.db import init_database
    from labquorum.store.seed import seed_demo

    connection = init_database(tmp_path / "sunday.sqlite")
    try:
        seed_demo(connection, date(2026, 11, 8))
        row = connection.execute("SELECT start_utc FROM booking WHERE id = 'BK-0041'").fetchone()
        assert row["start_utc"].startswith("2026-11-09T08:30:00")
    finally:
        connection.close()
