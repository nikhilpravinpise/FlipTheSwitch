"""Safe JSON evidence and binding version tuple helpers."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

_SECRET_KEY = re.compile(r"password|token|secret|authorization|cookie|credential|api[_-]?key", re.I)
_SECRET_VALUE = re.compile(
    r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+|"
    r"((?:password|token|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+"
)
_SCENARIO_SLUG = re.compile(r"[^a-zA-Z0-9_-]+")


def write_evidence(
    evidence_dir: Path,
    scenario: str,
    evidence: dict[str, Any],
) -> Path:
    """Write one timestamped UTF-8 JSON file with sensitive fields redacted."""
    safe_scenario = _SCENARIO_SLUG.sub("-", scenario).strip("-_").lower()
    if not safe_scenario:
        raise ValueError("Scenario name must contain letters or numbers.")
    generated_at = datetime.now(UTC)
    payload = cast(dict[str, Any], _redact(evidence))
    payload.setdefault("scenario", safe_scenario)
    payload.setdefault("generated_at_utc", generated_at.isoformat(timespec="milliseconds"))
    stamp = generated_at.strftime("%Y%m%dT%H%M%S%fZ")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    output_path = evidence_dir / f"{safe_scenario}-{stamp}.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a template or other evidence input."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _redact(value: Any, key: str | None = None) -> Any:
    if key is not None and _SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        return {
            str(child_key): _redact(child, str(child_key)) for child_key, child in mapping.items()
        }
    if isinstance(value, (list, tuple)):
        sequence = cast(list[Any] | tuple[Any, ...], value)
        return [_redact(child) for child in sequence]
    if isinstance(value, str):
        return _SECRET_VALUE.sub(
            lambda match: f"{match.group(1) or match.group(2)}[REDACTED]", value
        )
    return value
