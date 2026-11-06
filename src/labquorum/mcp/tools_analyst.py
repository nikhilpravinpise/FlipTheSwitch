"""Dataset provenance and vetted analysis tools for the analyst MCP profile."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from contextlib import closing
from datetime import timedelta
from functools import wraps
from pathlib import Path
from typing import Annotated, Any, Literal

import structlog
from pydantic import Field

from labquorum.analysis.service import (
    execute_analysis,
    get_analysis_status,
    list_analysis_runs,
)
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.guards import RateGuard
from labquorum.domain.timeutil import Clock, SystemClock
from labquorum.mcp.profiles import Profile
from labquorum.mcp.tools_lab import MAX_RESULT_BYTES, compact_result
from labquorum.store.db import default_database_path, open_database
from labquorum.store.provenance import dataset_profile, register_dataset, staging_root

logger = structlog.get_logger("labquorum.mcp.analyst")

ANALYST_TOOL_DESCRIPTIONS: dict[str, str] = {
    "register_dataset": (
        "Register UTF-8 CSV text as an immutable, hashed dataset version under LabQuorum's "
        "private staging root. Supply a stable dataset ID, sensitivity, and correction reason. "
        "Human-subject data is refused. File paths and shell commands are not accepted."
    ),
    "dataset_profile": (
        "Read a staged dataset's columns, inferred types, missing values, duplicate rows or wells, "
        "out-of-range OD values, formula-like cells, and mapping warnings by dataset version ID. "
        "No file path is accepted."
    ),
    "run_analysis": (
        "Run the vetted descriptive recipe on a current staged plate dataset. It records input, "
        "recipe, lockfile and output hashes and returns a JSON summary and PNG figure. Wells are "
        "technical replicates; no p-values or significance claims are produced. No shell or path is accepted."
    ),
    "list_runs": (
        "List recent analysis runs and their current or stale state, optionally scoped by dataset ID."
    ),
    "run_status": (
        "Read one analysis run and its JSON/PNG artifact hashes, status, and stale reason. "
        "A stale run never becomes current; reruns receive new IDs."
    ),
}


class AnalystTools:
    """Profile-bound runtime. All paths are resolved internally from the ledger path."""

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.profile = Profile.ANALYST
        self.database_path = database_path or default_database_path()
        self.clock = clock or SystemClock()
        self.rate_guard = RateGuard(clock=self.clock, limit=30, period=timedelta(minutes=1))
        self._methods: dict[str, Callable[..., dict[str, Any]]] = {
            "register_dataset": self.register_dataset,
            "dataset_profile": self.dataset_profile,
            "run_analysis": self.run_analysis,
            "list_runs": self.list_runs,
            "run_status": self.run_status,
        }

    def tool_method(self, name: str) -> Callable[..., dict[str, Any]]:
        """Return one named tool handler for the profile-scoped MCP registrar."""
        try:
            return self._methods[name]
        except KeyError as exc:
            raise ValueError(f"Unknown analyst tool: {name}") from exc

    def tool_names(self) -> tuple[str, ...]:
        """Return the registered analyst tool names in their stable order."""
        return tuple(self._methods)

    def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Run a profile tool directly for deterministic local replays."""
        return self.tool_method(name)(**arguments)

    def register_dataset(
        self,
        dataset_id: Annotated[str, Field(min_length=1, max_length=80)],
        csv_text: Annotated[str, Field(min_length=1)],
        sensitivity: Literal["internal", "unpublished", "human_subjects"] = "internal",
        change_reason: Annotated[str, Field(max_length=240)] = "",
    ) -> dict[str, Any]:
        """Stage CSV bytes, assigning the next immutable version for the dataset ID."""
        with closing(open_database(self.database_path)) as connection:
            return register_dataset(
                connection,
                staging_root(self.database_path),
                dataset_id=dataset_id,
                csv_bytes=csv_text.encode("utf-8"),
                sensitivity=sensitivity,
                change_reason=change_reason,
                registered_by=self.profile.value,
                clock=self.clock,
            )

    def dataset_profile(
        self,
        dataset_version_id: Annotated[str, Field(min_length=1, max_length=120)],
    ) -> dict[str, Any]:
        """Report shape and validation findings without returning paths or raw rows."""
        with closing(open_database(self.database_path)) as connection:
            return dataset_profile(
                connection,
                staging_root(self.database_path),
                dataset_version_id,
            )

    def run_analysis(
        self,
        dataset_version_id: Annotated[str, Field(min_length=1, max_length=120)],
        recipe: Literal["descriptive"],
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute only the fixed descriptive analysis recipe in its subprocess."""
        with closing(open_database(self.database_path)) as connection:
            return execute_analysis(
                connection,
                self.database_path,
                dataset_version_id=dataset_version_id,
                recipe=recipe,
                params=params or {},
                clock=self.clock,
            )

    def list_runs(
        self,
        dataset_id: Annotated[str | None, Field(max_length=80)] = None,
        limit: Annotated[int, Field(ge=1, le=50)] = 20,
    ) -> dict[str, Any]:
        """List recent run metadata and statuses."""
        with closing(open_database(self.database_path)) as connection:
            return {"runs": list_analysis_runs(connection, dataset_id=dataset_id, limit=limit)}

    def run_status(
        self,
        run_id: Annotated[str, Field(min_length=1, max_length=100)],
    ) -> dict[str, Any]:
        """Read an analysis run and its output artifact states."""
        with closing(open_database(self.database_path)) as connection:
            return get_analysis_status(connection, run_id)


def register_analyst_tools(server: Any, runtime: AnalystTools) -> None:
    """Register the analyst-only tool set without altering booking handlers."""
    for name in runtime.tool_names():
        server.tool(
            name=name,
            description=ANALYST_TOOL_DESCRIPTIONS[name],
            structured_output=True,
        )(runtime.tool_method(name))


def _safe_tool(function: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    @wraps(function)
    def wrapped(self: AnalystTools, *args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            self.rate_guard.check(self.profile.value)
            result = compact_result(function(self, *args, **kwargs))
            logger.info(
                "analyst_tool_call",
                tool=function.__name__,
                outcome="error" if "error" in result else "success",
                error_code=result.get("error"),
            )
            return result
        except LabQuorumError as error:
            result = compact_result(
                {"error": error.code.value, "message": error.message, "details": error.details}
            )
            logger.info(
                "analyst_tool_call",
                tool=function.__name__,
                outcome="error",
                error_code=error.code.value,
            )
            return result
        except (OSError, sqlite3.Error):
            logger.exception("analyst_tool_call_failed", tool=function.__name__)
            return compact_result(
                {
                    "error": ErrorCode.INVALID_ARGUMENT.value,
                    "message": "Ledger operation failed. Check the ledger path and try again.",
                }
            )
        except Exception:
            logger.exception("analyst_tool_call_failed", tool=function.__name__)
            return compact_result(
                {
                    "error": ErrorCode.INVALID_ARGUMENT.value,
                    "message": "Tool operation failed. Check the arguments and ledger, then try again.",
                }
            )

    return wrapped


for _method_name in (
    "register_dataset",
    "dataset_profile",
    "run_analysis",
    "list_runs",
    "run_status",
):
    setattr(AnalystTools, _method_name, _safe_tool(getattr(AnalystTools, _method_name)))


assert MAX_RESULT_BYTES == 8_192
