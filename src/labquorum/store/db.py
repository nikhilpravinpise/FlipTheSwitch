"""SQLite connections, schema versioning, and journal selection."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from labquorum.domain.errors import ErrorCode, LabQuorumError

SCHEMA_VERSION = 2
BUSY_TIMEOUT_MS = 5_000


@dataclass(frozen=True)
class DatabaseInfo:
    """Observed SQLite library and active ledger schema settings."""

    sqlite_version: str
    journal_mode: str
    schema_version: int


@contextmanager
def immediate_transaction(connection: sqlite3.Connection) -> Generator[None, None, None]:
    """Take SQLite's writer lock before reading any rows used by a mutation."""
    if connection.in_transaction:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Nested ledger transactions are not supported."
        )
    connection.execute("BEGIN IMMEDIATE")
    completed = False
    try:
        yield
        completed = True
    finally:
        if connection.in_transaction:
            if completed:
                connection.commit()
            else:
                connection.rollback()


def select_journal_mode(sqlite_version: tuple[int, ...]) -> str:
    """Use WAL only after the SQLite WAL-reset fix is present."""
    # SQLite documents the WAL reset bug and its fixed releases at:
    # https://sqlite.org/wal.html#the_wal_reset_bug
    if sqlite_version >= (3, 51, 3):
        return "WAL"
    return "DELETE"


def default_database_path() -> Path:
    """Return the per-user platform data path for a new ledger."""
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        root = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return root / "LabQuorum" / "ledger.sqlite"
    data_home = os.environ.get("XDG_DATA_HOME")
    root = Path(data_home) if data_home else Path.home() / ".local" / "share"
    return root / "labquorum" / "ledger.sqlite"


def _normalized_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def onedrive_warning(path: Path) -> str | None:
    """Return a doctor-ready warning when a ledger path is under OneDrive."""
    candidate = _normalized_path(path)
    if any(part.casefold().startswith("onedrive") for part in candidate.parts):
        return f"Ledger path is under OneDrive: {candidate}"
    configured_roots = (
        os.environ.get("ONEDRIVE"),
        os.environ.get("ONEDRIVECONSUMER"),
        os.environ.get("ONEDRIVECOMMERCIAL"),
    )
    for configured in configured_roots:
        if not configured:
            continue
        root = _normalized_path(Path(configured))
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        return f"Ledger path is under OneDrive: {candidate}"
    return None


def _reject_onedrive(path: Path) -> None:
    warning = onedrive_warning(path)
    if warning is not None:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, warning, {"path": str(path)})


def _connect(path: Path) -> sqlite3.Connection:
    _reject_onedrive(path)
    connection = sqlite3.connect(
        _normalized_path(path),
        timeout=BUSY_TIMEOUT_MS / 1_000,
        isolation_level=None,
    )
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        requested_mode = select_journal_mode(sqlite3.sqlite_version_info)
        actual_mode = str(
            connection.execute(f"PRAGMA journal_mode = {requested_mode}").fetchone()[0]
        )
        if actual_mode.casefold() != requested_mode.casefold():
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                f"SQLite selected journal mode {actual_mode}, expected {requested_mode}.",
            )
    except BaseException:
        connection.close()
        raise
    return connection


def _schema_version(connection: sqlite3.Connection) -> int:
    try:
        rows = connection.execute("SELECT version FROM schema_version").fetchall()
    except sqlite3.DatabaseError as exc:
        raise LabQuorumError(
            ErrorCode.SCHEMA_VERSION_MISMATCH,
            "Ledger has no readable schema_version table.",
        ) from exc
    if len(rows) != 1:
        raise LabQuorumError(
            ErrorCode.SCHEMA_VERSION_MISMATCH,
            "Ledger must contain exactly one schema version row.",
        )
    return int(rows[0]["version"])


def _check_schema_version(connection: sqlite3.Connection) -> int:
    version = _schema_version(connection)
    if version != SCHEMA_VERSION:
        raise LabQuorumError(
            ErrorCode.SCHEMA_VERSION_MISMATCH,
            f"Ledger schema version {version} is unsupported; expected {SCHEMA_VERSION}.",
            {"found": version, "expected": SCHEMA_VERSION},
        )
    return version


def init_database(path: Path) -> sqlite3.Connection:
    """Create the schema or open the current schema without resetting data."""
    resolved = _normalized_path(path)
    _reject_onedrive(resolved)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = _connect(resolved)
    try:
        version_table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'"
        ).fetchone()
        if version_table is not None:
            versions = connection.execute("SELECT version FROM schema_version").fetchall()
            if versions and (len(versions) != 1 or int(versions[0]["version"]) != SCHEMA_VERSION):
                found = int(versions[0]["version"]) if versions else None
                raise LabQuorumError(
                    ErrorCode.SCHEMA_VERSION_MISMATCH,
                    f"Ledger schema version {found} is unsupported; expected {SCHEMA_VERSION}.",
                    {"found": found, "expected": SCHEMA_VERSION},
                )

        schema_path = resources.files("labquorum.store").joinpath("schema.sql")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        if (
            version_table is None
            or not connection.execute("SELECT 1 FROM schema_version").fetchone()
        ):
            connection.execute("INSERT INTO schema_version(version) VALUES (?)", (SCHEMA_VERSION,))
        _check_schema_version(connection)
    except BaseException:
        connection.close()
        raise
    return connection


def open_database(path: Path) -> sqlite3.Connection:
    """Open a current ledger and refuse missing or incompatible schema versions."""
    connection = _connect(path)
    try:
        _check_schema_version(connection)
    except LabQuorumError:
        connection.close()
        raise
    return connection


def database_info(connection: sqlite3.Connection) -> DatabaseInfo:
    """Report the SQLite build, actual journal mode, and stored schema version."""
    mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0]).casefold()
    return DatabaseInfo(
        sqlite_version=sqlite3.sqlite_version,
        journal_mode=mode,
        schema_version=_check_schema_version(connection),
    )
