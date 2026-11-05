"""Pure booking and instrument policy rules."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class Interval:
    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        raise NotImplementedError


@dataclass(frozen=True)
class Training:
    granted_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class Booking:
    booking_id: str
    interval: Interval
    status: str = "committed"


@dataclass(frozen=True)
class InstrumentPolicy:
    instrument_id: str
    timezone: str
    opening_hours: Mapping[int, tuple[time, time]]
    max_block_minutes: int
    min_gap_minutes: int
    booking_window_days: int
    status: str = "ok"
    down_until: datetime | None = None
    requires_training: bool = True


def intervals_conflict(candidate: Interval, existing: Interval, *, gap_minutes: int = 0) -> bool:
    raise NotImplementedError


def check_booking(
    instrument: InstrumentPolicy,
    interval: Interval,
    *,
    now: datetime,
    training: Training | None,
    existing_bookings: list[Booking] | tuple[Booking, ...] = (),
) -> None:
    raise NotImplementedError


def nearest_free_slot(
    instrument: InstrumentPolicy,
    requested_start: datetime,
    *,
    duration_minutes: int,
    now: datetime,
    existing_bookings: list[Booking] | tuple[Booking, ...] = (),
) -> Interval | None:
    raise NotImplementedError
