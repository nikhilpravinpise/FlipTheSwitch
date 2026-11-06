"""Adversarial P3 boundary regression tests."""

import json
from pathlib import Path

import pytest

from labquorum.domain.errors import LabQuorumError
from labquorum.mcp import binding
from labquorum.mcp.profiles import Profile
from labquorum.provisioning import _template, lint_template_data


def test_audit_p3_unverified_tuple_is_not_certification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
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
    with pytest.raises(LabQuorumError):
        binding.validate_binding_request(
            "on", Profile.APPROVER, root / "ledger.sqlite", root, evidence, cwd
        )


def test_audit_p3_template_rejects_agent_management(tmp_path: Path) -> None:
    template = _template(tmp_path)
    template["agents"][0]["can_manage_agents"] = True
    assert lint_template_data(template)


def test_audit_p3_certify_directory_does_not_make_live_ledger_test_only(tmp_path: Path) -> None:
    ledger = tmp_path / "certify" / "ledger.sqlite"
    ledger.parent.mkdir()
    ledger.touch()
    with pytest.raises(LabQuorumError):
        binding.validate_binding_request("certify", Profile.APPROVER, ledger, None, None, tmp_path)
