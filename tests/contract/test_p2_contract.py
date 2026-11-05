"""P2 MCP profile and contract behavior."""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent
from syrupy.assertion import SnapshotAssertion

from labquorum.cli.main import _inspect_agent_configs
from labquorum.domain.errors import ErrorCode
from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.profiles import Profile, profile_for_agent, tool_names_for_profile
from labquorum.mcp.server import create_runtime
from labquorum.mcp.tools_lab import MAX_RESULT_BYTES
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo

ROOT = Path(__file__).resolve().parents[2]
REPLAY_PATH = ROOT / "tests" / "fixtures" / "p2_replay.json"
REPLAY_NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
PROBE_START = "2026-11-09T10:00:00+05:30"
PROBE_END = "2026-11-09T11:00:00+05:30"


def _seed_database(path: Path) -> None:
    connection = init_database(path)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS labquorum_test_marker (marker TEXT PRIMARY KEY)"
        )
        connection.execute(
            "INSERT OR IGNORE INTO labquorum_test_marker(marker) VALUES (?)",
            ("p3-certify-only",),
        )
        seed_demo(
            connection,
            date(2026, 11, 6),
            clock=FixedClock(REPLAY_NOW),
        )
    finally:
        connection.close()


@asynccontextmanager
async def _connect(profile: str, database: Path) -> AsyncIterator[ClientSession]:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "labquorum.mcp.server",
            "--profile",
            profile,
            "--db",
            str(database),
            *(["--binding", "certify"] if profile == "approver" else []),
        ],
        cwd=ROOT,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        yield session


async def _list_tools(profile: str, database: Path) -> list[dict[str, Any]]:
    async with _connect(profile, database) as session:
        listing = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in sorted(listing.tools, key=lambda item: item.name)
        ]


def _payload(result: Any) -> dict[str, Any]:
    if result.structuredContent is not None:
        return dict(result.structuredContent)
    text = "\n".join(block.text for block in result.content if hasattr(block, "text"))
    parsed = json.loads(text)
    assert isinstance(parsed, dict)
    return parsed


def test_C_01_tool_names_descriptions_and_schemas_match_profile_snapshots(
    tmp_path: Path,
    snapshot: SnapshotAssertion,
) -> None:
    database = tmp_path / "snapshot.sqlite"
    _seed_database(database)
    actual = {
        profile: asyncio.run(_list_tools(profile, database))
        for profile in ("proposer", "approver", "unavailable")
    }
    assert actual == snapshot


def test_C_02_only_approver_has_binding_commit_tools() -> None:
    proposer = tool_names_for_profile(Profile.PROPOSER)
    approver = tool_names_for_profile(Profile.APPROVER)
    assert "commit_booking" in approver
    assert not any(name.startswith("commit_") for name in proposer)


def test_C_03_unavailable_profile_exposes_only_capability_status() -> None:
    assert tool_names_for_profile(Profile.UNAVAILABLE) == ("capability_status",)
    assert "commit_booking" not in tool_names_for_profile(Profile.PROPOSER)


def test_C_09_agent_folder_maps_to_its_expected_mcp_profile(
    tmp_path: Path,
    monkeypatch,
) -> None:
    assert profile_for_agent("labops") is Profile.PROPOSER
    assert profile_for_agent("pi-desk") is Profile.APPROVER
    assert profile_for_agent("scout") is Profile.UNAVAILABLE
    assert profile_for_agent("analyst") is Profile.UNAVAILABLE
    agents_dir = tmp_path / "agents"
    labops_dir = agents_dir / "labops"
    labops_dir.mkdir(parents=True)
    (labops_dir / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "labquorum": {
                        "command": "uv",
                        "args": ["run", "lq-mcp", "--profile", "proposer"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    original_which = shutil.which
    monkeypatch.setattr(
        shutil,
        "which",
        lambda name: sys.executable if name == "uv" else original_which(name),
    )
    findings = _inspect_agent_configs(agents_dir)
    assert any(finding["code"] == "MCP_CONFIG_RESOLVED" for finding in findings)


def test_C_10_error_enum_is_shared_with_p2_documentation() -> None:
    document = ROOT / "docs" / "build" / "p2-mcp.md"
    assert document.is_file()
    contents = document.read_text(encoding="utf-8")
    for code in ErrorCode:
        assert f"| {code.value} |" in contents


def test_C_13_commit_schema_and_transaction_require_the_full_decision(
    tmp_path: Path,
) -> None:
    database = tmp_path / "decision.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("approver", database) as approver:
            listing = await approver.list_tools()
            commit_tool = next(tool for tool in listing.tools if tool.name == "commit_booking")
            properties = commit_tool.inputSchema["properties"]
            expected_arguments = {
                "request_id",
                "revision",
                "content_hash",
                "action",
                "instrument_id",
                "instrument_name",
                "requester_handle",
                "requester_display_name",
                "project_untrusted_text",
                "start_local",
                "end_local",
                "start_utc",
                "end_utc",
            }
            assert set(commit_tool.inputSchema["required"]) == expected_arguments
            assert set(properties) == expected_arguments
            assert "decision" not in properties
            assert properties["project_untrusted_text"]["maxLength"] == 120

        async with _connect("proposer", database) as proposer:
            proposed = _payload(
                await proposer.call_tool(
                    "propose_booking",
                    {
                        "requester_handle": "maya",
                        "instrument_id": "INS-01",
                        "project_id": "p2-contract",
                        "start": PROBE_START,
                        "end": PROBE_END,
                    },
                )
            )
        async with _connect("approver", database) as approver:
            request = _payload(
                await approver.call_tool("get_request", {"request_id": proposed["request_id"]})
            )
            encoded_args = json.dumps(
                request,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            assert len(encoded_args) < 900
            assert set(proposed) == set(request)
            assert (
                "Fri 6 Nov 2026" in request["start_local"]
                or "Mon 9 Nov 2026" in request["start_local"]
            )
            tampered = dict(request)
            tampered["project_untrusted_text"] = "tampered-project"
            tampered = _payload(
                await approver.call_tool(
                    "commit_booking",
                    tampered,
                )
            )
            assert tampered["error"] == "DECISION_MISMATCH"

    asyncio.run(exercise())


def test_C_14_tool_results_are_compact_and_below_the_size_cap(tmp_path: Path) -> None:
    database = tmp_path / "compact.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("proposer", database) as session:
            result = _payload(await session.call_tool("lab_state", {}))
        encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        assert len(encoded) <= MAX_RESULT_BYTES

    asyncio.run(exercise())


def test_U_B11_tool_rejects_natural_language_time_with_needs_iso_datetime(
    tmp_path: Path,
) -> None:
    database = tmp_path / "datetime.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("proposer", database) as session:
            result = _payload(
                await session.call_tool(
                    "check_availability",
                    {
                        "instrument_id": "INS-01",
                        "start": "Thursday 2 to 5 pm",
                        "end": PROBE_END,
                    },
                )
            )
            assert result["error"] == "NEEDS_ISO_DATETIME"

    asyncio.run(exercise())


def test_U_B02_conflict_tool_names_owner_and_nearest_same_length_slot(
    tmp_path: Path,
) -> None:
    database = tmp_path / "conflict.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("proposer", database) as session:
            state = _payload(await session.call_tool("lab_state", {}))
            instrument = next(
                item for item in state["instruments"] if item["instrument_id"] == "INS-01"
            )
            instrument_timezone = ZoneInfo(instrument["timezone"])
            seeded_booking = next(
                item
                for item in state["bookings"]
                if item["instrument_id"] == "INS-01" and item["requester"] == "lena"
            )
            booking_day = (
                datetime.fromisoformat(seeded_booking["start_utc"].replace("Z", "+00:00"))
                .astimezone(instrument_timezone)
                .date()
            )
            requested_start = datetime.combine(booking_day, time(14, 0), tzinfo=instrument_timezone)
            requested_end = datetime.combine(booking_day, time(15, 0), tzinfo=instrument_timezone)
            result = _payload(
                await session.call_tool(
                    "propose_booking",
                    {
                        "requester_handle": "maya",
                        "instrument_id": "INS-01",
                        "project_id": "conflict-check",
                        "start": requested_start.isoformat(),
                        "end": requested_end.isoformat(),
                    },
                )
            )
        assert result["error"] == "CONFLICT"
        assert result["details"]["conflicting_booking"]["owner"] == "lena"
        assert result["details"]["conflicting_booking"]["owner_name"] == "Dr. Lena Okafor"
        nearest_slot = result["details"]["nearest_free_slot"]
        nearest_start = datetime.fromisoformat(
            nearest_slot["start_utc"].replace("Z", "+00:00")
        ).astimezone(instrument_timezone)
        nearest_end = datetime.fromisoformat(
            nearest_slot["end_utc"].replace("Z", "+00:00")
        ).astimezone(instrument_timezone)
        assert (nearest_start.date(), nearest_start.time()) == (booking_day, time(15, 45))
        assert (nearest_end.date(), nearest_end.time()) == (booking_day, time(16, 45))
        assert nearest_end - nearest_start == requested_end - requested_start

    asyncio.run(exercise())


def test_I_02_stdio_lists_profiles_and_calls_each_read_tool_on_seed(tmp_path: Path) -> None:
    database = tmp_path / "stdio.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("proposer", database) as proposer:
            names = {tool.name for tool in (await proposer.list_tools()).tools}
            assert names == set(tool_names_for_profile("proposer"))
            instruments = _payload(await proposer.call_tool("list_instruments", {}))
            assert "instruments" in instruments
            availability = _payload(
                await proposer.call_tool(
                    "check_availability",
                    {"instrument_id": "INS-01", "start": PROBE_START, "end": PROBE_END},
                )
            )
            assert availability["available"] is True
            assert "bookings" in _payload(await proposer.call_tool("lab_state", {}))

        async with _connect("approver", database) as approver:
            names = {tool.name for tool in (await approver.list_tools()).tools}
            assert names == set(tool_names_for_profile("approver"))
            request = _payload(await approver.call_tool("get_request", {"request_id": "AR-0041"}))
            assert request["status"] == "committed"
            policy = _payload(await approver.call_tool("policy_check", {"request_id": "AR-0041"}))
            assert "checks" in policy
            assert "bookings" in _payload(await approver.call_tool("lab_state", {}))

        async with _connect("unavailable", database) as unavailable:
            names = {tool.name for tool in (await unavailable.list_tools()).tools}
            assert names == set(tool_names_for_profile("unavailable"))
            status = _payload(await unavailable.call_tool("capability_status", {}))
            assert status["unavailable_capabilities"]

    asyncio.run(exercise())


def test_I_03_commit_from_proposer_is_an_unknown_tool(tmp_path: Path) -> None:
    database = tmp_path / "unknown-tool.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("proposer", database) as session:
            try:
                result = await session.call_tool("commit_booking", {})
            except Exception as exc:
                message = str(exc).casefold()
                assert "commit_booking" in message
                assert "unknown" in message or "not found" in message or "not registered" in message
            else:
                assert result.isError is True
                text = "\n".join(
                    block.text for block in result.content if isinstance(block, TextContent)
                )
                assert "commit_booking" in text.casefold()

    asyncio.run(exercise())


def test_I_12_recorded_tool_sequence_replays_identically_on_fresh_seeds(
    tmp_path: Path,
) -> None:
    recording = json.loads(REPLAY_PATH.read_text(encoding="utf-8"))
    assert isinstance(recording, dict)
    provenance = recording["provenance"]
    assert provenance["transport"] == "MCP stdio"
    assert provenance["seed"]["anchor_date"] == "2026-11-06"
    assert provenance["clock_now"] == "2026-11-05T12:00:00Z"
    sequence = recording["steps"]
    assert isinstance(sequence, list)

    def replay(database: Path) -> list[dict[str, Any]]:
        _seed_database(database)
        runtimes = {
            profile: create_runtime(
                profile,
                database,
                clock=FixedClock(REPLAY_NOW),
            )
            for profile in ("proposer", "approver")
        }
        results: list[dict[str, Any]] = []
        context: dict[str, Any] = {"results": results}
        for step in sequence:
            arguments: dict[str, Any] = {}
            for name, value in step["arguments"].items():
                if isinstance(value, dict) and set(value) == {"$ref"}:
                    reference = value["$ref"].split(".")
                    resolved: Any = context
                    for part in reference:
                        resolved = (
                            resolved[int(part)] if isinstance(resolved, list) else resolved[part]
                        )
                    arguments[name] = resolved
                else:
                    arguments[name] = value
            result = runtimes[step["profile"]].tool_method(step["tool"])(**arguments)
            assert "error" not in result
            results.append(result)
        return results

    expected = [step["expected"] for step in sequence]
    assert replay(tmp_path / "first.sqlite") == expected
    assert replay(tmp_path / "second.sqlite") == expected


def test_U_G01_rate_guard_is_wired_to_mcp_profile_calls(tmp_path: Path) -> None:
    database = tmp_path / "rate.sqlite"
    _seed_database(database)

    async def exercise() -> None:
        async with _connect("proposer", database) as session:
            for _ in range(30):
                result = _payload(await session.call_tool("list_instruments", {}))
                assert "error" not in result
            limited = _payload(await session.call_tool("list_instruments", {}))
            assert limited["error"] == "RATE_LIMITED"

    asyncio.run(exercise())
