"""Exercise the P2 MCP server over the official MCP stdio client."""

from __future__ import annotations

import asyncio
import copy
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Verified against MCP 1.30.0 installed source: .venv/Lib/site-packages/mcp/client/stdio/__init__.py:72,106,189 and mcp/client/session.py:113,122,160,386,532.
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "tests" / "contract" / "p2_probe_args.json"
EXPECTED_TOOLS_PATH = ROOT / "scripts" / "gates" / "p2_expected_tools.json"
REQUIRED_ERROR_CODES = {"STALE_REQUEST", "DECISION_MISMATCH"}


@asynccontextmanager
async def _connect(profile: str, database: Path) -> AsyncIterator[ClientSession]:
    parameters = StdioServerParameters(
        command="uv",
        args=["run", "lq-mcp", "--profile", profile, "--db", str(database)],
        cwd=ROOT,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        yield session


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"could not read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must contain a JSON object")
    return value


def _check_template(template: dict[str, Any]) -> None:
    required = {"propose_booking", "get_request", "commit_booking"}
    missing = sorted(required - template.keys())
    if missing:
        raise RuntimeError(f"probe args template is missing sections: {', '.join(missing)}")
    proposal = template["propose_booking"]
    getter = template["get_request"]
    committer = template["commit_booking"]
    if (
        not isinstance(proposal, dict)
        or not isinstance(getter, dict)
        or not isinstance(committer, dict)
    ):
        raise RuntimeError("propose_booking, get_request and commit_booking must be JSON objects")
    if not isinstance(proposal.get("arguments"), dict):
        raise RuntimeError(
            "propose_booking.arguments must define the builder's exact call arguments"
        )
    if not isinstance(getter.get("arguments"), dict):
        raise RuntimeError("get_request.arguments must define the builder's exact call arguments")
    if not isinstance(committer.get("arguments"), dict):
        raise RuntimeError(
            "commit_booking.arguments must define the builder's exact call arguments"
        )
    for section, required_keys in (
        (proposal, {"request_id_path"}),
        (getter, {"request_paths"}),
        (committer, {"result_paths", "committed_value", "idempotent_values"}),
    ):
        if not required_keys.issubset(section):
            raise RuntimeError(
                f"probe args section is missing: {', '.join(sorted(required_keys - section.keys()))}"
            )
    paths = getter["request_paths"]
    if (
        not isinstance(paths, dict)
        or not {"request_id", "revision", "content_hash"}.issubset(paths)
        or not ({"decision", "commit_arguments"} & paths.keys())
    ):
        raise RuntimeError(
            "get_request.request_paths must locate id, revision, content_hash and either "
            "decision (nested contract) or commit_arguments (flat card contract)"
        )
    if "commit_arguments" in paths and not isinstance(committer.get("tampered_field_path"), str):
        raise RuntimeError(
            "flat card contract requires commit_booking.tampered_field_path (a JSON Pointer "
            "to a decision field other than request_id, revision or content_hash)"
        )
    result_paths = committer["result_paths"]
    if not isinstance(result_paths, dict) or not isinstance(result_paths.get("status"), str):
        raise RuntimeError("commit_booking.result_paths.status must be a JSON Pointer")
    if not isinstance(committer["idempotent_values"], list):
        raise RuntimeError("commit_booking.idempotent_values must be a list")
    codes = committer.get("error_codes", sorted(REQUIRED_ERROR_CODES))
    if not isinstance(codes, list) or not codes or not set(codes).issubset(REQUIRED_ERROR_CODES):
        raise RuntimeError(
            "commit_booking.error_codes must list STALE_REQUEST and/or DECISION_MISMATCH"
        )


def _run_cli(args: list[str], label: str) -> None:
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"could not start {label}: {exc}") from exc
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)
    if result.returncode != 0:
        raise RuntimeError(f"{label} exited {result.returncode}")
    print(f"PASS {label}")


def _pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError(f"JSON Pointer must be empty or start with '/': {pointer}")
    current = document
    for raw_segment in pointer[1:].split("/"):
        segment = raw_segment.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            current = current[segment]
        elif isinstance(current, list):
            current = current[int(segment)]
        else:
            raise ValueError(f"JSON Pointer {pointer} does not resolve")
    return current


def _render(value: Any, context: Mapping[str, Any]) -> Any:
    if isinstance(value, dict):
        if set(value) == {"$ref"}:
            reference = value["$ref"]
            if not isinstance(reference, str):
                raise ValueError("$ref values must be strings")
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


def _tool_payload(result: Any) -> tuple[dict[str, Any], str, bool]:
    structured = result.structuredContent
    texts = [
        block.text for block in result.content if isinstance(getattr(block, "text", None), str)
    ]
    text = "\n".join(texts)
    if structured is not None:
        return dict(structured), text, bool(result.isError)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {"text": text}
    if isinstance(parsed, dict):
        return parsed, text, bool(result.isError)
    return {"result": parsed}, text, bool(result.isError)


def _call_error(payload: Mapping[str, Any], text: str) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n" + text


def _call_arguments(section: Mapping[str, Any], context: Mapping[str, Any]) -> dict[str, Any]:
    raw = section.get("arguments")
    if not isinstance(raw, dict):
        raise ValueError("tool arguments must be an object")
    rendered = _render(raw, context)
    if not isinstance(rendered, dict):
        raise ValueError("rendered tool arguments are not an object")
    return rendered


async def _invoke(
    session: ClientSession, section: Mapping[str, Any], default_tool: str, args: dict[str, Any]
) -> tuple[dict[str, Any], str, bool]:
    tool_name = section.get("tool", default_tool)
    if not isinstance(tool_name, str):
        raise ValueError(f"{default_tool}.tool must be a string")
    result = await session.call_tool(tool_name, args)
    return _tool_payload(result)


async def _verify_tool_sets(expected: dict[str, Any], database: Path) -> None:
    for profile in ("proposer", "approver", "unavailable"):
        expected_names = expected.get(profile)
        if not isinstance(expected_names, list) or not all(
            isinstance(name, str) for name in expected_names
        ):
            raise RuntimeError(f"expected tool list for profile {profile!r} is missing or invalid")
        async with _connect(profile, database) as session:
            listing = await session.list_tools()
        actual_names = [tool.name for tool in listing.tools]
        if len(actual_names) != len(set(actual_names)) or set(actual_names) != set(expected_names):
            raise RuntimeError(
                f"profile {profile} tools differ: expected {sorted(expected_names)}, "
                f"received {sorted(actual_names)}"
            )
        print(f"PASS MCP tool list {profile}: {', '.join(sorted(actual_names))}")


def _echoed_fields(payload: Mapping[str, Any], paths: Mapping[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    fields = ("request_id", "revision", "content_hash") + tuple(
        name for name in ("decision", "commit_arguments") if name in paths
    )
    for field in fields:
        pointer = paths[field]
        if not isinstance(pointer, str):
            raise ValueError(f"get_request.request_paths.{field} must be a JSON Pointer")
        # The empty JSON Pointer refers to the whole document (RFC 6901 section 5).
        values[field] = payload if pointer == "" else _pointer(payload, pointer)
    if any(values[field] is None for field in fields):
        raise ValueError("get_request did not return all fields required for a commit")
    return values


def _mutate_value(value: Any) -> Any:
    if isinstance(value, str):
        return value + "_tampered"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    if value is None:
        return "tampered"
    if isinstance(value, dict):
        for key, child in value.items():
            try:
                value[key] = _mutate_value(child)
                return value
            except ValueError:
                continue
    if isinstance(value, list):
        for index, child in enumerate(value):
            try:
                value[index] = _mutate_value(child)
                return value
            except ValueError:
                continue
    raise ValueError("decision has no scalar field to tamper")


def _tamper_decision(decision: Any, pointer: str | None) -> Any:
    changed = copy.deepcopy(decision)
    if pointer:
        if not pointer.startswith("/"):
            raise ValueError("tampered_decision_path must be a JSON Pointer")
        segments = pointer[1:].split("/")
        parent = changed
        for segment in segments[:-1]:
            parent = _pointer(parent, "/" + segment)
        leaf = segments[-1].replace("~1", "/").replace("~0", "~")
        if isinstance(parent, dict):
            if leaf not in parent:
                raise ValueError(f"tampered_decision_path does not exist: {pointer}")
            parent[leaf] = _mutate_value(parent[leaf])
        elif isinstance(parent, list):
            index = int(leaf)
            parent[index] = _mutate_value(parent[index])
        else:
            raise ValueError(f"tampered_decision_path does not resolve: {pointer}")
        return changed
    return _mutate_value(changed)


async def _round_trip(template: dict[str, Any], database: Path) -> None:
    proposal_section = template["propose_booking"]
    getter_section = template["get_request"]
    committer_section = template["commit_booking"]
    if not isinstance(proposal_section, dict) or not isinstance(getter_section, dict):
        raise RuntimeError("probe tool sections must be objects")
    if not isinstance(committer_section, dict):
        raise RuntimeError("commit_booking probe section must be an object")

    context: dict[str, Any] = {"proposal": {}, "request": {}}
    async with _connect("proposer", database) as proposer:
        proposal_payload, proposal_text, proposal_error = await _invoke(
            proposer,
            proposal_section,
            "propose_booking",
            _call_arguments(proposal_section, context),
        )
    if proposal_error:
        raise RuntimeError(
            f"propose_booking returned an MCP error: {_call_error(proposal_payload, proposal_text)}"
        )
    request_id_path = proposal_section["request_id_path"]
    if not isinstance(request_id_path, str):
        raise RuntimeError("propose_booking.request_id_path must be a JSON Pointer")
    context["proposal"]["request_id"] = _pointer(proposal_payload, request_id_path)
    print("PASS proposer propose_booking")

    async with _connect("approver", database) as approver:
        request_payload, request_text, request_error = await _invoke(
            approver,
            getter_section,
            "get_request",
            _call_arguments(getter_section, context),
        )
        if request_error:
            raise RuntimeError(
                f"get_request returned an MCP error: {_call_error(request_payload, request_text)}"
            )
        request_paths = getter_section["request_paths"]
        if not isinstance(request_paths, dict):
            raise RuntimeError("get_request.request_paths must be a JSON object")
        echoed = _echoed_fields(request_payload, request_paths)
        if echoed["request_id"] != context["proposal"]["request_id"]:
            raise RuntimeError("get_request returned a different request ID than propose_booking")
        context["request"].update(echoed)
        flat = "commit_arguments" in echoed
        if flat:
            commit_args = copy.deepcopy(echoed["commit_arguments"])
            if not isinstance(commit_args, dict):
                raise RuntimeError("get_request commit_arguments must be a JSON object")
        else:
            commit_args = _call_arguments(committer_section, context)
        for field in ("request_id", "revision", "content_hash") + (() if flat else ("decision",)):
            if commit_args.get(field) != echoed[field]:
                raise RuntimeError(f"commit_booking did not echo the exact get_request {field}")

        first_payload, first_text, first_error = await _invoke(
            approver, committer_section, "commit_booking", commit_args
        )
        if first_error:
            raise RuntimeError(f"commit_booking failed: {_call_error(first_payload, first_text)}")
        result_paths = committer_section["result_paths"]
        if not isinstance(result_paths, dict):
            raise RuntimeError("commit_booking.result_paths must be an object")
        status_path = result_paths["status"]
        first_status = _pointer(first_payload, status_path)
        committed_value = committer_section["committed_value"]
        if first_status != committed_value:
            raise RuntimeError(
                f"first commit status was {first_status!r}, expected {committed_value!r}"
            )
        print("PASS approver commit_booking")

        second_payload, second_text, second_error = await _invoke(
            approver, committer_section, "commit_booking", commit_args
        )
        if second_error:
            raise RuntimeError(
                f"idempotent second commit failed: {_call_error(second_payload, second_text)}"
            )
        second_status = _pointer(second_payload, status_path)
        idempotent_values = committer_section["idempotent_values"]
        if second_status not in idempotent_values:
            raise RuntimeError(
                f"second commit status was {second_status!r}, expected one of {idempotent_values!r}"
            )
        print("PASS approver commit_booking idempotent repeat")

        if flat:
            tampered_field = str(committer_section["tampered_field_path"])
            if tampered_field.lstrip("/") in {"request_id", "revision", "content_hash"}:
                raise RuntimeError("tampered_field_path must name a decision field")
            tampered_args = _tamper_decision(commit_args, tampered_field)
        else:
            tampered_args = copy.deepcopy(commit_args)
            tampered_args["decision"] = _tamper_decision(
                echoed["decision"], committer_section.get("tampered_decision_path")
            )
        tampered_payload, tampered_text, tampered_error = await _invoke(
            approver, committer_section, "commit_booking", tampered_args
        )
        error_blob = _call_error(tampered_payload, tampered_text)
        allowed_codes = committer_section.get("error_codes", sorted(REQUIRED_ERROR_CODES))
        found = {code for code in allowed_codes if re.search(rf"\b{re.escape(code)}\b", error_blob)}
        if not tampered_error and not found:
            raise RuntimeError("tampered decision unexpectedly succeeded")
        if not found:
            raise RuntimeError(
                "tampered decision did not return STALE_REQUEST or DECISION_MISMATCH: " + error_blob
            )
        print(f"PASS tampered decision rejected with {sorted(found)[0]}")


async def _run_probe(database: Path) -> None:
    expected = _load_json(EXPECTED_TOOLS_PATH, "expected MCP tool manifest")
    await _verify_tool_sets(expected, database)


def main() -> int:
    if not TEMPLATE_PATH.is_file():
        print(
            "FAIL P2 stdio probe: tests/contract/p2_probe_args.json is missing; "
            "the P2 builder must provide the exact tool argument template"
        )
        return 1
    try:
        template = _load_json(TEMPLATE_PATH, "P2 probe argument template")
        _check_template(template)
        with tempfile.TemporaryDirectory(prefix="labquorum-p2-") as temp_name:
            database = Path(temp_name) / "g.sqlite"
            _run_cli(["uv", "run", "lq", "init", "--db", str(database)], "lq init")
            _run_cli(
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
                "lq seed --demo",
            )
            asyncio.run(_run_probe(database))
            asyncio.run(_round_trip(template, database))
    except Exception as exc:
        print(f"FAIL P2 stdio probe: {exc}")
        return 1
    print("PASS P2 stdio probe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
