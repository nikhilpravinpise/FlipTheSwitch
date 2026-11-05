"""Injected clocks and strict ISO 8601 time handling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        raise NotImplementedError


@dataclass
class FixedClock:
    instant: datetime

    def now(self) -> datetime:
        raise NotImplementedError

    def set(self, instant: datetime) -> None:
        raise NotImplementedError


def parse_iso_datetime(value: str, *, timezone: str | ZoneInfo | None = None) -> datetime:
    raise NotImplementedError


def format_interval(start: datetime, end: datetime, timezone: str | ZoneInfo) -> str:
    raise NotImplementedError


def utc_timestamp(value: datetime) -> str:
    raise NotImplementedError
