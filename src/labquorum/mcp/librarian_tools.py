"""MCP literature tools for the librarian profile."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from functools import wraps
from pathlib import Path
from typing import Annotated, Any, cast

from mcp.server.fastmcp.tools.base import Tool
from pydantic import BaseModel, ConfigDict, Field

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.guards import RateGuard
from labquorum.domain.timeutil import Clock, SystemClock
from labquorum.mcp.profiles import PROFILE_TOOLS, TOOL_DESCRIPTIONS, Profile
from labquorum.scholarly.http import CrossrefClient, OpenAlexClient, RequestBudget
from labquorum.scholarly.verify import (
    CitationClaim,
)
from labquorum.scholarly.verify import (
    verify_bibliography as verify_bibliography_entries,
)
from labquorum.scholarly.verify import (
    verify_citation as verify_one_citation,
)

MAX_RESULT_BYTES = 8_192


class CitationInput(BaseModel):
    """Bounded citation fields accepted by the bibliography tool."""

    model_config = ConfigDict(extra="forbid")

    doi: str | None = Field(default=None, max_length=512)
    title: str | None = Field(default=None, max_length=1_000)
    first_author: str | None = Field(default=None, max_length=200)
    year: int | None = Field(default=None, ge=1_000, le=2_200)


def _as_mapping(value: object) -> Mapping[str, object] | None:
    if isinstance(value, dict):
        return cast(dict[str, object], value)
    return None


def _as_list(value: object) -> list[object] | None:
    if isinstance(value, list):
        return cast(list[object], value)
    return None


def _compact(value: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) <= MAX_RESULT_BYTES:
        return value
    return {
        "error": ErrorCode.INVALID_ARGUMENT.value,
        "message": "The literature result exceeds the compact output limit.",
        "details": {"limit_bytes": MAX_RESULT_BYTES},
    }


def _safe_tool(function: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    @wraps(function)
    def wrapped(self: LibrarianTools, *args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            self.rate_guard.check(Profile.LIBRARIAN.value)
            return _compact(function(self, *args, **kwargs))
        except LabQuorumError as error:
            return _compact(
                {"error": error.code.value, "message": error.message, "details": error.details}
            )
        except Exception:
            return _compact(
                {
                    "error": ErrorCode.INVALID_ARGUMENT.value,
                    "message": "The literature tool could not complete this request.",
                }
            )

    return wrapped


class LibrarianTools:
    """Tools available to scout for public literature metadata only."""

    def __init__(
        self,
        *,
        cache_dir: Path | None = None,
        clock: Clock | None = None,
        crossref: CrossrefClient | None = None,
        openalex: OpenAlexClient | None = None,
    ) -> None:
        self.profile = Profile.LIBRARIAN
        self.clock = clock or SystemClock()
        self.rate_guard = RateGuard(clock=self.clock, limit=30)
        self.cache_dir = cache_dir
        self._crossref = crossref
        self._openalex = openalex
        self._methods: dict[str, Callable[..., dict[str, Any]]] = {
            "verify_citation": self.verify_citation,
            "verify_bibliography": self.verify_bibliography,
            "search_literature": self.search_literature,
        }

    @property
    def crossref(self) -> CrossrefClient:
        if self._crossref is None:
            self._crossref = CrossrefClient(cache_dir=self.cache_dir)
        return self._crossref

    @property
    def openalex(self) -> OpenAlexClient:
        if self._openalex is None:
            self._openalex = OpenAlexClient(cache_dir=self.cache_dir)
        return self._openalex

    def tool_method(self, name: str) -> Callable[..., dict[str, Any]]:
        if name not in PROFILE_TOOLS[self.profile]:
            raise LabQuorumError(
                ErrorCode.NOT_FOUND,
                f"Tool {name} is not enabled for the librarian profile.",
            )
        return self._methods[name]

    @_safe_tool
    def verify_citation(
        self,
        doi: Annotated[str | None, Field(max_length=512)] = None,
        title: Annotated[str | None, Field(max_length=1_000)] = None,
        first_author: Annotated[str | None, Field(max_length=200)] = None,
        year: Annotated[int | None, Field(ge=1_000, le=2_200)] = None,
    ) -> dict[str, Any]:
        """Check citation metadata, DOI identity, and available retraction signals."""
        result = verify_one_citation(
            CitationClaim(doi=doi, title=title, first_author=first_author, year=year),
            crossref=self.crossref,
            openalex=self.openalex,
            checked_at=self.clock.now(),
            budget=RequestBudget(),
        )
        return result.as_dict()

    @_safe_tool
    def verify_bibliography(
        self,
        citations: Annotated[list[CitationInput], Field(max_length=50)],
    ) -> dict[str, Any]:
        """Verify and deduplicate up to 50 citation records by DOI or bibliographic identity."""
        budget = RequestBudget()
        return verify_bibliography_entries(
            [citation.model_dump(exclude_none=True) for citation in citations],
            crossref=self.crossref,
            openalex=self.openalex,
            checked_at=self.clock.now(),
            budget=budget,
        )

    @_safe_tool
    def search_literature(
        self,
        query: Annotated[str, Field(min_length=1, max_length=300)],
        max_results: Annotated[int, Field(ge=1, le=8)] = 8,
    ) -> dict[str, Any]:
        """Search OpenAlex for up to eight public metadata records using a query of 300 characters or fewer."""
        budget = RequestBudget()
        response = self.openalex.search_works(
            query,
            budget,
            max_results=max_results,
        )
        candidates = _as_list(response.payload.get("results", []))
        results: list[dict[str, Any]] = []
        if candidates is not None:
            for item in candidates[:max_results]:
                candidate = _as_mapping(item)
                if candidate is not None:
                    results.append(_search_summary(candidate))
        return {
            "query": query,
            "results": results,
            "checked_at": response.checked_at.isoformat().replace("+00:00", "Z"),
            "cache_age": response.age_label,
            "http_requests": budget.requests,
            "message": "Candidate metadata only; claim support is not established.",
        }

    @staticmethod
    def contract_snapshot() -> list[dict[str, Any]]:
        """Return MCP input contracts generated by the installed FastMCP schema builder."""
        runtime = LibrarianTools()
        snapshot: list[dict[str, Any]] = []
        for name in PROFILE_TOOLS[Profile.LIBRARIAN]:
            tool = Tool.from_function(
                runtime._methods[name],
                name=name,
                description=TOOL_DESCRIPTIONS[name],
                structured_output=True,
            )
            snapshot.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.parameters,
                }
            )
        return snapshot


def _search_summary(record: Mapping[str, object]) -> dict[str, Any]:
    authorships = _as_list(record.get("authorships"))
    first_author = None
    first_authorship = _as_mapping(authorships[0]) if authorships else None
    if first_authorship is not None:
        author = _as_mapping(first_authorship.get("author"))
        if author is not None:
            author_name = author.get("display_name")
            if isinstance(author_name, str):
                first_author = author_name
    primary_location = _as_mapping(record.get("primary_location"))
    source_name = None
    if primary_location is not None:
        source = _as_mapping(primary_location.get("source"))
        if source is not None:
            name = source.get("display_name")
            if isinstance(name, str):
                source_name = name
    return {
        "openalex_id": record.get("id"),
        "doi": record.get("doi"),
        "title": record.get("title"),
        "first_author": first_author,
        "year": record.get("publication_year"),
        "source": source_name,
        "is_retracted": record.get("is_retracted", False),
    }
