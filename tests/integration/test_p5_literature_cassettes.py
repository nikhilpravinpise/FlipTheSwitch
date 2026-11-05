"""Cassette-backed citation goldens. Tests are socket-blocked in normal mode."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from labquorum.scholarly.http import CrossrefClient, OpenAlexClient
from labquorum.scholarly.verify import CitationClaim, Verdict, verify_citation

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = ROOT / "tests" / "fixtures" / "p5_citation_goldens.json"


@pytest.fixture
def vcr_config() -> dict[str, object]:
    return {
        "filter_headers": ["authorization", "user-agent"],
        "filter_query_parameters": ["mailto", "api_key"],
    }


def _goldens() -> dict[str, dict[str, object]]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _verify(tmp_path: Path, claim: CitationClaim):
    return verify_citation(
        claim,
        crossref=CrossrefClient(cache_dir=tmp_path),
        openalex=OpenAlexClient(cache_dir=tmp_path),
    )


@pytest.mark.vcr()
def test_I04_crossref_cassette_verifies_seeded_real_doi(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONTACT_EMAIL", "labquorum-dev@example.invalid")
    fixture = _goldens()["verified"]
    result = _verify(tmp_path, CitationClaim(**fixture["claim"]))
    assert result.verdict is Verdict.VERIFIED
    assert result.fields["doi"] == fixture["doi"]


@pytest.mark.vcr()
def test_I04_crossref_cassette_reports_seeded_retraction(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONTACT_EMAIL", "labquorum-dev@example.invalid")
    fixture = _goldens()["retracted"]
    result = _verify(tmp_path, CitationClaim(**fixture["claim"]))
    assert result.verdict is Verdict.RETRACTED
    assert result.fields["retraction_signal_source"] in {"Crossref", "OpenAlex"}
    if result.fields["retraction_signal_source"] == "Crossref":
        assert result.fields["retraction_doi"] == fixture["notice_doi"]


@pytest.mark.vcr()
def test_I04_cassette_reports_seeded_fabricated_doi_as_unresolved(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CONTACT_EMAIL", "labquorum-dev@example.invalid")
    fixture = _goldens()["fabricated"]
    result = _verify(tmp_path, CitationClaim(**fixture["claim"]))
    assert result.verdict is Verdict.UNRESOLVED


def test_G_golden_set_has_only_explicit_expected_fixture_classes() -> None:
    fixtures = _goldens()
    assert {record["label"] for record in fixtures.values()} == {
        "verified",
        "retracted",
        "fabricated",
    }
    assert {record["expected"] for record in fixtures.values()} == {
        "VERIFIED",
        "RETRACTED",
        "UNRESOLVED",
    }

