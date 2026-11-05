"""Profile-scoped LabQuorum MCP tool names."""

from __future__ import annotations

from enum import StrEnum


class Profile(StrEnum):
    PROPOSER = "proposer"
    APPROVER = "approver"
    UNAVAILABLE = "unavailable"


PROFILE_TOOLS: dict[Profile, tuple[str, ...]] = {}


def tool_names_for_profile(profile: Profile | str) -> tuple[str, ...]:
    """Return the MCP tools available to a profile."""
    raise NotImplementedError("P2 profile tool registration is not implemented yet")


def profile_for_agent(agent_name: str) -> Profile | None:
    """Return the booking-phase profile assigned to an agent folder."""
    raise NotImplementedError("P2 agent profile mapping is not implemented yet")
