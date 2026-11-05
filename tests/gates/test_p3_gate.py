"""Unit tests for the P3 gate's mutation and parsing helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts.gates import p3, p3_live_check


def _template() -> dict[str, Any]:
    return {
        "agents": [
            {
                "name": "labops",
                "provider": "codex",
                "model": "gpt-6-luna",
                "advanced_config": {"effort": "high"},
                "instructions": "Propose bookings.",
            },
            {
                "name": "pi-desk",
                "provider": "codex",
                "model": "gpt-6-luna",
                "advanced_config": {"effort": "high"},
                "addressing": "owner-agents",
                "instructions": "Present decisions.",
            },
        ]
    }


def test_C_04_error_code_parser_finds_distinct_commit_refusal() -> None:
    payload = {"error": {"code": "BINDING_COMMIT_LIMIT"}}
    assert p3.error_code(payload, "") == "BINDING_COMMIT_LIMIT"


def test_C_05_json_pointer_reads_idempotent_retry_status() -> None:
    assert p3.json_pointer({"result": {"status": "committed"}}, "/result/status") == "committed"


def test_C_06_tool_inventory_parser_reads_names_from_client_listing() -> None:
    listing = SimpleNamespace(tools=[SimpleNamespace(name="get_request")])
    assert p3.extract_tool_names(listing) == {"get_request"}


def test_C_07_template_mutations_change_provider_model_and_effort() -> None:
    mutations = p3.template_mutations(_template())
    assert mutations["provider"]["agents"][0]["provider"] == "claude"
    assert mutations["model"]["agents"][0]["model"] != "gpt-6-luna"
    assert mutations["effort"]["agents"][0]["advanced_config"]["effort"] == "medium"


def test_C_08_template_mutations_change_addressing_and_trailing_mention() -> None:
    mutations = p3.template_mutations(_template())
    pi_desk = next(
        agent for agent in mutations["addressing"]["agents"] if agent["name"] == "pi-desk"
    )
    labops = next(
        agent for agent in mutations["trailing_mention"]["agents"] if agent["name"] == "labops"
    )
    assert pi_desk["addressing"] == "anyone"
    assert any(line.endswith("@labops.") for line in labops["instructions"].splitlines())


def test_C_09_server_arguments_select_the_requested_profile() -> None:
    args = p3.server_arguments("approver", Path("ledger.sqlite"))
    assert args[args.index("--profile") + 1] == "approver"
    assert args[args.index("--db") + 1] == "ledger.sqlite"
    assert "--binding" not in args


def test_C_11_runtime_directory_parser_accepts_a_child_of_root(tmp_path: Path) -> None:
    runtime_root = tmp_path / "LabQuorum"
    directory = runtime_root / "agents" / "labops"
    assert p3_live_check.directory_issue(directory, runtime_root) is None


def test_C_12_default_binding_profile_is_rejected_if_commit_is_exposed() -> None:
    issue = p3.binding_tool_exposure_issue({"get_request", "commit_booking"}, expected=False)
    assert issue is not None


def test_I_13_addressing_parser_distinguishes_safe_and_open_modes() -> None:
    owner_agents = {
        "rules": [
            {
                "rooms": "*",
                "room_groups": "*",
                "users": [],
                "agents": [],
                "owner": True,
                "owner_agents": True,
            }
        ]
    }
    assert p3_live_check.addressing_mode(owner_agents) == "ownerAndAgents"
    assert p3_live_check.addressing_mode(None) == "anyone"
