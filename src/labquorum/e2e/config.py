"""Local configuration for persona logins and the target E2E fixture."""

from __future__ import annotations

import json
import ntpath
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


def _ledger_path(raw_path: str) -> Path:
    expanded = ntpath.expandvars(raw_path)
    if os.name != "nt" and expanded != os.path.expandvars(raw_path):
        expanded = expanded.replace("\\", "/")
    return Path(expanded).expanduser()


def load_config(path: Path) -> HarnessConfig:  # noqa: PLR0912
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
    mattermost_url = root.get("mattermost_url", root.get("server"))
    channel_id: Any = root.get("channel_id")
    if channel_id is None:
        private_room: Any = root.get("private_room")
        if isinstance(private_room, dict):
            private_room_data = cast(dict[str, Any], private_room)
            channel_id = private_room_data.get("id")
        else:
            channel_id = private_room
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
    for raw_name, item in persona_data.items():
        if not raw_name.strip():
            raise HarnessConfigError("Persona names must be non-empty strings.")
        if not isinstance(item, dict):
            raise HarnessConfigError(f"Persona {raw_name} must be an object.")
        details = cast(dict[str, Any], item)
        login_id = details.get("login_id", details.get("username"))
        password = details.get("password")
        if not isinstance(login_id, str) or not login_id:
            raise HarnessConfigError(f"Persona {raw_name} requires login_id or username.")
        if not isinstance(password, str) or not password:
            raise HarnessConfigError(f"Persona {raw_name} requires a password.")
        personas[raw_name] = PersonaCredentials(login_id=login_id, password=password)
    for name in ("maya", "prof-rao"):
        if name not in personas:
            raise HarnessConfigError(f"Persona configuration is missing {name}.")
    ledger_path = (
        _ledger_path(raw_ledger_path)
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
