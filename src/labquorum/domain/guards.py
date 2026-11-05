"""Per-profile tool call rate guards."""

from __future__ import annotations

from datetime import timedelta

from labquorum.domain.timeutil import Clock


class RateGuard:
    def __init__(
        self,
        *,
        clock: Clock,
        limit: int = 30,
        period: timedelta = timedelta(minutes=1),
    ) -> None:
        raise NotImplementedError

    def check(self, profile: str) -> None:
        raise NotImplementedError
