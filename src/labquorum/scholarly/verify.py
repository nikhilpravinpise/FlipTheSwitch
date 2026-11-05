"""Deterministic citation metadata verification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Verdict(StrEnum):
    VERIFIED = "VERIFIED"
    VERIFIED_WITH_NOTE = "VERIFIED_WITH_NOTE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    UNRESOLVED = "UNRESOLVED"
    MISMATCH = "MISMATCH"
    RETRACTED = "RETRACTED"
    UNREACHABLE = "UNREACHABLE"


@dataclass(frozen=True)
class CitationClaim:
    doi: str | None = None
    title: str | None = None
    first_author: str | None = None
    year: int | None = None


@dataclass(frozen=True)
class CitationResult:
    verdict: Verdict
    fields: dict[str, Any]


def normalize_doi(value: str) -> str:
    raise NotImplementedError


def normalize_title(value: str) -> str:
    raise NotImplementedError


def verify_citation(*args: Any, **kwargs: Any) -> CitationResult:
    raise NotImplementedError


def verify_bibliography(*args: Any, **kwargs: Any) -> dict[str, Any]:
    raise NotImplementedError

