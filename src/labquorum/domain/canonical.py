"""Canonical JSON encoding and hashes for decision and audit payloads."""

from __future__ import annotations

from typing import Any


def canonical_json(value: Any) -> str:
    raise NotImplementedError


def content_hash(value: Any) -> str:
    raise NotImplementedError
