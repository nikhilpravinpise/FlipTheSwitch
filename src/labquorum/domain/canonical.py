"""Canonical JSON encoding and hashes for decision and audit payloads."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from enum import Enum
from typing import Any, cast

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.timeutil import utc_timestamp


def _normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        return utc_timestamp(value)
    if isinstance(value, Enum):
        return _normalize(value.value)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Canonical JSON supports integer quantities only.",
        )
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, Any], value)
        normalized: dict[str, Any] = {}
        for key, item in mapping.items():
            if not isinstance(key, str):
                raise LabQuorumError(
                    ErrorCode.INVALID_ARGUMENT,
                    "Canonical JSON object keys must be strings.",
                )
            normalized[key] = _normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        sequence = cast(Sequence[Any], value)
        return [_normalize(item) for item in sequence]
    raise LabQuorumError(
        ErrorCode.INVALID_ARGUMENT,
        f"Unsupported canonical JSON value: {type(value).__name__}.",
    )


def canonical_json(value: Any) -> str:
    """Return sorted, compact UTF-8 JSON with aware UTC timestamps."""
    normalized = _normalize(value)
    try:
        return json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT, "Value cannot be represented as canonical JSON."
        ) from exc


def content_hash(value: Any) -> str:
    """Hash a canonical JSON value using SHA-256."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
