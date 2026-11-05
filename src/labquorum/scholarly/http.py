"""Interfaces for polite, cached scholarly API clients."""

from __future__ import annotations

from typing import Any

CACHE_TTLS: dict[str, Any] = {}


class RequestBudget:
    def __init__(self, max_requests: int = 50) -> None:
        self.max_requests = max_requests
        self.requests = 0

    def consume(self) -> None:
        raise NotImplementedError


class CacheStore:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def get(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class SharedHostLimiter:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def acquire(self) -> Any:
        raise NotImplementedError


class CrossrefClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def get_work(self, doi: str, budget: RequestBudget | None = None) -> Any:
        raise NotImplementedError


class OpenAlexClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def get_work(self, doi: str, budget: RequestBudget | None = None) -> Any:
        raise NotImplementedError

    def search_works(self, query: str, budget: RequestBudget | None = None) -> Any:
        raise NotImplementedError

