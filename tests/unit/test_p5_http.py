"""Plan-linked tests for scholarly retries, budgets, limiters, and cache behavior."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest
import respx

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.scholarly.http import (
    CACHE_TTLS,
    CacheStore,
    CrossrefClient,
    RequestBudget,
    SharedHostLimiter,
)


def test_I_06_429_retry_after_is_honored(tmp_path) -> None:
    sleeps: list[float] = []
    url = "https://api.crossref.org/works/10.1000/example"
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url).mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "2"}, json={"status": "error"}),
                httpx.Response(200, json={"message": {"DOI": "10.1000/example"}}),
            ]
        )
        client = CrossrefClient(
            cache_dir=tmp_path,
            contact_email="labquorum-dev@example.invalid",
            sleep=sleeps.append,
            jitter=lambda: 0.0,
        )
        result = client.get_work("10.1000/example", RequestBudget())
    assert route.call_count == 2
    assert sleeps == [2.0]
    assert result.payload["DOI"] == "10.1000/example"


def test_I_06_five_consecutive_5xx_open_a_sixty_second_circuit(tmp_path) -> None:
    now = [100.0]
    sleeps: list[float] = []
    url = "https://api.crossref.org/works/10.1000/example"
    with respx.mock(assert_all_called=False) as router:
        route = router.get(url).mock(return_value=httpx.Response(503, json={"error": "down"}))
        client = CrossrefClient(
            cache_dir=tmp_path,
            contact_email="labquorum-dev@example.invalid",
            monotonic=lambda: now[0],
            sleep=lambda seconds: (sleeps.append(seconds), now.__setitem__(0, now[0] + seconds)),
            jitter=lambda: 0.0,
        )
        for _ in range(2):
            with pytest.raises(LabQuorumError) as error:
                client.get_work("10.1000/example", RequestBudget())
            assert error.value.code is ErrorCode.UNREACHABLE
        assert route.call_count == 5
        with pytest.raises(LabQuorumError) as open_error:
            client.get_work("10.1000/example", RequestBudget())
        assert open_error.value.code is ErrorCode.UNREACHABLE
        assert route.call_count == 5
        now[0] += 60
        route.mock(return_value=httpx.Response(200, json={"message": {"DOI": "10.1000/example"}}))
        assert client.get_work("10.1000/example", RequestBudget()).payload["DOI"]


def test_I_07_cache_hits_avoid_network_and_label_age(tmp_path) -> None:
    now = [datetime(2026, 11, 5, 12, tzinfo=UTC)]
    url = "https://api.crossref.org/works/10.1000/example"
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url).mock(
            return_value=httpx.Response(200, json={"message": {"DOI": "10.1000/example"}})
        )
        cache = CacheStore(tmp_path, clock=lambda: now[0])
        client = CrossrefClient(
            cache=cache,
            contact_email="labquorum-dev@example.invalid",
            clock=lambda: now[0],
        )
        first = client.get_work("10.1000/example", RequestBudget())
        now[0] += timedelta(hours=1)
        second = client.get_work("10.1000/example", RequestBudget())
        assert first.from_cache is False
        assert second.from_cache is True
        assert second.age_label == "cached, 1h old"
    assert route.call_count == 1
    assert CACHE_TTLS["search"] == timedelta(days=7)
    assert CACHE_TTLS["doi_metadata"] == timedelta(days=30)
    assert CACHE_TTLS["retraction_status"] == timedelta(days=1)


def test_I_05_shared_limiter_enforces_cross_process_policy(tmp_path) -> None:
    limiter = SharedHostLimiter(
        tmp_path / "limiter.sqlite3",
        host="fake.scholar.test",
        rate_per_second=3.0,
        max_in_flight=3,
    )
    assert limiter.host == "fake.scholar.test"
    assert limiter.rate_per_second == 3.0
    assert limiter.max_in_flight == 3


def test_http_call_budget_exceeding_fifty_is_refused() -> None:
    budget = RequestBudget(max_requests=50)
    for _ in range(50):
        budget.consume()
    with pytest.raises(LabQuorumError) as error:
        budget.consume()
    assert error.value.code is ErrorCode.BUDGET_EXCEEDED

