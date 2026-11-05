"""Append-only audit event hashing and verification."""

from __future__ import annotations

import sqlite3
from typing import Any

from labquorum.domain.timeutil import Clock


def append_event(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    actor: str,
    tool: str,
    args: dict[str, Any],
    result: dict[str, Any],
    clock: Clock,
) -> int:
    raise NotImplementedError


def verify(connection: sqlite3.Connection) -> int | None:
    raise NotImplementedError


def tail(connection: sqlite3.Connection, *, limit: int = 20) -> list[dict[str, Any]]:
    raise NotImplementedError
