"""Regression tests for independent P3 audit findings."""

from __future__ import annotations

import json
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import pytest

from labquorum import provisioning as provisioning_module
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.mcp import binding
from labquorum.mcp import server as mcp_server
from labquorum.mcp.profiles import Profile
from labquorum.provisioning import (
    _template,
    lint_template_data,
    runtime_doctor_findings,
    setup_runtime,
)


def _command(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def test_C_04_setup_uses_runtime_codex_home_without_reading_user_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_home = tmp_path / "profile home"
    user_codex = user_home / ".codex"
    user_codex.mkdir(parents=True)
    user_config = user_codex / "config.toml"
    user_contents = 'sandbox_mode = "danger-full-access"\n'
    user_config.write_text(user_contents, encoding="utf-8")
    auth_contents = '{"fixture":"not-a-real-secret"}'
    (user_codex / "auth.json").write_text(auth_contents, encoding="utf-8")
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: user_home))
    original_open = Path.open
    accessed_user_config: list[str] = []
    track_config_access = True

    def tracked_open(path: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if track_config_access and path.resolve(strict=False) == user_config.resolve():
            accessed_user_config.append(mode)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked_open)

    root = tmp_path / "runtime with spaces"
    command = _command(tmp_path / "stable bin" / "lq-mcp.exe")
    setup_runtime(
        root,
        command_path=command,
        codex_home=user_codex,
        install_codex_config=True,
    )
    track_config_access = False

    assert accessed_user_config == []
    assert user_config.read_text(encoding="utf-8") == user_contents
    runtime_home = root / "codex-home"
    runtime_config = runtime_home / "config.toml"
    assert runtime_config.is_file()
    assert (runtime_home / "auth.json").read_text(encoding="utf-8") == auth_contents
    assert "LabQuorum managed config" in runtime_config.read_text(encoding="utf-8")
    manifest = json.loads((root / "runtime.json").read_text(encoding="utf-8"))
    assert manifest["source_home_config"] == str(runtime_config.resolve())


def test_C_04_setup_assigns_approve_to_non_commit_tools_and_prompt_to_commit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime with spaces"
    command = _command(root / "venv" / "Scripts" / "lq-mcp.exe")
    setup_runtime(root, command_path=command)

    config_path = root / "codex-home" / "config.toml"
    assert config_path.is_file(), "setup must register the source home inside the runtime root"
    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)
    server = config["mcp_servers"]["labquorum"]
    assert server["default_tools_approval_mode"] == "approve"
    assert server["tools"]["commit_booking"]["approval_mode"] == "prompt"
    assert server["args"] == [
        "--runtime-root",
        str(root.resolve()),
        "--db",
        str((root / "ledger.sqlite").resolve()),
    ]


def test_C_05_setup_rejects_mcp_executable_inside_a_worktree(tmp_path: Path) -> None:
    command = _command(
        tmp_path / ".claude" / "worktrees" / "builder" / ".venv" / "Scripts" / "lq-mcp.exe"
    )
    with pytest.raises(LabQuorumError):
        setup_runtime(tmp_path / "runtime", command_path=command)


def test_C_11_doctor_reports_runtime_codex_home_and_rejects_global_managed_block(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_home = tmp_path / "profile home"
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: user_home))
    root = tmp_path / "runtime"
    command = _command(tmp_path / "stable bin" / "lq-mcp.exe")
    setup_runtime(root, command_path=command)
    findings = runtime_doctor_findings(root)
    assert any(
        item["code"] == "RUNTIME_CODEX_HOME" and str(root / "codex-home") in item["message"]
        for item in findings
    )

    user_codex = user_home / ".codex"
    user_codex.mkdir(parents=True)
    (user_codex / "config.toml").write_text(
        "# BEGIN LabQuorum managed config\n# END LabQuorum managed config\n",
        encoding="utf-8",
    )
    findings = runtime_doctor_findings(root)
    assert any(
        item["code"] == "RUNTIME_GLOBAL_CODEX_HOME_POLLUTED" and item["severity"] == "error"
        for item in findings
    )


def test_C_11_doctor_rejects_an_mcp_command_inside_a_worktree(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    stable = _command(root / "venv" / "Scripts" / "lq-mcp.exe")
    setup_runtime(root, command_path=stable)
    worktree_command = _command(
        tmp_path / ".claude" / "worktrees" / "other" / ".venv" / "Scripts" / "lq-mcp.exe"
    )
    config_path = root / "agents" / "labops" / ".codex" / "config.toml"
    contents = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        contents.replace(json.dumps(str(stable)), json.dumps(str(worktree_command))),
        encoding="utf-8",
    )

    findings = runtime_doctor_findings(root)
    assert any(
        item["code"] == "RUNTIME_MCP_INVALID" and "worktree" in item["message"].casefold()
        for item in findings
    )


def test_C_11_windows_agent_write_deny_preserves_read_access() -> None:
    build_deny_entry = getattr(provisioning_module, "_windows_agent_write_deny_entry", None)
    assert callable(build_deny_entry), "Windows write policy needs a read-preserving deny entry"
    assert build_deny_entry("S-1-5-21-1-2-3-1000") == (
        "*S-1-5-21-1-2-3-1000:(OI)(CI)(WD,AD,WEA,WA,DE,DC,WDAC,WO)"
    )


def test_C_11_agent_directory_write_probe_checks_file_creation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    probe = cast(
        Callable[[Path], str | None],
        getattr(provisioning_module, "_agent_directory_write_issue", None),
    )
    assert callable(probe), "doctor needs an actual filesystem write probe"
    issue = probe(tmp_path)
    assert issue is not None and "writable" in issue

    original_open = Path.open

    def denied_probe(path: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if path.name.startswith(".lq-write-probe-"):
            raise PermissionError("write denied")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied_probe)
    assert probe(tmp_path) is None


def test_C_07_template_lint_rejects_agent_management_and_extra_connections(
    tmp_path: Path,
) -> None:
    template = _template(tmp_path)
    template["agents"][0]["can_manage_agents"] = True
    assert lint_template_data(template)

    template = _template(tmp_path)
    template["agents"][0]["connections"] = ["unreviewed-service"]
    assert lint_template_data(template)


def test_C_12_binding_on_rejects_fabricated_tuple_even_if_it_matches_installed_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "runtime"
    cwd = root / "agents" / "pi-desk"
    cwd.mkdir(parents=True)
    evidence = tmp_path / "invented.json"
    installed = {
        "codex_cli_version": "0",
        "switch_console_version": "0",
        "labquorum_version": "0",
        "template_sha256": "0",
    }
    evidence.write_text(json.dumps({"certified_tuple": installed}), encoding="utf-8")
    monkeypatch.setattr(binding, "installed_certification_tuple", lambda _: installed)

    with pytest.raises(LabQuorumError) as refused:
        binding.validate_binding_request(
            "on", Profile.APPROVER, root / "ledger.sqlite", root, evidence, cwd
        )
    assert refused.value.code is ErrorCode.BINDING_CERTIFICATION_REQUIRED


def test_C_12_certify_mode_rejects_a_ledger_because_its_folder_is_named_certify(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "certify" / "ledger.sqlite"
    ledger.parent.mkdir()
    ledger.touch()

    with pytest.raises(LabQuorumError) as refused:
        binding.validate_binding_request("certify", Profile.APPROVER, ledger, None, None, tmp_path)
    assert refused.value.code is ErrorCode.BINDING_CERTIFICATION_REQUIRED


def test_C_12_certify_mode_accepts_only_the_p2_temporary_gate_ledger(
    tmp_path: Path,
) -> None:
    p2_root = tmp_path / "labquorum-p2-contract"
    p2_root.mkdir()
    p2_database = p2_root / "g.sqlite"
    p2_database.touch()
    binding.validate_binding_request("certify", Profile.APPROVER, p2_database, None, None, tmp_path)

    other_database = tmp_path / "g.sqlite"
    other_database.touch()
    with pytest.raises(LabQuorumError) as refused:
        binding.validate_binding_request(
            "certify", Profile.APPROVER, other_database, None, None, tmp_path
        )
    assert refused.value.code is ErrorCode.BINDING_CERTIFICATION_REQUIRED


def test_C_12_p2_gate_ledger_does_not_use_the_p3_one_commit_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p2_root = tmp_path / "labquorum-p2-contract"
    p2_root.mkdir()
    database = p2_root / "g.sqlite"
    database.touch()
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex home"))
    homes: list[Path] = []

    class RecordingLimiter:
        @classmethod
        def for_session_home(cls, session_home: Path) -> RecordingLimiter:
            homes.append(session_home)
            return cls()

        def wrap(self, commit: Any) -> Any:
            return commit

    monkeypatch.setattr(mcp_server, "BindingCommitLimiter", RecordingLimiter)
    mcp_server.create_server(
        Profile.APPROVER,
        database,
        binding="certify",
        cwd=tmp_path,
    )

    assert homes == []


def test_C_12_commit_limiter_persists_one_distinct_commit_across_instances(
    tmp_path: Path,
) -> None:
    factory = cast(
        Callable[[Path], binding.BindingCommitLimiter],
        getattr(binding.BindingCommitLimiter, "for_session_home", None),
    )
    assert callable(factory), "binding limiter needs a Codex-session-scoped persistent mode"

    state_home = tmp_path / "session home"
    first_calls: list[dict[str, Any]] = []

    def first_commit(**arguments: Any) -> dict[str, Any]:
        first_calls.append(dict(arguments))
        return {"request_id": arguments["request_id"], "status": "committed"}

    limiter = factory(state_home)
    first = {"request_id": "AR-0001", "revision": 1}
    assert limiter.wrap(first_commit)(**first)["status"] == "committed"

    second_calls: list[dict[str, Any]] = []

    def second_commit(**arguments: Any) -> dict[str, Any]:
        second_calls.append(dict(arguments))
        return {"request_id": arguments["request_id"], "status": "committed"}

    resumed_limiter = factory(state_home)
    with pytest.raises(LabQuorumError) as refused:
        resumed_limiter.wrap(second_commit)(request_id="AR-0002", revision=1)
    assert refused.value.code is ErrorCode.BINDING_COMMIT_LIMIT
    assert resumed_limiter.wrap(second_commit)(**first)["status"] == "committed"
    assert len(first_calls) == 1
    assert len(second_calls) == 1


def test_C_12_certify_server_binds_limiter_to_codex_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "labquorum-p3-binding-runtime"
    runtime_root.mkdir()
    agent_directory = runtime_root / "agents" / "pi-desk"
    agent_directory.mkdir(parents=True)
    database = runtime_root / "p3-test-ledger.sqlite"
    database.touch()
    manifest = {
        "schema_version": 1,
        "runtime_root": str(runtime_root.resolve()),
        "ledger_path": str((runtime_root / "ledger.sqlite").resolve()),
        "binding_mode": "off",
    }
    (runtime_root / "runtime.json").write_text(json.dumps(manifest), encoding="utf-8")
    codex_home = tmp_path / "codex home"
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    homes: list[Path] = []

    class RecordingLimiter:
        @classmethod
        def for_session_home(cls, session_home: Path) -> RecordingLimiter:
            homes.append(session_home)
            return cls()

        def wrap(self, commit: Any) -> Any:
            return commit

    monkeypatch.setattr(mcp_server, "BindingCommitLimiter", RecordingLimiter)
    mcp_server.create_server(
        Profile.APPROVER,
        database,
        binding="certify",
        runtime_root=runtime_root,
        cwd=agent_directory,
    )

    assert homes == [codex_home]


def test_C_06_launch_console_script_sets_runtime_home_and_waits_for_cdp() -> None:
    script = Path("scripts/ops/launch_console.ps1")
    assert script.is_file(), "the documented runtime needs a Console launcher"
    contents = script.read_text(encoding="utf-8")
    for expected in (
        "CloseMainWindow",
        "Machine",
        "User",
        "CODEX_HOME",
        "GetDirectoryName",
        "remote-debugging-port=9333",
        "/json/version",
        "(WD,AD,WEA,WA,DE,DC,WDAC,WO)",
    ):
        assert expected in contents
