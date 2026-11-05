"""Immutable dataset versions and monotonic dependency invalidation."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import deque
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from labquorum.analysis.csvdata import contains_human_subject_data, parse_csv, profile_csv
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock, SystemClock, utc_timestamp
from labquorum.store.audit import append_event
from labquorum.store.db import immediate_transaction

_DATASET_ID = re.compile(r"\A[A-Za-z][A-Za-z0-9_-]{0,79}\Z")
_SENSITIVITY = {"internal", "unpublished", "human_subjects"}


@dataclass(frozen=True)
class DatasetVersionInfo:
    dataset_id: str
    version: int
    version_id: str
    sha256: str
    byte_count: int
    sensitivity: str
    supersedes_id: str | None


def staging_root(database_path: Path) -> Path:
    """Return the private dataset and run root associated with a ledger path."""
    resolved = database_path.expanduser().resolve(strict=False)
    return resolved.with_name(resolved.name + ".staging")


def register_dataset(  # noqa: PLR0913
    connection: sqlite3.Connection,
    root: Path,
    *,
    dataset_id: str,
    csv_bytes: bytes,
    sensitivity: str = "internal",
    change_reason: str = "",
    registered_by: str = "analyst",
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Stage immutable CSV bytes and supersede the prior version of one dataset key."""
    digest, schema_json = _validate_submission(dataset_id, sensitivity, csv_bytes)
    active_clock = clock or SystemClock()
    root_resolved = root.expanduser().resolve(strict=False)
    root_resolved.mkdir(parents=True, exist_ok=True)
    staged_relative: str | None = None
    created_file = False

    try:
        with immediate_transaction(connection):
            latest = connection.execute(
                "SELECT id, version, sha256, sensitivity, relative_path, supersedes_id "
                "FROM dataset_version WHERE dataset_id = ? ORDER BY version DESC LIMIT 1",
                (dataset_id,),
            ).fetchone()
            if latest is not None and _is_idempotent(latest, digest, sensitivity):
                existing = safe_staging_path(root_resolved, str(latest["relative_path"]))
                if not existing.is_file() or _hash_file(existing) != digest:
                    raise LabQuorumError(
                        ErrorCode.TAMPERED,
                        "The staged dataset bytes do not match the immutable ledger hash.",
                    )
                return _dataset_result(
                    DatasetVersionInfo(
                        dataset_id=dataset_id,
                        version=int(latest["version"]),
                        version_id=str(latest["id"]),
                        sha256=digest,
                        byte_count=len(csv_bytes),
                        sensitivity=sensitivity,
                        supersedes_id=(
                            str(latest["supersedes_id"]) if latest["supersedes_id"] else None
                        ),
                    ),
                    idempotent=True,
                )

            version = int(latest["version"]) + 1 if latest is not None else 1
            version_id = f"{dataset_id}-v{version}"
            staged_relative = PurePosixPath(
                "datasets", dataset_id, f"v{version}", f"{digest}.csv"
            ).as_posix()
            staged_path = safe_staging_path(root_resolved, staged_relative)
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            if staged_path.exists():
                if not staged_path.is_file() or _hash_file(staged_path) != digest:
                    raise LabQuorumError(
                        ErrorCode.TAMPERED,
                        "A staged dataset path already exists with different bytes.",
                    )
            else:
                with staged_path.open("xb") as handle:
                    handle.write(csv_bytes)
                created_file = True

            supersedes_id = str(latest["id"]) if latest is not None else None
            connection.execute(
                "INSERT INTO dataset_version "
                "(id, dataset_id, version, relative_path, sha256, byte_count, schema_json, "
                "sensitivity, registered_by, supersedes_id, created_utc) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    version_id,
                    dataset_id,
                    version,
                    staged_relative,
                    digest,
                    len(csv_bytes),
                    schema_json,
                    sensitivity,
                    registered_by,
                    supersedes_id,
                    utc_timestamp(active_clock.now()),
                ),
            )
            reason = change_reason.strip() or "dataset bytes or metadata were updated"
            if latest is not None:
                stale_reason = (
                    f"{dataset_id} v{version} supersedes v{int(latest['version'])}: {reason}"
                )
                _mark_descendants_stale(
                    connection,
                    "dataset_version",
                    supersedes_id or "",
                    stale_reason,
                )
            info = DatasetVersionInfo(
                dataset_id=dataset_id,
                version=version,
                version_id=version_id,
                sha256=digest,
                byte_count=len(csv_bytes),
                sensitivity=sensitivity,
                supersedes_id=supersedes_id,
            )
            result = _dataset_result(info)
            append_event(
                connection,
                actor=registered_by,
                tool="register_dataset",
                args={
                    "dataset_id": dataset_id,
                    "version": version,
                    "sha256": digest,
                    "bytes": len(csv_bytes),
                    "sensitivity": sensitivity,
                    "change_reason": reason,
                },
                result={
                    "dataset_version_id": version_id,
                    "supersedes": supersedes_id,
                    "status": "registered",
                },
                clock=active_clock,
            )
            return result
    except BaseException:
        if created_file and staged_relative is not None:
            safe_staging_path(root_resolved, staged_relative).unlink(missing_ok=True)
        raise


def _validate_submission(dataset_id: str, sensitivity: str, csv_bytes: bytes) -> tuple[str, str]:
    if _DATASET_ID.fullmatch(dataset_id) is None:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Dataset ID must start with a letter and contain only letters, digits, underscore, or hyphen.",
        )
    if sensitivity not in _SENSITIVITY:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Sensitivity must be internal, unpublished, or human_subjects.",
        )
    if sensitivity == "human_subjects":
        raise LabQuorumError(
            ErrorCode.ETHICS_REVIEW_REQUIRED,
            "human_subjects datasets cannot be staged or analyzed.",
        )
    if len(csv_bytes) > 50 * 1024 * 1024:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "A staged dataset must be 50 MiB or smaller.",
        )
    headers, rows, delimiter, decimal_mark = parse_csv(csv_bytes)
    if contains_human_subject_data(headers, rows):
        raise LabQuorumError(
            ErrorCode.ETHICS_REVIEW_REQUIRED,
            "Dataset appears to contain human_subjects data and was not staged.",
        )

    digest = hashlib.sha256(csv_bytes).hexdigest()
    profile = profile_csv(csv_bytes)
    schema = {
        "columns": headers,
        "column_types": profile["column_types"],
        "delimiter": delimiter,
        "decimal_mark": decimal_mark,
    }
    return digest, json.dumps(schema, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _is_idempotent(latest: sqlite3.Row, digest: str, sensitivity: str) -> bool:
    return str(latest["sha256"]) == digest and str(latest["sensitivity"]) == sensitivity


def dataset_profile(
    connection: sqlite3.Connection,
    root: Path,
    dataset_version_id: str,
) -> dict[str, Any]:
    """Return schema and quality findings for an immutable staged version."""
    row = connection.execute(
        "SELECT id, dataset_id, version, relative_path, sha256, byte_count, sensitivity, "
        "supersedes_id FROM dataset_version WHERE id = ?",
        (dataset_version_id,),
    ).fetchone()
    if row is None:
        raise LabQuorumError(
            ErrorCode.NOT_FOUND, f"Dataset version {dataset_version_id} was not found."
        )
    path = safe_staging_path(root, str(row["relative_path"]))
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise LabQuorumError(
            ErrorCode.TAMPERED,
            "The staged dataset file is missing or unreadable.",
        ) from exc
    if len(content) != int(row["byte_count"]) or hashlib.sha256(content).hexdigest() != str(
        row["sha256"]
    ):
        raise LabQuorumError(
            ErrorCode.TAMPERED,
            "The staged dataset bytes do not match the immutable ledger hash.",
        )
    result = profile_csv(content)
    result.update(
        {
            "dataset_id": str(row["dataset_id"]),
            "dataset_version_id": str(row["id"]),
            "version": int(row["version"]),
            "sha256": str(row["sha256"]),
            "bytes": int(row["byte_count"]),
            "sensitivity": str(row["sensitivity"]),
            "supersedes": row["supersedes_id"],
        }
    )
    return result


def dataset_record(
    connection: sqlite3.Connection,
    root: Path,
    dataset_version_id: str,
) -> tuple[sqlite3.Row, Path]:
    """Load one version and its contained path for the vetted analysis worker."""
    row = connection.execute(
        "SELECT * FROM dataset_version WHERE id = ?", (dataset_version_id,)
    ).fetchone()
    if row is None:
        raise LabQuorumError(
            ErrorCode.NOT_FOUND, f"Dataset version {dataset_version_id} was not found."
        )
    if connection.execute(
        "SELECT 1 FROM dataset_version WHERE supersedes_id = ? LIMIT 1", (dataset_version_id,)
    ).fetchone():
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Dataset version {dataset_version_id} has been superseded; register or select its current version.",
        )
    path = safe_staging_path(root, str(row["relative_path"]))
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise LabQuorumError(ErrorCode.TAMPERED, "The staged dataset file is missing.") from exc
    if hashlib.sha256(content).hexdigest() != str(row["sha256"]):
        raise LabQuorumError(
            ErrorCode.TAMPERED,
            "The staged dataset bytes do not match the immutable ledger hash.",
        )
    return row, path


def mark_descendants_stale(
    connection: sqlite3.Connection,
    parent_type: str,
    parent_id: str,
    reason: str,
) -> set[tuple[str, str]]:
    """Mark each current descendant stale once and retain its first stale reason."""
    with immediate_transaction(connection):
        return _mark_descendants_stale(connection, parent_type, parent_id, reason)


def _mark_descendants_stale(
    connection: sqlite3.Connection,
    parent_type: str,
    parent_id: str,
    reason: str,
) -> set[tuple[str, str]]:
    visited: set[tuple[str, str]] = set()
    pending = deque([(parent_type, parent_id)])
    while pending:
        current_type, current_id = pending.popleft()
        for edge in connection.execute(
            "SELECT child_type, child_id FROM dependency_edge "
            "WHERE parent_type = ? AND parent_id = ?",
            (current_type, current_id),
        ):
            child = (str(edge["child_type"]), str(edge["child_id"]))
            if child in visited:
                continue
            visited.add(child)
            pending.append(child)
            if child[0] == "analysis_run":
                connection.execute(
                    "UPDATE analysis_run SET status = 'STALE', stale_reason = ? "
                    "WHERE id = ? AND status = 'CURRENT'",
                    (reason, child[1]),
                )
            elif child[0] == "artifact":
                connection.execute(
                    "UPDATE artifact SET status = 'STALE', stale_reason = ? "
                    "WHERE id = ? AND status = 'CURRENT'",
                    (reason, child[1]),
                )
    return visited


def _dataset_result(
    info: DatasetVersionInfo,
    *,
    idempotent: bool = False,
) -> dict[str, Any]:
    return {
        "dataset_id": info.dataset_id,
        "version": info.version,
        "dataset_version_id": info.version_id,
        "sha256": info.sha256,
        "bytes": info.byte_count,
        "sensitivity": info.sensitivity,
        "supersedes": info.supersedes_id,
        "status": "registered",
        "idempotent": idempotent,
    }


def safe_staging_path(root: Path, relative_path: str) -> Path:
    candidate_relative = PurePosixPath(relative_path)
    if candidate_relative.is_absolute() or ".." in candidate_relative.parts:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Staged dataset path is not relative and contained."
        )
    root_resolved = root.expanduser().resolve(strict=False)
    candidate = root_resolved.joinpath(*candidate_relative.parts).resolve(strict=False)
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Staged dataset path escapes the approved staging root.",
        ) from exc
    return candidate


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(128 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
