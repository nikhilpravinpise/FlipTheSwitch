"""P5 dataset provenance, descriptive analysis, and stale propagation tests."""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from collections import deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from labquorum.analysis.runner import run_process_with_timeout
from labquorum.cli.main import main as lq_main
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.profiles import Profile, tool_names_for_profile
from labquorum.mcp.server import create_runtime
from labquorum.store.db import SCHEMA_VERSION, init_database, open_database
from labquorum.store.provenance import mark_descendants_stale

ROOT = Path(__file__).resolve().parents[2]
PLATE_V1 = ROOT / "seed" / "plate3_od590.csv"
PLATE_V2 = ROOT / "seed" / "plate3_od590_v2.csv"
NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
ANALYST_TOOLS = {
    "register_dataset",
    "dataset_profile",
    "run_analysis",
    "list_runs",
    "run_status",
}


def _require_analyst_profile() -> Profile:
    profile = next((candidate for candidate in Profile if candidate.value == "analyst"), None)
    assert profile is not None, "P5 analyst MCP profile is not registered"
    assert set(tool_names_for_profile(profile)) == ANALYST_TOOLS
    return profile


def _runtime(tmp_path: Path) -> tuple[Any, Path]:
    profile = _require_analyst_profile()
    database = tmp_path / "ledger.sqlite"
    connection = init_database(database)
    connection.close()
    return create_runtime(profile, database, clock=FixedClock(NOW)), database


def _call(runtime: Any, name: str, **arguments: Any) -> dict[str, Any]:
    result = runtime.tool_method(name)(**arguments)
    assert isinstance(result, dict)
    return result


def _register(
    runtime: Any,
    dataset_id: str,
    csv_text: str,
    *,
    change_reason: str = "Initial synthetic plate registration",
    sensitivity: str = "internal",
) -> dict[str, Any]:
    return _call(
        runtime,
        "register_dataset",
        dataset_id=dataset_id,
        csv_text=csv_text,
        sensitivity=sensitivity,
        change_reason=change_reason,
    )


def _plate_csv(path: Path = PLATE_V1) -> str:
    with path.open(encoding="utf-8", newline="") as handle:
        return handle.read()


def _run_descriptive(runtime: Any, dataset_version_id: str) -> dict[str, Any]:
    return _call(
        runtime,
        "run_analysis",
        dataset_version_id=dataset_version_id,
        recipe="descriptive",
        params={},
    )


def test_U_D01_csv_sniffing_handles_delimiters_decimal_comma_bom_and_crlf(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    examples = [
        ("well,value\nA1,0.5\n", ",", "."),
        ("well;value\nA1;0,5\n", ";", ","),
        ("well\tvalue\r\nA1\t0.5\r\n", "\t", "."),
        ("\ufeffwell,value\r\nA1,0.5\r\n", ",", "."),
    ]
    for index, (csv_text, delimiter, decimal_mark) in enumerate(examples):
        registered = _register(runtime, f"DS-SNIFF-{index}", csv_text)
        assert "error" not in registered
        profile = _call(
            runtime,
            "dataset_profile",
            dataset_version_id=registered["dataset_version_id"],
        )
        assert profile["delimiter"] == delimiter
        assert profile["decimal_mark"] == decimal_mark
        assert profile["rows"] == 1


def test_U_D02_profile_reports_types_missing_duplicates_and_out_of_range_od(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    csv_text = (
        "well,row,col,condition,egcg_ug_ml,replicate,od590\n"
        "B2,B,2,EGCG,0,1,0.4\n"
        "B2,B,2,EGCG,0,1,0.4\n"
        "B3,B,3,EGCG,2,2,4.5\n"
        "B4,B,4,EGCG,4,3,\n"
    )
    registered = _register(runtime, "DS-PROFILE", csv_text)
    profile = _call(
        runtime,
        "dataset_profile",
        dataset_version_id=registered["dataset_version_id"],
    )
    assert profile["column_types"]["od590"] == "numeric"
    assert profile["missing_counts"]["od590"] == 1
    assert profile["duplicate_rows"] == 1
    assert profile["duplicate_wells"] == ["B2"]
    assert profile["out_of_range_od"] == [{"well": "B3", "value": "4.5"}]


def test_U_D04_human_subjects_datasets_are_refused(tmp_path: Path) -> None:
    runtime, _ = _runtime(tmp_path)
    explicit = _register(runtime, "DS-HUMAN", "well,value\nA1,0.5\n", sensitivity="human_subjects")
    assert explicit["error"] == ErrorCode.ETHICS_REVIEW_REQUIRED.value

    detected = _register(
        runtime,
        "DS-PII",
        "participant_email,well,od590\nperson@example.test,A1,0.5\n",
    )
    assert detected["error"] == ErrorCode.ETHICS_REVIEW_REQUIRED.value
    assert "human_subjects" in detected["message"]


def test_U_D05_descriptive_plate_summary_matches_independent_goldens(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    registered = _register(runtime, "DS-PLATE", _plate_csv())
    result = _run_descriptive(runtime, registered["dataset_version_id"])
    assert result["status"] == "CURRENT"
    summary_artifact = next(item for item in result["outputs"] if item["kind"] == "json")
    summary_path = _run_file_for_hash(result["run_id"], summary_artifact["sha256"], tmp_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    groups = {item["condition"]: item for item in summary["groups"]}
    assert sum(item["count"] for item in groups.values()) == 42
    assert set(groups) == {"0", "2", "4", "8", "16", "32", "64"}
    assert all(item["count"] == 6 for item in groups.values())
    assert groups["8"]["mean_od590"] == pytest.approx(0.803333, abs=1e-6)
    assert groups["8"]["sd_od590"] == pytest.approx(0.361933, abs=1e-6)
    assert _plate_differences(_plate_csv(), _plate_csv(PLATE_V2)) == {
        "od590": ("0.083", "0.830"),
    }
    assert _changed_plate_wells(_plate_csv(), _plate_csv(PLATE_V2)) == ["C5"]
    repeated = _run_descriptive(runtime, registered["dataset_version_id"])
    assert {item["kind"]: item["sha256"] for item in repeated["outputs"]} == {
        item["kind"]: item["sha256"] for item in result["outputs"]
    }

    registered_v2 = _register(
        runtime,
        "DS-PLATE",
        _plate_csv(PLATE_V2),
        change_reason="C5 transcription corrected from 0.083 to 0.830 OD590",
    )
    corrected = _run_descriptive(runtime, registered_v2["dataset_version_id"])
    corrected_json = next(item for item in corrected["outputs"] if item["kind"] == "json")
    corrected_path = _run_file_for_hash(corrected["run_id"], corrected_json["sha256"], tmp_path)
    corrected_groups = {
        item["condition"]: item
        for item in json.loads(corrected_path.read_text(encoding="utf-8"))["groups"]
    }
    assert corrected_groups["8"]["mean_od590"] - groups["8"]["mean_od590"] == pytest.approx(
        0.1245,
        abs=1e-6,
    )


def test_U_D06_analysis_timeout_kills_the_process_tree(tmp_path: Path) -> None:
    _require_analyst_profile()
    marker = tmp_path / "child.pid"
    child_code = (
        "import subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
        "open(sys.argv[1],'w',encoding='utf-8').write(str(p.pid)); time.sleep(30)"
    )
    with pytest.raises(TimeoutError):
        run_process_with_timeout(
            [sys.executable, "-c", child_code, str(marker)],
            timeout_seconds=0.25,
        )
    assert marker.is_file()
    child_pid = int(marker.read_text(encoding="utf-8"))
    assert _wait_until_stopped(child_pid)


@pytest.mark.timeout(15)
def test_U_D06b_timeout_returns_promptly_when_grandchild_holds_pipes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = tmp_path / "grandchild.pid"
    grandchild_code = "import time; time.sleep(30)"
    parent_code = (
        "import subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-c',sys.argv[2]]); "
        "open(sys.argv[1],'w',encoding='utf-8').write(str(p.pid)); time.sleep(30)"
    )
    if os.name == "nt":
        original_run = subprocess.run

        def taskkill_races_child_spawn(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
            command = args[0] if args else kwargs.get("args", [])
            if command and command[0].lower() == "taskkill":
                return subprocess.CompletedProcess(command, 0, "", "")
            return original_run(*args, **kwargs)

        monkeypatch.setattr(subprocess, "run", taskkill_races_child_spawn)
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        run_process_with_timeout(
            [sys.executable, "-c", parent_code, str(marker), grandchild_code],
            timeout_seconds=0.25,
        )
    assert time.monotonic() - started < 10
    assert marker.is_file()
    grandchild_pid = int(marker.read_text(encoding="utf-8"))
    assert _wait_until_stopped(grandchild_pid)


def test_U_D07_qc_blanks_are_flagged_without_removing_treatment_wells(tmp_path: Path) -> None:
    runtime, _ = _runtime(tmp_path)
    registered = _register(runtime, "DS-QC", _plate_csv())
    result = _run_descriptive(runtime, registered["dataset_version_id"])
    summary_artifact = next(item for item in result["outputs"] if item["kind"] == "json")
    summary_path = _run_file_for_hash(result["run_id"], summary_artifact["sha256"], tmp_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["flagged_qc_blanks"] == ["A1", "H12"]
    assert summary["treatment_wells"] == 42
    assert summary["blank_summary"]["count"] == 52
    assert "not proven evaporation" in summary["blank_summary"]["interpretation"]


def test_U_D08_unknown_well_is_reported_for_correction_not_auto_matched(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    rows = list(csv.DictReader(PLATE_V1.open(encoding="utf-8", newline="")))
    rows[13]["well"] = "Z99"
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    registered = _register(runtime, "DS-UNKNOWN-WELL", output.getvalue())
    profile = _call(
        runtime,
        "dataset_profile",
        dataset_version_id=registered["dataset_version_id"],
    )
    assert profile["unknown_wells"] == ["Z99"]
    assert profile["requires_correction"] is True
    result = _run_descriptive(runtime, registered["dataset_version_id"])
    assert result["error"] == ErrorCode.INVALID_ARGUMENT.value
    assert "Z99" in result["message"]


def test_U_D09_formula_cells_remain_inert_and_are_escaped_in_profile(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    registered = _register(
        runtime,
        "DS-FORMULA",
        'well,notes\nA1,"=1+1"\nA2,"+SUM(1,2)"\nA3,"-3+4"\nA4,"@SUM(1,2)"\n',
    )
    profile = _call(
        runtime,
        "dataset_profile",
        dataset_version_id=registered["dataset_version_id"],
    )
    escaped = [item["value"] for item in profile["formula_cells"]]
    assert escaped == ["'=1+1", "'+SUM(1,2)", "'-3+4", "'@SUM(1,2)"]
    assert profile["formula_cells"][0]["row"] == 2


def test_U_D10_plate_recipe_reports_technical_replicates_without_p_values(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    registered = _register(runtime, "DS-TECHNICAL", _plate_csv())
    result = _run_descriptive(runtime, registered["dataset_version_id"])
    summary_artifact = next(item for item in result["outputs"] if item["kind"] == "json")
    summary = json.loads(
        _run_file_for_hash(result["run_id"], summary_artifact["sha256"], tmp_path).read_text(
            encoding="utf-8"
        )
    )
    assert summary["experimental_unit"] == "technical well replicate"
    assert summary["inference"] == "descriptive only; no p-values or significance claims"
    assert "p_value" not in summary
    assert all("p_value" not in item for item in summary["groups"])


def test_U_S01_dataset_supersession_stales_runs_and_artifacts_with_reason(
    tmp_path: Path,
) -> None:
    runtime, database = _runtime(tmp_path)
    first = _register(runtime, "DS-CASCADE", _plate_csv())
    run = _run_descriptive(runtime, first["dataset_version_id"])
    second = _register(
        runtime,
        "DS-CASCADE",
        _plate_csv(PLATE_V2),
        change_reason="C5 corrected after transcription review",
    )
    status = _call(runtime, "run_status", run_id=run["run_id"])
    assert second["dataset_version_id"] != first["dataset_version_id"]
    assert status["status"] == "STALE"
    assert "C5 corrected after transcription review" in status["stale_reason"]
    assert all(item["status"] == "STALE" for item in status["outputs"])
    connection = open_database(database)
    try:
        assert (
            connection.execute(
                "SELECT count(*) FROM dependency_edge WHERE parent_type = 'dataset_version'"
            ).fetchone()[0]
            == 1
        )
    finally:
        connection.close()


def test_U_S03_rerun_has_new_ids_and_never_makes_the_old_run_current(tmp_path: Path) -> None:
    runtime, _ = _runtime(tmp_path)
    first = _register(runtime, "DS-RERUN", _plate_csv())
    old_run = _run_descriptive(runtime, first["dataset_version_id"])
    current = _register(
        runtime,
        "DS-RERUN",
        _plate_csv(PLATE_V2),
        change_reason="C5 correction",
    )
    new_run = _run_descriptive(runtime, current["dataset_version_id"])
    assert new_run["run_id"] != old_run["run_id"]
    assert {item["artifact_id"] for item in new_run["outputs"]}.isdisjoint(
        item["artifact_id"] for item in old_run["outputs"]
    )
    assert _call(runtime, "run_status", run_id=old_run["run_id"])["status"] == "STALE"
    assert _call(runtime, "run_status", run_id=new_run["run_id"])["status"] == "CURRENT"


def test_U_S06_unrelated_dataset_runs_remain_current(tmp_path: Path) -> None:
    runtime, _ = _runtime(tmp_path)
    affected = _register(runtime, "DS-AFFECTED", _plate_csv())
    unrelated = _register(runtime, "DS-UNRELATED", _plate_csv())
    affected_run = _run_descriptive(runtime, affected["dataset_version_id"])
    unrelated_run = _run_descriptive(runtime, unrelated["dataset_version_id"])
    _register(
        runtime,
        "DS-AFFECTED",
        _plate_csv(PLATE_V2),
        change_reason="Corrected one transcription",
    )
    assert _call(runtime, "run_status", run_id=affected_run["run_id"])["status"] == "STALE"
    assert _call(runtime, "run_status", run_id=unrelated_run["run_id"])["status"] == "CURRENT"


# Each example creates a fresh file-backed SQLite ledger; Windows CI runners need more than the
# suite-wide 60 s for 100 examples. The property, strategy and example count are unchanged.
@pytest.mark.timeout(300)
@given(edge_codes=st.sets(st.integers(0, 41), max_size=42))
def test_P_07_stale_propagation_is_monotonic_and_complete_against_independent_oracle(
    edge_codes: set[int],
) -> None:
    _require_analyst_profile()
    with tempfile.TemporaryDirectory(prefix="labquorum-p5-property-") as temp_dir:
        database = Path(temp_dir) / "property.sqlite"
        connection = init_database(database)
        try:
            connection.execute("BEGIN IMMEDIATE")
            _insert_property_graph(connection, edge_codes)
            connection.execute("COMMIT")
            children: dict[tuple[str, str], list[tuple[str, str]]] = {}
            for edge_code in edge_codes:
                if edge_code < 6:
                    child = ("analysis_run", f"RUN-{edge_code}")
                    parent = ("dataset_version", "DS-ROOT")
                else:
                    run_index, artifact_index = divmod(edge_code - 6, 6)
                    child = ("artifact", f"ART-{artifact_index}")
                    parent = ("analysis_run", f"RUN-{run_index}")
                children.setdefault(parent, []).append(child)

            expected: set[tuple[str, str]] = set()
            pending = deque([("dataset_version", "DS-ROOT")])
            while pending:
                parent = pending.popleft()
                for child in children.get(parent, []):
                    if child not in expected:
                        expected.add(child)
                        pending.append(child)

            mark_descendants_stale(
                connection,
                "dataset_version",
                "DS-ROOT",
                "DS-ROOT v2 supersedes v1: independent property mutation",
            )
            observed = _stale_nodes(connection)
            assert observed == expected
            mark_descendants_stale(
                connection,
                "dataset_version",
                "DS-ROOT",
                "later reason must not rewrite prior stale evidence",
            )
            assert _stale_nodes(connection) == expected
            assert all(
                "independent property mutation" in str(row["stale_reason"])
                for row in connection.execute(
                    "SELECT stale_reason FROM analysis_run WHERE status = 'STALE'"
                )
            )
            stale_run = connection.execute(
                "SELECT id FROM analysis_run WHERE status = 'STALE' LIMIT 1"
            ).fetchone()
            if stale_run is not None:
                with pytest.raises(sqlite3.IntegrityError):
                    connection.execute(
                        "UPDATE analysis_run SET status = 'CURRENT', stale_reason = NULL WHERE id = ?",
                        (stale_run["id"],),
                    )
        finally:
            connection.close()


def test_I_09_analysis_end_to_end_records_hashes_json_and_png(tmp_path: Path) -> None:
    runtime, database = _runtime(tmp_path)
    registered = _register(runtime, "DS-I09-PLATE", _plate_csv())
    result = _run_descriptive(runtime, registered["dataset_version_id"])
    assert result["status"] == "CURRENT"
    assert {item["kind"] for item in result["outputs"]} == {"json", "png"}
    connection = open_database(database)
    try:
        rows = connection.execute(
            "SELECT kind, relative_path, sha256, byte_count FROM artifact WHERE run_id = ?",
            (result["run_id"],),
        ).fetchall()
        assert len(rows) == 2
        for row in rows:
            output_path = _staging_root(database) / str(row["relative_path"])
            data = output_path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == row["sha256"]
            assert len(data) == row["byte_count"]
            if row["kind"] == "png":
                assert data.startswith(b"\x89PNG\r\n\x1a\n")
    finally:
        connection.close()


def test_I_15_corrected_dataset_cascades_stale_through_runs_and_artifacts(
    tmp_path: Path,
) -> None:
    runtime, _ = _runtime(tmp_path)
    initial = _register(runtime, "DS-I15", _plate_csv())
    first = _run_descriptive(runtime, initial["dataset_version_id"])
    replacement = _register(
        runtime,
        "DS-I15",
        _plate_csv(PLATE_V2),
        change_reason="C5 correction from 0.083 to 0.830 OD590",
    )
    assert replacement["supersedes"] == initial["dataset_version_id"]
    status = _call(runtime, "run_status", run_id=first["run_id"])
    assert status["status"] == "STALE"
    assert "C5 correction" in status["stale_reason"]
    assert all(item["status"] == "STALE" for item in status["outputs"])


def test_I_19_old_schema_refuses_and_backup_guidance_is_executable(tmp_path: Path) -> None:
    old_path = tmp_path / "old-v2.sqlite"
    old = sqlite3.connect(old_path)
    old.execute("CREATE TABLE schema_version(version INTEGER NOT NULL)")
    old.execute("INSERT INTO schema_version(version) VALUES (2)")
    old.commit()
    old.close()
    assert SCHEMA_VERSION == 3
    with pytest.raises(LabQuorumError) as error:
        open_database(old_path)
    assert error.value.code is ErrorCode.SCHEMA_VERSION_MISMATCH
    assert "lq backup" in error.value.message

    backup_path = tmp_path / "old-v2-backup.sqlite"
    assert lq_main(["backup", "--db", str(old_path), "--output", str(backup_path)]) == 0
    backup = sqlite3.connect(backup_path)
    try:
        assert backup.execute("SELECT version FROM schema_version").fetchone()[0] == 2
    finally:
        backup.close()
    with pytest.raises(LabQuorumError):
        init_database(old_path)


def test_I_27_analyst_tools_reject_traversal_and_expose_no_path_arguments(
    tmp_path: Path,
) -> None:
    profile = _require_analyst_profile()
    runtime, _ = _runtime(tmp_path)
    rejected = _register(runtime, "../../outside", _plate_csv())
    assert rejected["error"] == ErrorCode.INVALID_ARGUMENT.value
    assert profile.value == "analyst"

    database = tmp_path / "ledger.sqlite"
    connection = init_database(database)
    connection.close()
    schemas = asyncio.run(_list_tools(profile.value, database))
    assert {tool["name"] for tool in schemas} == ANALYST_TOOLS
    for tool in schemas:
        assert not (set(tool["inputSchema"].get("properties", {})) & {"path", "file_path", "root"})


def test_C_01_analyst_tool_contract_matches_snapshot(tmp_path: Path) -> None:
    profile = _require_analyst_profile()
    database = tmp_path / "contract.sqlite"
    connection = init_database(database)
    connection.close()
    actual = asyncio.run(_list_tools(profile.value, database))
    expected_path = ROOT / "tests" / "contract" / "p5_analyst_snapshot.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert actual == expected


def _run_file_for_hash(run_id: str, digest: str, tmp_path: Path) -> Path:
    database = tmp_path / "ledger.sqlite"
    connection = open_database(database)
    try:
        row = connection.execute(
            "SELECT relative_path FROM artifact WHERE run_id = ? AND sha256 = ?",
            (run_id, digest),
        ).fetchone()
        assert row is not None
        return _staging_root(database) / str(row["relative_path"])
    finally:
        connection.close()


def _plate_differences(first: str, second: str) -> dict[str, tuple[str, str]]:
    first_rows = list(csv.DictReader(StringIO(first, newline="")))
    second_rows = list(csv.DictReader(StringIO(second, newline="")))
    differences: dict[str, tuple[str, str]] = {}
    for first_row, second_row in zip(first_rows, second_rows, strict=True):
        for field in first_row:
            if first_row[field] != second_row[field]:
                differences[field] = (first_row[field], second_row[field])
    return differences


def _changed_plate_wells(first: str, second: str) -> list[str]:
    first_rows = list(csv.DictReader(StringIO(first, newline="")))
    second_rows = list(csv.DictReader(StringIO(second, newline="")))
    return [
        first_row["well"]
        for first_row, second_row in zip(first_rows, second_rows, strict=True)
        if first_row != second_row
    ]


def _staging_root(database: Path) -> Path:
    return database.resolve().with_name(database.name + ".staging")


@asynccontextmanager
async def _connect(profile: str, database: Path) -> AsyncIterator[ClientSession]:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "labquorum.mcp.server", "--profile", profile, "--db", str(database)],
        cwd=ROOT,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        yield session


async def _list_tools(profile: str, database: Path) -> list[dict[str, Any]]:
    async with _connect(profile, database) as session:
        listing = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in sorted(listing.tools, key=lambda item: item.name)
        ]


def _insert_property_graph(
    connection: sqlite3.Connection,
    edge_codes: set[int],
) -> None:
    connection.execute(
        "INSERT INTO dataset_version "
        "(id, dataset_id, version, relative_path, sha256, byte_count, schema_json, sensitivity, "
        "registered_by, supersedes_id, created_utc) "
        "VALUES ('DS-ROOT', 'DS-ROOT', 1, 'datasets/root.csv', ?, 1, '{}', 'internal', 'test', NULL, ?)",
        ("0" * 64, "2026-11-05T12:00:00.000000Z"),
    )
    for index in range(6):
        connection.execute(
            "INSERT INTO analysis_run "
            "(id, inputs_json, recipe, recipe_version, params_json, outputs_json, "
            "env_lock_sha256, status, stale_reason, created_utc) "
            "VALUES (?, '[]', 'descriptive', '1', '{}', '[]', ?, 'CURRENT', NULL, ?)",
            (f"RUN-{index}", "0" * 64, "2026-11-05T12:00:00.000000Z"),
        )
        connection.execute(
            "INSERT INTO artifact "
            "(id, run_id, kind, relative_path, sha256, byte_count, status, stale_reason) "
            "VALUES (?, ?, 'json', ?, ?, 1, 'CURRENT', NULL)",
            (f"ART-{index}", f"RUN-{index}", f"runs/{index}/summary.json", "0" * 64),
        )
    for edge_code in edge_codes:
        if edge_code < 6:
            parent_type, parent_id = "dataset_version", "DS-ROOT"
            child_type, child_id = "analysis_run", f"RUN-{edge_code}"
        else:
            run_index, artifact_index = divmod(edge_code - 6, 6)
            parent_type, parent_id = "analysis_run", f"RUN-{run_index}"
            child_type, child_id = "artifact", f"ART-{artifact_index}"
        connection.execute(
            "INSERT INTO dependency_edge(parent_type, parent_id, child_type, child_id, created_utc) "
            "VALUES (?, ?, ?, ?, ?)",
            (parent_type, parent_id, child_type, child_id, "2026-11-05T12:00:00.000000Z"),
        )


def _stale_nodes(connection: sqlite3.Connection) -> set[tuple[str, str]]:
    nodes = {
        ("analysis_run", str(row["id"]))
        for row in connection.execute("SELECT id FROM analysis_run WHERE status = 'STALE'")
    }
    nodes.update(
        ("artifact", str(row["id"]))
        for row in connection.execute("SELECT id FROM artifact WHERE status = 'STALE'")
    )
    return nodes


def _process_is_running(pid: int) -> bool:
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        return f'"{pid}"' in result.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _wait_until_stopped(pid: int) -> bool:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not _process_is_running(pid):
            return True
        time.sleep(0.05)
    return not _process_is_running(pid)
