"""Ledger-backed service for executing the vetted descriptive recipe."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

from labquorum.analysis.descriptive import RECIPE_NAME, RECIPE_VERSION, validate_descriptive_dataset
from labquorum.analysis.runner import (
    ANALYSIS_TIMEOUT_SECONDS,
    REPO_ROOT,
    execute_descriptive_worker,
)
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock, SystemClock, utc_timestamp
from labquorum.store.audit import append_event
from labquorum.store.db import immediate_transaction
from labquorum.store.provenance import (
    dataset_record,
    safe_staging_path,
    staging_root,
)


@dataclass(frozen=True)
class AnalysisExecution:
    dataset_version_id: str
    dataset_path: Path
    root: Path
    dataset_sha256: str
    run_id: str
    run_directory: Path
    lock_hash: str
    clock: Clock
    started_monotonic: float
    inputs: list[dict[str, Any]]


class AnalysisArtifact(TypedDict):
    artifact_id: str
    kind: str
    relative_path: str
    sha256: str
    bytes: int


def execute_analysis(  # noqa: PLR0913
    connection: sqlite3.Connection,
    database_path: Path,
    *,
    dataset_version_id: str,
    recipe: str,
    params: dict[str, Any],
    clock: Clock | None = None,
    timeout_seconds: float = ANALYSIS_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Execute one version of the descriptive recipe and record content hashes."""
    active_clock = clock or SystemClock()
    _validate_recipe(recipe, params)
    execution = _start_analysis_run(
        connection,
        database_path=database_path,
        dataset_version_id=dataset_version_id,
        recipe=recipe,
        params=params,
        clock=active_clock,
    )

    try:
        outputs = _run_descriptive(execution, timeout_seconds)
    except TimeoutError as exc:
        _record_failed_run(
            connection,
            execution.run_id,
            "Analysis exceeded the 120 second wall-clock limit and its process tree was terminated.",
            active_clock,
            execution.started_monotonic,
        )
        _remove_run_directory(execution.run_directory)
        raise LabQuorumError(
            ErrorCode.BUDGET_EXCEEDED,
            "Analysis exceeded the 120 second wall-clock limit; the process tree was terminated.",
            {"run_id": execution.run_id},
        ) from exc
    except (LabQuorumError, OSError) as exc:
        _record_failed_run(
            connection,
            execution.run_id,
            str(exc),
            active_clock,
            execution.started_monotonic,
        )
        _remove_run_directory(execution.run_directory)
        if isinstance(exc, LabQuorumError):
            raise
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "The analysis worker could not read its staged input or write its outputs.",
            {"run_id": execution.run_id},
        ) from exc

    _record_success(connection, execution, outputs, recipe, params)
    return _analysis_result(execution.run_id, recipe, outputs)


def _validate_recipe(recipe: str, params: dict[str, Any]) -> None:
    if recipe != RECIPE_NAME:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Recipe {recipe!r} is not available. The vetted recipe is {RECIPE_NAME!r}.",
        )
    if params:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "The descriptive recipe accepts no parameters; provide an empty object.",
        )


def _start_analysis_run(  # noqa: PLR0913
    connection: sqlite3.Connection,
    *,
    database_path: Path,
    dataset_version_id: str,
    recipe: str,
    params: dict[str, Any],
    clock: Clock,
) -> AnalysisExecution:
    root = staging_root(database_path)
    dataset, dataset_path = dataset_record(connection, root, dataset_version_id)
    validate_descriptive_dataset(dataset_path.read_bytes())
    dataset_sha256 = str(dataset["sha256"])
    run_id = f"RUN-{uuid.uuid4().hex}"
    run_directory = safe_staging_path(root, (Path("runs") / run_id).as_posix())
    try:
        lock_hash = hashlib.sha256((REPO_ROOT / "uv.lock").read_bytes()).hexdigest()
    except OSError as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "The locked environment file is unavailable."
        ) from exc
    started_monotonic = time.perf_counter()
    created_utc = utc_timestamp(clock.now())
    inputs = [
        {
            "dataset_version_id": dataset_version_id,
            "sha256": dataset_sha256,
            "bytes": int(dataset["byte_count"]),
        }
    ]
    with immediate_transaction(connection):
        connection.execute(
            "INSERT INTO analysis_run "
            "(id, inputs_json, recipe, recipe_version, params_json, outputs_json, env_lock_sha256, "
            "status, stale_reason, created_utc) "
            "VALUES (?, ?, ?, ?, ?, '[]', ?, 'RUNNING', NULL, ?)",
            (
                run_id,
                _json_text(inputs),
                recipe,
                RECIPE_VERSION,
                _json_text(params),
                lock_hash,
                created_utc,
            ),
        )
        connection.execute(
            "INSERT INTO dependency_edge(parent_type, parent_id, child_type, child_id, created_utc) "
            "VALUES ('dataset_version', ?, 'analysis_run', ?, ?)",
            (dataset_version_id, run_id, created_utc),
        )
        append_event(
            connection,
            actor="analyst",
            tool="run_analysis_started",
            args={"dataset_version_id": dataset_version_id, "recipe": recipe},
            result={"run_id": run_id, "status": "RUNNING"},
            clock=clock,
        )
    return AnalysisExecution(
        dataset_version_id=dataset_version_id,
        dataset_path=dataset_path,
        root=root,
        dataset_sha256=dataset_sha256,
        run_id=run_id,
        run_directory=run_directory,
        lock_hash=lock_hash,
        clock=clock,
        started_monotonic=started_monotonic,
        inputs=inputs,
    )


def _run_descriptive(
    execution: AnalysisExecution,
    timeout_seconds: float,
) -> list[AnalysisArtifact]:
    execute_descriptive_worker(
        staging_root=execution.root,
        dataset_path=execution.dataset_path,
        output_dir=execution.run_directory,
        dataset_sha256=execution.dataset_sha256,
        timeout_seconds=timeout_seconds,
    )
    output_files: dict[Literal["json", "png"], Path] = {
        "json": safe_staging_path(
            execution.root,
            (execution.run_directory / "summary.json").relative_to(execution.root).as_posix(),
        ),
        "png": safe_staging_path(
            execution.root,
            (execution.run_directory / "summary.png").relative_to(execution.root).as_posix(),
        ),
    }
    outputs: list[AnalysisArtifact] = [
        AnalysisArtifact(
            artifact_id=f"ART-{uuid.uuid4().hex}",
            kind=kind,
            relative_path=path.relative_to(execution.root).as_posix(),
            sha256=_hash_file(path),
            bytes=path.stat().st_size,
        )
        for kind, path in output_files.items()
    ]
    if any(output["bytes"] <= 0 for output in outputs):
        raise LabQuorumError(ErrorCode.TAMPERED, "The analysis worker produced an empty output.")
    return outputs


def _record_success(
    connection: sqlite3.Connection,
    execution: AnalysisExecution,
    outputs: list[AnalysisArtifact],
    recipe: str,
    params: dict[str, Any],
) -> None:
    finished_utc = utc_timestamp(execution.clock.now())
    duration_ms = max(0, round((time.perf_counter() - execution.started_monotonic) * 1_000))
    output_payload = [
        {key: value for key, value in output.items() if key != "relative_path"}
        for output in outputs
    ]
    with immediate_transaction(connection):
        connection.execute(
            "UPDATE analysis_run SET outputs_json = ?, status = 'CURRENT', finished_utc = ?, "
            "duration_ms = ? WHERE id = ? AND status = 'RUNNING'",
            (
                json.dumps(
                    output_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                ),
                finished_utc,
                duration_ms,
                execution.run_id,
            ),
        )
        for output in outputs:
            connection.execute(
                "INSERT INTO artifact "
                "(id, run_id, kind, relative_path, sha256, byte_count, status, stale_reason) "
                "VALUES (?, ?, ?, ?, ?, ?, 'CURRENT', NULL)",
                (
                    output["artifact_id"],
                    execution.run_id,
                    output["kind"],
                    output["relative_path"],
                    output["sha256"],
                    output["bytes"],
                ),
            )
            connection.execute(
                "INSERT INTO dependency_edge(parent_type, parent_id, child_type, child_id, created_utc) "
                "VALUES ('analysis_run', ?, 'artifact', ?, ?)",
                (execution.run_id, output["artifact_id"], finished_utc),
            )
        append_event(
            connection,
            actor="analyst",
            tool="run_analysis",
            args={
                "dataset_version_id": execution.dataset_version_id,
                "recipe": recipe,
                "recipe_version": RECIPE_VERSION,
                "params": params,
                "inputs": execution.inputs,
                "env_lock_sha256": execution.lock_hash,
            },
            result={"run_id": execution.run_id, "status": "CURRENT", "outputs": output_payload},
            clock=execution.clock,
        )


def _analysis_result(
    run_id: str,
    recipe: str,
    outputs: list[AnalysisArtifact],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "status": "CURRENT",
        "recipe": recipe,
        "recipe_version": RECIPE_VERSION,
        "outputs": [
            {
                "artifact_id": item["artifact_id"],
                "kind": item["kind"],
                "sha256": item["sha256"],
                "bytes": item["bytes"],
                "status": "CURRENT",
            }
            for item in outputs
        ],
    }


def list_analysis_runs(
    connection: sqlite3.Connection,
    *,
    dataset_id: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List latest analysis records, optionally scoped to one dataset key."""
    if not 1 <= limit <= 50:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Run list limit must be between 1 and 50.")
    if dataset_id is None:
        rows = connection.execute(
            "SELECT * FROM analysis_run ORDER BY created_utc DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
    else:
        rows = connection.execute(
            "SELECT DISTINCT r.* FROM analysis_run AS r "
            "JOIN dependency_edge AS e ON e.child_type = 'analysis_run' AND e.child_id = r.id "
            "JOIN dataset_version AS d ON e.parent_type = 'dataset_version' AND e.parent_id = d.id "
            "WHERE d.dataset_id = ? ORDER BY r.created_utc DESC, r.id DESC LIMIT ?",
            (dataset_id, limit),
        ).fetchall()
    return [_run_summary(row) for row in rows]


def get_analysis_status(connection: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    """Read a run and its artifact statuses without exposing staged filesystem paths."""
    row = connection.execute("SELECT * FROM analysis_run WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise LabQuorumError(ErrorCode.NOT_FOUND, f"Analysis run {run_id} was not found.")
    outputs = connection.execute(
        "SELECT id, kind, sha256, byte_count, status, stale_reason FROM artifact "
        "WHERE run_id = ? ORDER BY kind",
        (run_id,),
    ).fetchall()
    result = _run_summary(row)
    result["outputs"] = [
        {
            "artifact_id": str(item["id"]),
            "kind": str(item["kind"]),
            "sha256": str(item["sha256"]),
            "bytes": int(item["byte_count"]),
            "status": str(item["status"]),
            "stale_reason": item["stale_reason"],
        }
        for item in outputs
    ]
    return result


def _run_summary(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "run_id": str(row["id"]),
        "status": str(row["status"]),
        "recipe": str(row["recipe"]),
        "recipe_version": str(row["recipe_version"]),
        "inputs": json.loads(str(row["inputs_json"])),
        "params": json.loads(str(row["params_json"])),
        "outputs": json.loads(str(row["outputs_json"])),
        "created_utc": str(row["created_utc"]),
        "finished_utc": row["finished_utc"],
        "duration_ms": row["duration_ms"],
        "stale_reason": row["stale_reason"],
    }


def _record_failed_run(
    connection: sqlite3.Connection,
    run_id: str,
    reason: str,
    clock: Clock,
    started_monotonic: float,
) -> None:
    finished_utc = utc_timestamp(clock.now())
    duration_ms = max(0, round((time.perf_counter() - started_monotonic) * 1_000))
    with immediate_transaction(connection):
        connection.execute(
            "UPDATE analysis_run SET status = 'FAILED', stale_reason = ?, finished_utc = ?, "
            "duration_ms = ? WHERE id = ? AND status = 'RUNNING'",
            (reason[:1_000], finished_utc, duration_ms, run_id),
        )
        append_event(
            connection,
            actor="analyst",
            tool="run_analysis_failed",
            args={"run_id": run_id},
            result={"status": "FAILED", "reason": reason[:1_000]},
            clock=clock,
        )


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(128 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _remove_run_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
