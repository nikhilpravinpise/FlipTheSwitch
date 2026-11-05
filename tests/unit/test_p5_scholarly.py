"""Plan-linked unit tests for citation identity and verdict rules."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest
from hypothesis import given, strategies as st

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.scholarly.http import CrossrefClient, OpenAlexClient, RequestBudget
from labquorum.scholarly.verify import (
    CitationClaim,
    Verdict,
    normalize_doi,
    normalize_title,
    verify_bibliography,
    verify_citation,
)

CHECKED_AT = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        (" DOI:HTTPS://DOI.ORG/10.1038/S41586-021-03819-2. ", "10.1038/s41586-021-03819-2"),
        ("https://doi.org/10.1000%2FABC", "10.1000/abc"),
    ],
)
def test_U_C01_doi_normalization(supplied: str, expected: str) -> None:
    assert normalize_doi(supplied) == expected


@given(st.text(min_size=1, max_size=100))
def test_P_04_doi_normalization_is_idempotent(value: str) -> None:
    normalized = normalize_doi(value)
    assert normalize_doi(normalized) == normalized


def test_U_C02_exact_normalized_title_or_needs_review(tmp_path) -> None:
    assert normalize_title(r"<i>ＡlphaFold</i>: \textit{accurate} structure") == (
        "alphafold accurate structure"
    )
    claim = CitationClaim(doi="10.1038/example", title="A study of the evidence")
    crossref = CrossrefClient(
        cache_dir=tmp_path,
        transport=httpx.MockTransport(lambda request: httpx.Response(200)),
    )
    result = verify_citation(
        claim,
        crossref=crossref,
        openalex=OpenAlexClient(
            cache_dir=tmp_path,
            transport=httpx.MockTransport(lambda request: httpx.Response(404)),
        ),
        checked_at=CHECKED_AT,
        record={
            "DOI": "10.1038/example",
            "title": ["A study of the evidence and its limits"],
            "author": [{"family": "Example"}],
            "published": {"date-parts": [[2024]]},
        },
        source="crossref",
    )
    assert result.verdict is Verdict.NEEDS_REVIEW


@pytest.mark.parametrize(
    ("supplied_title", "expected"),
    [
        ("Accurate protein structure prediction", Verdict.NEEDS_REVIEW),
        (
            "Highly accurate protein structure prediction with AlphaFold is definitive",
            Verdict.NEEDS_REVIEW,
        ),
        ("Highly accurate protein structure prediction with AlphaFold", Verdict.VERIFIED),
    ],
)
def test_U_C02_title_search_candidates_require_exact_full_title(
    supplied_title: str,
    expected: Verdict,
    tmp_path,
) -> None:
    def search_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "doi": "https://doi.org/10.1038/s41586-021-03819-2",
                        "title": "Highly accurate protein structure prediction with AlphaFold",
                        "publication_year": 2021,
                        "authorships": [{"author": {"display_name": "John Jumper"}}],
                        "is_retracted": False,
                        "locations": [],
                    }
                ]
            },
        )

    result = verify_citation(
        CitationClaim(title=supplied_title),
        openalex=OpenAlexClient(
            cache_dir=tmp_path,
            transport=httpx.MockTransport(search_response),
        ),
        checked_at=CHECKED_AT,
    )
    assert result.verdict is expected


@pytest.mark.parametrize(
    ("claimed", "recorded"),
    [("García", "Garcia"), ("SMITH", "Smith")],
)
def test_U_C03_first_author_surname_is_accent_and_case_insensitive(
    claimed: str,
    recorded: str,
) -> None:
    claim = CitationClaim(title="A complete title", first_author=claimed, year=2020)
    result = verify_citation(
        claim,
        record={
            "title": ["A complete title"],
            "author": [{"family": recorded}],
            "published": {"date-parts": [[2020]]},
        },
        source="crossref",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.VERIFIED
    assert result.fields["message"] == (
        "metadata matched; no retraction signal found in checked sources as of "
        "2026-11-05; claim support not established"
    )


@pytest.mark.parametrize(
    ("claimed_year", "expected"),
    [(2021, Verdict.VERIFIED), (2024, Verdict.MISMATCH)],
)
def test_U_C04_year_tolerance_is_one_year(
    claimed_year: int,
    expected: Verdict,
) -> None:
    result = verify_citation(
        CitationClaim(title="A complete title", year=claimed_year),
        record={
            "title": ["A complete title"],
            "published": {"date-parts": [[2022]]},
        },
        source="crossref",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is expected
    if expected is Verdict.MISMATCH:
        assert result.fields["diff"]["year"] == {"claimed": 2024, "found": 2022}


def test_U_C05_crossref_retraction_update_returns_notice_doi() -> None:
    result = verify_citation(
        CitationClaim(doi="10.1038/s41598-019-45611-3"),
        record={
            "DOI": "10.1038/s41598-019-45611-3",
            "title": ["A retracted article"],
            "update-to": [
                {
                    "DOI": "10.1038/s41598-023-44593-7",
                    "type": "retraction",
                    "source": "retraction-watch",
                }
            ],
        },
        source="crossref",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.RETRACTED
    assert result.fields["retraction_doi"] == "10.1038/s41598-023-44593-7"
    assert result.fields["retraction_signal_source"] == "Crossref"


def test_U_C06_openalex_is_retracted_returns_retracted() -> None:
    result = verify_citation(
        CitationClaim(doi="10.1000/retracted"),
        record={
            "doi": "https://doi.org/10.1000/retracted",
            "title": "A retracted article",
            "publication_year": 2022,
            "is_retracted": True,
        },
        source="openalex",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.RETRACTED
    assert result.fields["retraction_signal_source"] == "OpenAlex"


@pytest.mark.parametrize(
    "claimed_title",
    [
        "Highly accurate protein structure prediction",
        "Highly accurate protein structure prediction with AlphaFold is definitive",
    ],
)
def test_I_35_exact_doi_with_truncated_or_qualified_title_needs_review(
    claimed_title: str,
) -> None:
    result = verify_citation(
        CitationClaim(doi="10.1038/s41586-021-03819-2", title=claimed_title),
        record={
            "DOI": "10.1038/s41586-021-03819-2",
            "title": ["Highly accurate protein structure prediction with AlphaFold"],
            "author": [{"family": "Jumper"}],
            "published": {"date-parts": [[2021]]},
        },
        source="crossref",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.NEEDS_REVIEW
    assert result.verdict is not Verdict.VERIFIED


def test_U_C07_preprint_with_published_version_returns_note() -> None:
    result = verify_citation(
        CitationClaim(doi="10.48550/arxiv.1234", title="A complete title"),
        record={
            "DOI": "10.48550/arxiv.1234",
            "title": ["A complete title"],
            "relation": {
                "is-preprint-of": [
                    {"id-type": "doi", "id": "10.1000/version-of-record"}
                ]
            },
        },
        source="crossref",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.VERIFIED_WITH_NOTE
    assert result.fields["version_of_record_doi"] == "10.1000/version-of-record"


def test_U_C08_failed_network_is_unreachable_never_verified(tmp_path) -> None:
    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("connection timed out", request=request)

    crossref = CrossrefClient(
        cache_dir=tmp_path,
        contact_email="labquorum-dev@example.invalid",
        transport=httpx.MockTransport(timeout),
        sleep=lambda _: None,
    )
    result = verify_citation(
        CitationClaim(doi="10.1000/missing", title="A complete title"),
        crossref=crossref,
        openalex=OpenAlexClient(
            cache_dir=tmp_path,
            transport=httpx.MockTransport(timeout),
            sleep=lambda _: None,
        ),
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.UNREACHABLE
    assert result.verdict is not Verdict.VERIFIED


def test_U_C12_correction_returns_verified_with_note() -> None:
    result = verify_citation(
        CitationClaim(title="A complete title"),
        record={
            "title": ["A complete title"],
            "update-to": [
                {"DOI": "10.1000/correction", "type": "correction", "source": "publisher"}
            ],
        },
        source="crossref",
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.VERIFIED_WITH_NOTE


def test_U_C09_bibliography_deduplicates_by_doi_and_title_author_year(tmp_path) -> None:
    def crossref_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "message": {
                    "DOI": "10.1000/example",
                    "title": ["A complete title"],
                    "author": [{"family": "Smith"}],
                    "published": {"date-parts": [[2020]]},
                }
            },
        )

    def openalex_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "doi": "https://doi.org/10.1000/example",
                        "title": "A complete title",
                        "publication_year": 2020,
                        "authorships": [{"author": {"display_name": "Jane Smith"}}],
                    }
                ]
            },
        )

    crossref = CrossrefClient(
        cache_dir=tmp_path,
        contact_email="labquorum-dev@example.invalid",
        transport=httpx.MockTransport(crossref_response),
    )
    openalex = OpenAlexClient(
        cache_dir=tmp_path,
        transport=httpx.MockTransport(openalex_response),
    )
    result = verify_bibliography(
        [
            CitationClaim(doi="10.1000/example", title="A complete title"),
            CitationClaim(doi="DOI:10.1000/EXAMPLE.", title="Different supplied title"),
            CitationClaim(title="A complete title", first_author="Smith", year=2020),
            CitationClaim(title="A complete title", first_author="Smith", year=2020),
        ],
        crossref=crossref,
        openalex=openalex,
        checked_at=CHECKED_AT,
    )
    assert result["unique_count"] == 2
    assert result["duplicates"] == [
        {"duplicate_index": 1, "canonical_index": 0},
        {"duplicate_index": 3, "canonical_index": 2},
    ]


def test_U_C12_datacite_doi_falls_back_to_openalex(tmp_path) -> None:
    doi = "10.5281/zenodo.1234567"

    def crossref_miss(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": "error", "message": "not found"})

    def openalex_hit(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "doi": f"https://doi.org/{doi}",
                "title": "A complete title",
                "publication_year": 2020,
                "authorships": [{"author": {"display_name": "Jane Smith"}}],
                "is_retracted": False,
                "locations": [],
            },
        )

    result = verify_citation(
        CitationClaim(doi=doi, title="A complete title", first_author="Smith", year=2020),
        crossref=CrossrefClient(
            cache_dir=tmp_path,
            contact_email="labquorum-dev@example.invalid",
            transport=httpx.MockTransport(crossref_miss),
        ),
        openalex=OpenAlexClient(
            cache_dir=tmp_path,
            transport=httpx.MockTransport(openalex_hit),
        ),
        checked_at=CHECKED_AT,
    )
    assert result.verdict is Verdict.VERIFIED
    assert result.fields["checked_sources"] == ["Crossref", "OpenAlex"]


def test_I_06_request_budget_exhaustion_is_a_domain_error() -> None:
    budget = RequestBudget(max_requests=1)
    budget.consume()
    with pytest.raises(LabQuorumError) as error:
        budget.consume()
    assert error.value.code is ErrorCode.BUDGET_EXCEEDED

