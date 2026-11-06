"""Student-facing reply material: conflicts carry everything LabOps must say."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import yaml

from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.server import create_runtime
from labquorum.provisioning import setup_runtime
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
# With anchor 2026-11-06 and this clock, the demo seed places Lena's committed INS-01 booking
# BK-0041 on Sat 7 Nov 2026, 14:00-15:30 IST (08:30-10:00 UTC).
CONFLICT_START = "2026-11-07T14:00:00+05:30"
CONFLICT_END = "2026-11-07T15:00:00+05:30"


def _seeded(tmp_path: Path) -> Path:
    database = tmp_path / "reply-clarity.sqlite"
    connection = init_database(database)
    try:
        seed_demo(connection, date(2026, 11, 6), clock=FixedClock(NOW))
    finally:
        connection.close()
    return database


def _assert_conflict_reply_material(details: dict[str, object]) -> None:
    conflicting = details["conflicting_booking"]
    assert isinstance(conflicting, dict)
    assert conflicting["owner_name"] == "Dr. Lena Okafor"
    assert {"start_utc", "end_utc", "summary"} <= set(conflicting)
    assert conflicting["start_utc"] == "2026-11-07T08:30:00.000000Z"
    assert conflicting["end_utc"] == "2026-11-07T10:00:00.000000Z"
    assert conflicting["summary"] == "Sat 7 Nov 2026, 14:00-15:30 IST"

    assert "reply_summary" in details
    summary = details["reply_summary"]
    assert isinstance(summary, str)
    assert summary == (
        "INS-01 (Plate reader (Tecan Spark)) is not available for Sat 7 Nov 2026, "
        "14:00-15:00 IST: it conflicts with Dr. Lena Okafor's committed booking BK-0041, "
        "Sat 7 Nov 2026, 14:00-15:30 IST. Nearest free 60-minute slot: "
        "Sat 7 Nov 2026, 15:45-16:45 IST. Nothing has been booked."
    )


def test_U_B02_availability_conflict_names_interval_and_reply_summary(tmp_path: Path) -> None:
    proposer = create_runtime("proposer", _seeded(tmp_path), clock=FixedClock(NOW))

    result = proposer.tool_method("check_availability")(
        requester_handle="darved2305",
        instrument_id="INS-01",
        start=CONFLICT_START,
        end=CONFLICT_END,
    )

    assert result["available"] is False
    assert result["error"] == "CONFLICT"
    _assert_conflict_reply_material(result["details"])


def test_U_B02_proposal_conflict_names_interval_and_reply_summary(tmp_path: Path) -> None:
    proposer = create_runtime("proposer", _seeded(tmp_path), clock=FixedClock(NOW))

    result = proposer.tool_method("propose_booking")(
        requester_handle="darved2305",
        instrument_id="INS-01",
        project_id="reply clarity",
        start=CONFLICT_START,
        end=CONFLICT_END,
    )

    assert result["error"] == "CONFLICT"
    _assert_conflict_reply_material(result["details"])


def test_C_04_labops_reply_contract_names_requester_and_proposal_is_not_a_reservation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    command = root / "venv" / "Scripts" / "lq-mcp.exe"
    command.parent.mkdir(parents=True, exist_ok=True)
    command.touch()
    setup_runtime(root, command_path=command, codex_home=tmp_path / "source-codex-home")
    labops = (root / "agents" / "labops" / "AGENTS.md").read_text(encoding="utf-8")
    template = yaml.safe_load(
        (root / "switch" / "labquorum.template.yaml").read_text(encoding="utf-8")
    )
    template_labops = next(
        agent["instructions"] for agent in template["agents"] if agent["name"] == "labops"
    )

    for instructions in (labops, template_labops):
        normalized = instructions.casefold()
        assert "requester_display_name" in normalized
        assert "reply_summary" in normalized
        assert "a proposal is not a reservation" in normalized
        assert "not booked yet; @pi-desk will review" in normalized
