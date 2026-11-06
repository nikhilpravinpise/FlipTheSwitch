"""Record a scripted two-persona LabQuorum run in Mattermost."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import closing
from datetime import UTC, date, datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Protocol, cast
from urllib.parse import quote
from zoneinfo import ZoneInfo

from labquorum.e2e.assertions import (
    assert_approval,
    assert_card_matches_request,
    assert_no_commit,
    assert_read_propose_smoke,
    assert_refusal,
)
from labquorum.e2e.cards import ApprovalCard, find_approval_cards
from labquorum.e2e.config import (
    HarnessConfig,
    HarnessConfigError,
    PersonaCredentials,
    default_personas_path,
    load_config,
)
from labquorum.e2e.ledger import LedgerInspector, LedgerSnapshot, RequestRecord
from labquorum.e2e.mattermost import MattermostClient, MattermostError, MattermostPost
from labquorum.e2e.runner import REFUSAL_PROMPT

WIDTH = 1280
HEIGHT = 720
MAX_POLL_SECONDS = 2.0
TARGET_SECONDS = 135.0
SUBMISSION_LIMIT_SECONDS = 180.0
DEFAULT_STEP_TIMEOUT = 60.0
_REQUEST_ID = re.compile(r"\bAR-[0-9]{4,}\b", re.IGNORECASE)
_SECRET_KEY = re.compile(r"password|token|secret|authorization|cookie|credential|api[_-]?key", re.I)
_SECRET_VALUE = re.compile(
    r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+|"
    r"((?:password|token|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+"
)


class DemoRecordingError(RuntimeError):
    """A demo could not be recorded without violating its observed state."""


class DemoMattermostClient(Protocol):
    username: str

    def wait_for_post(  # noqa: PLR0913
        self,
        channel_id: str,
        *,
        from_user: str,
        message: str,
        after_ms: int,
        timeout: float,
        poll_interval: float,
    ) -> MattermostPost: ...

    def wait_for_reply(  # noqa: PLR0913
        self,
        channel_id: str,
        *,
        from_agent: str,
        after_ms: int,
        timeout: float,
        poll_interval: float,
        root_id: str,
    ) -> MattermostPost: ...

    def get_channel_posts(
        self,
        channel_id: str,
        *,
        include_deleted: bool = False,
    ) -> list[MattermostPost]: ...

    def wait_for_approval_card(
        self,
        channel_id: str,
        *,
        after_ms: int,
        timeout: float,
        poll_interval: float,
        root_id: str,
    ) -> ApprovalCard: ...

    def wait_for_settled_card(
        self,
        card: ApprovalCard,
        *,
        expected_settler: str,
        timeout: float,
        poll_interval: float,
    ) -> tuple[str, str | None]: ...


class DemoLedger(Protocol):
    def snapshot(self) -> LedgerSnapshot: ...


def inject_caption(
    page: Any,
    caption: str,
    *,
    audit_output: str | None = None,
    end_card: str | None = None,
) -> None:
    """Render captions and audit output as literal text in fixed page overlays."""
    page.evaluate(
        """(payload) => {
          const style = (node, css) => { node.style.cssText = css; };
          const ensure = (id, tag) => {
            let node = document.getElementById(id);
            if (!node) {
              node = document.createElement(tag);
              node.id = id;
              node.setAttribute('data-lq-demo-overlay', 'true');
              document.body.appendChild(node);
            }
            return node;
          };
          const badge = ensure('lq-demo-synthetic-badge', 'div');
          badge.textContent = 'Synthetic lab data';
          style(badge, 'position:fixed;top:10px;left:12px;z-index:2147483647;' +
            'padding:7px 12px;border-radius:5px;background:#542b12;color:#fff;' +
            'font:600 15px/1.2 Arial,sans-serif;box-shadow:0 2px 8px #0008;');
          const banner = ensure('lq-demo-caption', 'div');
          banner.textContent = payload.caption;
          style(banner, 'position:fixed;top:8px;left:50%;transform:translateX(-50%);' +
            'z-index:2147483646;max-width:72vw;padding:10px 18px;border-radius:6px;' +
            'background:#102536;color:#fff;text-align:center;' +
            'font:600 20px/1.25 Arial,sans-serif;box-shadow:0 2px 10px #0009;');
          let audit = document.getElementById('lq-demo-audit');
          if (payload.audit_output) {
            audit = audit || ensure('lq-demo-audit', 'pre');
            audit.textContent = 'lq audit tail\n' + payload.audit_output;
            style(audit, 'position:fixed;right:12px;bottom:12px;z-index:2147483645;' +
              'width:min(48vw,680px);max-height:40vh;overflow:auto;margin:0;padding:12px;' +
              'border:1px solid #7294ad;border-radius:6px;background:#08131eef;color:#d8f1ff;' +
              'white-space:pre-wrap;overflow-wrap:anywhere;' +
              'font:13px/1.35 Consolas,monospace;box-shadow:0 2px 10px #0009;');
          } else if (audit) {
            audit.remove();
          }
          let ending = document.getElementById('lq-demo-end-card');
          if (payload.end_card) {
            ending = ending || ensure('lq-demo-end-card', 'div');
            ending.textContent = payload.end_card;
            style(ending, 'position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);' +
              'z-index:2147483647;max-width:80vw;padding:28px 36px;border:2px solid #93d5ff;' +
              'border-radius:10px;background:#102536f5;color:#fff;text-align:center;' +
              'font:700 30px/1.25 Arial,sans-serif;box-shadow:0 4px 20px #000b;');
          } else if (ending) {
            ending.remove();
          }
        }""",
        {"caption": caption, "audit_output": audit_output, "end_card": end_card},
    )


def select_student_credentials(config: HarnessConfig, selector: str) -> PersonaCredentials:
    """Resolve a student persona by key or configured Mattermost username."""
    normalized = selector.strip().casefold()
    if not normalized or normalized == "prof-rao":
        raise ValueError("Select a student persona, such as maya or darved2305.")
    for name, credentials in config.personas.items():
        if name.casefold() == normalized or credentials.login_id.casefold() == normalized:
            if name.casefold() == "prof-rao":
                break
            return credentials
    raise ValueError(f"No student persona matches {selector!r} in the persona file.")


class DemoRecorder:
    """Drive and time the real Mattermost events while two pages record them."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        student: DemoMattermostClient,
        pi: DemoMattermostClient,
        ledger: DemoLedger,
        channel_id: str,
        student_page: Any,
        pi_page: Any,
        output_dir: Path,
        proposal_only: bool,
        request_date: date | None = None,
        step_timeout: float = DEFAULT_STEP_TIMEOUT,
        poll_interval: float = 0.5,
        typing_delay_ms: int = 45,
        type_message: Callable[[Any, str, int], None] | None = None,
        wait_visible: Callable[[Any, str, float], None] | None = None,
        click_approval: Callable[[Any, ApprovalCard, float], None] | None = None,
        audit_tail: Callable[[Path, int], str] | None = None,
        monotonic: Callable[[], float] = time.monotonic,
        utc_now: Callable[[], datetime] = lambda: datetime.now(UTC),
        sleep: Callable[[float], None] = time.sleep,
        end_card_hold_seconds: float = 2.0,
    ) -> None:
        if step_timeout <= 0:
            raise ValueError("Step timeout must be positive.")
        if poll_interval <= 0 or poll_interval > MAX_POLL_SECONDS:
            raise ValueError("Poll interval must be positive and no longer than 2 seconds.")
        if typing_delay_ms < 0:
            raise ValueError("Typing delay cannot be negative.")
        if end_card_hold_seconds < 0 or end_card_hold_seconds > MAX_POLL_SECONDS:
            raise ValueError("End-card hold must be between zero and 2 seconds.")
        self.student = student
        self.pi = pi
        self.ledger = ledger
        self.channel_id = channel_id
        self.student_page = student_page
        self.pi_page = pi_page
        self.output_dir = output_dir
        self.proposal_only = proposal_only
        self.request_date = request_date
        self.step_timeout = step_timeout
        self.poll_interval = poll_interval
        self.typing_delay_ms = typing_delay_ms
        self.type_message = type_message or type_message_in_ui
        self.wait_visible = wait_visible or wait_for_visible_text
        self.click_approval = click_approval or click_allow_once
        self.audit_tail = audit_tail or run_audit_tail
        self.monotonic = monotonic
        self.utc_now = utc_now
        self.sleep = sleep
        self.end_card_hold_seconds = end_card_hold_seconds
        self._steps: list[dict[str, Any]] = []
        self._shots: list[dict[str, Any]] = []
        self._started_monotonic = 0.0
        self._started_at_utc = datetime.now(UTC)
        self._caption = ""
        self._audit_output: str | None = None
        self._request_id: str | None = None
        self._request_date: date | None = None
        self._result: dict[str, Any] = {}
        self._video_directories = {"student": "student-video", "pi": "pi-video"}
        self._ledger_path = getattr(ledger, "path", Path("ledger.sqlite"))

    def run(self) -> dict[str, Any]:
        """Record one causal take and write timings even if a step fails."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._started_at_utc = self.utc_now()
        self._started_monotonic = self.monotonic()
        try:
            self._result = self._run_flow()
        except Exception as exc:
            self._close_open_shot()
            failure = f"{type(exc).__name__}: {exc}"
            self._result = {
                "status": "fail",
                "mode": "proposal-only" if self.proposal_only else "binding",
                "failure": failure,
                "request_id": self._request_id,
                "request_date": self._request_date.isoformat() if self._request_date else None,
            }
            self._write_artifacts(self._result)
            raise
        self._close_open_shot()
        self._write_artifacts(self._result)
        return self._result

    def _run_flow(self) -> dict[str, Any]:
        shot_total = 4 if self.proposal_only else 5
        self._shot_total = shot_total
        self._set_shot("Student asks @labops")

        before = self._timed_step("ledger.snapshot_before", self.ledger.snapshot)
        request_date = self.request_date or _seed_conflict_date(before, self.utc_now())
        self._request_date = request_date
        prompt = _build_request_prompt(request_date)
        proposal_post = self._send_student_message(prompt)
        proposal_reply = self._wait_for_reply(
            self.student,
            "labops",
            proposal_post,
            "mattermost.wait_labops_proposal",
        )
        self._show_post_on_both(proposal_reply.message, "ui.show_labops_reply")
        proposal_snapshot = self._wait_for_request(proposal_reply, before)
        request_id = self._request_id_from_reply(proposal_reply, before, proposal_snapshot)
        self._request_id = request_id
        self._timed_step(
            "assertion.read_propose_smoke",
            lambda: assert_read_propose_smoke(
                proposal_reply.message,
                request_id,
                proposal_snapshot,
            ),
        )
        request = _require_request(proposal_snapshot, request_id)
        if self.proposal_only:
            self._timed_step(
                "mattermost.check_proposal_only_card_absence",
                lambda: self._assert_no_approval_card(proposal_post),
            )
        self._set_shot("Conflict and 15:45-16:45 proposal")

        refusal_before = self._timed_step("ledger.snapshot_before_refusal", self.ledger.snapshot)
        refusal_post = self._send_student_message(REFUSAL_PROMPT)
        refusal_reply = self._wait_for_reply(
            self.student,
            "pi-desk",
            refusal_post,
            "mattermost.wait_pi_desk_refusal",
        )
        self._show_post_on_both(refusal_reply.message, "ui.show_pi_desk_refusal")
        refusal_after = self._timed_step("ledger.snapshot_after_refusal", self.ledger.snapshot)
        self._timed_step(
            "assertion.student_refusal_without_mutation",
            lambda: assert_refusal(refusal_reply.message, refusal_before, refusal_after),
        )
        self._set_shot("Student cannot approve")

        if self.proposal_only:
            final_snapshot, end_card, commit_audit_count = self._proposal_only_ending(
                proposal_post,
                request_id,
            )
        else:
            self._set_shot("PI reviews the native approval card and approves once")
            card = self._timed_step(
                "mattermost.wait_native_approval_card",
                lambda: self.pi.wait_for_approval_card(
                    self.channel_id,
                    after_ms=proposal_post.create_at,
                    timeout=self.step_timeout,
                    poll_interval=self.poll_interval,
                    root_id=proposal_post.post_id,
                ),
            )
            self._timed_step(
                "assertion.card_matches_pending_request",
                lambda: assert_card_matches_request(card.message, request),
            )
            self._timed_step(
                "ui.show_native_approval_card",
                lambda: self.wait_visible(self.pi_page, request_id, self.step_timeout),
            )
            self._timed_step(
                "ui.pi_click_approve_once",
                lambda: self.click_approval(self.pi_page, card, self.step_timeout),
            )
            settled_text, actor = self._timed_step(
                "mattermost.wait_settled_card",
                lambda: self.pi.wait_for_settled_card(
                    card,
                    expected_settler="prof-rao",
                    timeout=self.step_timeout,
                    poll_interval=self.poll_interval,
                ),
            )
            final_snapshot = self._wait_for_status(request_id, "committed")
            self._timed_step(
                "assertion.committed_booking_and_audit",
                lambda: assert_approval(final_snapshot, request_id, settled_text, actor),
            )
            end_card = f"Committed booking and audit verified - {request_id}"
            commit_audit_count = len(final_snapshot.commit_events_for(request_id))

        self._set_shot(
            "Committed booking and audit" if not self.proposal_only else "Proposal-only ending"
        )
        audit_output = self._timed_step(
            "lq.audit_tail", lambda: self.audit_tail(self._ledger_path, 5)
        )
        self._audit_output = audit_output
        self._timed_step(
            "overlay.audit_and_end_card",
            lambda: self._inject_overlays(end_card=end_card),
        )
        if self.end_card_hold_seconds:
            self._timed_step(
                "end_card.read_hold",
                lambda: self.sleep(min(self.end_card_hold_seconds, MAX_POLL_SECONDS)),
            )
        final_request = _require_request(final_snapshot, request_id)
        return {
            "status": "pass",
            "mode": "proposal-only" if self.proposal_only else "binding",
            "request_id": request_id,
            "request_date": request_date.isoformat(),
            "request_status": final_request.status,
            "commit_audit_count": commit_audit_count,
            "audit_valid": final_snapshot.audit_valid,
            "end_card": end_card,
        }

    def _proposal_only_ending(
        self,
        proposal_post: MattermostPost,
        request_id: str,
    ) -> tuple[LedgerSnapshot, str, int]:
        final_snapshot = self._timed_step(
            "ledger.snapshot_before_proposal_only_ending",
            self.ledger.snapshot,
        )
        self._timed_step(
            "assertion.proposal_only_not_committed",
            lambda: assert_no_commit(final_snapshot, request_id),
        )
        final_request = _require_request(final_snapshot, request_id)
        if final_request.status != "pending":
            raise DemoRecordingError(
                f"Proposal-only request {request_id} is no longer pending; "
                "the take cannot claim it is unbooked."
            )
        self._timed_step(
            "mattermost.recheck_proposal_only_card_absence",
            lambda: self._assert_no_approval_card(proposal_post),
        )
        return final_snapshot, "Proposal only - not booked", 0

    def _send_student_message(self, message: str) -> MattermostPost:
        after_ms = int(self.utc_now().timestamp() * 1000)
        self._timed_step(
            "ui.student_type_message",
            lambda: self.type_message(self.student_page, message, self.typing_delay_ms),
        )
        post = self._timed_step(
            "mattermost.wait_student_post",
            lambda: self.student.wait_for_post(
                self.channel_id,
                from_user=self.student.username,
                message=message,
                after_ms=after_ms,
                timeout=self.step_timeout,
                poll_interval=self.poll_interval,
            ),
        )
        if post.message != message:
            raise DemoRecordingError("Mattermost did not record the exact typed student message.")
        self._show_post_on_both(message, "ui.confirm_student_post")
        return post

    def _wait_for_reply(
        self,
        client: DemoMattermostClient,
        from_agent: str,
        sent: MattermostPost,
        step_name: str,
    ) -> MattermostPost:
        return cast(
            MattermostPost,
            self._timed_step(
                step_name,
                lambda: client.wait_for_reply(
                    self.channel_id,
                    from_agent=from_agent,
                    after_ms=sent.create_at,
                    timeout=self.step_timeout,
                    poll_interval=self.poll_interval,
                    root_id=sent.post_id,
                ),
            ),
        )

    def _wait_for_request(
        self,
        reply: MattermostPost,
        before: LedgerSnapshot,
    ) -> LedgerSnapshot:
        request_id_match = _REQUEST_ID.findall(reply.message)
        request_id = request_id_match[-1].upper() if request_id_match else None
        previous = {request.request_id for request in before.requests}

        def requested(snapshot: LedgerSnapshot) -> bool:
            if request_id is not None:
                request = snapshot.request(request_id)
                return request is not None and request.status in {"pending", "committed"}
            additions = [
                request for request in snapshot.requests if request.request_id not in previous
            ]
            return len(additions) == 1 and additions[0].status in {"pending", "committed"}

        return cast(
            LedgerSnapshot,
            self._timed_step(
                "ledger.wait_for_proposal",
                lambda: self._poll_ledger(requested, "Proposal did not reach the ledger."),
            ),
        )

    def _assert_no_approval_card(self, proposal_post: MattermostPost) -> None:
        posts = self.student.get_channel_posts(self.channel_id)
        cards = find_approval_cards(post for post in posts if post.root_id == proposal_post.post_id)
        if cards:
            raise DemoRecordingError(
                "Proposal-only mode observed an approval card in the request thread. "
                "This take cannot be labeled as an approval-free proposal."
            )

    def _wait_for_status(self, request_id: str, status: str) -> LedgerSnapshot:
        return cast(
            LedgerSnapshot,
            self._timed_step(
                "ledger.wait_for_status",
                lambda: self._poll_ledger(
                    lambda snapshot: (
                        (request := snapshot.request(request_id)) is not None
                        and request.status == status
                    ),
                    f"Request {request_id} did not reach status {status}.",
                ),
            ),
        )

    def _poll_ledger(
        self,
        predicate: Callable[[LedgerSnapshot], bool],
        timeout_message: str,
    ) -> LedgerSnapshot:
        deadline = self.monotonic() + self.step_timeout
        while True:
            snapshot = self.ledger.snapshot()
            if predicate(snapshot):
                return snapshot
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                raise DemoRecordingError(timeout_message)
            self.sleep(min(self.poll_interval, MAX_POLL_SECONDS, remaining))

    def _request_id_from_reply(
        self,
        reply: MattermostPost,
        before: LedgerSnapshot,
        after: LedgerSnapshot,
    ) -> str:
        matches = _REQUEST_ID.findall(reply.message)
        if matches:
            return matches[-1].upper()
        previous = {request.request_id for request in before.requests}
        added = [
            request.request_id for request in after.requests if request.request_id not in previous
        ]
        if len(added) == 1:
            return added[0]
        raise DemoRecordingError("Could not identify one request ID from the reply or ledger.")

    def _show_post_on_both(self, message: str, step_name: str) -> None:
        def show() -> None:
            self.wait_visible(self.student_page, message, self.step_timeout)
            self.wait_visible(self.pi_page, message, self.step_timeout)

        self._timed_step(step_name, show)

    def _set_shot(self, title: str) -> None:
        self._close_open_shot()
        index = len(self._shots) + 1
        self._caption = f"{index}/{self._shot_total} {title}"
        self._shots.append(
            {
                "index": index,
                "caption": self._caption,
                "start_seconds": self._elapsed_seconds(),
                "end_seconds": None,
            }
        )
        self._timed_step("caption.inject", self._inject_overlays)

    def _inject_overlays(self, *, end_card: str | None = None) -> None:
        inject_caption(
            self.student_page,
            self._caption,
            audit_output=self._audit_output,
            end_card=end_card,
        )
        inject_caption(
            self.pi_page,
            self._caption,
            audit_output=self._audit_output,
            end_card=end_card,
        )

    def _close_open_shot(self) -> None:
        if self._shots and self._shots[-1]["end_seconds"] is None:
            self._shots[-1]["end_seconds"] = self._elapsed_seconds()

    def _timed_step(self, name: str, action: Callable[[], Any]) -> Any:
        started_at = self.utc_now()
        start_seconds = self._elapsed_seconds()
        started = self.monotonic()
        status = "pass"
        try:
            return action()
        except Exception as exc:
            status = "fail"
            raise DemoRecordingError(f"Step {name} failed: {exc}") from exc
        finally:
            ended = self.monotonic()
            self._steps.append(
                {
                    "name": name,
                    "started_at_utc": started_at.isoformat(timespec="milliseconds"),
                    "start_seconds": round(start_seconds, 3),
                    "end_seconds": round(self._elapsed_seconds(), 3),
                    "elapsed_seconds": round(max(0.0, ended - started), 3),
                    "timeout_seconds": self.step_timeout,
                    "status": status,
                }
            )

    def _elapsed_seconds(self) -> float:
        return max(0.0, self.monotonic() - self._started_monotonic)

    def _write_artifacts(self, result: dict[str, Any]) -> None:
        finished_at = self.utc_now()
        elapsed = self._elapsed_seconds()
        timing = {
            "version": 1,
            "status": result.get("status", "fail"),
            "mode": result.get("mode", "proposal-only" if self.proposal_only else "binding"),
            "started_at_utc": self._started_at_utc.isoformat(timespec="milliseconds"),
            "finished_at_utc": finished_at.isoformat(timespec="milliseconds"),
            "sequence_elapsed_seconds": round(elapsed, 3),
            "sequence_under_180_seconds": elapsed < SUBMISSION_LIMIT_SECONDS,
            "target_seconds": TARGET_SECONDS,
            "submission_limit_seconds": SUBMISSION_LIMIT_SECONDS,
            "request_date": result.get("request_date"),
            "request_id": result.get("request_id"),
            "request_status": result.get("request_status"),
            "steps": self._steps,
            "shots": self._shots,
            "video_directories": self._video_directories,
        }
        if result.get("failure"):
            timing["failure"] = result["failure"]
        (self.output_dir / "timing.json").write_text(
            json.dumps(timing, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (self.output_dir / "shots.md").write_text(
            _build_shots_markdown(timing, result),
            encoding="utf-8",
        )


def type_message_in_ui(page: Any, message: str, typing_delay_ms: int) -> None:
    """Type into the last visible Mattermost textbox and submit it."""
    textboxes = page.get_by_role("textbox")
    if textboxes.count() == 0:
        textboxes = page.locator("[contenteditable='true']")
    if textboxes.count() == 0:
        raise DemoRecordingError("Mattermost did not expose a message composer textbox.")
    composer = textboxes.last
    if not composer.is_visible() or not composer.is_enabled():
        raise DemoRecordingError("Mattermost message composer is not visible and enabled.")
    if composer.get_attribute("contenteditable") == "true":
        existing = composer.inner_text()
    else:
        existing = composer.input_value()
    if existing.strip():
        raise DemoRecordingError(
            "Mattermost composer has an unsent draft; clear it before recording."
        )
    composer.click()
    composer.press_sequentially(message, delay=typing_delay_ms)
    composer.press("Enter")


def wait_for_visible_text(page: Any, text: str, timeout_seconds: float) -> None:
    """Wait for a Mattermost post to become visible in the recorded page."""
    locator = page.get_by_text(text, exact=False).last
    locator.wait_for(state="visible", timeout=int(timeout_seconds * 1000))


def click_allow_once(page: Any, card: ApprovalCard, timeout_seconds: float) -> None:
    """Click one unambiguous native approval action on the PI's Mattermost page."""
    del card
    label = re.compile(r"^\s*[1-9][0-9]*[.)]?\s*(?:allow|approve|accept)(?:\s+once)?\s*$", re.I)
    buttons = page.get_by_role("button", name=label)
    visible = [button for button in buttons.all() if button.is_visible() and button.is_enabled()]
    if len(visible) != 1:
        raise DemoRecordingError(
            "Expected exactly one visible Allow once action on the PI page; no answer was sent."
        )
    visible[0].click(timeout=int(timeout_seconds * 1000))


def run_audit_tail(ledger_path: Path, limit: int = 5) -> str:
    """Run lq audit tail on a consistent temporary copy and redact its output."""
    try:
        with tempfile.TemporaryDirectory(prefix="lq-demo-audit-") as temporary_directory:
            snapshot_path = Path(temporary_directory) / "ledger.sqlite"
            _copy_ledger_read_only(ledger_path, snapshot_path)
            executable = shutil.which("lq")
            command = (
                [executable, "audit", "tail", "--db", str(snapshot_path), "-n", str(limit)]
                if executable
                else [
                    sys.executable,
                    "-m",
                    "labquorum.cli.main",
                    "audit",
                    "tail",
                    "--db",
                    str(snapshot_path),
                    "-n",
                    str(limit),
                ]
            )
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
    except (OSError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        raise DemoRecordingError(
            "Could not run lq audit tail against a read-only ledger copy."
        ) from exc
    if completed.returncode != 0:
        raise DemoRecordingError("lq audit tail failed against the temporary ledger copy.")
    try:
        output: Any = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise DemoRecordingError("lq audit tail returned invalid JSON.") from exc
    return json.dumps(_redact_audit(output), ensure_ascii=False, indent=2, sort_keys=True)


def _copy_ledger_read_only(source_path: Path, destination_path: Path) -> None:
    source = source_path.expanduser().resolve(strict=True)
    encoded = quote(source.as_posix(), safe="/:\\")
    source_uri = f"file:{encoded}?mode=ro"
    with closing(sqlite3.connect(source_uri, uri=True, timeout=5.0)) as source_connection:
        source_connection.execute("PRAGMA query_only = ON")
        with closing(sqlite3.connect(destination_path, timeout=5.0)) as destination_connection:
            source_connection.backup(destination_connection)
            destination_connection.commit()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--personas", type=Path, default=default_personas_path())
    parser.add_argument("--student", default="maya", help="Student persona key or username")
    parser.add_argument(
        "--student-state", type=Path, help="Optional Playwright student storage state"
    )
    parser.add_argument("--pi-state", type=Path, help="Optional Playwright PI storage state")
    parser.add_argument("--request-date", type=_date_argument)
    parser.add_argument("--timeout", type=float, default=DEFAULT_STEP_TIMEOUT)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--typing-delay-ms", type=int, default=45)
    parser.add_argument("--end-card-hold", type=float, default=2.0)
    parser.add_argument("--output-dir", type=Path, help="Override the LocalAppData demo output")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--proposal-only", action="store_true")
    mode.add_argument(
        "--binding-certified",
        action="store_true",
        help="Enable the approval shot only after the installed P4 binding tuple is certified",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.proposal_only and not args.binding_certified:
        parser.error("Choose --proposal-only or --binding-certified after the P4 certification.")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.poll_interval <= 0 or args.poll_interval > MAX_POLL_SECONDS:
        parser.error("--poll-interval must be positive and no longer than 2 seconds")
    if args.typing_delay_ms < 0:
        parser.error("--typing-delay-ms cannot be negative")
    if args.end_card_hold < 0 or args.end_card_hold > MAX_POLL_SECONDS:
        parser.error("--end-card-hold must be between zero and 2 seconds")
    for state in (args.student_state, args.pi_state):
        if state is not None and not state.is_file():
            parser.error(f"Storage state file does not exist: {state}")

    try:
        config = load_config(args.personas)
        student_credentials = select_student_credentials(config, args.student)
        pi_credentials = config.personas["prof-rao"]
        output_dir = args.output_dir or _default_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        result = record_demo(
            config,
            student_credentials,
            pi_credentials,
            output_dir,
            proposal_only=args.proposal_only,
            request_date=args.request_date,
            step_timeout=args.timeout,
            poll_interval=args.poll_interval,
            typing_delay_ms=args.typing_delay_ms,
            student_state=args.student_state,
            pi_state=args.pi_state,
            end_card_hold_seconds=args.end_card_hold,
        )
    except (DemoRecordingError, HarnessConfigError, MattermostError, OSError, ValueError) as exc:
        print(f"Demo recording failed: {exc}")
        return 1
    print(f"Demo recording {result['status']}; mode {result['mode']}; output: {output_dir}")
    return 0 if result["status"] == "pass" else 1


def record_demo(  # noqa: PLR0913
    config: HarnessConfig,
    student_credentials: PersonaCredentials,
    pi_credentials: PersonaCredentials,
    output_dir: Path,
    *,
    proposal_only: bool,
    request_date: date | None,
    step_timeout: float,
    poll_interval: float,
    typing_delay_ms: int,
    student_state: Path | None,
    pi_state: Path | None,
    end_card_hold_seconds: float,
) -> dict[str, Any]:
    """Authenticate both harness personas, open the configured room, then record."""
    with (
        MattermostClient(
            config.mattermost_url,
            student_credentials.login_id,
            student_credentials.password,
        ) as student,
        MattermostClient(
            config.mattermost_url,
            pi_credentials.login_id,
            pi_credentials.password,
        ) as pi,
    ):
        room_url = pi.room_url(config.channel_id)
        return _record_pages(
            config,
            student,
            pi,
            LedgerInspector(config.ledger_path),
            room_url,
            output_dir,
            proposal_only=proposal_only,
            request_date=request_date,
            step_timeout=step_timeout,
            poll_interval=poll_interval,
            typing_delay_ms=typing_delay_ms,
            student_state=student_state,
            pi_state=pi_state,
            end_card_hold_seconds=end_card_hold_seconds,
        )


def _record_pages(  # noqa: PLR0913, PLR0917
    config: HarnessConfig,
    student: MattermostClient,
    pi: MattermostClient,
    ledger: LedgerInspector,
    room_url: str,
    output_dir: Path,
    *,
    proposal_only: bool,
    request_date: date | None,
    step_timeout: float,
    poll_interval: float,
    typing_delay_ms: int,
    student_state: Path | None,
    pi_state: Path | None,
    end_card_hold_seconds: float,
) -> dict[str, Any]:
    try:
        sync_api_module = import_module("playwright.sync_api")
        sync_playwright = cast(Callable[[], Any], sync_api_module.__dict__["sync_playwright"])
    except ImportError as exc:
        raise DemoRecordingError(
            "Playwright is unavailable. Install it with uv sync --extra demo, then install Chromium."
        ) from exc

    student_video_dir = output_dir / "student-video"
    pi_video_dir = output_dir / "pi-video"
    student_video_dir.mkdir(parents=True, exist_ok=True)
    pi_video_dir.mkdir(parents=True, exist_ok=True)
    launch_timeout_ms = int(step_timeout * 1000)
    with sync_playwright() as playwright:
        student_browser = playwright.chromium.launch(
            headless=False,
            timeout=launch_timeout_ms,
            args=[f"--window-size={WIDTH},{HEIGHT}", "--window-position=0,0"],
        )
        pi_browser = playwright.chromium.launch(
            headless=False,
            timeout=launch_timeout_ms,
            args=[f"--window-size={WIDTH},{HEIGHT}", f"--window-position={WIDTH},0"],
        )
        student_context = student_browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            record_video_dir=str(student_video_dir),
            record_video_size={"width": WIDTH, "height": HEIGHT},
            **({"storage_state": str(student_state)} if student_state else {}),
        )
        pi_context = pi_browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            record_video_dir=str(pi_video_dir),
            record_video_size={"width": WIDTH, "height": HEIGHT},
            **({"storage_state": str(pi_state)} if pi_state else {}),
        )
        try:
            if student_state is None:
                student_context.add_cookies(
                    [
                        {
                            "name": "MMAUTHTOKEN",
                            "value": student.session_token,
                            "url": config.mattermost_url,
                        }
                    ]
                )
            if pi_state is None:
                pi_context.add_cookies(
                    [
                        {
                            "name": "MMAUTHTOKEN",
                            "value": pi.session_token,
                            "url": config.mattermost_url,
                        }
                    ]
                )
            student_page = student_context.new_page()
            pi_page = pi_context.new_page()
            for page in (student_page, pi_page):
                page.set_default_timeout(launch_timeout_ms)
                page.goto(room_url, wait_until="domcontentloaded", timeout=launch_timeout_ms)
            recorder = DemoRecorder(
                student=student,
                pi=pi,
                ledger=ledger,
                channel_id=config.channel_id,
                student_page=student_page,
                pi_page=pi_page,
                output_dir=output_dir,
                proposal_only=proposal_only,
                request_date=request_date,
                step_timeout=step_timeout,
                poll_interval=poll_interval,
                typing_delay_ms=typing_delay_ms,
                end_card_hold_seconds=end_card_hold_seconds,
            )
            result = recorder.run()
            return result
        finally:
            student_context.close()
            pi_context.close()
            student_browser.close()
            pi_browser.close()


def _build_request_prompt(request_date: date) -> str:
    return (
        "@labops, propose a 60-minute INS-01 plate reader booking for Maya on "
        f"{request_date.isoformat()} between 14:00 and 17:00 Asia/Kolkata."
    )


def _seed_conflict_date(snapshot: LedgerSnapshot, now: datetime) -> date:
    zone = ZoneInfo("Asia/Kolkata")
    local_today = now.astimezone(zone).date()
    matching_dates: list[date] = []
    for booking in snapshot.bookings:
        if (
            booking.instrument_id.casefold() != "ins-01"
            or booking.person_id.casefold() != "lena"
            or booking.status.casefold() != "committed"
        ):
            continue
        start = _parse_timestamp(booking.start_utc).astimezone(zone)
        end = _parse_timestamp(booking.end_utc).astimezone(zone)
        if (start.hour, start.minute, end.hour, end.minute) == (14, 0, 15, 30) and (
            start.date() >= local_today
        ):
            matching_dates.append(start.date())
    if not matching_dates:
        raise DemoRecordingError(
            "No future Lena INS-01 conflict from 14:00 to 15:30 was found in the read-only ledger."
        )
    return min(matching_dates)


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise DemoRecordingError("Ledger timestamp did not include a UTC offset.")
    return parsed


def _require_request(snapshot: LedgerSnapshot, request_id: str) -> RequestRecord:
    request = snapshot.request(request_id)
    if request is None:
        raise DemoRecordingError(f"Request {request_id} was not present in the read-only ledger.")
    return request


def _build_shots_markdown(timing: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    lines = [
        "# Demo edit list",
        "",
        f"Mode: `{result.get('mode', timing.get('mode', 'unknown'))}`",
        f"Status: `{result.get('status', timing.get('status', 'unknown'))}`",
        f"Request: `{result.get('request_id') or 'not identified'}`",
        f"Request date: `{result.get('request_date') or 'not identified'}`",
        f"Measured sequence time: `{timing['sequence_elapsed_seconds']:.3f}s`",
        "Cut target: 2:15. Submission limit: under 3:00. Do not speed up hidden waits.",
        "",
        "Playwright videos are in `student-video/` and `pi-video/`.",
        "Times below are sequence-relative; allow for page-load pre-roll in the raw videos.",
        "Both use a 1280x720 viewport. Keep the synthetic-data badge and verify captions against footage.",
        "",
        "## Shots",
        "",
        "| # | Sequence in | Sequence out | Duration | Caption |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    shots = cast(list[dict[str, Any]], timing.get("shots", []))
    for shot in shots:
        start = float(shot.get("start_seconds") or 0.0)
        end = float(shot.get("end_seconds") or start)
        lines.append(
            f"| {shot.get('index', '')} | {_format_time(start)} | {_format_time(end)} | "
            f"{max(0.0, end - start):.3f}s | {shot.get('caption', '')} |"
        )
    if not shots:
        lines.append("| - | - | - | - | No complete shot was recorded. |")
    lines.extend(
        [
            "",
            "## Measured steps",
            "",
            "| Sequence in | Step | Wait | Result |",
            "| ---: | --- | ---: | --- |",
        ]
    )
    steps = cast(list[dict[str, Any]], timing.get("steps", []))
    for step in steps:
        lines.append(
            f"| {_format_time(float(step.get('start_seconds') or 0.0))} | "
            f"{step.get('name', '')} | {float(step.get('elapsed_seconds') or 0.0):.3f}s | "
            f"{step.get('status', 'unknown')} |"
        )
    lines.append("")
    if timing.get("sequence_under_180_seconds"):
        lines.append("The measured sequence is under the three-minute submission limit.")
    else:
        lines.append(
            "The measured sequence exceeds the three-minute limit and needs an honest trim."
        )
    if result.get("end_card"):
        lines.append(f"End card: `{result['end_card']}`")
    if result.get("failure"):
        lines.append(f"Failure: `{result['failure']}`")
    return "\n".join(lines) + "\n"


def _format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes:02d}:{remainder:06.3f}"


def _redact_audit(value: Any, key: str | None = None) -> Any:
    if key is not None and _SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        return {
            str(child_key): _redact_audit(child, str(child_key))
            for child_key, child in mapping.items()
        }
    if isinstance(value, list):
        return [_redact_audit(child) for child in cast(list[Any], value)]
    if isinstance(value, str):
        return _SECRET_VALUE.sub(
            lambda match: f"{match.group(1) or match.group(2)}[REDACTED]",
            value,
        )
    return value


def _date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Request date must use YYYY-MM-DD.") from exc


def _default_output_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    root = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return root / "LabQuorum" / "demo" / timestamp


if __name__ == "__main__":
    raise SystemExit(main())
