"""Regression tests for the offline P3 requester and setup fixes."""

from __future__ import annotations

import tomllib
from datetime import UTC, date, datetime
from pathlib import Path

from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.server import create_runtime
from labquorum.provisioning import setup_runtime
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
START = "2026-11-06T15:45:00+05:30"
END = "2026-11-06T16:45:00+05:30"


def _seed_database(path: Path) -> None:
    connection = init_database(path)
    try:
        seed_demo(connection, date(2026, 11, 6), clock=FixedClock(NOW))
    finally:
        connection.close()


def _command(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def test_C_01_proposal_uses_the_supplied_ledger_requester_handle(tmp_path: Path) -> None:
    database = tmp_path / "requester.sqlite"
    _seed_database(database)
    propose = create_runtime("proposer", database, clock=FixedClock(NOW)).tool_method(
        "propose_booking"
    )

    unknown = propose(
        requester_handle="unregistered-user",
        instrument_id="INS-01",
        project_id="identity-check",
        start=START,
        end=END,
    )
    assert unknown["error"] == "UNKNOWN_REQUESTER"
    assert "ask the lab admin" in unknown["message"].casefold()

    proposal = propose(
        requester_handle="DARVED2305",
        instrument_id="INS-01",
        project_id="identity-check",
        start=START,
        end=END,
    )
    assert proposal["requester_handle"] == "darved2305"
    assert proposal["requester_display_name"] == "Darshan Ved (student)"


def test_I_10_demo_seed_adds_synthetic_darshan_and_valid_ins01_training(
    tmp_path: Path,
) -> None:
    database = tmp_path / "seed.sqlite"
    connection = init_database(database)
    try:
        first = seed_demo(connection, date(2026, 11, 6), clock=FixedClock(NOW))
        second = seed_demo(connection, date(2026, 11, 6), clock=FixedClock(NOW))
        person = connection.execute(
            "SELECT display_name, role FROM person WHERE id = ?", ("darved2305",)
        ).fetchone()
        training = connection.execute(
            "SELECT expires_at_utc FROM training WHERE person_id = ? AND instrument_id = ?",
            ("darved2305", "INS-01"),
        ).fetchone()
        people_count = int(connection.execute("SELECT COUNT(*) FROM person").fetchone()[0])
        training_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM training WHERE person_id = ? AND instrument_id = ?",
                ("darved2305", "INS-01"),
            ).fetchone()[0]
        )
    finally:
        connection.close()

    assert first["seeded"] is True
    assert second["seeded"] is False
    assert person is not None
    assert person["display_name"] == "Darshan Ved (student)"
    assert person["role"] == "student"
    assert training is not None
    assert training["expires_at_utc"] > "2026-11-06T10:15:00.000000Z"
    assert people_count == 6
    assert training_count == 1


def test_C_04_setup_writes_labops_requester_and_reply_instructions(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    command = _command(root / "venv" / "Scripts" / "lq-mcp.exe")
    setup_runtime(root, command_path=command, codex_home=tmp_path / "source-codex-home")
    instructions = (root / "agents" / "labops" / "AGENTS.md").read_text(encoding="utf-8")
    normalized = instructions.casefold()

    for required in (
        "switch sender's platform handle as requester_handle",
        "never ask humans to vouch for training",
        "training is checked inside propose_booking and policy_check",
        "training_required",
        "expires_at",
        "approval-card answers",
        "a7 1",
        "weekday, date, time, and zone",
        "request id",
        "not booked yet; @pi-desk will review",
    ):
        assert required in normalized


def test_C_04_runtime_codex_toml_approves_only_noncommit_labquorum_tools(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    command = _command(root / "venv" / "Scripts" / "lq-mcp.exe")
    setup_runtime(root, command_path=command, codex_home=tmp_path / "source-codex-home")
    config_path = root / "codex-home" / "config.toml"

    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)

    server = config["mcp_servers"]["labquorum"]
    assert server["default_tools_approval_mode"] == "approve"
    assert set(server["tools"]) == {"commit_booking"}
    assert server["tools"]["commit_booking"]["approval_mode"] == "prompt"
