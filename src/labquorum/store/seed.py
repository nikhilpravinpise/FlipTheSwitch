"""Anchor-relative demo seed for the booking-only ledger."""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any

from labquorum.domain.timeutil import Clock


def seed_demo(
    connection: sqlite3.Connection,
    anchor_date: date,
    *,
    clock: Clock | None = None,
) -> dict[str, Any]:
    raise NotImplementedError
