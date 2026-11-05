"""Profile-scoped LabQuorum MCP tool names and agent mapping."""

from __future__ import annotations

from enum import StrEnum


class Profile(StrEnum):
    PROPOSER = "proposer"
    APPROVER = "approver"
    UNAVAILABLE = "unavailable"


PROFILE_TOOLS: dict[Profile, tuple[str, ...]] = {
    Profile.PROPOSER: (
        "list_instruments",
        "check_availability",
        "propose_booking",
        "cancel_my_proposal",
        "lab_state",
    ),
    Profile.APPROVER: (
        "get_request",
        "policy_check",
        "lab_state",
        "decline_request",
        "commit_booking",
    ),
    Profile.UNAVAILABLE: ("capability_status",),
}

TOOL_DESCRIPTIONS: dict[str, str] = {
    "list_instruments": (
        "List bookable laboratory instruments and their location, status, time zone, "
        "training requirement, booking limit, and cleaning gap."
    ),
    "check_availability": (
        "Check whether a proposed interval can be booked for the seeded requester Maya. "
        "Supply both datetimes as ISO 8601 strings with an explicit UTC offset. A conflict "
        "names the committed booking owner and gives the nearest free interval of the same length."
    ),
    "propose_booking": (
        "Create a pending booking proposal for the seeded requester Maya. Supply an instrument "
        "ID, project, and ISO 8601 start and end datetimes with explicit offsets. The result "
        "includes the request ID, revision, content hash, complete canonical decision, and a "
        "weekday/date/time/time-zone summary. Conflicts include the owner and nearest same-length slot."
    ),
    "cancel_my_proposal": (
        "Cancel one of Maya's committed bookings by booking ID. The ledger checks ownership "
        "before applying the cancellation."
    ),
    "lab_state": (
        "Read a compact snapshot of instrument status and booking state from the LabQuorum ledger."
    ),
    "get_request": (
        "Read an approval request by ID. Returns its current status, revision, content hash, and "
        "complete canonical decision for an exact commit echo."
    ),
    "policy_check": (
        "Recheck a pending request against current booking policy and report each check, its "
        "result, and any stable error code. The commit transaction checks policy again."
    ),
    "decline_request": (
        "Decline a pending request at the supplied revision and record a human-readable reason."
    ),
    "commit_booking": (
        "Commit the exact pending booking decision after human approval. Echo request_id, revision, "
        "content_hash, and the complete decision object returned by get_request. The decision "
        "must match current canonical bytes; a repeated identical call is idempotent."
    ),
    "capability_status": (
        "List booking and laboratory capabilities that are not enabled in this profile and explain why."
    ),
}

_AGENT_PROFILES: dict[str, Profile] = {
    "labops": Profile.PROPOSER,
    "pi-desk": Profile.APPROVER,
    "scout": Profile.UNAVAILABLE,
    "analyst": Profile.UNAVAILABLE,
}


def tool_names_for_profile(profile: Profile | str) -> tuple[str, ...]:
    """Return the MCP tools available to a profile."""
    try:
        normalized = profile if isinstance(profile, Profile) else Profile(profile)
    except ValueError as exc:
        raise ValueError(f"Unknown LabQuorum MCP profile: {profile!s}") from exc
    return PROFILE_TOOLS[normalized]


def profile_for_agent(agent_name: str) -> Profile | None:
    """Return the booking-phase profile assigned to an agent folder."""
    return _AGENT_PROFILES.get(agent_name.casefold())
