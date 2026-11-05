"""Shared pytest configuration for LabQuorum tests."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Generator
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from labquorum.domain.booking import InstrumentPolicy
from labquorum.domain.timeutil import FixedClock
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo

BASE_NOW = datetime(2026, 11, 5, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
ANCHOR_DATE = date(2026, 11, 6)


def at(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=ZoneInfo("Asia/Kolkata"))


def make_policy(
    *,
    instrument_id: str = "INS-01",
    status: str = "ok",
    down_until: datetime | None = None,
) -> InstrumentPolicy:
    return InstrumentPolicy(
        instrument_id=instrument_id,
        timezone="Asia/Kolkata",
        opening_hours={day: (time(8), time(20)) for day in range(6)},
        max_block_minutes=240,
        min_gap_minutes=15,
        booking_window_days=30,
        status=status,
        down_until=down_until,
        requires_training=True,
    )


def make_seeded_ledger(
    path: Path,
    *,
    now: datetime = BASE_NOW,
    anchor_date: date = ANCHOR_DATE,
) -> tuple[sqlite3.Connection, FixedClock]:
    connection = init_database(path)
    clock = FixedClock(now)
    seed_demo(connection, anchor_date, clock=clock)
    return connection, clock


@pytest.fixture
def seeded_ledger(
    tmp_path: Path,
) -> Generator[tuple[sqlite3.Connection, FixedClock], None, None]:
    clock = FixedClock(BASE_NOW)
    try:
        connection = init_database(tmp_path / "ledger.sqlite")
    except NotImplementedError:
        connection = sqlite3.connect(":memory:")
    else:
        seed_demo(connection, ANCHOR_DATE, clock=clock)
    yield connection, clock
    connection.close()


@pytest.fixture
def ledger_factory(
    tmp_path: Path,
) -> Generator[Callable[..., tuple[sqlite3.Connection, FixedClock]], None, None]:
    created: list[sqlite3.Connection] = []

    def make(
        name: str = "ledger.sqlite",
        *,
        now: datetime = BASE_NOW,
    ) -> tuple[sqlite3.Connection, FixedClock]:
        connection, clock = make_seeded_ledger(tmp_path / name, now=now)
        created.append(connection)
        return connection, clock

    yield make
    for connection in created:
        connection.close()
