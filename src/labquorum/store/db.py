"""SQLite connections, schema versioning, and journal selection."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class DatabaseInfo:
    sqlite_version: str
    journal_mode: str
    schema_version: int


def select_journal_mode(sqlite_version: tuple[int, ...]) -> str:
    raise NotImplementedError


def default_database_path() -> Path:
    raise NotImplementedError


def onedrive_warning(path: Path) -> str | None:
    raise NotImplementedError


def init_database(path: Path) -> sqlite3.Connection:
    raise NotImplementedError


def open_database(path: Path) -> sqlite3.Connection:
    raise NotImplementedError


def database_info(connection: sqlite3.Connection) -> DatabaseInfo:
    raise NotImplementedError
