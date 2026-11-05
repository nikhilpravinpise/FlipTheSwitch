"""Record the P2 replay fixture from a real MCP stdio client/server session."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager, closing
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.server import _configure_logging, create_server
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "p2_replay.json"
CLOCK_NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
CLOCK_TEXT = "2026-11-05T12:00:00Z"
ANCHOR_DATE = date(2026, 11, 6)
COMMIT_FIELDS = (
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
)


@asynccontextmanager
async def _connect(profile: str, database: Path) -> AsyncIterator[ClientSession]:
    script = Path(__file__).resolve()
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            str(script),
            "--serve",
            "--profile",
            profile,
            "--db",
            str(database),
        ],
        cwd=ROOT,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        yield session


def _payload(result: Any) -> dict[str, Any]:
    if result.structuredContent is not None:
        return dict(result.structuredContent)
    text = "\n".join(block.text for block in result.content if hasattr(block, "text"))
    value = json.loads(text)
    if not isinstance(value, dict):
        raise TypeError("MCP tool result was not a JSON object")
    return value


def _step_specs() -> list[dict[str, Any]]:
    return [
        {
            "profile": "proposer",
            "tool": "propose_booking",
            "arguments": {
                "instrument_id": "INS-01",
                "project_id": "I-12 recorded stdio replay",
                "start": "2026-11-09T10:00:00+05:30",
                "end": "2026-11-09T11:00:00+05:30",
            },
        },
        {
            "profile": "approver",
            "tool": "get_request",
            "arguments": {"request_id": {"$ref": "results.0.request_id"}},
        },
        {
            "profile": "approver",
            "tool": "policy_check",
            "arguments": {"request_id": {"$ref": "results.0.request_id"}},
        },
        {
            "profile": "approver",
            "tool": "commit_booking",
            "arguments": {field: {"$ref": f"results.1.{field}"} for field in COMMIT_FIELDS},
        },
    ]


async def _record_session(database: Path) -> list[dict[str, Any]]:
    recorded: list[dict[str, Any]] = []
    context: dict[str, Any] = {"results": []}
    async with AsyncExitStack() as stack:
        sessions = {
            profile: await stack.enter_async_context(_connect(profile, database))
            for profile in ("proposer", "approver")
        }
        for specification in _step_specs():
            arguments: dict[str, Any] = {}
            for name, value in specification["arguments"].items():
                if isinstance(value, dict) and set(value) == {"$ref"}:
                    resolved: Any = context
                    for part in value["$ref"].split("."):
                        resolved = (
                            resolved[int(part)] if isinstance(resolved, list) else resolved[part]
                        )
                    arguments[name] = resolved
                else:
                    arguments[name] = value
            result = _payload(
                await sessions[specification["profile"]].call_tool(specification["tool"], arguments)
            )
            if "error" in result:
                raise RuntimeError(f"Could not record {specification['tool']}: {result['error']}")
            recorded.append({**specification, "expected": result})
            context["results"].append(result)
    return recorded


def _serve(profile: str, database: Path) -> int:
    _configure_logging()
    server = create_server(profile, database, clock=FixedClock(CLOCK_NOW))
    asyncio.run(server.run_stdio_async())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--profile", choices=("proposer", "approver"))
    parser.add_argument("--db", type=Path)
    parser.add_argument("--output", type=Path, default=FIXTURE)
    arguments = parser.parse_args(argv)
    if arguments.serve:
        if arguments.profile is None or arguments.db is None:
            parser.error("--serve requires --profile and --db")
        return _serve(arguments.profile, arguments.db)

    with tempfile.TemporaryDirectory(prefix="labquorum-p2-record-") as temporary:
        database = Path(temporary) / "recording.sqlite"
        with closing(init_database(database)) as connection:
            seed_result = seed_demo(
                connection,
                ANCHOR_DATE,
                clock=FixedClock(CLOCK_NOW),
            )
        steps = asyncio.run(_record_session(database))
    fixture = {
        "provenance": {
            "transport": "MCP stdio",
            "client": "mcp.client.stdio.stdio_client and ClientSession",
            "server": "labquorum.mcp.server.create_server",
            "recorder": "scripts/dev/record_p2_replay.py",
            "recorded_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "clock_now": CLOCK_TEXT,
            "seed": {"anchor_date": ANCHOR_DATE.isoformat(), "result": seed_result},
        },
        "steps": steps,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Recorded {len(steps)} MCP stdio calls in {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
