"""Subprocess isolation and process-tree timeout handling for vetted recipes."""

from __future__ import annotations

import contextlib
import ctypes
import os
import signal
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from labquorum.domain.errors import ErrorCode, LabQuorumError

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_TIMEOUT_SECONDS = 120.0
_WINDOWS_JOB_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
_WINDOWS_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
_TIMEOUT_DRAIN_SECONDS = 2.0


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
    job_handle: int | None = None
    if os.name == "nt":
        job_handle = _create_windows_job()
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
    if job_handle is not None and not _assign_process_to_job(job_handle, process):
        _close_windows_job(job_handle)
        job_handle = None
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        _kill_process_tree(process, job_handle)
        try:
            stdout, stderr = process.communicate(timeout=_TIMEOUT_DRAIN_SECONDS)
        except subprocess.TimeoutExpired:
            _close_process_pipes(process)
            if process.poll() is None:
                process.kill()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=_TIMEOUT_DRAIN_SECONDS)
        raise TimeoutError(f"Analysis subprocess exceeded {timeout_seconds:g} seconds.") from exc
    finally:
        if job_handle is not None:
            _close_windows_job(job_handle)
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


def _create_windows_job() -> int | None:
    if os.name != "nt":
        return None

    # Win32 APIs: CreateJobObjectW https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw
    # SetInformationJobObject https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-setinformationjobobject
    class BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [
            (name, ctypes.c_ulonglong)
            for name in (
                "ReadOperationCount",
                "WriteOperationCount",
                "OtherOperationCount",
                "ReadTransferCount",
                "WriteTransferCount",
                "OtherTransferCount",
            )
        ]

    class ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimitInformation),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    kernel32.CreateJobObjectW.restype = ctypes.c_void_p
    kernel32.SetInformationJobObject.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_uint32,
    ]
    kernel32.SetInformationJobObject.restype = ctypes.c_int
    handle = kernel32.CreateJobObjectW(None, None)
    if not handle:
        return None
    limits = ExtendedLimitInformation()
    limits.BasicLimitInformation.LimitFlags = _WINDOWS_JOB_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        handle,
        _WINDOWS_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(limits),
        ctypes.sizeof(limits),
    ):
        _close_windows_job(handle)
        return None
    return int(handle)


def _assign_process_to_job(job_handle: int, process: subprocess.Popen[str]) -> bool:
    # AssignProcessToJobObject: https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel32.AssignProcessToJobObject.restype = ctypes.c_int
    process_handle = cast(Any, process)._handle
    return bool(kernel32.AssignProcessToJobObject(job_handle, process_handle))


def _terminate_windows_job(job_handle: int) -> bool:
    # TerminateJobObject: https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.TerminateJobObject.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    kernel32.TerminateJobObject.restype = ctypes.c_int
    return bool(kernel32.TerminateJobObject(job_handle, 1))


def _close_windows_job(job_handle: int) -> None:
    # CloseHandle: https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    kernel32.CloseHandle(job_handle)


def _close_process_pipes(process: subprocess.Popen[str]) -> None:
    for stream in (process.stdout, process.stderr):
        if stream is not None:
            with contextlib.suppress(OSError):
                os.close(stream.fileno())


def _kill_process_tree(process: subprocess.Popen[str], job_handle: int | None = None) -> None:
    if job_handle is not None:
        if not _terminate_windows_job(job_handle) and process.poll() is None:
            process.kill()
        return
    if os.name == "nt":
        if process.poll() is not None:
            return
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=_TIMEOUT_DRAIN_SECONDS,
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
