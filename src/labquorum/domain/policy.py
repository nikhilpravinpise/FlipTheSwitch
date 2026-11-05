"""Structured booking policy check results."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from labquorum.domain.errors import ErrorCode


@dataclass(frozen=True)
class PolicyCheck:
    name: str
    passed: bool
    code: ErrorCode | None
    reason: str


def policy_check(checks: Sequence[PolicyCheck]) -> list[dict[str, object]]:
    raise NotImplementedError
