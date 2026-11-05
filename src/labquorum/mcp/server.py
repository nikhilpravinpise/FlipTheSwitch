"""Profile-scoped LabQuorum MCP server entry point."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from labquorum.domain.timeutil import Clock


def create_runtime(
    profile: str,
    database_path: Path | None = None,
    *,
    clock: Clock | None = None,
) -> Any:
    """Build a deterministic profile runtime for MCP calls and replay tests."""
    raise NotImplementedError("P2 MCP runtime is not implemented yet")


def create_server(
    profile: str,
    database_path: Path | None = None,
    *,
    clock: Clock | None = None,
) -> Any:
    """Create the profile's FastMCP server."""
    raise NotImplementedError("P2 FastMCP server is not implemented yet")


def main(argv: list[str] | None = None) -> int:
    """Run the LabQuorum stdio server."""
    raise NotImplementedError("P2 MCP CLI is not implemented yet")


if __name__ == "__main__":
    raise SystemExit(main())
