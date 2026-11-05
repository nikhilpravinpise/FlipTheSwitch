"""Plan-linked tests for scholarly retries, budgets, limiters, and cache behavior."""

from __future__ import annotations

import multiprocessing
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.scholarly.http import (
    CACHE_TTLS,
    CacheStore,
    CrossrefClient,
    OpenAlexClient,
    RequestBudget,
    SharedHostLimiter,
)


class ProcessFakeClock:
    def __init__(self, value, lock) -> None:
        self.value = value
        self.lock = lock

    def __call__(self) -> float:
        with self.lock:
            return self.value.value

    def sleep(self, seconds: float) -> None:
        with self.lock:
            self.value.value += seconds


@dataclass
class WorkerState:
    clock: ProcessFakeClock
    active_count: Any
    maximum_active: Any
    state_lock: Any
    events: Any


def _fake_scholar_worker(database_path: Path, state: WorkerState) -> None:
    clock = state.clock
    active_count = state.active_count
    maximum_active = state.maximum_active
    state_lock = state.state_lock
    events = state.events
    limiter = SharedHostLimiter(
        database_path,
        host="fake.scholar.test",
        rate_per_second=3.0,
        max_in_flight=3,
        monotonic=clock,
        sleep=clock.sleep,
    )
    for _ in range(4):
        lease = limiter.acquire()
        with state_lock:
            active_count.value += 1
            maximum_active.value = max(maximum_active.value, active_count.value)
            started_at = clock()
            events.put(started_at)
        clock.sleep(0.5)
        time.sleep(0.01)
        with state_lock:
            active_count.value -= 1
        lease.release()


def _advance_clock(sleeps: list[float], now: list[float], seconds: float) -> None:
    sleeps.append(seconds)
    now[0] += seconds


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
    assert sleeps[0] == 2.0
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
            sleep=lambda seconds: _advance_clock(sleeps, now, seconds),
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


def test_I_05_two_processes_share_host_rate_and_concurrency_limits(tmp_path) -> None:
    context = multiprocessing.get_context("spawn")
    clock_value = context.Value("d", 100.0)
    clock_lock = context.Lock()
    fake_clock = ProcessFakeClock(clock_value, clock_lock)
    active_count = context.Value("i", 0)
    maximum_active = context.Value("i", 0)
    state_lock = context.Lock()
    events = context.Queue()
    database_path = tmp_path / "shared-limiter.sqlite3"
    state = WorkerState(fake_clock, active_count, maximum_active, state_lock, events)
    workers = [
        context.Process(
            target=_fake_scholar_worker,
            args=(database_path, state),
        )
        for _ in range(2)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=15)
    assert [worker.exitcode for worker in workers] == [0, 0]
    starts = sorted(events.get(timeout=2) for _ in range(8))
    assert maximum_active.value <= 3
    assert all(right - left >= (1 / 3) - 0.000001 for left, right in pairwise(starts))


def test_http_call_budget_exceeding_fifty_is_refused() -> None:
    budget = RequestBudget(max_requests=50)
    for _ in range(50):
        budget.consume()
    with pytest.raises(LabQuorumError) as error:
        budget.consume()
    assert error.value.code is ErrorCode.BUDGET_EXCEEDED


def test_openalex_query_and_result_limits_are_enforced_before_http(tmp_path) -> None:
    client = OpenAlexClient(
        cache_dir=tmp_path,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"results": []})),
    )
    with pytest.raises(LabQuorumError) as long_query:
        client.search_works("q" * 301, RequestBudget())
    assert long_query.value.code is ErrorCode.INVALID_ARGUMENT
    with pytest.raises(LabQuorumError) as too_many:
        client.search_works("microscopy", RequestBudget(), max_results=9)
    assert too_many.value.code is ErrorCode.INVALID_ARGUMENT
