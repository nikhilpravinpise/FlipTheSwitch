"""Minimal ledger initialization, demo seed, and audit commands."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from collections.abc import Sequence
from contextlib import closing, redirect_stderr
from datetime import date
from pathlib import Path
from typing import Any, cast

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import SystemClock
from labquorum.mcp.profiles import profile_for_agent
from labquorum.mcp.server import argument_parser as _server_argument_parser
from labquorum.provisioning import (
    default_runtime_root,
    lint_template_file,
    runtime_doctor_findings,
    setup_runtime,
)
from labquorum.store.audit import tail, verify
from labquorum.store.db import (
    database_info,
    default_database_path,
    init_database,
    onedrive_warning,
    open_database,
    select_journal_mode,
)
from labquorum.store.repos import get_request
from labquorum.store.seed import seed_demo

REPO_ROOT = Path(__file__).resolve().parents[3]


def _date_argument(value: str) -> date:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise argparse.ArgumentTypeError("anchor date must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("anchor date is invalid") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lq", description="LabQuorum booking ledger utilities")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create or inspect a ledger")
    init.add_argument("--db", type=Path, default=default_database_path())

    seed = commands.add_parser("seed", help="load the demo booking fixtures")
    seed.add_argument("--demo", action="store_true", required=True)
    seed.add_argument("--db", type=Path, default=default_database_path())
    seed.add_argument("--anchor-date", type=_date_argument, required=True)

    doctor = commands.add_parser("doctor", help="check the local LabQuorum environment")
    doctor.add_argument("--db", type=Path)
    doctor.add_argument("--agents-dir", type=Path, default=REPO_ROOT / "agents")
    doctor.add_argument("--runtime-root", type=Path)

    setup = commands.add_parser("setup", help="create the booking agent runtime")
    setup.add_argument("--runtime-root", type=Path, default=default_runtime_root())

    template = commands.add_parser("template", help="check a Switch agent template")
    template_commands = template.add_subparsers(dest="template_command", required=True)
    lint = template_commands.add_parser("lint", help="lint a booking-only Switch template")
    lint.add_argument("path", type=Path)

    request = commands.add_parser("request", help="inspect approval requests")
    request_commands = request.add_subparsers(dest="request_command", required=True)
    request_show = request_commands.add_parser("show", help="show one approval request")
    request_show.add_argument("request_id")
    request_show.add_argument("--db", type=Path, default=default_database_path())

    audit = commands.add_parser("audit", help="inspect the ledger audit chain")
    audit_commands = audit.add_subparsers(dest="audit_command", required=True)
    audit_verify = audit_commands.add_parser("verify", help="verify the hash chain")
    audit_verify.add_argument("--db", type=Path, default=default_database_path())
    audit_tail = audit_commands.add_parser("tail", help="show recent audit rows")
    audit_tail.add_argument("--db", type=Path, default=default_database_path())
    audit_tail.add_argument("-n", type=int, default=20)
    return parser


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _finding(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _env_key_is_set(name: str, repo_root: Path) -> bool:
    if os.environ.get(name, "").strip():
        return True
    env_path = repo_root / ".env"
    if not env_path.is_file():
        return False
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for line in lines:
        key, separator, value = line.partition("=")
        if separator and key.strip() == name and value.strip().strip("\"'"):
            return True
    return False


def _check_uv() -> tuple[str | None, list[dict[str, str]]]:
    executable = shutil.which("uv")
    if executable is None:
        return None, [
            _finding(
                "UV_UNAVAILABLE",
                "error",
                "uv was not found on PATH. Install uv and reopen the terminal, or add its install directory to PATH.",
            )
        ]
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, [
            _finding(
                "UV_EXECUTION_FAILED",
                "error",
                f"Could not run uv at {executable}: {exc}. Check the executable path and permissions.",
            )
        ]
    if result.returncode != 0:
        return None, [
            _finding(
                "UV_EXECUTION_FAILED",
                "error",
                f"uv at {executable} exited {result.returncode}. Check that PATH points to a working uv installation.",
            )
        ]
    version = result.stdout.strip() or result.stderr.strip()
    return version, [_finding("UV_AVAILABLE", "info", f"Found {version} at {executable}.")]


def _check_docker() -> dict[str, str]:
    executable = shutil.which("docker")
    if executable is None:
        return _finding(
            "DOCKER_UNAVAILABLE",
            "warning",
            "Docker is not on PATH. Switch Mattermost and optional container tools will be unavailable.",
        )
    try:
        result = subprocess.run(
            [executable, "info"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _finding("DOCKER_UNAVAILABLE", "warning", f"Docker did not respond: {exc}.")
    if result.returncode != 0:
        return _finding(
            "DOCKER_UNAVAILABLE",
            "warning",
            "Docker is installed but its local engine is not responding. Start Docker Desktop.",
        )
    return _finding("DOCKER_AVAILABLE", "info", f"Docker engine is responding at {executable}.")


def _resolve_mcp_command(command: str, folder: Path) -> str | None:
    expanded = os.path.expandvars(command)
    candidate = Path(expanded).expanduser()
    if candidate.is_absolute() or len(candidate.parts) > 1:
        resolved = candidate if candidate.is_absolute() else folder / candidate
        absolute = resolved.resolve(strict=False)
        return str(absolute) if absolute.is_file() and os.access(absolute, os.X_OK) else None
    return shutil.which(expanded)


class _McpConfigIssue(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _read_agent_mcp_config(config_path: Path) -> tuple[str, list[str]]:
    if not config_path.is_file():
        raise _McpConfigIssue(
            "MCP_CONFIG_MISSING", f"{config_path.parent.name} is missing .mcp.json."
        )
    try:
        config: Any = json.loads(
            config_path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise _McpConfigIssue(
            "MCP_CONFIG_INVALID", f"Could not read {config_path}: {exc}."
        ) from exc
    if not isinstance(config, dict):
        raise _McpConfigIssue("MCP_CONFIG_INVALID", f"{config_path} must be a JSON object.")
    config_object = cast(dict[str, Any], config)
    servers_value: Any = config_object.get("mcpServers")
    if not isinstance(servers_value, dict):
        raise _McpConfigIssue("MCP_CONFIG_INVALID", f"{config_path} needs mcpServers.labquorum.")
    servers = cast(dict[str, Any], servers_value)
    labquorum_value: Any = servers.get("labquorum")
    if not isinstance(labquorum_value, dict):
        raise _McpConfigIssue("MCP_CONFIG_INVALID", f"{config_path} needs mcpServers.labquorum.")
    labquorum = cast(dict[str, Any], labquorum_value)
    command: Any = labquorum.get("command")
    raw_arguments: Any = labquorum.get("args", [])
    if not isinstance(command, str) or not command.strip() or not isinstance(raw_arguments, list):
        raise _McpConfigIssue(
            "MCP_CONFIG_INVALID", f"{config_path} needs a command and argument array."
        )
    arguments: list[str] = []
    for raw_argument in cast(list[object], raw_arguments):
        if not isinstance(raw_argument, str):
            raise _McpConfigIssue("MCP_CONFIG_INVALID", f"{config_path} args must all be strings.")
        arguments.append(os.path.expandvars(raw_argument))
    return command, arguments


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON property {key!r}")
        result[key] = value
    return result


def _effective_server_arguments(command: str, arguments: list[str]) -> list[str] | None:
    """Extract the arguments consumed by the actual LabQuorum server entry point."""
    command_name = Path(os.path.expandvars(command)).stem.casefold()
    if command_name == "lq-mcp":
        return arguments
    if command_name == "uv":
        run_positions = [index for index, argument in enumerate(arguments) if argument == "run"]
        entrypoints = [
            index
            for index, argument in enumerate(arguments)
            if Path(argument).stem.casefold() == "lq-mcp"
            and run_positions
            and index > run_positions[0]
        ]
        if len(run_positions) == 1 and len(entrypoints) == 1:
            return arguments[entrypoints[0] + 1 :]
    if command_name.startswith("python"):
        module_positions = [
            index
            for index in range(len(arguments) - 1)
            if arguments[index] == "-m" and arguments[index + 1] == "labquorum.mcp.server"
        ]
        if len(module_positions) == 1:
            return arguments[module_positions[0] + 2 :]
    return None


def _agent_config_finding(folder: Path) -> dict[str, str]:
    config_path = folder / ".mcp.json"
    try:
        command, arguments = _read_agent_mcp_config(config_path)
        executable = _resolve_mcp_command(command, folder)
        if executable is None:
            raise _McpConfigIssue(
                "MCP_COMMAND_UNRESOLVED",
                f"Could not resolve MCP command {command!r} in {config_path}.",
            )
        server_arguments = _effective_server_arguments(command, arguments)
        if server_arguments is None:
            raise _McpConfigIssue(
                "MCP_CONFIG_INVALID",
                f"{config_path} must launch lq-mcp or python -m labquorum.mcp.server.",
            )
        parser = _server_argument_parser()
        repeated_option = parser.duplicate_option(server_arguments)
        if repeated_option is not None:
            raise _McpConfigIssue(
                "MCP_CONFIG_DUPLICATE_OPTION",
                f"{config_path} contains duplicate launch option {repeated_option}.",
            )
        try:
            with redirect_stderr(io.StringIO()):
                parsed_arguments = parser.parse_args(server_arguments)
        except SystemExit as exc:
            raise _McpConfigIssue(
                "MCP_CONFIG_INVALID",
                f"{config_path} has invalid lq-mcp launch arguments (parser exit {exc.code}).",
            ) from exc
        configured_profile = parsed_arguments.profile
        expected_profile = profile_for_agent(folder.name)
        if expected_profile is None or configured_profile != expected_profile.value:
            expected = expected_profile.value if expected_profile is not None else "no P2 profile"
            raise _McpConfigIssue(
                "MCP_PROFILE_MISMATCH",
                f"{folder.name} expects profile {expected}, but {config_path} uses {configured_profile}.",
            )
    except _McpConfigIssue as issue:
        return _finding(issue.code, "error", issue.message)
    return _finding(
        "MCP_CONFIG_RESOLVED",
        "info",
        f"{config_path} resolves to {executable} with profile {configured_profile}.",
    )


def _inspect_agent_configs(agents_dir: Path) -> list[dict[str, str]]:
    if not agents_dir.is_dir():
        return [_finding("AGENTS_NOT_FOUND", "info", f"No agents directory at {agents_dir}.")]
    folders = sorted(path for path in agents_dir.iterdir() if path.is_dir())
    if not folders:
        return [_finding("AGENT_FOLDERS_EMPTY", "warning", f"No agent folders in {agents_dir}.")]
    return [_agent_config_finding(folder) for folder in folders]


def doctor_report(
    database_path: Path,
    *,
    agents_dir: Path,
    repo_root: Path = REPO_ROOT,
    inspect_agents: bool = True,
) -> dict[str, Any]:
    """Collect distinct local setup findings without mutating the ledger or contacting APIs."""
    database_path = database_path.expanduser().resolve(strict=False)
    uv_version, findings = _check_uv()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    findings.append(_finding("PYTHON_AVAILABLE", "info", f"Python {python_version} is running."))

    ledger_parent = database_path.parent
    if not ledger_parent.is_dir():
        findings.append(
            _finding(
                "LEDGER_PARENT_MISSING",
                "error",
                f"Ledger parent directory does not exist: {ledger_parent}.",
            )
        )
    elif not os.access(ledger_parent, os.W_OK):
        findings.append(
            _finding(
                "LEDGER_PARENT_NOT_WRITABLE",
                "error",
                f"Ledger parent directory is not writable: {ledger_parent}.",
            )
        )

    warning = onedrive_warning(database_path)
    if warning is not None:
        findings.append(_finding("LEDGER_ONEDRIVE", "error", warning))
    else:
        findings.append(
            _finding(
                "LEDGER_PATH_SAFE",
                "info",
                f"Ledger path is outside OneDrive: {database_path.expanduser().resolve(strict=False)}.",
            )
        )

    journal_decision = select_journal_mode(sqlite3.sqlite_version_info).casefold()
    active_journal_mode = None
    if database_path.is_file():
        try:
            with closing(open_database(database_path)) as connection:
                info = database_info(connection)
            active_journal_mode = info.journal_mode
            if active_journal_mode != journal_decision:
                findings.append(
                    _finding(
                        "SQLITE_JOURNAL_MISMATCH",
                        "error",
                        f"Ledger uses {active_journal_mode}, but SQLite {info.sqlite_version} selects {journal_decision}.",
                    )
                )
            else:
                findings.append(
                    _finding(
                        "SQLITE_LEDGER_READY",
                        "info",
                        f"SQLite {info.sqlite_version}, journal mode {active_journal_mode}.",
                    )
                )
        except (LabQuorumError, OSError, sqlite3.Error) as exc:
            findings.append(
                _finding(
                    "SQLITE_LEDGER_INVALID",
                    "error",
                    f"Could not open ledger {database_path}: {exc}. Check the path and run lq init if it is new.",
                )
            )
    else:
        findings.append(
            _finding(
                "SQLITE_LEDGER_NOT_CREATED",
                "info",
                f"SQLite {sqlite3.sqlite_version}; new ledgers will use journal mode {journal_decision}.",
            )
        )

    if _env_key_is_set("OPENALEX_API_KEY", repo_root):
        findings.append(
            _finding("OPENALEX_KEY_CONFIGURED", "info", "OpenAlex API key is configured.")
        )
    else:
        findings.append(
            _finding(
                "OPENALEX_KEY_MISSING",
                "warning",
                "OPENALEX_API_KEY is not configured. Literature tools are not enabled in P2.",
            )
        )
    findings.append(_check_docker())
    if inspect_agents:
        findings.extend(_inspect_agent_configs(agents_dir))
    return {
        "python_version": python_version,
        "uv_version": uv_version,
        "ledger_path": str(database_path.expanduser().resolve(strict=False)),
        "sqlite_version": sqlite3.sqlite_version,
        "journal_mode_decision": journal_decision,
        "active_journal_mode": active_journal_mode,
        "findings": findings,
        "ok": not any(item["severity"] == "error" for item in findings),
    }


def _run(args: argparse.Namespace) -> int:  # noqa: PLR0911
    if args.command == "setup":
        manifest = setup_runtime(args.runtime_root)
        connection = init_database(Path(manifest["ledger_path"]))
        connection.close()
        print(_json(manifest))
        return 0
    if args.command == "template" and args.template_command == "lint":
        issues = lint_template_file(args.path)
        print(
            _json(
                {"path": str(args.path.resolve(strict=False)), "issues": issues, "ok": not issues}
            )
        )
        return 0 if not issues else 1
    if args.command == "doctor":
        runtime_root = args.runtime_root
        path = (
            runtime_root.expanduser().resolve(strict=False) / "ledger.sqlite"
            if runtime_root is not None and args.db is None
            else args.db or default_database_path()
        )
        agents_dir = runtime_root / "agents" if runtime_root is not None else args.agents_dir
        report = doctor_report(
            path,
            agents_dir=agents_dir,
            inspect_agents=runtime_root is None,
        )
        if runtime_root is not None:
            resolved_root = runtime_root.expanduser().resolve(strict=False)
            report["runtime_root"] = str(resolved_root)
            report["findings"].extend(runtime_doctor_findings(resolved_root))
            report["ok"] = not any(item["severity"] == "error" for item in report["findings"])
        print(_json(report))
        return 0 if report["ok"] else 1
    path: Path = args.db
    if args.command == "init":
        connection = init_database(path)
        try:
            info = database_info(connection)
            print(
                _json(
                    {
                        "database": str(path.resolve()),
                        "schema_version": info.schema_version,
                        "sqlite_version": info.sqlite_version,
                        "journal_mode": info.journal_mode,
                    }
                )
            )
        finally:
            connection.close()
        return 0

    connection = open_database(path)
    try:
        if args.command == "seed":
            result = seed_demo(connection, args.anchor_date)
            print(_json(result))
            return 0
        if args.command == "request" and args.request_command == "show":
            print(_json(get_request(connection, args.request_id, clock=SystemClock())))
            return 0
        if args.audit_command == "verify":
            bad_sequence = verify(connection)
            valid = bad_sequence is None
            print(
                _json(
                    {
                        "valid": valid,
                        "first_bad_seq": bad_sequence,
                        "scope": "internal chain consistency",
                        "limitation": "Truncation and recomputed chains are not detectable without an external checkpoint.",
                    }
                )
            )
            return 0 if valid else 1
        if args.audit_command == "tail":
            if args.n <= 0:
                raise LabQuorumError(
                    ErrorCode.INVALID_ARGUMENT,
                    "Audit tail count must be positive.",
                )
            print(_json(tail(connection, limit=args.n)))
            return 0
    finally:
        connection.close()
    raise RuntimeError("Argument parser produced an unsupported command.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except LabQuorumError as error:
        print(
            _json({"error": error.code.value, "message": error.message, "details": error.details}),
            file=sys.stderr,
        )
        return 1
    except (OSError, sqlite3.Error) as error:
        print(
            _json(
                {
                    "error": ErrorCode.INVALID_ARGUMENT.value,
                    "message": (
                        f"Could not use ledger path {getattr(args, 'db', '')}: {error}. "
                        "Check that the path names a writable SQLite file."
                    ),
                }
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
