"""Scripted two-persona LabQuorum demo recorder."""

from __future__ import annotations

from typing import Any


class DemoRecorder:
    """Recorder implementation scaffold used by the test-first commit."""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def run(self) -> dict[str, Any]:
        raise NotImplementedError("Demo recorder is not implemented yet.")


def inject_caption(page: Any, caption: str, *, audit_output: str | None = None) -> None:
    """Inject the fixed caption banner and optional audit output overlay."""
    raise NotImplementedError("Caption overlay is not implemented yet.")


def select_student_credentials(config: Any, selector: str) -> Any:
    """Resolve a configured student by persona key or Mattermost username."""
    raise NotImplementedError("Student persona selection is not implemented yet.")
