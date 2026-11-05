"""Local configuration for persona logins and the target E2E fixture."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from labquorum.store.db import default_database_path


class HarnessConfigError(ValueError):
    """Raised when the local persona file is missing required fields."""


@dataclass(frozen=True)
class PersonaCredentials:
    login_id: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class HarnessConfig:
    mattermost_url: str
    channel_id: str
    ledger_path: Path
    personas: dict[str, PersonaCredentials]


def default_personas_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    root = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return root / "LabQuorum" / "personas.json"


def load_config(path: Path) -> HarnessConfig:
    """Read persona passwords from LocalAppData without echoing their values."""
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise HarnessConfigError(f"Could not read persona configuration at {path}.") from exc
    except json.JSONDecodeError as exc:
        raise HarnessConfigError("Persona configuration is not valid JSON.") from exc
    if not isinstance(data, dict):
        raise HarnessConfigError("Persona configuration must be a JSON object.")
    root = cast(dict[str, Any], data)
    mattermost_url = root.get("mattermost_url")
    channel_id = root.get("channel_id")
    raw_ledger_path = root.get("ledger_path")
    raw_personas = root.get("personas")
    if not isinstance(mattermost_url, str) or not mattermost_url.startswith(
        ("http://", "https://")
    ):
        raise HarnessConfigError("Persona configuration requires a Mattermost http(s) URL.")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise HarnessConfigError("Persona configuration requires the target channel_id.")
    if not isinstance(raw_personas, dict):
        raise HarnessConfigError("Persona configuration requires a personas object.")
    persona_data = cast(dict[str, Any], raw_personas)
    personas: dict[str, PersonaCredentials] = {}
    for name in ("maya", "prof-rao"):
        item = persona_data.get(name)
        if not isinstance(item, dict):
            raise HarnessConfigError(f"Persona configuration is missing {name}.")
        details = cast(dict[str, Any], item)
        login_id = details.get("login_id", details.get("username"))
        password = details.get("password")
        if not isinstance(login_id, str) or not login_id:
            raise HarnessConfigError(f"Persona {name} requires login_id or username.")
        if not isinstance(password, str) or not password:
            raise HarnessConfigError(f"Persona {name} requires a password.")
        personas[name] = PersonaCredentials(login_id=login_id, password=password)
    ledger_path = (
        Path(os.path.expandvars(raw_ledger_path)).expanduser()
        if isinstance(raw_ledger_path, str) and raw_ledger_path
        else default_database_path()
    )
    return HarnessConfig(
        mattermost_url=mattermost_url.rstrip("/"),
        channel_id=channel_id,
        ledger_path=ledger_path,
        personas=personas,
    )


def override_config(
    config: HarnessConfig,
    *,
    channel_id: str | None = None,
    ledger_path: Path | None = None,
) -> HarnessConfig:
    """Apply non-secret CLI overrides without modifying the persona file."""
    return HarnessConfig(
        mattermost_url=config.mattermost_url,
        channel_id=channel_id or config.channel_id,
        ledger_path=ledger_path or config.ledger_path,
        personas=dict(config.personas),
    )
