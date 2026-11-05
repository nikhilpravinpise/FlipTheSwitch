"""FastMCP stdio server entry point for LabQuorum booking tools."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sqlite3
import sys
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path

import structlog
from mcp.server.fastmcp import FastMCP
from structlog import make_filtering_bound_logger
from structlog._output import PrintLoggerFactory
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock
from labquorum.mcp.profiles import TOOL_DESCRIPTIONS, Profile, tool_names_for_profile
from labquorum.mcp.tools_lab import LabTools
from labquorum.store.db import default_database_path, open_database

# Verified with MCP 1.30.0 installed source: FastMCP constructor and tool decorator at
# .venv/Lib/site-packages/mcp/server/fastmcp/server.py:156-185,462-495; stdio runner at :769-775.


def create_runtime(
    profile: str | Profile,
    database_path: Path | None = None,
    *,
    clock: Clock | None = None,
) -> LabTools:
    """Build a profile-bound runtime, with an injectable clock for deterministic replay."""
    try:
        resolved_profile = profile if isinstance(profile, Profile) else Profile(profile)
    except ValueError as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            message=f"Unknown LabQuorum MCP profile: {profile!s}.",
        ) from exc
    return LabTools(resolved_profile, database_path, clock=clock)


def create_server(
    profile: str | Profile,
    database_path: Path | None = None,
    *,
    clock: Clock | None = None,
) -> FastMCP:
    """Create a FastMCP server named labquorum with only this profile's tools."""
    runtime = create_runtime(profile, database_path, clock=clock)
    server = FastMCP(
        name="labquorum",
        instructions=(
            "LabQuorum booking ledger. Tool availability is profile-scoped. Datetimes must be "
            "ISO 8601 with an explicit offset. Binding commits must echo the complete current "
            "decision from get_request."
        ),
        log_level="ERROR",
    )
    for name in tool_names_for_profile(runtime.profile):
        server.tool(
            name=name,
            description=TOOL_DESCRIPTIONS[name],
            structured_output=True,
        )(runtime.tool_method(name))
    return server


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lq-mcp",
        description="Run one profile-scoped LabQuorum MCP server over stdio.",
    )
    parser.add_argument(
        "--profile",
        choices=[profile.value for profile in Profile],
        required=True,
        help="Agent capability profile for this MCP process.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=default_database_path(),
        help="SQLite ledger path (defaults to the lq CLI ledger path).",
    )
    return parser


def _configure_logging() -> None:
    structlog.configure(
        processors=[
            TimeStamper(fmt="iso", utc=True),
            add_log_level,
            JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=make_filtering_bound_logger(logging.INFO),
        logger_factory=PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.ERROR,
        format="%(message)s",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Start an MCP stdio server without writing application output to stdout."""
    args = _parser().parse_args(argv)
    _configure_logging()
    logger = structlog.get_logger("labquorum.mcp.server")
    try:
        with closing(open_database(args.db)) as connection:
            connection.execute("SELECT 1").fetchone()
        server = create_server(args.profile, args.db)
        logger.info("server_started", profile=args.profile, database=str(args.db.resolve()))
        asyncio.run(server.run_stdio_async())
        return 0
    except (LabQuorumError, OSError, sqlite3.Error) as error:
        logger.error(
            "server_start_failed",
            profile=args.profile,
            database=str(args.db),
            error_code=getattr(getattr(error, "code", None), "value", "INVALID_ARGUMENT"),
            message=str(error),
        )
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
