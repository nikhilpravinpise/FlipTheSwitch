"""Contract snapshot for the literature profile exposed to scout."""

from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from labquorum.mcp.profiles import Profile, PROFILE_TOOLS, profile_for_agent
from labquorum.mcp.librarian_tools import LibrarianTools


def test_C_01_librarian_tools_have_a_stable_contract(snapshot: SnapshotAssertion) -> None:
    actual = LibrarianTools.contract_snapshot()
    assert actual == snapshot


def test_C_16_librarian_profile_is_assigned_to_scout() -> None:
    librarian = getattr(Profile, "LIBRARIAN", None)
    assert librarian is not None
    assert librarian.value == "librarian"
    assert profile_for_agent("scout") is librarian
    assert PROFILE_TOOLS.get(librarian) == (
        "verify_citation",
        "verify_bibliography",
        "search_literature",
    )

