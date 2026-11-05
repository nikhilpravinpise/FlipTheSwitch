"""Evidence writer placeholder for the P4 harness."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_evidence(
    evidence_dir: Path,
    scenario: str,
    evidence: dict[str, Any],
) -> Path:
    raise NotImplementedError("Evidence writing is not implemented yet.")
