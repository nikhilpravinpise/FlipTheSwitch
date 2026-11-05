"""Fail-closed controls for exposing the booking commit tool."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from threading import RLock
from typing import Any, cast

from labquorum import __version__
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.mcp.profiles import Profile

_AGENT_PROFILES = {"labops": Profile.PROPOSER, "pi-desk": Profile.APPROVER}
_MARKER_TABLE = "labquorum_test_marker"
_MARKER_VALUE = "p3-certify-only"


def _within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def resolve_runtime_profile(
    requested_profile: str | Profile | None,
    runtime_root: Path | None,
    cwd: Path,
) -> Profile | None:
    """Resolve a registration only from its matching runtime agent folder."""
    if requested_profile is not None:
        try:
            profile = (
                requested_profile
                if isinstance(requested_profile, Profile)
                else Profile(requested_profile)
            )
        except ValueError:
            return None
        if runtime_root is None:
            return profile
    else:
        profile = None
    if runtime_root is None:
        return None
    root = runtime_root.expanduser().resolve(strict=False)
    workdir = cwd.expanduser().resolve(strict=False)
    for agent_name, expected in _AGENT_PROFILES.items():
        agent_dir = (root / "agents" / agent_name).resolve(strict=False)
        if _within(workdir, agent_dir):
            return expected if profile is None or profile is expected else None
    return None


def _is_test_ledger(database_path: Path) -> bool:
    path = database_path.expanduser().resolve(strict=False)
    if "certify" in {part.casefold() for part in path.parts}:
        return True
    temp_root = Path(tempfile.gettempdir()).resolve(strict=False)
    if path.name.casefold() == "p3-test-ledger.sqlite" and _within(path, temp_root):
        return True
    if not path.is_file():
        return False
    try:
        with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (_MARKER_TABLE,),
            ).fetchone()
            if table is None:
                return False
            row = connection.execute(
                f"SELECT 1 FROM {_MARKER_TABLE} WHERE marker = ? LIMIT 1",
                (_MARKER_VALUE,),
            ).fetchone()
            return row is not None
    except sqlite3.Error:
        return False


def installed_certification_tuple(runtime_root: Path) -> dict[str, str]:
    """Collect the four installed values required by a certification record."""
    codex = shutil.which("codex")
    if codex is None:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Certification requires an installed Codex CLI version.",
        )
    try:
        result = subprocess.run(
            [codex, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            f"Could not read the Codex CLI version: {exc}",
        ) from exc
    version_match = re.search(
        r"\b\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?\b", result.stdout + result.stderr
    )
    switch_version = os.environ.get("LABQUORUM_SWITCH_CONSOLE_VERSION", "").strip()
    template_path = (
        runtime_root.expanduser().resolve(strict=False) / "switch" / "labquorum.template.yaml"
    )
    if result.returncode != 0 or version_match is None or not switch_version:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Certification needs Codex CLI and LABQUORUM_SWITCH_CONSOLE_VERSION to be available.",
        )
    try:
        template_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            f"Could not read the installed Switch template: {exc}",
        ) from exc
    return {
        "codex_cli_version": version_match.group(0),
        "switch_console_version": switch_version.removeprefix("v"),
        "labquorum_version": __version__,
        "template_sha256": template_hash,
    }


def validate_binding_request(  # noqa: PLR0912, PLR0913, PLR0917
    binding: str,
    profile: Profile,
    database_path: Path,
    runtime_root: Path | None,
    certification_evidence: Path | None,
    cwd: Path,
) -> None:
    """Reject unsafe binding requests before constructing the MCP tool list."""
    if binding not in {"off", "certify", "on"}:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, f"Unknown binding mode: {binding}")
    if binding == "off":
        return
    if profile is not Profile.APPROVER:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Only the approver profile can expose commit_booking.",
        )
    if binding == "certify":
        if not _is_test_ledger(database_path):
            raise LabQuorumError(
                ErrorCode.BINDING_CERTIFICATION_REQUIRED,
                "Certify mode requires a marker ledger or a ledger under a certify directory.",
            )
        return
    if runtime_root is None or certification_evidence is None:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Binding on requires runtime-root and a certification evidence file.",
        )
    expected_root = runtime_root.expanduser().resolve(strict=False)
    expected_database = (expected_root / "ledger.sqlite").resolve(strict=False)
    if database_path.expanduser().resolve(strict=False) != expected_database:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Binding on requires the runtime root's ledger.sqlite.",
        )
    profile_at_cwd = resolve_runtime_profile(None, expected_root, cwd)
    if profile_at_cwd is not Profile.APPROVER:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Binding on is available only from the pi-desk runtime folder.",
        )
    evidence_path = certification_evidence.expanduser().resolve(strict=False)
    if not evidence_path.is_absolute() or not evidence_path.is_file():
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Binding certification evidence must be an existing absolute file.",
        )
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            f"Could not read certification evidence: {exc}",
        ) from exc
    if not isinstance(evidence, dict):
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Certification evidence must contain a certified_tuple object.",
        )
    evidence_object = cast(dict[str, Any], evidence)
    supplied_value = evidence_object.get("certified_tuple")
    if not isinstance(supplied_value, dict):
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_REQUIRED,
            "Certification evidence must contain a certified_tuple object.",
        )
    supplied = cast(dict[str, Any], supplied_value)
    installed = installed_certification_tuple(expected_root)
    if supplied != installed:
        raise LabQuorumError(
            ErrorCode.BINDING_CERTIFICATION_MISMATCH,
            "Certification evidence tuple does not match the installed runtime tuple.",
            {"installed": installed},
        )


class BindingCommitLimiter:
    """Allow one successful distinct commit per process and identical retries."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._successful_arguments: str | None = None

    def wrap(
        self,
        commit: Callable[..., dict[str, Any]],
    ) -> Callable[..., dict[str, Any]]:
        @wraps(commit)
        def guarded(**arguments: Any) -> dict[str, Any]:
            fingerprint = json.dumps(
                arguments,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            )
            with self._lock:
                if (
                    self._successful_arguments is not None
                    and fingerprint != self._successful_arguments
                ):
                    raise LabQuorumError(
                        ErrorCode.BINDING_COMMIT_LIMIT,
                        f"{ErrorCode.BINDING_COMMIT_LIMIT.value}: This MCP process has already "
                        "committed a different booking.",
                    )
                result = commit(**arguments)
                if self._successful_arguments is None and result.get("status") in {
                    "committed",
                    "already_committed",
                }:
                    self._successful_arguments = fingerprint
                return result

        return guarded
