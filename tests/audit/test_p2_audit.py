import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from labquorum.cli.main import _agent_config_finding
from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.server import create_runtime
from labquorum.store.db import init_database
from labquorum.store.seed import seed_demo


def test_audit_proposal_can_be_echoed_to_commit(tmp_path: Path) -> None:
    database = tmp_path / "ledger.sqlite"
    clock = FixedClock(datetime(2026, 11, 5, 12, tzinfo=UTC))
    connection = init_database(database)
    seed_demo(connection, date(2026, 11, 6), clock=clock)
    connection.close()
    proposer = create_runtime("proposer", database, clock=clock)
    approver = create_runtime("approver", database, clock=clock)
    proposal = proposer.invoke(
        "propose_booking",
        {
            "instrument_id": "INS-01",
            "requester_handle": "maya",
            "project_id": "x" * 81,
            "start": "2026-11-09T10:00:00+05:30",
            "end": "2026-11-09T11:00:00+05:30",
        },
    )
    assert proposal["status"] == "pending"
    args = {key: proposal[key] for key in ("request_id", "revision", "content_hash", "decision")}
    result = approver.invoke("commit_booking", args)
    assert result.get("status") == "committed", result


def test_audit_doctor_rejects_duplicate_profile(tmp_path: Path) -> None:
    folder = tmp_path / "labops"
    folder.mkdir()
    (folder / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "labquorum": {
                        "command": shutil.which("uv"),
                        "args": ["run", "lq-mcp", "--profile", "proposer", "--profile", "approver"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    finding = _agent_config_finding(folder)
    assert finding["severity"] == "error", finding
