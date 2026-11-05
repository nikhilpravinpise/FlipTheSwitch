"""Booking tools exposed by the P2 profile-scoped MCP server."""

from __future__ import annotations

import json
import sqlite3
import time as monotonic_time
from collections.abc import Callable, Mapping
from contextlib import closing
from datetime import datetime, time
from functools import wraps
from inspect import signature
from pathlib import Path
from typing import Annotated, Any, Literal, get_type_hints

import structlog
from pydantic import BaseModel, ConfigDict, Field

from labquorum.domain.approvals import serialize_decision
from labquorum.domain.booking import (
    Booking,
    InstrumentPolicy,
    Interval,
    Training,
    check_booking,
    nearest_free_slot,
)
from labquorum.domain.canonical import canonical_json
from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.domain.guards import RateGuard
from labquorum.domain.timeutil import (
    Clock,
    SystemClock,
    format_interval,
    parse_iso_datetime,
    utc_timestamp,
)
from labquorum.mcp.profiles import Profile, tool_names_for_profile
from labquorum.store import repos
from labquorum.store.db import default_database_path, open_database

MAX_RESULT_BYTES = 8_192
DEMO_REQUESTER_ID = "maya"
logger = structlog.get_logger("labquorum.mcp")


class DecisionIntervalInput(BaseModel):
    """The complete UTC interval in a canonical booking decision."""

    model_config = ConfigDict(extra="forbid", strict=True)

    start_utc: str = Field(
        max_length=32,
        description="Canonical ISO 8601 start instant, normally ending in Z.",
    )
    end_utc: str = Field(
        max_length=32,
        description="Canonical ISO 8601 end instant, normally ending in Z.",
    )


class BookingDecisionInput(BaseModel):
    """All canonical fields required to approve a booking commit."""

    model_config = ConfigDict(extra="forbid", strict=True)

    action: Literal["commit_booking"] = Field(description="Must be commit_booking.")
    requester: str = Field(
        min_length=1,
        max_length=64,
        description="Canonical requester ID from get_request.",
    )
    resource: str = Field(
        min_length=1,
        max_length=64,
        description="Canonical instrument ID from get_request.",
    )
    interval: DecisionIntervalInput = Field(description="Complete canonical UTC booking interval.")
    project: str = Field(max_length=80, description="Canonical project ID from get_request.")
    request_id: str = Field(
        max_length=32,
        description="Approval request ID returned by get_request.",
    )
    revision: int = Field(ge=1, description="Current positive request revision.")


def compact_result(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact JSON-ready result under the MCP output cap."""
    result = dict(value)
    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) <= MAX_RESULT_BYTES:
        return result
    return {
        "error": ErrorCode.INVALID_ARGUMENT.value,
        "message": "Tool result exceeds the compact output limit.",
        "details": {"limit_bytes": MAX_RESULT_BYTES},
    }


def _error_result(error: LabQuorumError) -> dict[str, Any]:
    return {"error": error.code.value, "message": error.message, "details": error.details}


def _safe_tool(function: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    @wraps(function)
    def wrapped(self: LabTools, *args: Any, **kwargs: Any) -> dict[str, Any]:
        started = monotonic_time.perf_counter()
        try:
            self.rate_guard.check(self.profile.value)
            result = function(self, *args, **kwargs)
            compact = compact_result(result)
            logger.info(
                "mcp_tool_call",
                profile=self.profile.value,
                tool=function.__name__,
                duration_ms=round((monotonic_time.perf_counter() - started) * 1_000, 2),
                outcome="error" if "error" in compact else "success",
                error_code=compact.get("error"),
            )
            return compact
        except LabQuorumError as error:
            result = compact_result(_error_result(error))
            logger.info(
                "mcp_tool_call",
                profile=self.profile.value,
                tool=function.__name__,
                duration_ms=round((monotonic_time.perf_counter() - started) * 1_000, 2),
                outcome="error",
                error_code=error.code.value,
            )
            return result
        except (OSError, sqlite3.Error):
            logger.exception(
                "mcp_tool_call_failed",
                profile=self.profile.value,
                tool=function.__name__,
            )
            return compact_result(
                {
                    "error": ErrorCode.INVALID_ARGUMENT.value,
                    "message": "Ledger operation failed. Check the ledger path and try again.",
                }
            )
        except Exception:
            logger.exception(
                "mcp_tool_call_failed",
                profile=self.profile.value,
                tool=function.__name__,
            )
            return compact_result(
                {
                    "error": ErrorCode.INVALID_ARGUMENT.value,
                    "message": "Tool operation failed. Check the arguments and ledger, then try again.",
                }
            )

    return wrapped


class _BookingContext:
    def __init__(
        self,
        policy: InstrumentPolicy,
        training: Training | None,
        bookings: list[Booking],
        owners: dict[str, dict[str, str]],
    ) -> None:
        self.policy = policy
        self.training = training
        self.bookings = bookings
        self.owners = owners


def _load_booking_context(
    connection: sqlite3.Connection,
    *,
    instrument_id: str,
    person_id: str,
) -> _BookingContext:
    instrument = connection.execute(
        "SELECT * FROM instrument WHERE id = ?", (instrument_id,)
    ).fetchone()
    if instrument is None:
        raise LabQuorumError(ErrorCode.NOT_FOUND, f"Instrument {instrument_id} was not found.")

    opening_raw = json.loads(str(instrument["opening_hours_json"]))
    opening_hours = {
        int(day): (time.fromisoformat(hours[0]), time.fromisoformat(hours[1]))
        for day, hours in opening_raw.items()
    }
    down_until = (
        parse_iso_datetime(str(instrument["down_until_utc"]))
        if instrument["down_until_utc"] is not None
        else None
    )
    policy = InstrumentPolicy(
        instrument_id=str(instrument["id"]),
        timezone=str(instrument["timezone"]),
        opening_hours=opening_hours,
        max_block_minutes=int(instrument["max_block_minutes"]),
        min_gap_minutes=int(instrument["min_gap_minutes"]),
        booking_window_days=int(instrument["booking_window_days"]),
        status=str(instrument["status"]),
        down_until=down_until,
        requires_training=bool(instrument["requires_training"]),
    )

    training_row = connection.execute(
        "SELECT granted_at_utc, expires_at_utc FROM training "
        "WHERE person_id = ? AND instrument_id = ?",
        (person_id, instrument_id),
    ).fetchone()
    training = (
        Training(
            granted_at=parse_iso_datetime(str(training_row["granted_at_utc"])),
            expires_at=parse_iso_datetime(str(training_row["expires_at_utc"])),
        )
        if training_row is not None
        else None
    )

    booking_rows = connection.execute(
        "SELECT b.id, b.start_utc, b.end_utc, b.status, b.person_id, p.display_name "
        "FROM booking AS b JOIN person AS p ON p.id = b.person_id "
        "WHERE b.instrument_id = ? AND b.status = 'committed' ORDER BY b.start_utc",
        (instrument_id,),
    ).fetchall()
    bookings: list[Booking] = []
    owners: dict[str, dict[str, str]] = {}
    for row in booking_rows:
        booking_id = str(row["id"])
        bookings.append(
            Booking(
                booking_id=booking_id,
                interval=Interval(
                    parse_iso_datetime(str(row["start_utc"])),
                    parse_iso_datetime(str(row["end_utc"])),
                ),
                status=str(row["status"]),
            )
        )
        owners[booking_id] = {
            "person_id": str(row["person_id"]),
            "display_name": str(row["display_name"]),
        }
    return _BookingContext(policy, training, bookings, owners)


def _conflict_details(
    error: LabQuorumError,
    *,
    context: _BookingContext,
    interval: Interval,
    now: datetime,
) -> dict[str, Any]:
    booking_id = str(error.details.get("booking_id", ""))
    nearest = nearest_free_slot(
        context.policy,
        interval.start,
        duration_minutes=interval.duration_minutes,
        now=now,
        existing_bookings=context.bookings,
    )
    nearest_result = None
    if nearest is not None:
        nearest_result = {
            "start_utc": utc_timestamp(nearest.start),
            "end_utc": utc_timestamp(nearest.end),
            "summary": format_interval(
                nearest.start,
                nearest.end,
                context.policy.timezone,
            ),
        }
    return {
        "conflicting_booking": {
            "booking_id": booking_id,
            "owner": context.owners.get(booking_id, {}).get("person_id", "unknown"),
            "owner_name": context.owners.get(booking_id, {}).get("display_name", "Unknown owner"),
        },
        "nearest_free_slot": nearest_result,
    }


class LabTools:
    """Profile-bound tool handlers that delegate booking rules to P1."""

    def __init__(
        self,
        profile: Profile,
        database_path: Path | None = None,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.profile = profile
        self.database_path = database_path or default_database_path()
        self.clock = clock or SystemClock()
        self.rate_guard = RateGuard(clock=self.clock, limit=30)
        self._methods: dict[str, Callable[..., dict[str, Any]]] = {
            "list_instruments": self.list_instruments,
            "check_availability": self.check_availability,
            "propose_booking": self.propose_booking,
            "cancel_my_proposal": self.cancel_my_proposal,
            "lab_state": self.lab_state,
            "get_request": self.get_request,
            "policy_check": self.policy_check,
            "decline_request": self.decline_request,
            "commit_booking": self.commit_booking,
            "capability_status": self.capability_status,
        }

    def tool_method(self, name: str) -> Callable[..., dict[str, Any]]:
        if name not in tool_names_for_profile(self.profile):
            raise LabQuorumError(
                ErrorCode.NOT_FOUND, f"Tool {name} is not enabled for this profile."
            )
        return self._methods[name]

    def invoke(self, name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        """Invoke an enabled tool by name for deterministic record/replay checks."""
        method = self.tool_method(name)
        supplied = dict(arguments)
        hints = get_type_hints(method)
        for parameter in signature(method).parameters.values():
            annotation = hints.get(parameter.name)
            if (
                parameter.name in supplied
                and isinstance(annotation, type)
                and issubclass(annotation, BaseModel)
            ):
                try:
                    supplied[parameter.name] = annotation.model_validate(supplied[parameter.name])
                except Exception as exc:
                    return compact_result(
                        {
                            "error": ErrorCode.INVALID_ARGUMENT.value,
                            "message": f"Invalid {parameter.name} object: {exc}",
                        }
                    )
        try:
            return method(**supplied)
        except TypeError as exc:
            return compact_result({"error": ErrorCode.INVALID_ARGUMENT.value, "message": str(exc)})

    @_safe_tool
    def list_instruments(self) -> dict[str, Any]:
        """List instruments with booking-relevant constraints."""
        with closing(open_database(self.database_path)) as connection:
            rows = connection.execute(
                "SELECT id, name, location, timezone, status, requires_training, "
                "max_block_minutes, min_gap_minutes, booking_window_days "
                "FROM instrument ORDER BY id"
            ).fetchall()
        return {
            "instruments": [
                {
                    "instrument_id": str(row["id"]),
                    "name": str(row["name"]),
                    "location": str(row["location"]),
                    "timezone": str(row["timezone"]),
                    "status": str(row["status"]),
                    "requires_training": bool(row["requires_training"]),
                    "max_block_minutes": int(row["max_block_minutes"]),
                    "min_gap_minutes": int(row["min_gap_minutes"]),
                    "booking_window_days": int(row["booking_window_days"]),
                }
                for row in rows
            ]
        }

    @_safe_tool
    def check_availability(
        self,
        instrument_id: Annotated[str, Field(description="Instrument ID from list_instruments.")],
        start: Annotated[str, Field(description="ISO 8601 start datetime including a UTC offset.")],
        end: Annotated[str, Field(description="ISO 8601 end datetime including a UTC offset.")],
    ) -> dict[str, Any]:
        """Check booking policy for Maya and return a same-length alternative on conflict."""
        start_value = parse_iso_datetime(start)
        end_value = parse_iso_datetime(end)
        interval = Interval(start_value, end_value)
        now = self.clock.now()
        with closing(open_database(self.database_path)) as connection:
            context = _load_booking_context(
                connection,
                instrument_id=instrument_id,
                person_id=DEMO_REQUESTER_ID,
            )
            try:
                check_booking(
                    context.policy,
                    interval,
                    now=now,
                    training=context.training,
                    existing_bookings=context.bookings,
                )
            except LabQuorumError as error:
                details = dict(error.details)
                if error.code is ErrorCode.CONFLICT:
                    details.update(
                        _conflict_details(error, context=context, interval=interval, now=now)
                    )
                return {
                    "available": False,
                    "error": error.code.value,
                    "message": error.message,
                    "details": details,
                }
        return {
            "available": True,
            "instrument_id": instrument_id,
            "summary": format_interval(start_value, end_value, context.policy.timezone),
        }

    @_safe_tool
    def propose_booking(
        self,
        instrument_id: Annotated[str, Field(description="Instrument ID from list_instruments.")],
        project_id: Annotated[
            str, Field(min_length=1, description="Project label for this booking.")
        ],
        start: Annotated[str, Field(description="ISO 8601 start datetime including a UTC offset.")],
        end: Annotated[str, Field(description="ISO 8601 end datetime including a UTC offset.")],
    ) -> dict[str, Any]:
        """Create a pending booking proposal and return its canonical decision for review."""
        start_value = parse_iso_datetime(start)
        end_value = parse_iso_datetime(end)
        interval = Interval(start_value, end_value)
        with closing(open_database(self.database_path)) as connection:
            now = self.clock.now()
            try:
                proposal = repos.propose_booking(
                    connection,
                    person_id=DEMO_REQUESTER_ID,
                    instrument_id=instrument_id,
                    project_id=project_id,
                    start=start_value,
                    end=end_value,
                    clock=self.clock,
                )
            except LabQuorumError as error:
                if error.code is not ErrorCode.CONFLICT:
                    raise
                context = _load_booking_context(
                    connection,
                    instrument_id=instrument_id,
                    person_id=DEMO_REQUESTER_ID,
                )
                raise LabQuorumError(
                    error.code,
                    error.message,
                    {
                        **error.details,
                        **_conflict_details(
                            error,
                            context=context,
                            interval=interval,
                            now=now,
                        ),
                    },
                ) from error
            context = _load_booking_context(
                connection,
                instrument_id=instrument_id,
                person_id=DEMO_REQUESTER_ID,
            )
        return {
            **proposal,
            "summary": format_interval(start_value, end_value, context.policy.timezone),
        }

    @_safe_tool
    def cancel_my_proposal(
        self,
        booking_id: Annotated[str, Field(description="Booking ID returned by propose_booking.")],
    ) -> dict[str, Any]:
        """Cancel a committed booking owned by Maya after checking its ledger owner."""
        with closing(open_database(self.database_path)) as connection:
            booking = connection.execute(
                "SELECT person_id FROM booking WHERE id = ?", (booking_id,)
            ).fetchone()
            if booking is None or str(booking["person_id"]) != DEMO_REQUESTER_ID:
                raise LabQuorumError(ErrorCode.NOT_FOUND, "Maya's booking was not found.")
            return repos.cancel_booking(
                connection,
                booking_id,
                actor="labops",
                clock=self.clock,
            )

    @_safe_tool
    def lab_state(self) -> dict[str, Any]:
        """Read a compact ledger snapshot without exposing raw database columns."""
        with closing(open_database(self.database_path)) as connection:
            state = repos.lab_state(connection, clock=self.clock)
        return {
            "instruments": [
                {
                    "instrument_id": str(item["id"]),
                    "name": str(item["name"]),
                    "location": str(item["location"]),
                    "status": str(item["status"]),
                    "timezone": str(item["timezone"]),
                }
                for item in state["instruments"]
            ],
            "bookings": [
                {
                    "booking_id": str(item["id"]),
                    "request_id": str(item["request_id"]),
                    "instrument_id": str(item["instrument_id"]),
                    "requester": str(item["person_id"]),
                    "project_id": str(item["project_id"]),
                    "start_utc": str(item["start_utc"]),
                    "end_utc": str(item["end_utc"]),
                    "status": str(item["status"]),
                }
                for item in state["bookings"]
            ],
        }

    @_safe_tool
    def get_request(
        self,
        request_id: Annotated[str, Field(description="Approval request ID, for example AR-0042.")],
    ) -> dict[str, Any]:
        """Read a request and return the canonical revision and decision fields."""
        with closing(open_database(self.database_path)) as connection:
            return repos.get_request(connection, request_id, clock=self.clock)

    @_safe_tool
    def policy_check(
        self,
        request_id: Annotated[
            str,
            Field(description="Approval request ID returned by propose_booking."),
        ],
    ) -> dict[str, Any]:
        """Recheck a pending booking's current training, hours, status, and conflict policy."""
        with closing(open_database(self.database_path)) as connection:
            request = repos.get_request(connection, request_id, clock=self.clock)
            checks: list[dict[str, Any]] = []
            pending = request["status"] == "pending"
            checks.append(
                {
                    "name": "request_pending",
                    "passed": pending,
                    "code": None if pending else ErrorCode.ALREADY_DECIDED.value,
                    "reason": "Request is pending."
                    if pending
                    else f"Request is {request['status']}.",
                }
            )
            if pending:
                start = parse_iso_datetime(str(request["start_utc"]))
                end = parse_iso_datetime(str(request["end_utc"]))
                context = _load_booking_context(
                    connection,
                    instrument_id=str(request["resource"]),
                    person_id=str(request["requester"]),
                )
                try:
                    check_booking(
                        context.policy,
                        Interval(start, end),
                        now=self.clock.now(),
                        training=context.training,
                        existing_bookings=context.bookings,
                    )
                except LabQuorumError as error:
                    details = dict(error.details)
                    if error.code is ErrorCode.CONFLICT:
                        details.update(
                            _conflict_details(
                                error,
                                context=context,
                                interval=Interval(start, end),
                                now=self.clock.now(),
                            )
                        )
                    checks.append(
                        {
                            "name": "booking_policy",
                            "passed": False,
                            "code": error.code.value,
                            "reason": error.message,
                            "details": details,
                        }
                    )
                else:
                    checks.append(
                        {
                            "name": "booking_policy",
                            "passed": True,
                            "code": None,
                            "reason": "Current booking policy passes.",
                        }
                    )
        return {
            "request_id": request_id,
            "allowed": all(item["passed"] for item in checks),
            "checks": checks,
        }

    @_safe_tool
    def decline_request(
        self,
        request_id: Annotated[str, Field(description="Approval request ID to decline.")],
        revision: Annotated[
            int, Field(ge=1, description="Current revision returned by get_request.")
        ],
        reason: Annotated[
            str, Field(min_length=1, description="Reason shown in the ledger audit.")
        ],
    ) -> dict[str, Any]:
        """Decline the pending request at its current revision with an auditable reason."""
        with closing(open_database(self.database_path)) as connection:
            result = repos.decline_request(
                connection,
                request_id,
                revision,
                reason,
                clock=self.clock,
            )
        return {
            "request_id": request_id,
            "revision": revision,
            "status": result["status"],
            "decline_reason": result["decline_reason"],
        }

    @_safe_tool
    def commit_booking(
        self,
        request_id: Annotated[
            str,
            Field(
                max_length=32,
                description="Current request ID returned by get_request.",
            ),
        ],
        revision: Annotated[int, Field(ge=1, description="Current positive request revision.")],
        content_hash: Annotated[
            str,
            Field(
                min_length=64,
                max_length=64,
                pattern=r"^[0-9a-f]{64}$",
                description="Current lowercase SHA-256 hash.",
            ),
        ],
        decision: Annotated[
            BookingDecisionInput,
            Field(description="Echo the complete canonical decision returned by get_request."),
        ],
    ) -> dict[str, Any]:
        """Commit only the exact request revision, hash, and full canonical decision."""
        decision_value = decision.model_dump(mode="json")
        serialize_decision(decision_value)
        serialized_arguments = canonical_json(
            {
                "request_id": request_id,
                "revision": revision,
                "content_hash": content_hash,
                "decision": decision_value,
            }
        )
        if len(serialized_arguments) >= 900:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                "Complete commit arguments must stay below 900 characters for approval-card visibility.",
                {"characters": len(serialized_arguments), "limit": 899},
            )
        with closing(open_database(self.database_path)) as connection:
            return repos.commit_booking(
                connection,
                request_id,
                revision,
                content_hash,
                decision_value,
                clock=self.clock,
            )

    @_safe_tool
    def capability_status(self) -> dict[str, Any]:
        """Explain which non-booking capabilities are not built in this profile."""
        unavailable = [
            {"capability": capability, "reason": reason}
            for capability, reason in (
                ("literature", "Not included in the booking-only P2 build."),
                ("analysis", "Not included in the booking-only P2 build."),
                ("inventory", "Deferred to a later separately gated phase."),
                ("protocols", "Deferred to a later separately gated phase."),
            )
        ]
        return {"enabled_capabilities": [], "unavailable_capabilities": unavailable}
