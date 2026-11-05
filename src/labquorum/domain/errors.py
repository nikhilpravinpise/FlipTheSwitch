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
    UNCOMMITTABLE_REQUEST = "UNCOMMITTABLE_REQUEST"
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
    meanings = {
        ErrorCode.CONFLICT: "The requested interval conflicts with a committed booking.",
        ErrorCode.INSTRUMENT_DOWN: "The instrument is unavailable for the requested interval.",
        ErrorCode.TRAINING_REQUIRED: "Required training is missing or expired at booking start.",
        ErrorCode.TOO_LONG: "The requested booking exceeds the instrument block limit.",
        ErrorCode.OUTSIDE_WINDOW: "The requested booking is beyond the booking window.",
        ErrorCode.OUTSIDE_HOURS: "The requested interval is outside instrument opening hours.",
        ErrorCode.IN_PAST: "The requested interval starts before the current time.",
        ErrorCode.NEEDS_ISO_DATETIME: "The input must be an explicit ISO 8601 datetime.",
        ErrorCode.AMBIGUOUS_LOCAL_TIME: "The local time occurs twice; provide a UTC offset.",
        ErrorCode.NONEXISTENT_LOCAL_TIME: "The local time does not exist because of a clock change.",
        ErrorCode.EXPIRED: "The approval request has expired.",
        ErrorCode.STALE_REQUEST: "The request revision or content hash is stale.",
        ErrorCode.DECISION_MISMATCH: "The submitted decision differs from the canonical decision.",
        ErrorCode.UNCOMMITTABLE_REQUEST: "The pending request predates or exceeds the current commit-card contract.",
        ErrorCode.ALREADY_DECIDED: "The request already has a terminal decision.",
        ErrorCode.DECLINED: "The request was declined and cannot be committed.",
        ErrorCode.NOT_FOUND: "The requested ledger record does not exist.",
        ErrorCode.RATE_LIMITED: "The profile exceeded its tool call rate limit.",
        ErrorCode.INVALID_ARGUMENT: "An argument is invalid or outside the supported format.",
        ErrorCode.SCHEMA_VERSION_MISMATCH: "The ledger schema version is not supported.",
        ErrorCode.UNIT_MISMATCH: "Quantities use incompatible units.",
        ErrorCode.UNKNOWN_HAZARD: "The hazard is unknown and must be reviewed.",
        ErrorCode.ETHICS_REVIEW_REQUIRED: "The request requires an ethics review.",
        ErrorCode.TAMPERED: "Stored content failed its integrity check.",
        ErrorCode.BUDGET_EXCEEDED: "The request exceeded its configured call budget.",
        ErrorCode.UNRESOLVED: "The requested source could not be resolved.",
        ErrorCode.MISMATCH: "The source metadata does not match the supplied metadata.",
        ErrorCode.RETRACTED: "The source has a recorded retraction.",
        ErrorCode.UNREACHABLE: "The remote source could not be reached.",
    }
    rows = ["| Code | Meaning |", "| --- | --- |"]
    rows.extend(f"| {code.value} | {meanings[code]} |" for code in ErrorCode)
    return "\n".join(rows)
