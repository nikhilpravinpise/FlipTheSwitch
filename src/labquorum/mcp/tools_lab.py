"""P2 MCP tool contracts and compact result helpers."""

from __future__ import annotations

MAX_RESULT_BYTES = 8_192


def compact_result(value: object) -> dict[str, object]:
    """Return a bounded compact JSON-ready tool result."""
    raise NotImplementedError("P2 compact tool results are not implemented yet")
