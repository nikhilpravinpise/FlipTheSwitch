"""P3 gate implementation; helpers begin as red-test stubs."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


def error_code(payload: Any, text: str) -> str | None:
    """Extract a dedicated error code from an MCP response."""
    raise NotImplementedError


def json_pointer(document: Any, pointer: str) -> Any:
    """Resolve a JSON Pointer in an MCP response."""
    raise NotImplementedError


def extract_tool_names(listing: Any) -> set[str]:
    """Read tool names from an official MCP client listing."""
    raise NotImplementedError


def template_mutations(template: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Create the five deliberately invalid lint mutations."""
    raise NotImplementedError


def server_arguments(profile: str, database: Path) -> list[str]:
    """Build the lq-mcp command arguments for a profile and ledger."""
    raise NotImplementedError


def binding_tool_exposure_issue(tool_names: set[str], *, expected: bool) -> str | None:
    """Check whether commit_booking exposure matches the requested mode."""
    raise NotImplementedError
