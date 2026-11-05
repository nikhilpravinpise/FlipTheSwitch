"""P2 CLI health and actionable error behavior."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from labquorum.cli import main as cli_module


def test_I_11_doctor_reports_onedrive_key_and_docker_findings_separately(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    missing_agents = tmp_path / "agents-absent"
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    monkeypatch.setattr(
        shutil,
        "which",
        lambda name: None if name == "docker" else shutil.which(name),
    )
    database = tmp_path / "OneDrive" / "ledger.sqlite"

    status = cli_module.main(
        ["doctor", "--db", str(database), "--agents-dir", str(missing_agents)]
    )

    report = json.loads(capsys.readouterr().out)
    codes = {finding["code"] for finding in report["findings"]}
    assert {"LEDGER_ONEDRIVE", "OPENALEX_KEY_MISSING", "DOCKER_UNAVAILABLE"}.issubset(codes)
    assert status != 0


def test_I_32_missing_uv_and_bad_ledger_path_have_actionable_errors(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    status = cli_module.main(["doctor", "--db", str(tmp_path / "ledger.sqlite")])
    doctor_output = capsys.readouterr()
    assert status != 0
    assert "uv" in doctor_output.out.casefold()
    assert "install" in doctor_output.out.casefold() or "path" in doctor_output.out.casefold()

    bad_path = cli_module.main(["init", "--db", str(tmp_path)])
    init_output = capsys.readouterr()
    assert bad_path != 0
    assert str(tmp_path) in init_output.err or str(tmp_path) in init_output.out
    assert "path" in init_output.err.casefold() or "open" in init_output.err.casefold()

