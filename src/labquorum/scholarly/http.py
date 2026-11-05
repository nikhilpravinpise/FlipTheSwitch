"""Bounded, cached HTTP clients for Crossref and OpenAlex."""

from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlencode

import httpx

from labquorum.domain.errors import ErrorCode, LabQuorumError

CROSSREF_BASE_URL = "https://api.crossref.org"
OPENALEX_BASE_URL = "https://api.openalex.org"
REQUEST_TIMEOUT_SECONDS = 10.0
MAX_ATTEMPTS = 3
MAX_REQUESTS_PER_TOOL_CALL = 50
CIRCUIT_FAILURE_THRESHOLD = 5
CIRCUIT_OPEN_SECONDS = 60.0

CACHE_TTLS: dict[str, timedelta] = {
    "search": timedelta(days=7),
    "doi_metadata": timedelta(days=30),
    "retraction_status": timedelta(days=1),
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Cache and HTTP clocks must return timezone-aware datetimes.")
    return value.astimezone(UTC)


def _default_cache_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if local_app_data:
        return Path(local_app_data) / "LabQuorum" / "cache" / "scholarly"
    if xdg_cache:
        return Path(xdg_cache) / "labquorum" / "scholarly"
    return Path.home() / ".cache" / "labquorum" / "scholarly"


@dataclass
class RequestBudget:
    """Count every outbound HTTP attempt made by one tool invocation."""

    max_requests: int = MAX_REQUESTS_PER_TOOL_CALL
    requests: int = 0

    def __post_init__(self) -> None:
        if self.max_requests < 1:
            raise ValueError("A request budget must allow at least one HTTP request.")

    def consume(self) -> None:
        if self.requests >= self.max_requests:
            raise LabQuorumError(
                ErrorCode.BUDGET_EXCEEDED,
                "The literature request exceeded its HTTP call budget.",
                {"limit": self.max_requests, "requests": self.requests},
            )
        self.requests += 1


@dataclass(frozen=True)
class CacheEntry:
    payload: dict[str, Any]
    status_code: int
    retrieved_at: datetime
    age_seconds: float


class CacheStore:
    """Persist JSON API responses with category-specific expiration."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        *,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.cache_dir = cache_dir or _default_cache_dir()
        self.clock = clock

    def load(
        self,
        request_key: str,
        categories: Sequence[str],
        *,
        now: datetime | None = None,
    ) -> CacheEntry | None:
        if not categories:
            return None
        current = _as_utc(now or self.clock())
        entries: list[CacheEntry] = []
        for category in categories:
            ttl = CACHE_TTLS.get(category)
            if ttl is None:
                raise ValueError(f"Unknown scholarly cache category: {category}")
            path = self._path(request_key, category)
            try:
                encoded = json.loads(path.read_text(encoding="utf-8"))
                payload_value = encoded["payload"]
                status_code = int(encoded["status_code"])
                retrieved_at = _as_utc(datetime.fromisoformat(encoded["retrieved_at"]))
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                return None
            if not isinstance(payload_value, dict):
                return None
            payload = cast(dict[str, Any], payload_value)
            age_seconds = max(0.0, (current - retrieved_at).total_seconds())
            if age_seconds > ttl.total_seconds():
                return None
            entries.append(CacheEntry(payload, status_code, retrieved_at, age_seconds))
        return min(entries, key=lambda entry: entry.age_seconds)

    def save(
        self,
        request_key: str,
        categories: Sequence[str],
        payload: dict[str, Any],
        status_code: int,
        *,
        retrieved_at: datetime | None = None,
    ) -> None:
        if not categories:
            return
        fetched = _as_utc(retrieved_at or self.clock())
        data = json.dumps(
            {
                "payload": payload,
                "status_code": status_code,
                "retrieved_at": fetched.isoformat(),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        for category in categories:
            if category not in CACHE_TTLS:
                raise ValueError(f"Unknown scholarly cache category: {category}")
            path = self._path(request_key, category)
            temporary = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
            temporary.write_text(data, encoding="utf-8")
            os.replace(temporary, path)

    def _path(self, request_key: str, category: str) -> Path:
        digest = hashlib.sha256(f"{category}\0{request_key}".encode()).hexdigest()
        return self.cache_dir / f"{digest}.json"


def _age_label(age_seconds: float, *, from_cache: bool) -> str:
    if not from_cache:
        return "fresh"
    if age_seconds < 60:
        return "cached, <1m old"
    if age_seconds < 3_600:
        minutes = max(1, int(age_seconds // 60))
        return f"cached, {minutes}m old"
    if age_seconds < 86_400:
        hours = max(1, int(age_seconds // 3_600))
        return f"cached, {hours}h old"
    days = max(1, int(age_seconds // 86_400))
    return f"cached, {days}d old"


@dataclass(frozen=True)
class HTTPResult:
    payload: dict[str, Any]
    status_code: int
    checked_at: datetime
    retrieved_at: datetime
    from_cache: bool
    age_seconds: float

    @property
    def age_label(self) -> str:
        return _age_label(self.age_seconds, from_cache=self.from_cache)


class HostLease:
    """A shared in-flight slot released after one outbound HTTP attempt."""

    def __init__(self, limiter: SharedHostLimiter, lease_id: str) -> None:
        self._limiter = limiter
        self._lease_id = lease_id
        self._released = False

    def release(self) -> None:
        if not self._released:
            self._limiter.release_lease(self._lease_id)
            self._released = True

    def __enter__(self) -> HostLease:
        return self

    def __exit__(self, *_: object) -> None:
        self.release()


class SharedHostLimiter:
    """Coordinate host request spacing and in-flight permits through SQLite."""

    def __init__(  # noqa: PLR0913 - limiter dependencies are injected for deterministic tests
        self,
        database_path: Path,
        *,
        host: str,
        rate_per_second: float,
        max_in_flight: int,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        lease_seconds: float = 30.0,
    ) -> None:
        if rate_per_second <= 0 or max_in_flight < 1:
            raise ValueError("Host limiter rates and concurrency must be positive.")
        self.database_path = database_path
        self.host = host
        self.rate_per_second = rate_per_second
        self.max_in_flight = max_in_flight
        self.monotonic = monotonic
        self.sleep = sleep
        self.lease_seconds = lease_seconds
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            self._create_schema(connection)

    def acquire(self) -> HostLease:
        lease_id = uuid.uuid4().hex
        while True:
            now = self.monotonic()
            wait_seconds = 0.0
            with self._connect() as connection:
                self._create_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "INSERT OR IGNORE INTO host_bucket "
                    "(host, next_allowed, consecutive_5xx, circuit_until) VALUES (?, ?, 0, 0)",
                    (self.host, now),
                )
                row = connection.execute(
                    "SELECT next_allowed, circuit_until FROM host_bucket WHERE host = ?",
                    (self.host,),
                ).fetchone()
                assert row is not None
                circuit_until = float(row["circuit_until"])
                if circuit_until > now:
                    connection.rollback()
                    raise self._unreachable(
                        f"The {self.host} circuit is open.",
                        {"retry_after_seconds": round(circuit_until - now, 3)},
                    )
                if circuit_until and circuit_until <= now:
                    connection.execute(
                        "UPDATE host_bucket SET consecutive_5xx = 0, circuit_until = 0 "
                        "WHERE host = ?",
                        (self.host,),
                    )
                connection.execute(
                    "DELETE FROM host_lease WHERE host = ? AND expires_at <= ?",
                    (self.host, now),
                )
                active = int(
                    connection.execute(
                        "SELECT COUNT(*) FROM host_lease WHERE host = ?", (self.host,)
                    ).fetchone()[0]
                )
                next_allowed = float(row["next_allowed"])
                if active < self.max_in_flight and next_allowed <= now:
                    connection.execute(
                        "INSERT INTO host_lease (lease_id, host, expires_at) VALUES (?, ?, ?)",
                        (lease_id, self.host, now + self.lease_seconds),
                    )
                    connection.execute(
                        "UPDATE host_bucket SET next_allowed = ? WHERE host = ?",
                        (now + 1.0 / self.rate_per_second, self.host),
                    )
                    connection.commit()
                    return HostLease(self, lease_id)
                wait_seconds = max(0.0, next_allowed - now)
                if active >= self.max_in_flight:
                    wait_seconds = min(wait_seconds or 0.05, 0.05)
                connection.commit()
            self.sleep(max(wait_seconds, 0.001))

    def circuit_is_open(self) -> bool:
        now = self.monotonic()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT circuit_until FROM host_bucket WHERE host = ?", (self.host,)
            ).fetchone()
        return row is not None and float(row[0]) > now

    def record_server_error(self) -> bool:
        now = self.monotonic()
        with self._connect() as connection:
            self._create_schema(connection)
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT OR IGNORE INTO host_bucket "
                "(host, next_allowed, consecutive_5xx, circuit_until) VALUES (?, ?, 0, 0)",
                (self.host, now),
            )
            row = connection.execute(
                "SELECT consecutive_5xx FROM host_bucket WHERE host = ?", (self.host,)
            ).fetchone()
            assert row is not None
            count = int(row[0]) + 1
            circuit_until = now + CIRCUIT_OPEN_SECONDS if count >= CIRCUIT_FAILURE_THRESHOLD else 0
            connection.execute(
                "UPDATE host_bucket SET consecutive_5xx = ?, circuit_until = ? WHERE host = ?",
                (count, circuit_until, self.host),
            )
            connection.commit()
        return count >= CIRCUIT_FAILURE_THRESHOLD

    def record_non_server_error(self) -> None:
        now = self.monotonic()
        with self._connect() as connection:
            self._create_schema(connection)
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT OR IGNORE INTO host_bucket "
                "(host, next_allowed, consecutive_5xx, circuit_until) VALUES (?, ?, 0, 0)",
                (self.host, now),
            )
            connection.execute(
                "UPDATE host_bucket SET consecutive_5xx = 0 WHERE host = ? AND circuit_until <= ?",
                (self.host, now),
            )
            connection.commit()

    def release_lease(self, lease_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM host_lease WHERE lease_id = ?", (lease_id,))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=5.0, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS host_bucket ("
            "host TEXT PRIMARY KEY, next_allowed REAL NOT NULL, "
            "consecutive_5xx INTEGER NOT NULL, circuit_until REAL NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS host_lease ("
            "lease_id TEXT PRIMARY KEY, host TEXT NOT NULL, expires_at REAL NOT NULL)"
        )
        connection.execute("CREATE INDEX IF NOT EXISTS host_lease_host ON host_lease(host)")

    @staticmethod
    def _unreachable(message: str, details: dict[str, Any] | None = None) -> LabQuorumError:
        return LabQuorumError(ErrorCode.UNREACHABLE, message, details)


class ScholarlyHTTP:
    """Issue safe GET requests with caching, limits, retries, and a circuit breaker."""

    def __init__(  # noqa: PLR0913 - HTTP policy is injected for fake clocks and transports
        self,
        *,
        host: str,
        cache: CacheStore,
        rate_per_second: float,
        max_in_flight: int = 3,
        transport: httpx.BaseTransport | None = None,
        clock: Callable[[], datetime] = _utc_now,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[], float] | None = None,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
        max_attempts: int = MAX_ATTEMPTS,
    ) -> None:
        self.host = host
        self.cache = cache
        self.clock = clock
        self.sleep = sleep
        self.jitter = jitter or (lambda: random.random() * 0.25)
        self.timeout = httpx.Timeout(timeout)
        self.max_attempts = max_attempts
        self.limiter = SharedHostLimiter(
            cache.cache_dir / "host-limits.sqlite3",
            host=host,
            rate_per_second=rate_per_second,
            max_in_flight=max_in_flight,
            monotonic=monotonic,
            sleep=sleep,
            lease_seconds=timeout + 5.0,
        )
        self.client = httpx.Client(
            timeout=self.timeout,
            transport=transport,
            headers={"User-Agent": "LabQuorum/0.1 scholarly-metadata-client"},
        )

    # The retry state machine stays in one place so every adapter shares these policies.
    def get_json(  # noqa: PLR0912, PLR0915
        self,
        url: str,
        *,
        params: Mapping[str, str | int] | None = None,
        cache_categories: Sequence[str] = (),
        budget: RequestBudget | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResult:
        request_budget = budget or RequestBudget()
        request_key = self._request_key(url, params)
        now = _as_utc(self.clock())
        cached = self.cache.load(request_key, cache_categories, now=now)
        if cached is not None:
            return HTTPResult(
                payload=cached.payload,
                status_code=cached.status_code,
                checked_at=now,
                retrieved_at=cached.retrieved_at,
                from_cache=True,
                age_seconds=cached.age_seconds,
            )

        request_headers = dict(headers or {})
        last_error = "The scholarly API request failed."
        for attempt in range(1, self.max_attempts + 1):
            if self.limiter.circuit_is_open():
                raise LabQuorumError(
                    ErrorCode.UNREACHABLE,
                    f"The {self.host} circuit is open.",
                    {"host": self.host, "attempts": attempt - 1},
                )
            lease = self.limiter.acquire()
            try:
                request_budget.consume()
                response = self.client.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout,
                )
            except httpx.RequestError as exc:
                last_error = f"The {self.host} request failed: {type(exc).__name__}."
                self.limiter.record_non_server_error()
                if attempt < self.max_attempts:
                    self.sleep(self._backoff(attempt))
                    continue
                raise LabQuorumError(
                    ErrorCode.UNREACHABLE,
                    last_error,
                    {"host": self.host, "attempts": attempt},
                ) from exc
            finally:
                lease.release()

            if response.status_code >= 500:
                last_error = f"The {self.host} service returned HTTP {response.status_code}."
                if self.limiter.record_server_error():
                    raise LabQuorumError(
                        ErrorCode.UNREACHABLE,
                        f"The {self.host} circuit opened after consecutive server errors.",
                        {"host": self.host, "status_code": response.status_code},
                    )
                if attempt < self.max_attempts:
                    self.sleep(self._backoff(attempt))
                    continue
                raise LabQuorumError(
                    ErrorCode.UNREACHABLE,
                    last_error,
                    {"host": self.host, "attempts": attempt},
                )

            self.limiter.record_non_server_error()
            if response.status_code in {429, 408}:
                last_error = f"The {self.host} service returned HTTP {response.status_code}."
                if attempt < self.max_attempts:
                    retry_after = _parse_retry_after(response.headers.get("Retry-After"), now)
                    self.sleep(max(self._backoff(attempt), retry_after or 0.0))
                    continue
                raise LabQuorumError(
                    ErrorCode.UNREACHABLE,
                    last_error,
                    {"host": self.host, "attempts": attempt},
                )

            try:
                decoded = response.json()
            except ValueError as exc:
                if response.status_code == 404:
                    decoded = {}
                else:
                    raise LabQuorumError(
                        ErrorCode.UNREACHABLE,
                        f"The {self.host} response was not valid JSON.",
                        {"host": self.host, "status_code": response.status_code},
                    ) from exc
            payload = (
                cast(dict[str, Any], decoded) if isinstance(decoded, dict) else {"_value": decoded}
            )
            checked_at = _as_utc(self.clock())
            retrieved_at = checked_at
            if response.status_code < 400 or response.status_code == 404:
                self.cache.save(
                    request_key,
                    cache_categories,
                    payload,
                    response.status_code,
                    retrieved_at=retrieved_at,
                )
            return HTTPResult(
                payload=payload,
                status_code=response.status_code,
                checked_at=checked_at,
                retrieved_at=retrieved_at,
                from_cache=False,
                age_seconds=0.0,
            )

        raise LabQuorumError(ErrorCode.UNREACHABLE, last_error, {"host": self.host})

    def close(self) -> None:
        self.client.close()

    def _backoff(self, attempt: int) -> float:
        base = 0.5 * (2 ** (attempt - 1))
        return min(base + max(0.0, self.jitter()), 10.0)

    @staticmethod
    def _request_key(url: str, params: Mapping[str, str | int] | None) -> str:
        if not params:
            return url
        query = urlencode(sorted((str(key), str(value)) for key, value in params.items()))
        return f"{url}?{query}"


def _parse_retry_after(value: str | None, now: datetime) -> float | None:
    if value is None:
        return None
    try:
        return max(0.0, float(value.strip()))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return max(0.0, (parsed.astimezone(UTC) - _as_utc(now)).total_seconds())


class CrossrefClient:
    """Crossref REST client that identifies polite-pool requests with mailto."""

    def __init__(  # noqa: PLR0913 - transport and clocks are injectable for offline tests
        self,
        *,
        cache_dir: Path | None = None,
        cache: CacheStore | None = None,
        contact_email: str | None = None,
        transport: httpx.BaseTransport | None = None,
        clock: Callable[[], datetime] = _utc_now,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[], float] | None = None,
    ) -> None:
        self.contact_email = (contact_email or os.environ.get("CONTACT_EMAIL", "")).strip()
        self.http = ScholarlyHTTP(
            host="api.crossref.org",
            cache=cache or CacheStore(cache_dir, clock=clock),
            rate_per_second=8.0,
            max_in_flight=3,
            transport=transport,
            clock=clock,
            monotonic=monotonic,
            sleep=sleep,
            jitter=jitter,
        )

    def get_work(self, doi: str, budget: RequestBudget | None = None) -> HTTPResult:
        if (
            not self.contact_email
            or "@" not in self.contact_email
            or any(character in self.contact_email for character in "\r\n")
        ):
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                "Set CONTACT_EMAIL to identify Crossref polite-pool requests.",
            )
        encoded_doi = doi.strip()
        result = self.http.get_json(
            f"{CROSSREF_BASE_URL}/works/{encoded_doi}",
            params={"mailto": self.contact_email},
            cache_categories=("doi_metadata", "retraction_status"),
            budget=budget,
        )
        if result.status_code == 404:
            return replace(result, payload={})
        if result.status_code >= 400:
            raise LabQuorumError(
                ErrorCode.UNREACHABLE,
                f"Crossref returned HTTP {result.status_code} for a DOI lookup.",
                {"status_code": result.status_code},
            )
        message = result.payload.get("message", result.payload)
        if not isinstance(message, dict):
            raise LabQuorumError(ErrorCode.UNREACHABLE, "Crossref returned an invalid work record.")
        return replace(result, payload=message)


class OpenAlexClient:
    """OpenAlex client with optional bearer-key authentication and bounded search."""

    def __init__(  # noqa: PLR0913 - HTTP dependencies are injected for offline tests
        self,
        *,
        cache_dir: Path | None = None,
        cache: CacheStore | None = None,
        api_key: str | None = None,
        transport: httpx.BaseTransport | None = None,
        clock: Callable[[], datetime] = _utc_now,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[], float] | None = None,
    ) -> None:
        self.api_key = (api_key or os.environ.get("OPENALEX_API_KEY", "")).strip()
        self.http = ScholarlyHTTP(
            host="api.openalex.org",
            cache=cache or CacheStore(cache_dir, clock=clock),
            rate_per_second=8.0,
            max_in_flight=3,
            transport=transport,
            clock=clock,
            monotonic=monotonic,
            sleep=sleep,
            jitter=jitter,
        )

    def get_work(self, doi: str, budget: RequestBudget | None = None) -> HTTPResult:
        headers = self._auth_headers()
        result = self.http.get_json(
            f"{OPENALEX_BASE_URL}/works/doi:{doi.strip()}",
            params={"select": "title,doi,publication_year,authorships,is_retracted,locations"},
            cache_categories=("doi_metadata", "retraction_status"),
            budget=budget,
            headers=headers,
        )
        self._raise_for_unexpected_error(result.status_code)
        return result

    def search_works(
        self,
        query: str,
        budget: RequestBudget | None = None,
        *,
        max_results: int = 8,
    ) -> HTTPResult:
        if len(query) > 300:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                "Literature queries must be 300 characters or fewer.",
                {"length": len(query), "limit": 300},
            )
        if not query.strip():
            return HTTPResult(
                payload={"results": []},
                status_code=200,
                checked_at=_as_utc(self.http.clock()),
                retrieved_at=_as_utc(self.http.clock()),
                from_cache=False,
                age_seconds=0.0,
            )
        if not 1 <= max_results <= 8:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                "Literature searches return between 1 and 8 results.",
                {"max_results": max_results, "limit": 8},
            )
        result = self.http.get_json(
            f"{OPENALEX_BASE_URL}/works",
            params={
                "search": query.strip(),
                "per_page": max_results,
                "select": "title,doi,publication_year,authorships,primary_location,is_retracted,locations",
            },
            cache_categories=("search",),
            budget=budget,
            headers=self._auth_headers(),
        )
        self._raise_for_unexpected_error(result.status_code)
        return result

    def _auth_headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    @staticmethod
    def _raise_for_unexpected_error(status_code: int) -> None:
        if status_code >= 400 and status_code != 404:
            raise LabQuorumError(
                ErrorCode.UNREACHABLE,
                f"OpenAlex returned HTTP {status_code}.",
                {"status_code": status_code},
            )
