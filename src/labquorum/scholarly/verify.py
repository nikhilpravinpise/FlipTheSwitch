"""Deterministic citation identity and retraction verification."""

from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, cast
from urllib.parse import unquote

from rapidfuzz.fuzz import token_set_ratio

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.scholarly.http import (
    CrossrefClient,
    HTTPResult,
    OpenAlexClient,
    RequestBudget,
)

_HTML_TAG = re.compile(r"<[^>]*>")
_LATEX_BRACED_COMMAND = re.compile(r"\\[A-Za-z]+\*?(?:\[[^]]*\])?\{([^{}]*)\}")
_LATEX_COMMAND = re.compile(r"\\[A-Za-z]+\*?")
_NON_WORD = re.compile(r"[^\w]+", flags=re.UNICODE)
_DOI_PREFIX = re.compile(r"^(?:https?://)?(?:dx\.)?doi\.org/", flags=re.IGNORECASE)
JSONMap = Mapping[str, object]


def _as_mapping(value: object) -> JSONMap | None:
    if isinstance(value, dict):
        return cast(dict[str, object], value)
    return None


def _as_list(value: object) -> list[object] | None:
    if isinstance(value, list):
        return cast(list[object], value)
    return None


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

    def as_dict(self) -> dict[str, Any]:
        return {"verdict": self.verdict.value, **self.fields}


def normalize_doi(value: str) -> str:
    """Return a stable lowercase DOI string without wrappers or terminal punctuation."""
    normalized = unquote(value).strip()
    while True:
        previous = normalized
        if normalized.casefold().startswith("doi:"):
            normalized = normalized[4:].strip()
        normalized = _DOI_PREFIX.sub("", normalized, count=1).strip()
        if normalized == previous:
            break
    while True:
        trimmed = normalized.rstrip(".,;:!?)]}>").strip()
        if trimmed == normalized:
            break
        normalized = trimmed
    return normalized.casefold()


def normalize_title(value: str) -> str:
    """Normalize title markup, compatibility characters, accents, and punctuation."""
    normalized = html.unescape(value)
    normalized = _HTML_TAG.sub(" ", normalized)
    previous = ""
    while previous != normalized:
        previous = normalized
        normalized = _LATEX_BRACED_COMMAND.sub(r"\1", normalized)
    normalized = _LATEX_COMMAND.sub(" ", normalized)
    normalized = normalized.replace("~", " ").replace("$", " ")
    normalized = unicodedata.normalize("NFKC", normalized)
    decomposed = unicodedata.normalize("NFKD", normalized)
    folded = "".join(character for character in decomposed if not unicodedata.combining(character))
    return " ".join(_NON_WORD.sub(" ", folded.casefold()).split())


def _coerce_claim(value: CitationClaim | Mapping[str, Any]) -> CitationClaim:
    if isinstance(value, CitationClaim):
        return value
    year = value.get("year")
    return CitationClaim(
        doi=str(value["doi"]) if value.get("doi") not in (None, "") else None,
        title=str(value["title"]) if value.get("title") not in (None, "") else None,
        first_author=(
            str(value["first_author"]) if value.get("first_author") not in (None, "") else None
        ),
        year=int(year) if year is not None else None,
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Citation check times must be timezone-aware.")
    return value.astimezone(UTC)


def _record_title(record: JSONMap, source: str) -> str | None:
    title_value = record.get("title")
    titles = _as_list(title_value)
    if source == "crossref" and titles is not None:
        title_value = titles[0] if titles else None
    if isinstance(title_value, str) and title_value.strip():
        return title_value
    return None


def _surname(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.split(",", maxsplit=1)[0] if "," in value else value.split()[-1]
    normalized = unicodedata.normalize("NFKD", candidate)
    unaccented = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(_NON_WORD.sub(" ", unaccented.casefold()).split()) or None


def _record_first_author(record: JSONMap, source: str) -> str | None:
    if source == "crossref":
        authors = _as_list(record.get("author"))
        first = _as_mapping(authors[0]) if authors else None
        if first is not None:
            family = first.get("family")
            if isinstance(family, str) and family.strip():
                return family
            given = first.get("given")
            if isinstance(given, str) and given.strip():
                return given
    else:
        authorships = _as_list(record.get("authorships"))
        first_authorship = _as_mapping(authorships[0]) if authorships else None
        if first_authorship is not None:
            author = _as_mapping(first_authorship.get("author"))
            if author is not None:
                name = author.get("display_name")
                if isinstance(name, str) and name.strip():
                    return name
    return None


def _record_year(record: JSONMap, source: str) -> int | None:
    if source != "crossref":
        year = record.get("publication_year")
        return int(year) if isinstance(year, (int, str)) and str(year).isdigit() else None
    for field in ("published-online", "published", "published-print", "issued"):
        value = _as_mapping(record.get(field))
        if value is None:
            continue
        parts = _as_list(value.get("date-parts"))
        date_parts = _as_list(parts[0]) if parts else None
        if date_parts:
            first = date_parts[0]
            if isinstance(first, (int, str)) and str(first).isdigit():
                return int(first)
    return None


def _record_doi(record: JSONMap) -> str | None:
    value = record.get("DOI", record.get("doi"))
    return normalize_doi(value) if isinstance(value, str) and value.strip() else None


def _retraction_doi(record: JSONMap) -> str | None:
    updates = _as_list(record.get("update-to"))
    if updates is None:
        return None
    for item in updates:
        update = _as_mapping(item)
        if update is None:
            continue
        update_type = str(update.get("type", "")).casefold().replace("_", "-")
        if update_type == "retraction":
            doi = update.get("DOI", update.get("doi"))
            if isinstance(doi, str) and doi.strip():
                return normalize_doi(doi)
    return None


def _has_correction_or_concern(record: JSONMap) -> bool:
    updates = _as_list(record.get("update-to"))
    if updates is None:
        return False
    note_types = {"correction", "expression-of-concern", "expression of concern"}
    return any(
        update is not None
        and str(update.get("type", "")).casefold().replace("_", "-") in note_types
        for update in (_as_mapping(item) for item in updates)
    )


def _version_of_record_doi(record: JSONMap, source: str) -> str | None:
    if source == "crossref":
        relations = _as_mapping(record.get("relation"))
        if relations is not None:
            versions = _as_list(relations.get("is-preprint-of"))
            if versions is not None:
                for item in versions:
                    version = _as_mapping(item)
                    if version is None:
                        continue
                    version_doi = version.get("id")
                    if (
                        str(version.get("id-type", "")).casefold() == "doi"
                        and isinstance(version_doi, str)
                        and version_doi.strip()
                    ):
                        return normalize_doi(version_doi)
        return None

    locations = _as_list(record.get("locations"))
    if locations is None:
        return None
    for item in locations:
        location = _as_mapping(item)
        if location is None:
            continue
        if str(location.get("version", "")).casefold() != "publishedversion":
            continue
        doi = location.get("doi")
        if isinstance(doi, str) and doi.strip():
            return normalize_doi(doi)
    return None


def _result(  # noqa: PLR0913 - explicit evidence fields keep results auditable
    verdict: Verdict,
    *,
    checked_at: datetime,
    claim_doi: str | None,
    record: JSONMap | None = None,
    source: str | None = None,
    checked_sources: Sequence[str] = (),
    response: HTTPResult | None = None,
    message: str | None = None,
    **extra: Any,
) -> CitationResult:
    date_text = _as_utc(checked_at).date().isoformat()
    fields: dict[str, Any] = {
        "doi": claim_doi,
        "matched_doi": _record_doi(record) if record else None,
        "title": _record_title(record, source or "") if record else None,
        "first_author": _record_first_author(record, source or "") if record else None,
        "year": _record_year(record, source or "") if record else None,
        "source": source,
        "checked_at": _as_utc(checked_at).isoformat().replace("+00:00", "Z"),
        "checked_sources": list(checked_sources),
        "cache_age": response.age_label if response else "not applicable",
        "claim_support": "not established",
        "message": message or _default_message(verdict, date_text),
    }
    fields.update(extra)
    return CitationResult(verdict, fields)


def _default_message(verdict: Verdict, date_text: str) -> str:
    if verdict in {Verdict.VERIFIED, Verdict.VERIFIED_WITH_NOTE}:
        return (
            "metadata matched; no retraction signal found in checked sources as of "
            f"{date_text}; claim support not established"
        )
    if verdict is Verdict.RETRACTED:
        return f"A checked source reports a retraction as of {date_text}."
    if verdict is Verdict.UNREACHABLE:
        return f"A checked source was unreachable as of {date_text}; no verification was made."
    if verdict is Verdict.UNRESOLVED:
        return f"No matching metadata was found in checked sources as of {date_text}."
    return "Bibliographic identity needs review against the retrieved metadata."


def _unreachable_result(
    claim_doi: str | None,
    checked_at: datetime,
    checked_sources: Sequence[str],
    error: LabQuorumError,
) -> CitationResult:
    return _result(
        Verdict.UNREACHABLE,
        checked_at=checked_at,
        claim_doi=claim_doi,
        checked_sources=checked_sources,
        message=f"Scholarly metadata could not be reached: {error.message}",
    )


def verify_citation(  # noqa: PLR0911, PLR0912, PLR0913, PLR0915
    claim_value: CitationClaim | Mapping[str, Any],
    *,
    crossref: CrossrefClient | None = None,
    openalex: OpenAlexClient | None = None,
    checked_at: datetime | None = None,
    record: JSONMap | None = None,
    source: str | None = None,
    budget: RequestBudget | None = None,
) -> CitationResult:
    """Verify DOI metadata deterministically, without inferring claim support."""
    claim = _coerce_claim(claim_value)
    claim_doi = normalize_doi(claim.doi) if claim.doi else None
    moment = _as_utc(checked_at or datetime.now(UTC))
    request_budget = budget or RequestBudget()
    checked_sources: list[str] = []
    response: HTTPResult | None = None
    retraction_response: HTTPResult | None = None
    retraction_record: JSONMap | None = None
    score: float | None = None

    if record is None:
        if claim_doi:
            if crossref is None or openalex is None:
                raise LabQuorumError(
                    ErrorCode.INVALID_ARGUMENT,
                    "Citation verification requires Crossref and OpenAlex clients.",
                )
            try:
                checked_sources.append("Crossref")
                response = crossref.get_work(claim_doi, request_budget)
                if response.status_code == 404:
                    checked_sources.append("OpenAlex")
                    response = openalex.get_work(claim_doi, request_budget)
                    source = "openalex"
                    retraction_record = response.payload
                else:
                    source = "crossref"
                    if _retraction_doi(response.payload) is None:
                        checked_sources.append("OpenAlex")
                        retraction_response = openalex.get_work(claim_doi, request_budget)
                        if retraction_response.status_code != 404:
                            retraction_record = retraction_response.payload
                if response.status_code == 404:
                    return _result(
                        Verdict.UNRESOLVED,
                        checked_at=checked_at or response.checked_at,
                        claim_doi=claim_doi,
                        checked_sources=checked_sources,
                        response=response,
                    )
                record = response.payload
                if source == "openalex":
                    retraction_response = response
            except LabQuorumError as error:
                if error.code is not ErrorCode.UNREACHABLE:
                    raise
                return _unreachable_result(claim_doi, moment, checked_sources, error)
        elif claim.title:
            if openalex is None:
                raise LabQuorumError(
                    ErrorCode.INVALID_ARGUMENT,
                    "Title verification requires an OpenAlex client.",
                )
            try:
                checked_sources.append("OpenAlex")
                response = openalex.search_works(claim.title, request_budget, max_results=8)
            except LabQuorumError as error:
                if error.code is not ErrorCode.UNREACHABLE:
                    raise
                return _unreachable_result(None, moment, checked_sources, error)
            candidates_value = _as_list(response.payload.get("results", []))
            if not candidates_value:
                return _result(
                    Verdict.UNRESOLVED,
                    checked_at=checked_at or response.checked_at,
                    claim_doi=None,
                    checked_sources=checked_sources,
                    response=response,
                )
            candidates = [
                candidate
                for item in candidates_value
                if (candidate := _as_mapping(item)) is not None
            ]
            claim_title = normalize_title(claim.title)
            ranked = [
                (
                    token_set_ratio(
                        claim_title,
                        normalize_title(_record_title(candidate, "openalex") or ""),
                    ),
                    index,
                    candidate,
                )
                for index, candidate in enumerate(candidates)
            ]
            if not ranked:
                return _result(
                    Verdict.UNRESOLVED,
                    checked_at=checked_at or response.checked_at,
                    claim_doi=None,
                    checked_sources=checked_sources,
                    response=response,
                )
            selected_score, _, record = max(ranked, key=lambda candidate: candidate[0])
            score = float(selected_score)
            source = "openalex"
            retraction_record = record
        else:
            return _result(
                Verdict.NEEDS_REVIEW,
                checked_at=moment,
                claim_doi=None,
                message="Provide a DOI or a title to retrieve citation metadata.",
            )
    else:
        if source is None:
            source = "crossref"
        checked_sources = ["Crossref" if source == "crossref" else "OpenAlex"]
        score = None
        retraction_record = record if source == "openalex" else None

    assert record is not None
    result_time = checked_at or (response.checked_at if response else moment)
    selected_source = source or "crossref"
    found_title = _record_title(record, selected_source)
    found_author = _record_first_author(record, selected_source)
    found_year = _record_year(record, selected_source)
    retraction_doi = _retraction_doi(record) if selected_source == "crossref" else None
    is_retracted = retraction_doi is not None or (
        retraction_record is not None and retraction_record.get("is_retracted") is True
    )
    base_fields: dict[str, Any] = {
        "diff": {},
        "retraction_doi": retraction_doi,
        "retraction_signal_source": (
            "Crossref"
            if retraction_doi is not None
            else "OpenAlex"
            if retraction_record is not None and retraction_record.get("is_retracted") is True
            else None
        ),
        "version_of_record_doi": None,
    }
    if score is not None:
        base_fields["retrieval_score"] = float(score)
    if is_retracted:
        return _result(
            Verdict.RETRACTED,
            checked_at=result_time,
            claim_doi=claim_doi,
            record=record,
            source=selected_source,
            checked_sources=checked_sources,
            response=response,
            retraction_cache_age=(
                retraction_response.age_label if retraction_response is not None else None
            ),
            **base_fields,
        )

    diff: dict[str, dict[str, Any]] = {}
    if claim.first_author:
        claimed_author = _surname(claim.first_author)
        found_surname = _surname(found_author)
        if claimed_author != found_surname:
            diff["first_author"] = {"claimed": claim.first_author, "found": found_author}
    if claim.year is not None and (found_year is None or abs(claim.year - found_year) > 1):
        diff["year"] = {"claimed": claim.year, "found": found_year}
    if diff:
        base_fields["diff"] = diff
        return _result(
            Verdict.MISMATCH,
            checked_at=result_time,
            claim_doi=claim_doi,
            record=record,
            source=selected_source,
            checked_sources=checked_sources,
            response=response,
            **base_fields,
        )

    exact_title = bool(claim.title and found_title)
    exact_title = exact_title and normalize_title(claim.title or "") == normalize_title(
        found_title or ""
    )
    if not exact_title:
        if claim.title and found_title:
            base_fields["diff"] = {"title": {"claimed": claim.title, "found": found_title}}
        return _result(
            Verdict.NEEDS_REVIEW,
            checked_at=result_time,
            claim_doi=claim_doi,
            record=record,
            source=selected_source,
            checked_sources=checked_sources,
            response=response,
            **base_fields,
        )

    notes: list[str] = []
    if selected_source == "crossref" and _has_correction_or_concern(record):
        notes.append("Crossref lists a correction or expression of concern.")
    version_doi = _version_of_record_doi(record, selected_source)
    if version_doi:
        notes.append("A published version is linked to this preprint.")
        base_fields["version_of_record_doi"] = version_doi
    base_fields["notes"] = notes
    verdict = Verdict.VERIFIED_WITH_NOTE if notes else Verdict.VERIFIED
    return _result(
        verdict,
        checked_at=result_time,
        claim_doi=claim_doi,
        record=record,
        source=selected_source,
        checked_sources=checked_sources,
        response=response,
        **base_fields,
    )


def _deduplication_key(claim: CitationClaim) -> tuple[Any, ...]:
    if claim.doi:
        normalized_doi = normalize_doi(claim.doi)
        if normalized_doi:
            return ("doi", normalized_doi)
    return (
        "metadata",
        normalize_title(claim.title or ""),
        _surname(claim.first_author),
        claim.year,
    )


def verify_bibliography(
    citations: Sequence[CitationClaim | Mapping[str, Any]],
    *,
    crossref: CrossrefClient | None = None,
    openalex: OpenAlexClient | None = None,
    checked_at: datetime | None = None,
    budget: RequestBudget | None = None,
) -> dict[str, Any]:
    """Verify unique bibliography entries while preserving duplicate positions."""
    if len(citations) > 50:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "A bibliography tool call accepts at most 50 citation entries.",
            {"entries": len(citations), "limit": 50},
        )
    request_budget = budget or RequestBudget()
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, int]] = []
    seen: dict[tuple[Any, ...], int] = {}
    for index, citation in enumerate(citations):
        claim = _coerce_claim(citation)
        key = _deduplication_key(claim)
        canonical_index = seen.get(key)
        if canonical_index is not None:
            duplicates.append({"duplicate_index": index, "canonical_index": canonical_index})
            continue
        seen[key] = index
        unique.append(
            verify_citation(
                claim,
                crossref=crossref,
                openalex=openalex,
                checked_at=checked_at,
                budget=request_budget,
            ).as_dict()
        )
    return {
        "entries": unique,
        "duplicates": duplicates,
        "input_count": len(citations),
        "unique_count": len(unique),
        "http_requests": request_budget.requests,
    }
