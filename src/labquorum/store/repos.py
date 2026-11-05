"""Transactional booking and approval request repository operations."""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from labquorum.domain.timeutil import Clock


def propose_booking(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    person_id: str,
    instrument_id: str,
    project_id: str,
    start: datetime,
    end: datetime,
    clock: Clock,
    hold_minutes: int = 10,
) -> dict[str, Any]:
    raise NotImplementedError


def revise_request(  # noqa: PLR0913
    connection: sqlite3.Connection,
    request_id: str,
    *,
    revision: int,
    start: datetime,
    end: datetime,
    project_id: str,
    clock: Clock,
) -> dict[str, Any]:
    raise NotImplementedError


def commit_booking(  # noqa: PLR0913
    connection: sqlite3.Connection,
    request_id: str,
    revision: int,
    content_hash: str,
    decision: Mapping[str, Any],
    *,
    clock: Clock,
) -> dict[str, Any]:
    raise NotImplementedError


def decline_request(
    connection: sqlite3.Connection,
    request_id: str,
    revision: int,
    reason: str,
    *,
    clock: Clock,
) -> dict[str, Any]:
    raise NotImplementedError


def cancel_booking(
    connection: sqlite3.Connection,
    booking_id: str,
    *,
    actor: str,
    clock: Clock,
) -> dict[str, Any]:
    raise NotImplementedError


def get_request(
    connection: sqlite3.Connection,
    request_id: str,
    *,
    clock: Clock,
) -> dict[str, Any]:
    raise NotImplementedError


def list_bookings(
    connection: sqlite3.Connection,
    *,
    clock: Clock,
    instrument_id: str | None = None,
) -> list[dict[str, Any]]:
    raise NotImplementedError


def lab_state(connection: sqlite3.Connection, *, clock: Clock) -> dict[str, Any]:
    raise NotImplementedError
