"""P2 CLI health and actionable error behavior."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from labquorum.cli import main as cli_module
from labquorum.domain.timeutil import FixedClock
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo


def test_I_11_doctor_reports_onedrive_key_and_docker_findings_separately(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    missing_agents = tmp_path / "agents-absent"
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    original_which = shutil.which
    monkeypatch.setattr(
        shutil,
        "which",
        lambda name: None if name == "docker" else original_which(name),
    )
    database = tmp_path / "OneDrive" / "ledger.sqlite"

    status = cli_module.main(["doctor", "--db", str(database), "--agents-dir", str(missing_agents)])

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
    init_error = json.loads(init_output.err)
    assert str(tmp_path) in init_error["message"]
    assert "path" in init_error["message"].casefold() or "open" in init_error["message"].casefold()


def test_lq_request_show_prints_the_current_seeded_request(
    tmp_path: Path,
    capsys,
) -> None:
    database = tmp_path / "request.sqlite"
    connection = init_database(database)
    try:
        seed_demo(
            connection,
            date(2026, 11, 6),
            clock=FixedClock(datetime(2026, 11, 5, 12, 0, tzinfo=UTC)),
        )
    finally:
        connection.close()

    status = cli_module.main(["request", "show", "AR-0041", "--db", str(database)])

    request = json.loads(capsys.readouterr().out)
    assert status == 0
    assert request["request_id"] == "AR-0041"
    assert request["status"] == "committed"
