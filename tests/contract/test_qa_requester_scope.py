"""Requester-scoped proposer tools: no tool may act as a different lab member."""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, date, datetime
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.server import create_runtime
from labquorum.store.db import init_database, open_database
from labquorum.store.seed import seed_demo

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
START = "2026-11-09T10:00:00+05:30"
END = "2026-11-09T11:00:00+05:30"
MAYA_COMMITTED_BOOKING = "BK-0040"


def _seeded(tmp_path: Path) -> Path:
    database = tmp_path / "requester-scope.sqlite"
    connection = init_database(database)
    try:
        seed_demo(connection, date(2026, 11, 6), clock=FixedClock(NOW))
    finally:
        connection.close()
    return database


def _booking_status(database: Path, booking_id: str) -> str:
    with open_database(database) as connection:
        row = connection.execute(
            "SELECT status FROM booking WHERE id = ?", (booking_id,)
        ).fetchone()
    assert row is not None
    return str(row["status"])


def _cancel_audit_events(database: Path) -> int:
    with open_database(database) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM audit_event WHERE tool = 'cancel_booking'"
        ).fetchone()
    return int(row[0])


def test_U_B12_student_cannot_cancel_another_members_committed_booking(tmp_path: Path) -> None:
    database = _seeded(tmp_path)
    proposer = create_runtime("proposer", database, clock=FixedClock(NOW))
    assert _booking_status(database, MAYA_COMMITTED_BOOKING) == "committed"

    result = proposer.tool_method("cancel_my_proposal")(
        requester_handle="darved2305",
        booking_id=MAYA_COMMITTED_BOOKING,
    )

    assert result["error"] == "NOT_FOUND"
    assert _booking_status(database, MAYA_COMMITTED_BOOKING) == "committed"
    assert _cancel_audit_events(database) == 0


def test_U_B12_owner_can_cancel_their_own_committed_booking_once(tmp_path: Path) -> None:
    database = _seeded(tmp_path)
    proposer = create_runtime("proposer", database, clock=FixedClock(NOW))
    cancel = proposer.tool_method("cancel_my_proposal")

    first = cancel(requester_handle="maya", booking_id=MAYA_COMMITTED_BOOKING)
    repeat = cancel(requester_handle="MAYA", booking_id=MAYA_COMMITTED_BOOKING)

    assert first == {"booking_id": MAYA_COMMITTED_BOOKING, "status": "cancelled"}
    assert repeat == first
    assert _booking_status(database, MAYA_COMMITTED_BOOKING) == "cancelled"
    assert _cancel_audit_events(database) == 1


def test_U_B12_cancel_rejects_an_unregistered_requester(tmp_path: Path) -> None:
    database = _seeded(tmp_path)
    proposer = create_runtime("proposer", database, clock=FixedClock(NOW))

    result = proposer.tool_method("cancel_my_proposal")(
        requester_handle="mallory",
        booking_id=MAYA_COMMITTED_BOOKING,
    )

    assert result["error"] == "UNKNOWN_REQUESTER"
    assert _booking_status(database, MAYA_COMMITTED_BOOKING) == "committed"


def test_U_B06_availability_checks_the_requesters_own_training(tmp_path: Path) -> None:
    database = _seeded(tmp_path)
    proposer = create_runtime("proposer", database, clock=FixedClock(NOW))
    check = proposer.tool_method("check_availability")

    untrained = check(requester_handle="jonas", instrument_id="INS-01", start=START, end=END)
    trained = check(requester_handle="maya", instrument_id="INS-01", start=START, end=END)

    assert untrained["available"] is False
    assert untrained["error"] == "TRAINING_REQUIRED"
    assert trained["available"] is True


def test_U_B06_availability_rejects_an_unregistered_requester(tmp_path: Path) -> None:
    database = _seeded(tmp_path)
    proposer = create_runtime("proposer", database, clock=FixedClock(NOW))

    result = proposer.tool_method("check_availability")(
        requester_handle="mallory", instrument_id="INS-01", start=START, end=END
    )

    assert result["error"] == "UNKNOWN_REQUESTER"


def test_C_01_requester_scoped_tools_require_requester_handle_over_stdio(tmp_path: Path) -> None:
    database = _seeded(tmp_path)

    async def required_arguments() -> dict[str, list[str]]:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "labquorum.mcp.server", "--profile", "proposer", "--db", str(database)],
            cwd=ROOT,
        )
        async with (
            stdio_client(parameters) as (read, write),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            tools = (await session.list_tools()).tools
        return {tool.name: list(tool.inputSchema.get("required", [])) for tool in tools}

    required = asyncio.run(required_arguments())

    for name in ("check_availability", "propose_booking", "cancel_my_proposal"):
        assert "requester_handle" in required[name], name
