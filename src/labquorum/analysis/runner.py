"""Subprocess isolation and process-tree timeout handling for vetted recipes."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from labquorum.domain.errors import ErrorCode, LabQuorumError

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_TIMEOUT_SECONDS = 120.0


def run_process_with_timeout(
    arguments: Sequence[str],
    *,
    timeout_seconds: float,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run an argument array and terminate its full process tree on timeout."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    process_options: dict[str, Any] = {}
    if os.name == "nt":
        process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        process_options["start_new_session"] = True
    process = subprocess.Popen(
        list(arguments),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        env=env,
        **process_options,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        _kill_process_tree(process)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
        raise TimeoutError(f"Analysis subprocess exceeded {timeout_seconds:g} seconds.") from exc
    return subprocess.CompletedProcess(list(arguments), process.returncode, stdout, stderr)


def execute_descriptive_worker(
    *,
    staging_root: Path,
    dataset_path: Path,
    output_dir: Path,
    dataset_sha256: str,
    timeout_seconds: float = ANALYSIS_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[str]:
    """Run only the installed LabQuorum descriptive worker, without shell access."""
    output_dir.mkdir(parents=True, exist_ok=False)
    environment = _worker_environment(output_dir)
    command = [
        sys.executable,
        "-m",
        "labquorum.analysis.worker",
        "--staging-root",
        str(staging_root),
        "--dataset",
        str(dataset_path),
        "--output-dir",
        str(output_dir),
        "--expected-sha256",
        dataset_sha256,
    ]
    result = run_process_with_timeout(
        command,
        timeout_seconds=timeout_seconds,
        cwd=staging_root,
        env=environment,
    )
    if result.returncode != 0:
        detail = result.stderr.strip()[-1_000:]
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Descriptive analysis worker failed: {detail or 'no diagnostic was returned'}.",
        )
    return result


def _worker_environment(output_dir: Path) -> dict[str, str]:
    names = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
    environment = {name: os.environ[name] for name in names if name in os.environ}
    environment.update(
        {
            "PYTHONUTF8": "1",
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(output_dir / ".mpl-config"),
        }
    )
    return environment


def _kill_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            process.kill()
            return
        if result.returncode != 0 and process.poll() is None:
            process.kill()
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        process.kill()
