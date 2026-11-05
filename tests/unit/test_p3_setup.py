"""P3 Codex setup, template, doctor, and binding requirements."""

from __future__ import annotations

import json
import sqlite3
import tomllib
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import pytest
import yaml

from labquorum.cli import main as cli_module
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.mcp import server as server_module
from labquorum.mcp.profiles import Profile


def _run_lq(arguments: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = cli_module.main(arguments)
    except SystemExit as exc:
        status = int(exc.code or 0)
    return status, stdout.getvalue(), stderr.getvalue()


def _setup(root: Path) -> dict[str, Any]:
    status, stdout, stderr = _run_lq(["setup", "--runtime-root", str(root)])
    assert status == 0, f"lq setup failed: {stdout}{stderr}"
    value = json.loads(stdout)
    assert isinstance(value, dict)
    return value


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as config_file:
        return tomllib.load(config_file)


def test_C_04_setup_sets_prompt_for_commit_booking_only(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _setup(root)

    user_config = _load_toml(root / "codex" / "source-home-config.toml")
    server = user_config["mcp_servers"]["labquorum"]
    assert server["tools"]["commit_booking"]["approval_mode"] == "prompt"
    assert "default_tools_approval_mode" not in server
    assert server["args"] == [
        "--runtime-root",
        str(root.resolve()),
        "--db",
        str((root / "ledger.sqlite").resolve()),
    ]


def test_C_05_per_agent_configs_expose_only_their_booking_profile(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _setup(root)

    labops = _load_toml(root / "agents" / "labops" / ".codex" / "config.toml")
    pi_desk = _load_toml(root / "agents" / "pi-desk" / ".codex" / "config.toml")
    assert labops["mcp_servers"]["labquorum"]["args"][1] == "proposer"
    assert pi_desk["mcp_servers"]["labquorum"]["args"][1] == "approver"
    assert "--binding" not in labops["mcp_servers"]["labquorum"]["args"]
    assert pi_desk["mcp_servers"]["labquorum"]["args"][-2:] == ["--binding", "off"]


def test_C_06_home_registration_is_cwd_scoped_and_restricts_codex_tools(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _setup(root)

    source_config = _load_toml(root / "codex" / "source-home-config.toml")
    assert "switch" not in source_config["mcp_servers"]
    assert source_config["features"]["shell_tool"] is False
    assert source_config["web_search"] == "disabled"
    assert source_config["sandbox_mode"] == "read-only"
    assert "--profile" not in source_config["mcp_servers"]["labquorum"]["args"]
    resolve_profile = getattr(server_module, "resolve_runtime_profile", None)
    assert callable(resolve_profile), "the server needs a cwd-scoped profile resolver"
    assert resolve_profile(None, root, root / "agents" / "labops") is Profile.PROPOSER
    assert resolve_profile(None, root, root / "agents" / "pi-desk") is Profile.APPROVER
    assert resolve_profile(None, root, tmp_path) is None


def test_C_07_template_lint_enforces_provider_model_effort_and_addressing(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    _setup(root)
    template_path = root / "switch" / "labquorum.template.yaml"
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    assert isinstance(template, dict)
    lint = getattr(cli_module, "lint_template_file", None)
    assert callable(lint), "lq template lint must enforce the Codex template contract"
    assert lint(template_path) == []

    for agent, field, value in (
        ("labops", "provider", "claude"),
        ("labops", "model", "gpt-6-test-invalid"),
        ("labops", "effort", "medium"),
        ("pi-desk", "addressing", "anyone"),
    ):
        changed = yaml.safe_load(yaml.safe_dump(template, sort_keys=False))
        target = next(entry for entry in changed["agents"] if entry["name"].endswith(agent))
        if field == "effort":
            target["advanced_config"][field] = value
        else:
            target[field] = value
        changed_path = tmp_path / f"invalid-{agent}-{field}.yaml"
        changed_path.write_text(yaml.safe_dump(changed, sort_keys=False), encoding="utf-8")
        assert lint(changed_path)


def test_C_08_template_lint_rejects_bad_names_mentions_and_em_dash(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _setup(root)
    template_path = root / "switch" / "labquorum.template.yaml"
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    assert isinstance(template, dict)
    lint = getattr(cli_module, "lint_template_file", None)
    assert callable(lint), "lq template lint must enforce template naming and text rules"

    bad_name = yaml.safe_load(yaml.safe_dump(template, sort_keys=False))
    bad_name["agents"][0]["name"] = "Bad_Name"
    bad_name_path = tmp_path / "bad-name.yaml"
    bad_name_path.write_text(yaml.safe_dump(bad_name, sort_keys=False), encoding="utf-8")
    assert lint(bad_name_path)

    bad_mention = yaml.safe_load(yaml.safe_dump(template, sort_keys=False))
    bad_mention["agents"][0]["instructions"] += "\nReply to @labops."
    mention_path = tmp_path / "bad-mention.yaml"
    mention_path.write_text(yaml.safe_dump(bad_mention, sort_keys=False), encoding="utf-8")
    assert lint(mention_path)

    em_dash_template = yaml.safe_load(yaml.safe_dump(template, sort_keys=False))
    em_dash_template["agents"][0]["description"] += chr(0x2014)
    em_dash_path = tmp_path / "em-dash.yaml"
    em_dash_path.write_text(yaml.safe_dump(em_dash_template, sort_keys=False), encoding="utf-8")
    assert lint(em_dash_path)


def test_C_09_setup_writes_absolute_codex_mcp_profiles_without_duplicate_flags(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    _setup(root)

    for agent, profile in (("labops", "proposer"), ("pi-desk", "approver")):
        config_path = root / "agents" / agent / ".codex" / "config.toml"
        config = _load_toml(config_path)
        registration = config["mcp_servers"]["labquorum"]
        assert Path(registration["command"]).is_absolute()
        args = registration["args"]
        assert args[args.index("--profile") + 1] == profile
        assert Path(args[args.index("--db") + 1]).is_absolute()
        assert Path(args[args.index("--runtime-root") + 1]).is_absolute()
        repeated = getattr(server_module, "duplicate_option", None)
        assert callable(repeated), "the MCP launch parser must detect repeated options"
        assert repeated(server_module.argument_parser(), args) is None


def test_C_11_doctor_rejects_invalid_runtime_configuration(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _setup(root)
    config_path = root / "agents" / "labops" / ".codex" / "config.toml"
    contents = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        contents.replace("args = [", 'args = ["--profile", "proposer", '), encoding="utf-8"
    )

    status, stdout, stderr = _run_lq(["doctor", "--runtime-root", str(root)])

    assert status != 0
    assert "MCP_CONFIG_DUPLICATE_OPTION" in stdout + stderr


def test_C_12_binding_fails_closed_and_limits_distinct_commits(tmp_path: Path) -> None:
    validate = getattr(server_module, "validate_binding_request", None)
    limiter_type = getattr(server_module, "BindingCommitLimiter", None)
    assert callable(validate), "binding modes need server-side validation"
    assert limiter_type is not None, "binding commits need a per-process limiter"

    with pytest.raises(LabQuorumError) as missing_evidence:
        validate(
            "on",
            Profile.APPROVER,
            tmp_path / "ledger.sqlite",
            tmp_path / "runtime",
            None,
            tmp_path / "runtime" / "agents" / "pi-desk",
        )
    assert missing_evidence.value.code is ErrorCode.BINDING_CERTIFICATION_REQUIRED

    calls: list[dict[str, Any]] = []

    def commit(**arguments: Any) -> dict[str, Any]:
        calls.append(dict(arguments))
        return {"request_id": arguments["request_id"], "status": "committed"}

    limiter = limiter_type()
    guarded: Callable[..., dict[str, Any]] = limiter.wrap(commit)
    first = {"request_id": "AR-0001", "revision": 1}
    assert guarded(**first)["status"] == "committed"
    assert guarded(**first)["status"] == "committed"
    with pytest.raises(LabQuorumError) as distinct_commit:
        guarded(request_id="AR-0002", revision=1)
    assert distinct_commit.value.code is ErrorCode.BINDING_COMMIT_LIMIT
    with pytest.raises(LabQuorumError) as changed_retry:
        guarded(request_id="AR-0001", revision=2)
    assert changed_retry.value.code is ErrorCode.BINDING_COMMIT_LIMIT
    assert len(calls) == 2


def test_I_13_doctor_reports_and_validates_effective_binding_state(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    _setup(root)

    status, stdout, stderr = _run_lq(["doctor", "--runtime-root", str(root)])

    assert status == 0, f"lq doctor failed: {stdout}{stderr}"
    report = json.loads(stdout)
    assert report["runtime_root"] == str(root.resolve())
    runtime_findings = [
        finding for finding in report["findings"] if finding["code"].startswith("RUNTIME_")
    ]
    assert any(finding["code"] == "RUNTIME_BINDING_OFF" for finding in runtime_findings)
    with sqlite3.connect(root / "ledger.sqlite") as connection:
        assert connection.execute("SELECT 1").fetchone() == (1,)
