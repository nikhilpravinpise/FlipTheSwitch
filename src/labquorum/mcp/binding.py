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
_TEST_LEDGER_NAME = "p3-test-ledger.sqlite"
_TEST_RUNTIME_PREFIX = "labquorum-p3-"


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
    temp_root = Path(tempfile.gettempdir()).resolve(strict=False)
    if (
        not _within(path, temp_root)
        or path.name.casefold() != _TEST_LEDGER_NAME
        or not path.parent.name.casefold().startswith(_TEST_RUNTIME_PREFIX)
        or "certify" in {part.casefold() for part in path.parts}
    ):
        return False
    try:
        manifest_value = json.loads((path.parent / "runtime.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(manifest_value, dict):
        return False
    manifest = cast(dict[str, object], manifest_value)
    return (
        manifest.get("schema_version") == 1
        and manifest.get("runtime_root") == str(path.parent)
        and manifest.get("ledger_path") == str(path.parent / "ledger.sqlite")
        and manifest.get("binding_mode") == "off"
        and path != path.parent / "ledger.sqlite"
        and path.is_file()
    )


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


def validate_binding_request(  # noqa: PLR0913, PLR0917
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
        resolved_database = database_path.expanduser().resolve(strict=False)
        resolved_root = runtime_root.expanduser().resolve(strict=False) if runtime_root else None
        if not _is_test_ledger(resolved_database) or (
            resolved_root is not None and resolved_database == resolved_root / "ledger.sqlite"
        ):
            raise LabQuorumError(
                ErrorCode.BINDING_CERTIFICATION_REQUIRED,
                "Certify mode requires the disposable P3 gate ledger under its temporary runtime root.",
            )
        return
    raise LabQuorumError(
        ErrorCode.BINDING_CERTIFICATION_REQUIRED,
        "Binding on is disabled until a trusted P4 certificate verifier and complete P4 record exist.",
    )


class BindingCommitLimiter:
    """Allow one distinct commit per process or persistent Codex session."""

    def __init__(self, state_path: Path | None = None) -> None:
        self._lock = RLock()
        self._successful_arguments: str | None = None
        self._state_path = state_path

    @classmethod
    def for_session_home(cls, session_home: Path) -> BindingCommitLimiter:
        """Bind a commit reservation to the persistent Codex session home."""
        state_path = session_home.expanduser().resolve(strict=False) / "labquorum-commit.sqlite"
        return cls(state_path)

    def wrap(
        self,
        commit: Callable[..., dict[str, Any]],
    ) -> Callable[..., dict[str, Any]]:
        @wraps(commit)
        def guarded(**arguments: Any) -> dict[str, Any]:
            fingerprint = _argument_fingerprint(arguments)
            with self._lock:
                if self._state_path is not None:
                    return self._guard_persistent(commit, arguments, fingerprint)
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

    def _guard_persistent(
        self,
        commit: Callable[..., dict[str, Any]],
        arguments: dict[str, Any],
        fingerprint: str,
    ) -> dict[str, Any]:
        assert self._state_path is not None
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(self._state_path, timeout=5) as connection:
                connection.execute("PRAGMA busy_timeout = 5000")
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS binding_commit_guard ("
                    "id INTEGER PRIMARY KEY CHECK (id = 1), fingerprint TEXT NOT NULL)"
                )
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT fingerprint FROM binding_commit_guard WHERE id = 1"
                ).fetchone()
                if row is not None and row[0] != fingerprint:
                    raise _commit_limit_error()
                if row is None:
                    connection.execute(
                        "INSERT INTO binding_commit_guard(id, fingerprint) VALUES (1, ?)",
                        (fingerprint,),
                    )
                connection.commit()
        except sqlite3.Error as exc:
            raise LabQuorumError(
                ErrorCode.BINDING_CERTIFICATION_REQUIRED,
                f"Could not persist the Codex-session commit reservation: {exc}",
            ) from exc
        return commit(**arguments)


def _argument_fingerprint(arguments: dict[str, Any]) -> str:
    return json.dumps(
        arguments,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _commit_limit_error() -> LabQuorumError:
    return LabQuorumError(
        ErrorCode.BINDING_COMMIT_LIMIT,
        f"{ErrorCode.BINDING_COMMIT_LIMIT.value}: This Codex session has already reserved "
        "a different booking commit.",
    )
