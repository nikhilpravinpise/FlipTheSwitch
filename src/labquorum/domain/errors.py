"""Closed domain error vocabulary for LabQuorum."""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    CONFLICT = "CONFLICT"
    INSTRUMENT_DOWN = "INSTRUMENT_DOWN"
    TRAINING_REQUIRED = "TRAINING_REQUIRED"
    TOO_LONG = "TOO_LONG"
    OUTSIDE_WINDOW = "OUTSIDE_WINDOW"
    OUTSIDE_HOURS = "OUTSIDE_HOURS"
    IN_PAST = "IN_PAST"
    NEEDS_ISO_DATETIME = "NEEDS_ISO_DATETIME"
    AMBIGUOUS_LOCAL_TIME = "AMBIGUOUS_LOCAL_TIME"
    NONEXISTENT_LOCAL_TIME = "NONEXISTENT_LOCAL_TIME"
    EXPIRED = "EXPIRED"
    STALE_REQUEST = "STALE_REQUEST"
    DECISION_MISMATCH = "DECISION_MISMATCH"
    ALREADY_DECIDED = "ALREADY_DECIDED"
    DECLINED = "DECLINED"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    SCHEMA_VERSION_MISMATCH = "SCHEMA_VERSION_MISMATCH"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    UNKNOWN_HAZARD = "UNKNOWN_HAZARD"
    ETHICS_REVIEW_REQUIRED = "ETHICS_REVIEW_REQUIRED"
    TAMPERED = "TAMPERED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    UNRESOLVED = "UNRESOLVED"
    MISMATCH = "MISMATCH"
    RETRACTED = "RETRACTED"
    UNREACHABLE = "UNREACHABLE"


class LabQuorumError(Exception):
    """A domain failure with a stable code and structured details."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def error_codes_markdown() -> str:
    """Render all supported error codes as a Markdown table."""
    raise NotImplementedError
