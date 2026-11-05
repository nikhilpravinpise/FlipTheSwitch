"""Per-profile tool call rate guards."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import Clock


class RateGuard:
    def __init__(
        self,
        *,
        clock: Clock,
        limit: int = 30,
        period: timedelta = timedelta(minutes=1),
    ) -> None:
        if limit <= 0 or period <= timedelta(0):
            raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Rate guard limits must be positive.")
        self._clock = clock
        self._limit = limit
        self._period = period
        self._calls: dict[str, deque[datetime]] = defaultdict(deque)
        self._last_seen: datetime | None = None

    def check(self, profile: str) -> None:
        if not profile.strip():
            raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Profile name cannot be empty.")
        now = self._clock.now()
        if now.tzinfo is None or now.utcoffset() is None:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT, "Rate guard clock must return aware datetimes."
            )
        now = now.astimezone(UTC)
        if self._last_seen is not None and now < self._last_seen:
            raise LabQuorumError(
                ErrorCode.RATE_LIMITED, "Clock moved backwards; rate guard failed closed."
            )
        self._last_seen = now
        calls = self._calls[profile]
        cutoff = now - self._period
        while calls and calls[0] <= cutoff:
            calls.popleft()
        if len(calls) >= self._limit:
            raise LabQuorumError(
                ErrorCode.RATE_LIMITED,
                f"Profile {profile} exceeded {self._limit} calls in the configured period.",
                {"profile": profile, "limit": self._limit},
            )
        calls.append(now)
