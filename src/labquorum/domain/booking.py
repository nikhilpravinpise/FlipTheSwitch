"""Pure booking and instrument policy rules."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import utc_timestamp


def _aware(value: datetime, label: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, f"{label} must be time-zone aware.")
    return value.astimezone(UTC)


def _zone(value: str) -> ZoneInfo:
    try:
        return ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, f"Unknown IANA time zone: {value}."
        ) from exc


@dataclass(frozen=True)
class Interval:
    """Aware half-open interval [start, end)."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        start_utc = _aware(self.start, "Interval start")
        end_utc = _aware(self.end, "Interval end")
        if end_utc <= start_utc:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT, "Interval end must be after its start."
            )

    @property
    def duration_minutes(self) -> int:
        seconds = (
            _aware(self.end, "Interval end") - _aware(self.start, "Interval start")
        ).total_seconds()
        return int((seconds + 59) // 60)


@dataclass(frozen=True)
class Training:
    """A training grant and its exclusive expiry instant."""

    granted_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class Booking:
    """An existing booking interval considered during policy checks."""

    booking_id: str
    interval: Interval
    status: str = "committed"


@dataclass(frozen=True)
class InstrumentPolicy:
    """Booking constraints for an instrument, with weekday-indexed local hours."""

    instrument_id: str
    timezone: str
    opening_hours: Mapping[int, tuple[time, time]]
    max_block_minutes: int
    min_gap_minutes: int
    booking_window_days: int
    status: str = "ok"
    down_until: datetime | None = None
    requires_training: bool = True

    def __post_init__(self) -> None:
        _zone(self.timezone)
        if self.max_block_minutes <= 0 or self.min_gap_minutes < 0 or self.booking_window_days < 0:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT, "Instrument booking limits are invalid."
            )
        if self.down_until is not None:
            _aware(self.down_until, "Instrument down-until time")


def intervals_conflict(candidate: Interval, existing: Interval, *, gap_minutes: int = 0) -> bool:
    """Apply the plan's half-open overlap rule, including symmetric cleaning gap."""
    if gap_minutes < 0:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Minimum gap cannot be negative.")
    candidate_start = _aware(candidate.start, "Candidate start")
    candidate_end = _aware(candidate.end, "Candidate end")
    existing_start = _aware(existing.start, "Existing start")
    existing_end = _aware(existing.end, "Existing end")
    gap = timedelta(minutes=gap_minutes)
    return existing_start < candidate_end + gap and existing_end + gap > candidate_start


def _opening_slice(
    interval: Interval,
    zone: ZoneInfo,
    hours: Mapping[int, tuple[time, time]],
) -> bool:
    local_start = interval.start.astimezone(zone)
    local_end = interval.end.astimezone(zone)
    day = local_start.date()
    while day <= local_end.date():
        schedule = hours.get(day.weekday())
        if schedule is None:
            if day < local_end.date() or local_end.time() > time.min:
                return False
            day += timedelta(days=1)
            continue
        opening, closing = schedule
        opens = datetime.combine(day, opening, zone)
        closes_day = day + timedelta(days=1) if closing <= opening else day
        closes = datetime.combine(closes_day, closing, zone)
        slice_start = max(local_start, datetime.combine(day, time.min, zone))
        next_midnight = datetime.combine(day + timedelta(days=1), time.min, zone)
        slice_end = min(local_end, next_midnight)
        if slice_start < slice_end and (slice_start < opens or slice_end > closes):
            return False
        day += timedelta(days=1)
    return True


def check_booking(
    instrument: InstrumentPolicy,
    interval: Interval,
    *,
    now: datetime,
    training: Training | None,
    existing_bookings: Sequence[Booking] = (),
) -> None:
    """Raise a stable policy error when a proposed interval cannot be booked."""
    now_utc = _aware(now, "Current time")
    start_utc = _aware(interval.start, "Booking start")
    zone = _zone(instrument.timezone)
    local_start = interval.start.astimezone(zone)
    local_now = now.astimezone(zone)

    if start_utc < now_utc:
        raise LabQuorumError(ErrorCode.IN_PAST, "Booking starts before the current time.")
    if (local_start.date() - local_now.date()).days > instrument.booking_window_days:
        raise LabQuorumError(
            ErrorCode.OUTSIDE_WINDOW,
            "Booking starts beyond the instrument booking window.",
            {"booking_window_days": instrument.booking_window_days},
        )
    is_down_before_start = instrument.status == "down" or (
        instrument.status == "down_until"
        and (
            instrument.down_until is None
            or start_utc < _aware(instrument.down_until, "Down-until time")
        )
    )
    if is_down_before_start:
        details = {}
        if instrument.down_until is not None:
            details["down_until"] = utc_timestamp(instrument.down_until)
        raise LabQuorumError(
            ErrorCode.INSTRUMENT_DOWN, "Instrument is down for the requested start.", details
        )
    if instrument.status not in {"ok", "down", "down_until"}:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Unknown instrument status: {instrument.status}.",
        )
    if instrument.requires_training and (
        training is None
        or _aware(training.granted_at, "Training grant") > start_utc
        or _aware(training.expires_at, "Training expiry") <= start_utc
    ):
        details: dict[str, str] = {}
        if training is not None:
            details["expires_at"] = utc_timestamp(training.expires_at)
        raise LabQuorumError(
            ErrorCode.TRAINING_REQUIRED,
            "Valid instrument training is required at booking start.",
            details,
        )
    duration = interval.duration_minutes
    if duration > instrument.max_block_minutes:
        split: list[int] = []
        remaining = duration
        while remaining > 0:
            piece = min(instrument.max_block_minutes, remaining)
            split.append(piece)
            remaining -= piece
        raise LabQuorumError(
            ErrorCode.TOO_LONG,
            f"Booking exceeds the {instrument.max_block_minutes}-minute maximum block.",
            {"max_block_minutes": instrument.max_block_minutes, "suggested_split_minutes": split},
        )
    if not _opening_slice(interval, zone, instrument.opening_hours):
        raise LabQuorumError(
            ErrorCode.OUTSIDE_HOURS, "Booking is outside instrument opening hours."
        )
    for booking in existing_bookings:
        if booking.status == "committed" and intervals_conflict(
            interval,
            booking.interval,
            gap_minutes=instrument.min_gap_minutes,
        ):
            raise LabQuorumError(
                ErrorCode.CONFLICT,
                f"Booking conflicts with committed booking {booking.booking_id}.",
                {"booking_id": booking.booking_id},
            )


def nearest_free_slot(
    instrument: InstrumentPolicy,
    requested_start: datetime,
    *,
    duration_minutes: int,
    now: datetime,
    existing_bookings: Sequence[Booking] = (),
) -> Interval | None:
    """Find the earliest same-length local-hours slot in the instrument window."""
    if duration_minutes <= 0:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Duration must be positive.")
    if duration_minutes > instrument.max_block_minutes or not instrument.opening_hours:
        return None
    if instrument.status == "down" or (
        instrument.status == "down_until" and instrument.down_until is None
    ):
        return None
    now_utc = _aware(now, "Current time")
    requested_utc = _aware(requested_start, "Requested start")
    zone = _zone(instrument.timezone)
    local_now = now_utc.astimezone(zone)
    local_requested = requested_utc.astimezone(zone)
    first_day = max(local_now.date(), local_requested.date())
    last_day = local_now.date() + timedelta(days=instrument.booking_window_days)
    duration = timedelta(minutes=duration_minutes)
    committed = [booking for booking in existing_bookings if booking.status == "committed"]

    day = first_day
    while day <= last_day:
        schedule = instrument.opening_hours.get(day.weekday())
        if schedule is not None:
            opening_time, closing_time = schedule
            opening_local = datetime.combine(day, opening_time, zone)
            closing_day = day + timedelta(days=1) if closing_time <= opening_time else day
            closing_local = datetime.combine(closing_day, closing_time, zone)
            lower_bound = opening_local
            if day == local_requested.date():
                lower_bound = max(lower_bound, local_requested)
            if day == local_now.date():
                lower_bound = max(lower_bound, local_now)
            if instrument.status == "down_until" and instrument.down_until is not None:
                lower_bound = max(lower_bound, instrument.down_until.astimezone(zone))
            candidate_utc = lower_bound.astimezone(UTC)
            opening_close_utc = closing_local.astimezone(UTC)
            while candidate_utc + duration <= opening_close_utc:
                candidate = Interval(candidate_utc, candidate_utc + duration)
                conflicts = [
                    booking
                    for booking in committed
                    if intervals_conflict(
                        candidate,
                        booking.interval,
                        gap_minutes=instrument.min_gap_minutes,
                    )
                ]
                if not conflicts:
                    return candidate
                candidate_utc = max(
                    _aware(booking.interval.end, "Existing booking end")
                    + timedelta(minutes=instrument.min_gap_minutes)
                    for booking in conflicts
                )
        day += timedelta(days=1)
    return None
