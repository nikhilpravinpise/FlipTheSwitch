"""Injected clocks and strict ISO 8601 time handling."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from labquorum.domain.errors import ErrorCode, LabQuorumError

_ISO_DATETIME = re.compile(
    r"\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?"
    r"(?:Z|[+-]\d{2}:\d{2})?\Z"
)


class Clock(Protocol):
    """Source of aware wall-clock instants used by domain and store code."""

    def now(self) -> datetime: ...


class SystemClock:
    """UTC clock backed by the operating system."""

    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass
class FixedClock:
    """Mutable clock for deterministic tests and simulations."""

    instant: datetime

    def __post_init__(self) -> None:
        _require_aware(self.instant)

    def now(self) -> datetime:
        return self.instant

    def set(self, instant: datetime) -> None:
        _require_aware(instant)
        self.instant = instant

    def advance(self, amount: timedelta) -> datetime:
        self.instant = self.now() + amount
        return self.instant


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Datetime must include a time zone offset."
        )


def parse_iso_datetime(value: str, *, timezone: str | ZoneInfo | None = None) -> datetime:
    """Parse a strict ISO datetime, rejecting naive, ambiguous, and nonexistent local times."""
    if _ISO_DATETIME.fullmatch(value) is None:
        raise LabQuorumError(
            ErrorCode.NEEDS_ISO_DATETIME,
            "Provide an ISO 8601 datetime, including an explicit UTC offset.",
        )
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise LabQuorumError(
            ErrorCode.NEEDS_ISO_DATETIME,
            "The datetime is not a valid ISO 8601 value.",
        ) from exc

    if parsed.tzinfo is not None and parsed.utcoffset() is not None:
        return parsed
    if timezone is None:
        raise LabQuorumError(
            ErrorCode.NEEDS_ISO_DATETIME,
            "A local datetime requires a time zone or an explicit UTC offset.",
        )
    try:
        zone = ZoneInfo(timezone) if isinstance(timezone, str) else timezone
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Unknown IANA time zone: {timezone!s}.",
        ) from exc

    candidates: list[datetime] = []
    for fold in (0, 1):
        candidate = parsed.replace(tzinfo=zone, fold=fold)
        round_trip = candidate.astimezone(UTC).astimezone(zone)
        if round_trip.replace(tzinfo=None) == parsed and round_trip.fold == fold:
            candidates.append(candidate)
    if not candidates:
        raise LabQuorumError(
            ErrorCode.NONEXISTENT_LOCAL_TIME,
            f"{value} does not exist in {zone.key} because the clock moves forward.",
            {"timezone": zone.key, "local_datetime": value},
        )
    if len(candidates) == 2 and candidates[0].utcoffset() != candidates[1].utcoffset():
        raise LabQuorumError(
            ErrorCode.AMBIGUOUS_LOCAL_TIME,
            f"{value} occurs twice in {zone.key}; provide an explicit UTC offset.",
            {"timezone": zone.key, "local_datetime": value},
        )
    return candidates[0]


def format_interval(start: datetime, end: datetime, timezone: str | ZoneInfo) -> str:
    """Render a half-open interval with weekday, date, local time, and zone."""
    _require_aware(start)
    _require_aware(end)
    if end.astimezone(UTC) <= start.astimezone(UTC):
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Interval end must be after its start.")
    try:
        zone = ZoneInfo(timezone) if isinstance(timezone, str) else timezone
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Unknown IANA time zone: {timezone!s}.",
        ) from exc
    local_start = start.astimezone(zone)
    local_end = end.astimezone(zone)
    start_date = f"{local_start:%a} {local_start.day} {local_start:%b %Y}"
    end_clock = f"{local_end:%H:%M}"
    zone_name = local_end.tzname() or zone.key
    if local_start.date() == local_end.date():
        start_zone = local_start.tzname() or zone.key
        clock_span = f"{local_start:%H:%M}-{end_clock}"
        if start_zone != zone_name:
            clock_span = f"{local_start:%H:%M} {start_zone}-{end_clock} {zone_name}"
        return f"{start_date}, {clock_span} {zone_name}"
    end_date = f"{local_end:%a} {local_end.day} {local_end:%b %Y}"
    return f"{start_date}, {local_start:%H:%M}-{end_date}, {end_clock} {zone_name}"


def utc_timestamp(value: datetime) -> str:
    """Serialize an aware datetime as fixed-width UTC YYYY-MM-DDTHH:MM:SS.ffffffZ."""
    _require_aware(value)
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
