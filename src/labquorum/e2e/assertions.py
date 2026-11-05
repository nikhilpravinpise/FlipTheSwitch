"""P4 scenario assertion placeholders."""

from __future__ import annotations

from typing import Any


class ScenarioAssertionError(AssertionError):
    """Raised when durable scenario evidence violates its acceptance rule."""


def assert_read_propose_smoke(reply: str, request_id: str, snapshot: Any) -> None:
    raise NotImplementedError("Read/propose smoke assertion is not implemented yet.")


def assert_refusal(reply: str, before: Any, after: Any) -> None:
    raise NotImplementedError("Refusal assertion is not implemented yet.")


def assert_approval(
    snapshot: Any,
    request_id: str,
    card_text: str,
    settled_by: str | None,
    expected_settler: str = "prof-rao",
) -> None:
    raise NotImplementedError("Approval assertion is not implemented yet.")


def assert_decline(
    snapshot: Any,
    request_id: str,
    settled_by: str | None,
    expected_settler: str = "prof-rao",
) -> None:
    raise NotImplementedError("Decline assertion is not implemented yet.")


def assert_repeat_second_commit(
    response: str,
    *,
    request_id: str,
    snapshot: Any,
    first_card_handle: str,
    second_card_handle: str | None,
) -> None:
    raise NotImplementedError("Repeated commit assertion is not implemented yet.")


def assert_injection_no_commit(snapshot: Any, request_id: str, attack_id: str) -> None:
    raise NotImplementedError("Injection assertion is not implemented yet.")


def assert_restart_safe(snapshot: Any, request_id: str, card_settled: bool) -> None:
    raise NotImplementedError("Restart assertion is not implemented yet.")
