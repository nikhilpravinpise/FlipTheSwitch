"""Verify P3 agents against a running Switch Console over its CDP RPC bridge."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SWITCH_RPC = ROOT / "scripts" / "ops" / "switch_rpc.py"
DEFAULT_CDP_URL = "http://127.0.0.1:9333"
EXPECTED = {
    "labops": {
        "provider": "codex",
        "model": "gpt-6-luna",
        "effort": "high",
        "addressing": "anyone",
    },
    "pi-desk": {
        "provider": "codex",
        "model": "gpt-6-luna",
        "effort": "high",
        "addressing": "ownerAndAgents",
    },
}


def _path_has_forbidden_segment(path: Path) -> str | None:
    parts = [part.casefold() for part in path.parts]
    if any("onedrive" in part for part in parts):
        return "path is inside OneDrive"
    if any(
        parts[index : index + 2] == [".claude", "worktrees"]
        for index in range(max(0, len(parts) - 1))
    ):
        return "path is inside .claude/worktrees"
    return None


def directory_issue(directory: str | Path | None, runtime_root: Path) -> str | None:
    """Explain why a Switch agent directory is outside the stable runtime root."""
    if directory is None or not str(directory).strip():
        return "directory is missing"
    candidate = Path(directory).expanduser()
    root = runtime_root.expanduser()
    if not candidate.is_absolute() or not root.is_absolute():
        return f"agent directory and runtime root must be absolute: {candidate}; {root}"
    candidate = candidate.resolve(strict=False)
    root = root.resolve(strict=False)
    for path in (root, candidate):
        forbidden = _path_has_forbidden_segment(path)
        if forbidden is not None:
            return forbidden
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        return f"directory is not under runtime root {root}: {candidate}"
    if not relative.parts:
        return "agent directory must be below the runtime root"
    return None


def addressing_mode(policy: Any) -> str:
    """Read the Switch AddressingPolicy chooser mode from its wire shape."""
    # Mirrors v0.40.1 owner-policy.ts:99-107 and switch-servers.ts:900-908.
    if policy is None:
        return "anyone"
    if not isinstance(policy, Mapping):
        return "custom"
    rules = policy.get("rules")
    if not isinstance(rules, list):
        return "custom"
    if not rules:
        return "anyone"
    if len(rules) != 1 or not isinstance(rules[0], Mapping):
        return "custom"
    return _single_rule_addressing_mode(rules[0])


def _single_rule_addressing_mode(rule: Mapping[str, Any]) -> str:
    if rule.get("rooms") != "*" or rule.get("room_groups") != "*":
        return "custom"
    users = rule.get("users")
    agents = rule.get("agents")
    owner = rule.get("owner") is True
    owner_agents = rule.get("owner_agents") is True
    if rule.get("owner") is False and not owner_agents and users == "*" and agents == "*":
        return "anyone"
    if owner and users == [] and agents == []:
        return "ownerAndAgents" if owner_agents else "owner"
    return "custom"


def agent_matches(name: Any, expected_name: str) -> bool:
    """Match a base name or a Switch name prefixed with a user or project key."""
    if not isinstance(name, str):
        return False
    return name == expected_name or name.endswith(f"-{expected_name}")


def _default_runtime_root() -> Path:
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA is unset; pass --runtime-root explicitly")
        return Path(local_app_data) / "LabQuorum"
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        return Path(data_home) / "labquorum"
    return Path.home() / ".local" / "share" / "labquorum"


def _rpc(procedure: str, arguments: Sequence[Any], cdp_url: str) -> Any:
    """Call a reviewed Switch Console RPC procedure over its CDP renderer bridge."""
    json_args = json.dumps(list(arguments), ensure_ascii=True, separators=(",", ":"))
    command = [
        "uv",
        "run",
        "--no-project",
        "--with",
        "playwright",
        "python",
        str(SWITCH_RPC),
        "--cdp-url",
        cdp_url,
        "call",
        procedure,
        json_args,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"could not start Switch RPC {procedure}: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr + result.stdout).strip()
        raise RuntimeError(f"Switch RPC {procedure} exited {result.returncode}: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Switch RPC {procedure} returned invalid JSON: {exc}") from exc


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise RuntimeError(f"Switch RPC {label} did not return a list")
    return value


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"Switch response is missing {label}")
    return value


def _server_ids(cdp_url: str) -> list[str]:
    # Switch v0.40.1 exposes switchServers.listServers in
    # console/apps/switch-console-desktop/src/main/core/switch-servers/controller.ts:267.
    servers = _require_list(
        _rpc("switchServers.listServers", [], cdp_url), "switchServers.listServers"
    )
    server_ids = [
        server["id"]
        for server in servers
        if isinstance(server, Mapping) and isinstance(server.get("id"), str)
    ]
    if not server_ids:
        raise RuntimeError("Switch Console has no registered Switch servers")
    return server_ids


def _managed_agents(cdp_url: str) -> list[dict[str, Any]]:
    # The v0.40.1 RPC router registers managedAgents in main/rpc.ts:59; its
    # list(serverId) result includes provider, model, advancedConfig, mode flags,
    # directory and status in main/core/managed-agents/controller.ts:75-115.
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for server_id in _server_ids(cdp_url):
        try:
            result = _rpc("managedAgents.list", [server_id], cdp_url)
        except RuntimeError as exc:
            errors.append(f"{server_id}: {exc}")
            continue
        if result is None:
            continue
        managed = _require_list(result, f"managedAgents.list({server_id})")
        entries.extend(entry for entry in managed if isinstance(entry, dict))
    if not entries and errors:
        raise RuntimeError(
            "could not read managed agents from any Switch server: " + "; ".join(errors)
        )
    return entries


def _workspace_agent(
    workspace_id: str, agent_id: str, agent_name: str, cdp_url: str
) -> Mapping[str, Any] | None:
    # workspaces.listAgents is registered at v0.40.1
    # console/apps/switch-console-desktop/src/main/core/workspaces/controller.ts:448-449.
    remote_agents = _require_list(
        _rpc("workspaces.listAgents", [workspace_id], cdp_url),
        f"workspaces.listAgents({workspace_id})",
    )
    for remote in remote_agents:
        if isinstance(remote, Mapping) and remote.get("id") == agent_id:
            return remote
    for remote in remote_agents:
        if isinstance(remote, Mapping) and remote.get("name") == agent_name:
            return remote
    return None


def _validate_agent(
    agent: Mapping[str, Any], expected_name: str, runtime_root: Path, cdp_url: str
) -> list[str]:
    name = str(agent.get("name", "<unnamed>"))
    definition = agent.get("definition")
    if not isinstance(definition, Mapping):
        return [f"{name}: Switch managed-agent definition is missing"]
    expected = EXPECTED[expected_name]
    return [
        *_configuration_problems(name, definition, expected),
        *_directory_problems(agent, definition, name, runtime_root),
        *_addressing_problems(agent, name, expected, cdp_url),
    ]


def _configuration_problems(
    name: str, definition: Mapping[str, Any], expected: Mapping[str, str]
) -> list[str]:
    problems: list[str] = []
    for key in ("provider", "model"):
        if definition.get(key) != expected[key]:
            problems.append(
                f"{name}: expected {key}={expected[key]!r}, got {definition.get(key)!r}"
            )
    advanced = definition.get("advancedConfig")
    effort = advanced.get("effort") if isinstance(advanced, Mapping) else None
    if effort != expected["effort"]:
        problems.append(f"{name}: expected effort='high', got {effort!r}")
    for key, label in (("autoMode", "auto mode"), ("autoApprove", "auto approve")):
        if definition.get(key) is not False:
            problems.append(f"{name}: {label} must be off")
    return problems


def _directory_problems(
    agent: Mapping[str, Any],
    definition: Mapping[str, Any],
    name: str,
    runtime_root: Path,
) -> list[str]:
    problems: list[str] = []
    configured_directory = definition.get("directory")
    issue = directory_issue(configured_directory, runtime_root)
    if issue is not None:
        problems.append(f"{name}: configured {issue}")
    status = agent.get("status")
    if isinstance(status, Mapping) and status.get("directory") is not None:
        issue = directory_issue(status.get("directory"), runtime_root)
        if issue is not None:
            problems.append(f"{name}: active {issue}")
    return problems


def _addressing_problems(
    agent: Mapping[str, Any],
    name: str,
    expected: Mapping[str, str],
    cdp_url: str,
) -> list[str]:
    workspace_id = agent.get("workspaceId")
    agent_id = agent.get("agentId")
    if not isinstance(workspace_id, str) or not isinstance(agent_id, str):
        return [f"{name}: Switch workspace or agent identity is missing"]
    remote = _workspace_agent(workspace_id, agent_id, name, cdp_url)
    if remote is None:
        return [f"{name}: agent is absent from the Switch workspace API"]
    mode = addressing_mode(remote.get("addressingPolicy"))
    if mode != expected["addressing"]:
        return [f"{name}: expected addressing={expected['addressing']!r}, got {mode!r}"]
    return []


def _check_named_agent(
    agents: Sequence[Mapping[str, Any]], target: str, runtime_root: Path, cdp_url: str
) -> list[str]:
    matches = [agent for agent in agents if agent_matches(agent.get("name"), target)]
    if not matches:
        return [f"Switch agent {target!r} does not exist"]
    if len(matches) != 1:
        return [f"Switch agent {target!r} is ambiguous: {len(matches)} prefixed or exact matches"]
    issues = _validate_agent(matches[0], target, runtime_root, cdp_url)
    if not issues:
        print(f"PASS live Switch agent {matches[0].get('name')}")
    return issues


def _check_switch_buddy(agents: Sequence[Mapping[str, Any]]) -> list[str]:
    matches = [agent for agent in agents if agent_matches(agent.get("name"), "switch-buddy-admin")]
    for agent in matches:
        definition = agent.get("definition")
        if not isinstance(definition, Mapping):
            return ["switch-buddy-admin is present but its provider cannot be verified"]
        is_claude = definition.get("provider") in {"claude", "claude-code"}
        stopped = agent.get("desiredState") == "stopped"
        if is_claude and not stopped:
            return [
                "switch-buddy-admin uses Claude Code and is not stopped "
                f"(desiredState={agent.get('desiredState')!r})"
            ]
    if matches:
        print("PASS switch-buddy-admin is not running on Claude Code, or is stopped")
    else:
        print("PASS switch-buddy-admin is absent")
    return []


def _check_live(runtime_root: Path, cdp_url: str) -> list[str]:
    agents = _managed_agents(cdp_url)
    problems: list[str] = []
    for target in EXPECTED:
        problems.extend(_check_named_agent(agents, target, runtime_root, cdp_url))
    problems.extend(_check_switch_buddy(agents))
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    args = parser.parse_args(argv)
    try:
        runtime_root = args.runtime_root or _default_runtime_root()
        problems = _check_live(runtime_root, args.cdp_url)
    except Exception as exc:
        print(f"FAIL P3 live check: {exc}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(f"FAIL P3 live check: {problem}")
        return 1
    print("PASS P3 live Switch wiring")
    return 0


if __name__ == "__main__":
    sys.exit(main())
