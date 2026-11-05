"""P3 gate for setup, Codex template linting, and fail-closed MCP binding."""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# PyYAML safe_load/safe_dump exports verified in .venv/Lib/site-packages/yaml/__init__.py:117,263.
# Python 3.12 tomllib.load is exported by Lib/tomllib/__init__.py.
ROOT = Path(__file__).resolve().parents[2]
PROBE_ARGS_PATH = ROOT / "tests" / "contract" / "p2_probe_args.json"
DISTINCT_COMMIT_ERROR = "BINDING_COMMIT_LIMIT"


class Gate:
    """Run every independent P3 check and report all failures."""

    def __init__(self) -> None:
        self.failures = 0

    def command(self, name: str, args: Sequence[str]) -> bool:
        result = _run_command(args)
        if isinstance(result, str):
            self.fail(name, result)
            return False
        output = (result.stdout + result.stderr).strip()
        if output:
            print(output)
        if result.returncode == 0:
            print(f"PASS {name}")
            return True
        self.fail(name, f"exited {result.returncode}")
        return False

    def expected_failure(self, name: str, args: Sequence[str]) -> bool:
        result = _run_command(args)
        if isinstance(result, str):
            self.fail(name, result)
            return False
        output = (result.stdout + result.stderr).strip()
        if output:
            print(output)
        if result.returncode != 0:
            print(f"PASS {name} rejected invalid input")
            return True
        self.fail(name, "invalid input unexpectedly passed")
        return False

    def fail(self, name: str, reason: str) -> None:
        self.failures += 1
        print(f"FAIL {name}: {reason}")


def _run_command(args: Sequence[str]) -> subprocess.CompletedProcess[str] | str:
    try:
        return subprocess.run(
            list(args),
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        return f"could not start {' '.join(args)}: {exc}"


def _exception_detail(exc: BaseException) -> str:
    if isinstance(exc, BaseExceptionGroup):
        return "; ".join(_exception_detail(child) for child in exc.exceptions)
    return f"{type(exc).__name__}: {exc}"


def error_code(payload: Any, text: str) -> str | None:
    """Extract a machine-readable error code from an MCP response."""

    def visit(value: Any) -> str | None:
        if isinstance(value, Mapping):
            for key in ("error_code", "errorCode", "code"):
                code = value.get(key)
                if isinstance(code, str) and re.fullmatch(r"[A-Z][A-Z0-9_]+", code):
                    return code
            for child in value.values():
                found = visit(child)
                if found is not None:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = visit(child)
                if found is not None:
                    return found
        return None

    found = visit(payload)
    if found is not None:
        return found
    match = re.search(r"\b[A-Z][A-Z0-9_]{2,}\b", text)
    return match.group(0) if match is not None else None


def json_pointer(document: Any, pointer: str) -> Any:
    """Resolve a JSON Pointer path against a decoded MCP result."""
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError(f"JSON Pointer must be empty or start with '/': {pointer}")
    current = document
    for raw_segment in pointer[1:].split("/"):
        segment = raw_segment.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if segment not in current:
                raise ValueError(f"JSON Pointer does not resolve: {pointer}")
            current = current[segment]
        elif isinstance(current, list):
            try:
                current = current[int(segment)]
            except (ValueError, IndexError) as exc:
                raise ValueError(f"JSON Pointer does not resolve: {pointer}") from exc
        else:
            raise ValueError(f"JSON Pointer does not resolve: {pointer}")
    return current


def extract_tool_names(listing: Any) -> set[str]:
    """Read tool names from the official MCP client's list_tools result."""
    tools = getattr(listing, "tools", None)
    if not isinstance(tools, list):
        raise ValueError("MCP list_tools response has no tools list")
    names = [getattr(tool, "name", None) for tool in tools]
    if not all(isinstance(name, str) and name for name in names):
        raise ValueError("MCP list_tools response contains a tool without a name")
    return {name for name in names if isinstance(name, str)}


def binding_tool_exposure_issue(tool_names: set[str], *, expected: bool) -> str | None:
    """Return a diagnostic when commit_booking exposure differs from expectation."""
    exposed = "commit_booking" in tool_names
    if exposed == expected:
        return None
    if expected:
        return "commit_booking is missing from the approver profile"
    return "commit_booking is exposed without an allowed binding mode"


def server_arguments(profile: str, database: Path) -> list[str]:
    """Build profile and ledger arguments without enabling binding."""
    return ["--profile", profile, "--db", str(database)]


def template_mutations(template: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Return separate invalid copies for each P3 template-lint rule."""
    agents = template.get("agents")
    if not isinstance(agents, list):
        raise ValueError("Switch template must contain an agents list")

    def changed_template(agent_name: str, change: str) -> dict[str, Any]:
        result = copy.deepcopy(dict(template))
        entries = result.get("agents")
        if not isinstance(entries, list):
            raise ValueError("Switch template must contain an agents list")
        agent = next(
            (item for item in entries if isinstance(item, dict) and item.get("name") == agent_name),
            None,
        )
        if not isinstance(agent, dict):
            raise ValueError(f"Switch template is missing the {agent_name!r} agent")
        if change == "provider":
            agent["provider"] = "claude"
        elif change == "model":
            agent["model"] = "gpt-6-test-invalid"
        elif change == "effort":
            advanced = agent.get("advanced_config")
            if not isinstance(advanced, dict):
                raise ValueError(f"{agent_name} advanced_config must be a mapping")
            advanced["effort"] = "medium"
        elif change == "addressing":
            agent["addressing"] = "anyone"
        elif change == "trailing_mention":
            instructions = agent.get("instructions", "")
            if not isinstance(instructions, str):
                raise ValueError(f"{agent_name} instructions must be text")
            agent["instructions"] = f"{instructions.rstrip()}\nMessage @labops."
        else:
            raise ValueError(f"unknown template mutation: {change}")
        return result

    return {
        "provider": changed_template("labops", "provider"),
        "model": changed_template("labops", "model"),
        "effort": changed_template("labops", "effort"),
        "addressing": changed_template("pi-desk", "addressing"),
        "trailing_mention": changed_template("labops", "trailing_mention"),
    }


def _load_yaml_template(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError(f"could not load generated Switch template: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("generated Switch template must be a YAML mapping")
    return value


def _registered_profile(agent_directory: Path, expected_profile: str) -> str | None:
    """Check per-agent Codex TOML for its explicit labquorum profile."""
    config_files = sorted(agent_directory.rglob("config.toml"))
    for config_path in config_files:
        registration, issue = _read_labquorum_registration(config_path)
        if issue is not None:
            return issue
        if registration is None:
            continue
        return _check_registration(config_path, registration, expected_profile)
    return f"{agent_directory} has no Codex labquorum MCP registration"


def _read_labquorum_registration(
    config_path: Path,
) -> tuple[Mapping[str, Any] | None, str | None]:
    try:
        with config_path.open("rb") as config_file:
            config = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, f"could not read Codex config {config_path}: {exc}"
    servers = config.get("mcp_servers")
    if not isinstance(servers, dict):
        return None, None
    registration = servers.get("labquorum")
    if not isinstance(registration, dict):
        return None, None
    return registration, None


def _check_registration(
    config_path: Path, registration: Mapping[str, Any], expected_profile: str
) -> str | None:
    command = registration.get("command")
    arguments = registration.get("args")
    if not isinstance(command, str) or not command:
        return f"{config_path} labquorum registration has no command"
    if not isinstance(arguments, list) or not all(
        isinstance(argument, str) for argument in arguments
    ):
        return f"{config_path} labquorum registration args must be a string list"
    executable_names = [
        Path(command).name.casefold(),
        *(Path(arg).name.casefold() for arg in arguments),
    ]
    if not any(name in {"lq-mcp", "lq-mcp.exe"} for name in executable_names):
        return f"{config_path} labquorum registration does not launch lq-mcp"
    profile = _profile_argument(arguments)
    if profile != expected_profile:
        return f"{config_path} launches profile {profile!r}, expected {expected_profile!r}"
    return None


def _profile_argument(arguments: Sequence[str]) -> str | None:
    for index, argument in enumerate(arguments):
        if argument == "--profile" and index + 1 < len(arguments):
            return arguments[index + 1]
        if argument.startswith("--profile="):
            return argument.partition("=")[2]
    return None


def _run_setup_artifact_checks(gate: Gate, runtime_root: Path) -> None:
    for agent_name, profile in (("labops", "proposer"), ("pi-desk", "approver")):
        agent_directory = runtime_root / "agents" / agent_name
        if not agent_directory.is_dir():
            gate.fail(f"{agent_name} agent folder", f"missing generated folder: {agent_directory}")
            continue
        instruction_file = agent_directory / "AGENTS.md"
        if (
            not instruction_file.is_file()
            or not instruction_file.read_text(encoding="utf-8").strip()
        ):
            gate.fail(f"{agent_name} instructions", f"missing or empty file: {instruction_file}")
        else:
            print(f"PASS {agent_name} instructions")
        issue = _registered_profile(agent_directory, profile)
        if issue is not None:
            gate.fail(f"{agent_name} MCP registration", issue)
        else:
            print(f"PASS {agent_name} MCP registration uses {profile}")


def _run_template_checks(gate: Gate, template_path: Path, temp_root: Path) -> None:
    if not template_path.is_file():
        gate.fail("setup template", f"missing generated file: {template_path}")
        return
    gate.command(
        "valid generated template lint",
        ["uv", "run", "lq", "template", "lint", str(template_path)],
    )
    try:
        mutations = template_mutations(_load_yaml_template(template_path))
    except (RuntimeError, ValueError) as exc:
        gate.fail("template lint mutations", str(exc))
        return
    for name, value in mutations.items():
        mutation_path = temp_root / f"p3-invalid-{name}.yaml"
        mutation_path.write_text(
            yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        gate.expected_failure(
            f"template lint rejects {name}",
            ["uv", "run", "lq", "template", "lint", str(mutation_path)],
        )


def _load_probe_args() -> dict[str, Any]:
    try:
        value = json.loads(PROBE_ARGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"could not read P2 probe contract at {PROBE_ARGS_PATH}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("P2 probe contract must be a JSON object")
    for key in ("propose_booking", "get_request", "commit_booking"):
        if not isinstance(value.get(key), dict):
            raise RuntimeError(f"P2 probe contract is missing its {key} object")
    return value


@asynccontextmanager
async def _connect(
    profile: str, database: Path, binding: str | None = None
) -> AsyncIterator[ClientSession]:
    # MCP 1.x stdio/session APIs verified in .venv/Lib/site-packages/mcp/client/stdio/__init__.py:72-189 and client/session.py:113-160,386,532.
    args = ["run", "lq-mcp", *server_arguments(profile, database)]
    if binding is not None:
        args.extend(["--binding", binding])
    parameters = StdioServerParameters(command="uv", args=args, cwd=ROOT)
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        yield session


def _tool_payload(result: Any) -> tuple[dict[str, Any], str, bool]:
    structured = getattr(result, "structuredContent", None)
    texts = [
        block.text
        for block in getattr(result, "content", [])
        if isinstance(getattr(block, "text", None), str)
    ]
    text = "\n".join(texts)
    if isinstance(structured, Mapping):
        return dict(structured), text, bool(getattr(result, "isError", False))
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {"text": text}
    if isinstance(parsed, dict):
        return parsed, text, bool(getattr(result, "isError", False))
    return {"result": parsed}, text, bool(getattr(result, "isError", False))


def _render(value: Any, context: Mapping[str, Any]) -> Any:
    if isinstance(value, dict):
        if set(value) == {"$ref"}:
            reference = value["$ref"]
            if not isinstance(reference, str):
                raise ValueError("probe $ref values must be strings")
            current: Any = context
            for part in reference.split("."):
                if not isinstance(current, Mapping) or part not in current:
                    raise ValueError(f"unknown probe reference: {reference}")
                current = current[part]
            return copy.deepcopy(current)
        return {key: _render(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [_render(item, context) for item in value]
    return value


def _call_arguments(section: Mapping[str, Any], context: Mapping[str, Any]) -> dict[str, Any]:
    raw = section.get("arguments")
    if not isinstance(raw, dict):
        raise ValueError("P2 probe tool arguments must be an object")
    rendered = _render(raw, context)
    if not isinstance(rendered, dict):
        raise ValueError("rendered MCP tool arguments are not an object")
    return rendered


async def _invoke(
    session: ClientSession,
    section: Mapping[str, Any],
    default_tool: str,
    arguments: dict[str, Any],
) -> tuple[dict[str, Any], str, bool]:
    tool_name = section.get("tool", default_tool)
    if not isinstance(tool_name, str):
        raise ValueError(f"{default_tool}.tool must be a string")
    return _tool_payload(await session.call_tool(tool_name, arguments))


def _raise_if_error(result: tuple[dict[str, Any], str, bool], label: str) -> dict[str, Any]:
    payload, text, is_error = result
    if is_error:
        detail = json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n" + text
        raise RuntimeError(f"{label} returned an MCP error: {detail}")
    return payload


def _request_fields(payload: Mapping[str, Any], section: Mapping[str, Any]) -> dict[str, Any]:
    paths = section.get("request_paths")
    if not isinstance(paths, dict):
        raise ValueError("get_request.request_paths must be a JSON object")
    fields: dict[str, Any] = {}
    for name in ("request_id", "revision", "content_hash", "decision"):
        pointer = paths.get(name)
        if not isinstance(pointer, str):
            raise ValueError(f"get_request.request_paths.{name} must be a JSON Pointer")
        fields[name] = json_pointer(payload, pointer)
    if any(fields[name] is None for name in fields):
        raise ValueError("get_request did not return all fields needed for commit")
    return fields


def _distinct_proposal_arguments(arguments: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(arguments))
    start = changed.get("start")
    end = changed.get("end")
    if not isinstance(start, str) or not isinstance(end, str):
        raise ValueError(
            "P2 proposal contract needs ISO start and end values for a distinct request"
        )
    try:
        changed["start"] = (datetime.fromisoformat(start) + timedelta(hours=2)).isoformat()
        changed["end"] = (datetime.fromisoformat(end) + timedelta(hours=2)).isoformat()
    except ValueError as exc:
        raise ValueError("P2 proposal start and end must be ISO datetimes") from exc
    if changed == arguments:
        raise ValueError("could not construct a distinct second proposal")
    return changed


async def _propose_two_requests(template: Mapping[str, Any], database: Path) -> tuple[str, str]:
    proposal_section = template["propose_booking"]
    if not isinstance(proposal_section, dict):
        raise ValueError("propose_booking probe section must be an object")
    context: dict[str, Any] = {"proposal": {}, "request": {}}
    first_args = _call_arguments(proposal_section, context)
    second_args = _distinct_proposal_arguments(first_args)
    request_ids: list[str] = []
    async with _connect("proposer", database) as proposer:
        for args in (first_args, second_args):
            payload = _raise_if_error(
                await _invoke(proposer, proposal_section, "propose_booking", args),
                "propose_booking",
            )
            request_id_path = proposal_section.get("request_id_path")
            if not isinstance(request_id_path, str):
                raise ValueError("propose_booking.request_id_path must be a JSON Pointer")
            request_id = json_pointer(payload, request_id_path)
            if not isinstance(request_id, str) or not request_id:
                raise ValueError("propose_booking did not return a request ID")
            request_ids.append(request_id)
    if request_ids[0] == request_ids[1]:
        raise RuntimeError("the two proposals returned the same request ID")
    print("PASS proposer created two distinct requests")
    return request_ids[0], request_ids[1]


async def _get_request(
    session: ClientSession,
    template: Mapping[str, Any],
    request_id: str,
) -> dict[str, Any]:
    getter = template["get_request"]
    if not isinstance(getter, dict):
        raise ValueError("get_request probe section must be an object")
    context = {"proposal": {"request_id": request_id}, "request": {}}
    payload = _raise_if_error(
        await _invoke(session, getter, "get_request", _call_arguments(getter, context)),
        "get_request",
    )
    fields = _request_fields(payload, getter)
    if fields["request_id"] != request_id:
        raise RuntimeError("get_request returned a different request ID")
    return fields


def _commit_arguments(
    template: Mapping[str, Any], request: Mapping[str, Any]
) -> tuple[Mapping[str, Any], dict[str, Any]]:
    committer = template["commit_booking"]
    if not isinstance(committer, dict):
        raise ValueError("commit_booking probe section must be an object")
    context = {"proposal": {}, "request": dict(request)}
    arguments = _call_arguments(committer, context)
    for name in ("request_id", "revision", "content_hash", "decision"):
        if arguments.get(name) != request.get(name):
            raise RuntimeError(f"commit_booking did not echo the exact request {name}")
    return committer, arguments


async def _certify_commit_probe(template: Mapping[str, Any], database: Path) -> None:
    first_id, second_id = await _propose_two_requests(template, database)
    async with _connect("approver", database, binding="certify") as approver:
        names = extract_tool_names(await approver.list_tools())
        issue = binding_tool_exposure_issue(names, expected=True)
        if issue is not None:
            raise RuntimeError(issue)
        print("PASS certify mode exposes commit_booking")

        first_request = await _get_request(approver, template, first_id)
        second_request = await _get_request(approver, template, second_id)
        committer, first_args = _commit_arguments(template, first_request)
        payload = _raise_if_error(
            await _invoke(approver, committer, "commit_booking", first_args),
            "first commit_booking",
        )
        result_paths = committer.get("result_paths")
        if not isinstance(result_paths, dict) or not isinstance(result_paths.get("status"), str):
            raise ValueError("commit_booking.result_paths.status must be a JSON Pointer")
        first_status = json_pointer(payload, result_paths["status"])
        if first_status != committer.get("committed_value"):
            raise RuntimeError(
                f"first commit status was {first_status!r}, expected {committer.get('committed_value')!r}"
            )
        print("PASS certify mode committed one request")

        _, second_args = _commit_arguments(template, second_request)
        second_payload, second_text, second_error = await _invoke(
            approver, committer, "commit_booking", second_args
        )
        code = error_code(second_payload, second_text)
        if not second_error or code != DISTINCT_COMMIT_ERROR:
            raise RuntimeError(
                "second distinct commit was not refused with "
                f"{DISTINCT_COMMIT_ERROR}: {second_payload!r} {second_text}"
            )
        print(f"PASS distinct second commit refused with {DISTINCT_COMMIT_ERROR}")

        retry_payload = _raise_if_error(
            await _invoke(approver, committer, "commit_booking", first_args),
            "identical commit retry",
        )
        retry_status = json_pointer(retry_payload, result_paths["status"])
        idempotent_values = committer.get("idempotent_values")
        if not isinstance(idempotent_values, list) or retry_status not in idempotent_values:
            raise RuntimeError(
                f"identical retry status {retry_status!r} is not listed as idempotent"
            )
        print("PASS identical commit retry is idempotent")


async def _check_on_without_evidence(database: Path) -> None:
    try:
        async with _connect("approver", database, binding="on") as server:
            names = extract_tool_names(await server.list_tools())
            issue = binding_tool_exposure_issue(names, expected=False)
            if issue is not None:
                raise RuntimeError(issue)
            print("PASS binding on without evidence exposes no commit_booking")
    except Exception as exc:
        detail = _exception_detail(exc)
        normalized = detail.casefold()
        unsupported = "unrecognized arguments" in normalized or "no such option" in normalized
        refuses_binding = "binding" in normalized and any(
            word in normalized for word in ("evidence", "certif", "disabled", "refus")
        )
        if refuses_binding and not unsupported:
            print(f"PASS binding on without evidence refused to start: {detail}")
            return
        raise RuntimeError(
            f"binding on without evidence failed for another reason: {detail}"
        ) from exc


async def _stdio_probe(database: Path) -> None:
    async with _connect("approver", database) as approver:
        names = extract_tool_names(await approver.list_tools())
        issue = binding_tool_exposure_issue(names, expected=False)
        if issue is not None:
            raise RuntimeError(issue)
        print("PASS default approver profile hides commit_booking")
    template = _load_probe_args()
    await _certify_commit_probe(template, database)
    await _check_on_without_evidence(database)


def _run_live_check(gate: Gate, runtime_root: Path | None) -> None:
    args = ["uv", "run", "python", "scripts/gates/p3_live_check.py"]
    if runtime_root is not None:
        args.extend(["--runtime-root", str(runtime_root)])
    gate.command("P3 live Switch wiring", args)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="check the running Switch Console")
    parser.add_argument(
        "--runtime-root",
        type=Path,
        help="runtime root to check in live mode; defaults to the lq setup root",
    )
    args = parser.parse_args(argv)

    gate = Gate()
    gate.command(
        "common gate p3",
        ["uv", "run", "python", "scripts/gates/common.py", "--phase", "p3"],
    )

    with tempfile.TemporaryDirectory(prefix="labquorum-p3-") as temp_name:
        runtime_root = Path(temp_name).resolve()
        setup_succeeded = gate.command(
            "lq setup",
            ["uv", "run", "lq", "setup", "--runtime-root", str(runtime_root)],
        )
        if setup_succeeded:
            gate.expected_failure(
                "lq setup rejects a worktree root",
                [
                    "uv",
                    "run",
                    "lq",
                    "setup",
                    "--runtime-root",
                    str(runtime_root / ".claude" / "worktrees" / "blocked"),
                ],
            )
            gate.expected_failure(
                "lq setup rejects a OneDrive root",
                [
                    "uv",
                    "run",
                    "lq",
                    "setup",
                    "--runtime-root",
                    str(runtime_root / "OneDrive" / "blocked"),
                ],
            )
        _run_setup_artifact_checks(gate, runtime_root)
        _run_template_checks(
            gate,
            runtime_root / "switch" / "labquorum.template.yaml",
            runtime_root,
        )
        gate.command(
            "lq doctor",
            ["uv", "run", "lq", "doctor", "--runtime-root", str(runtime_root)],
        )

        database = runtime_root / "p3-test-ledger.sqlite"
        initialized = gate.command(
            "initialize temporary test ledger",
            ["uv", "run", "lq", "init", "--db", str(database)],
        )
        seeded = gate.command(
            "seed temporary test ledger",
            [
                "uv",
                "run",
                "lq",
                "seed",
                "--demo",
                "--db",
                str(database),
                "--anchor-date",
                "2026-11-06",
            ],
        )
        if initialized and seeded:
            try:
                asyncio.run(_stdio_probe(database))
            except Exception as exc:
                gate.fail("P3 MCP stdio probe", _exception_detail(exc))
        else:
            print("SKIP P3 MCP stdio probe: temporary test ledger could not be prepared")

    if args.live:
        _run_live_check(gate, args.runtime_root)

    if gate.failures:
        print(f"FAIL P3 gate: {gate.failures} check(s) failed")
        return 1
    print("PASS P3 gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
