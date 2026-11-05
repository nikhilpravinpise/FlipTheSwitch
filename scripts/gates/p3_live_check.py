"""Live Switch checks; parsing helpers begin as red-test stubs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def directory_issue(directory: str | Path | None, runtime_root: Path) -> str | None:
    """Explain why a Switch agent directory is outside the allowed runtime root."""
    raise NotImplementedError


def addressing_mode(policy: Any) -> str:
    """Map Switch's serialized addressing policy to its chooser mode."""
    raise NotImplementedError
