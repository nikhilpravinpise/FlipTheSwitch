"""P6 backup and restore command safety."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from labquorum.cli import main as cli_module
from labquorum.domain.errors import ErrorCode
from labquorum.domain.timeutil import FixedClock
from labquorum.store.audit import verify
from labquorum.store.db import init_database, open_database
from labquorum.store.seed import seed_demo


def _seed_ledger(path: Path) -> None:
    connection = init_database(path)
    try:
        seed_demo(
            connection,
            date(2026, 11, 6),
            clock=FixedClock(datetime(2026, 11, 5, 12, 0, tzinfo=UTC)),
        )
    finally:
        connection.close()


def _run_cli(arguments: list[str]) -> int:
    try:
        return cli_module.main(arguments)
    except SystemExit as error:
        return int(error.code or 0)


def test_I_19_backup_restore_seeded_ledger_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    backup = tmp_path / "backup.sqlite"
    restored = tmp_path / "restored.sqlite"
    _seed_ledger(source)

    assert _run_cli(["backup", "--db", str(source), "--out", str(backup)]) == 0
    assert _run_cli(["restore", "--from", str(backup), "--db", str(restored)]) == 0

    with closing(open_database(source)) as source_connection:
        with closing(open_database(restored)) as restored_connection:
            assert verify(restored_connection) is None
            for table in ("person", "instrument", "approval_request", "booking", "audit_event"):
                source_count = source_connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                restored_count = restored_connection.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]
                assert restored_count == source_count


def test_I_19_restore_refuses_schema_version_mismatch_and_preserves_target(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    backup = tmp_path / "incompatible.sqlite"
    destination = tmp_path / "existing.sqlite"
    _seed_ledger(backup)
    _seed_ledger(destination)
    with sqlite3.connect(backup) as connection:
        connection.execute("UPDATE schema_version SET version = 999")
    original_bytes = destination.read_bytes()

    status = _run_cli(
        ["restore", "--from", str(backup), "--db", str(destination), "--force"]
    )

    assert status != 0
    assert ErrorCode.SCHEMA_VERSION_MISMATCH.value in capsys.readouterr().err
    assert destination.read_bytes() == original_bytes


def test_I_19_restore_refuses_overwrite_without_force(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    backup = tmp_path / "backup.sqlite"
    destination = tmp_path / "existing.sqlite"
    _seed_ledger(backup)
    _seed_ledger(destination)
    original_bytes = destination.read_bytes()

    status = _run_cli(["restore", "--from", str(backup), "--db", str(destination)])

    assert status != 0
    assert ErrorCode.INVALID_ARGUMENT.value in capsys.readouterr().err
    assert destination.read_bytes() == original_bytes


def test_I_19_restore_refuses_corrupt_file_and_preserves_target(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    corrupt = tmp_path / "corrupt.sqlite"
    corrupt.write_bytes(b"not a SQLite database")
    destination = tmp_path / "existing.sqlite"
    _seed_ledger(destination)
    original_bytes = destination.read_bytes()

    status = _run_cli(
        ["restore", "--from", str(corrupt), "--db", str(destination), "--force"]
    )

    assert status != 0
    assert ErrorCode.INVALID_ARGUMENT.value in capsys.readouterr().err
    assert destination.read_bytes() == original_bytes
