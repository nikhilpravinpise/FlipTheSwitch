"""Contract snapshot for the literature profile exposed to scout."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import httpx
from syrupy.assertion import SnapshotAssertion

from labquorum.domain.timeutil import FixedClock
from labquorum.mcp.librarian_tools import LibrarianTools
from labquorum.mcp.profiles import Profile, PROFILE_TOOLS, profile_for_agent
from labquorum.mcp.server import create_server
from labquorum.scholarly.http import OpenAlexClient


def test_C_01_librarian_tools_have_a_stable_contract(
    snapshot: SnapshotAssertion,
    tmp_path,
) -> None:
    actual = LibrarianTools.contract_snapshot()
    assert actual == snapshot
    server_tools = asyncio.run(create_server(Profile.LIBRARIAN, tmp_path / "unused.sqlite").list_tools())
    server_contract = [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema,
        }
        for tool in server_tools
    ]
    assert server_contract == actual


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


def test_C_01_search_literature_caps_candidates_and_query_length(tmp_path) -> None:
    requests: list[httpx.Request] = []

    def search_response(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"results": [{"id": f"https://openalex.org/W{index}"} for index in range(10)]},
        )

    tools = LibrarianTools(
        clock=FixedClock(datetime(2026, 11, 5, 12, tzinfo=UTC)),
        openalex=OpenAlexClient(
            cache_dir=tmp_path,
            transport=httpx.MockTransport(search_response),
        ),
    )
    result = tools.search_literature("protein structure", max_results=8)
    assert len(result["results"]) == 8
    assert requests[0].url.params["per_page"] == "8"
    too_long = tools.search_literature("q" * 301)
    assert too_long["error"] == "INVALID_ARGUMENT"
    assert len(requests) == 1

