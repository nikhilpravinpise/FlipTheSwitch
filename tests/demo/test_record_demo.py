from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx

from labquorum.domain.canonical import content_hash
from labquorum.e2e.cards import ApprovalCard
from labquorum.e2e.config import HarnessConfig, PersonaCredentials, load_config
from labquorum.e2e.ledger import (
    AuditEvent,
    BookingRecord,
    LedgerSnapshot,
    RequestRecord,
)
from labquorum.e2e.mattermost import MattermostClient, MattermostPost
from scripts.demo.record_demo import DemoRecorder, inject_caption, select_student_credentials


@dataclass
class FakePage:
    name: str
    overlays: list[dict[str, Any]]
    visible_text: list[str]

    def evaluate(self, _script: str, payload: dict[str, Any]) -> None:
        self.overlays.append(payload)


class FakeLedger:
    def __init__(self) -> None:
        self.state = "empty"
        self.proposal = _proposal_snapshot()
        self.committed = _committed_snapshot()

    def snapshot(self) -> LedgerSnapshot:
        if self.state == "committed":
            return self.committed
        if self.state == "proposal":
            return self.proposal
        return LedgerSnapshot((), (), (), True)


class FakeClient:
    def __init__(self, username: str, ledger: FakeLedger) -> None:
        self.username = username
        self.user_id = username
        self.ledger = ledger
        self.calls: list[str] = []
        self._last_prompt = ""
        self._post_number = 0

    def note_typed_message(self, message: str) -> None:
        self._last_prompt = message

    def wait_for_post(  # noqa: PLR0913
        self,
        channel_id: str,
        *,
        from_user: str,
        message: str,
        after_ms: int,
        timeout: float,
        poll_interval: float,
    ) -> MattermostPost:
        assert channel_id == "room-1"
        assert from_user == self.username
        assert message == self._last_prompt
        assert after_ms > 0
        assert timeout > 0
        assert 0 < poll_interval <= 2
        self.calls.append("wait_for_post")
        self._post_number += 1
        return MattermostPost(
            post_id=f"student-post-{self._post_number}",
            channel_id=channel_id,
            user_id=self.username,
            message=message,
            create_at=after_ms,
        )

    def wait_for_reply(  # noqa: PLR0913
        self,
        channel_id: str,
        *,
        from_agent: str,
        after_ms: int,
        timeout: float,
        poll_interval: float,
        root_id: str,
    ) -> MattermostPost:
        assert channel_id == "room-1"
        assert after_ms > 0
        assert timeout > 0
        assert 0 < poll_interval <= 2
        self.calls.append(f"wait_for_reply:{from_agent}")
        if from_agent == "labops":
            self.ledger.state = "proposal"
            message = (
                "Conflict with Lena's INS-01 booking from 14:00 to 15:30. "
                "The proposed slot is 15:45-16:45. Request AR-0042 is pending."
            )
        else:
            message = "I cannot approve Maya's request from the student account."
        return MattermostPost(
            post_id=f"reply-{from_agent}",
            channel_id=channel_id,
            user_id=from_agent,
            message=message,
            create_at=after_ms + 1,
            root_id=root_id,
        )

    def username_for(self, user_id: str) -> str:
        return user_id

    def wait_for_approval_card(
        self,
        channel_id: str,
        *,
        after_ms: int,
        timeout: float,
        poll_interval: float,
        root_id: str,
    ) -> ApprovalCard:
        assert channel_id == "room-1"
        assert after_ms > 0
        assert timeout > 0
        assert 0 < poll_interval <= 2
        self.calls.append("wait_for_approval_card")
        return _approval_card()

    def wait_for_settled_card(
        self,
        card: ApprovalCard,
        *,
        expected_settler: str,
        timeout: float,
        poll_interval: float,
    ) -> tuple[str, str]:
        assert card.post_id == "card-1"
        assert expected_settler == "prof-rao"
        assert timeout > 0
        assert 0 < poll_interval <= 2
        self.calls.append("wait_for_settled_card")
        return f"{card.message}\nChosen by @prof-rao", "prof-rao"


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def monotonic(self) -> float:
        self.value += 0.25
        return self.value

    def now(self) -> datetime:
        self.value += 0.25
        return datetime(2026, 11, 5, 12, 0, int(self.value), tzinfo=UTC)


def test_E2E_02_recorder_types_a_real_dated_request_and_logs_proposal_timing(
    tmp_path: Path,
) -> None:
    recorder, student, _, ledger, student_page, pi_page = _make_recorder(
        tmp_path, proposal_only=True
    )

    result = recorder.run()

    assert result["status"] == "pass"
    assert result["request_id"] == "AR-0042"
    assert result["request_status"] == "pending"
    assert "2026-11-06" in student_page.visible_text[0]
    assert student.calls == [
        "wait_for_post",
        "wait_for_reply:labops",
        "wait_for_post",
        "wait_for_reply:pi-desk",
    ]
    assert ledger.state == "proposal"
    assert not any(item.get("mode") == "approval" for item in pi_page.overlays)


def test_E2E_03_student_refusal_is_verified_before_its_caption_is_shown(
    tmp_path: Path,
) -> None:
    recorder, _, _, _, student_page, pi_page = _make_recorder(tmp_path, proposal_only=True)

    recorder.run()

    captions = [item["caption"] for item in student_page.overlays]
    assert any("Student cannot approve" in caption for caption in captions)
    assert any(
        "Student cannot approve" in caption
        for caption in [item["caption"] for item in pi_page.overlays]
    )


def test_E2E_04_pi_clicks_once_and_recorder_waits_for_commit_and_audit(
    tmp_path: Path,
) -> None:
    recorder, _, pi, ledger, _, pi_page = _make_recorder(tmp_path, proposal_only=False)
    clicks: list[str] = []

    def click_allow(_page: FakePage, card: ApprovalCard, _timeout: float) -> None:
        clicks.append(card.handle)
        ledger.state = "committed"

    recorder.click_approval = click_allow

    result = recorder.run()

    assert result["status"] == "pass"
    assert result["request_status"] == "committed"
    assert clicks == ["A1"]
    assert "wait_for_approval_card" in pi.calls
    assert "wait_for_settled_card" in pi.calls
    assert any(item.get("audit_output") == "[verified audit tail]" for item in pi_page.overlays)
    assert ledger.state == "committed"


def test_E2E_06_caption_injection_uses_fixed_banner_and_literal_text() -> None:
    page = FakePage("student", [], [])

    inject_caption(page, "1/5 Student asks @labops <literal>")

    assert page.overlays == [
        {
            "caption": "1/5 Student asks @labops <literal>",
            "audit_output": None,
            "end_card": None,
        }
    ]


def test_E2E_02_proposal_only_writes_honest_end_card_and_edit_list(
    tmp_path: Path,
) -> None:
    recorder, _student, pi, ledger, student_page, pi_page = _make_recorder(
        tmp_path, proposal_only=True
    )
    clicks: list[str] = []
    recorder.click_approval = lambda *_args: clicks.append("clicked")

    result = recorder.run()
    timing = json.loads((tmp_path / "timing.json").read_text(encoding="utf-8"))
    edit_list = (tmp_path / "shots.md").read_text(encoding="utf-8")

    assert result["mode"] == "proposal-only"
    assert result["end_card"] == "Proposal only - pending; not committed"
    assert not clicks
    assert "wait_for_approval_card" not in pi.calls
    assert ledger.state == "proposal"
    assert timing["status"] == "pass"
    assert timing["sequence_elapsed_seconds"] < 180
    assert timing["steps"]
    assert timing["shots"]
    assert "Proposal only - pending; not committed" in edit_list
    assert "under 3:00" in edit_list
    assert student_page.overlays[-1]["end_card"] == result["end_card"]
    assert pi_page.overlays[-1]["end_card"] == result["end_card"]


def test_E2E_02_student_persona_can_be_selected_by_username() -> None:
    config = HarnessConfig(
        mattermost_url="http://example.invalid",
        channel_id="room-1",
        ledger_path=Path("ledger.sqlite"),
        personas={
            "maya": PersonaCredentials("maya", "maya-secret"),
            "prof-rao": PersonaCredentials("prof-rao", "rao-secret"),
            "darshan": PersonaCredentials("darved2305", "darshan-secret"),
        },
    )

    selected = select_student_credentials(config, "darved2305")

    assert selected.login_id == "darved2305"


def test_E2E_02_persona_file_accepts_server_private_room_and_extra_student(
    tmp_path: Path,
) -> None:
    path = tmp_path / "personas.json"
    path.write_text(
        json.dumps(
            {
                "server": "https://mattermost.example",
                "team_id": "team-1",
                "private_room": {
                    "id": "room-1",
                    "name": "lab-quorum",
                    "display_name": "Lab Quorum",
                    "type": "P",
                },
                "ledger_path": str(tmp_path / "ledger.sqlite"),
                "personas": {
                    "maya": {"username": "maya", "password": "maya-secret"},
                    "prof-rao": {"username": "prof-rao", "password": "rao-secret"},
                    "darshan": {
                        "username": "darved2305",
                        "password": "darshan-secret",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.mattermost_url == "https://mattermost.example"
    assert config.channel_id == "room-1"
    assert config.personas["darshan"].login_id == "darved2305"
    assert "darshan-secret" not in repr(config)


def test_E2E_02_mattermost_session_token_is_available_for_browser_cookie() -> None:
    client = object.__new__(MattermostClient)
    client._session_token = "local-test-session-token"

    assert client.session_token == "local-test-session-token"


def test_E2E_02_mattermost_room_url_uses_channel_and_team_api_metadata() -> None:
    client = object.__new__(MattermostClient)
    client._base_url = "https://mattermost.example"
    responses = iter(
        (
            httpx.Response(200, json={"team_id": "team-1", "name": "lab-room"}),
            httpx.Response(200, json={"name": "research-team"}),
        )
    )
    calls: list[tuple[str, str]] = []

    def fake_request(method: str, path: str, **_kwargs: Any) -> httpx.Response:
        calls.append((method, path))
        return next(responses)

    client._request = fake_request

    room_url = client.room_url("room-1")

    assert room_url == "https://mattermost.example/research-team/channels/lab-room"
    assert calls == [("GET", "/channels/room-1"), ("GET", "/teams/team-1")]


def test_E2E_02_mattermost_wait_for_post_observes_exact_persona_message() -> None:
    client = object.__new__(MattermostClient)
    client._usernames = {"user-1": "maya"}
    post = MattermostPost(
        post_id="post-1",
        channel_id="room-1",
        user_id="user-1",
        message="@labops propose a booking",
        create_at=200,
    )
    client.get_channel_posts = lambda _channel_id: [post]

    observed = client.wait_for_post(
        "room-1",
        from_user="maya",
        message="@labops propose a booking",
        after_ms=100,
        timeout=1,
        poll_interval=0.5,
    )

    assert observed == post


def _make_recorder(
    tmp_path: Path,
    *,
    proposal_only: bool,
) -> tuple[DemoRecorder, FakeClient, FakeClient, FakeLedger, FakePage, FakePage]:
    ledger = FakeLedger()
    student = FakeClient("maya", ledger)
    pi = FakeClient("prof-rao", ledger)
    student_page = FakePage("student", [], [])
    pi_page = FakePage("pi", [], [])
    clock = FakeClock()

    def type_message(page: FakePage, message: str, _delay_ms: int) -> None:
        page.visible_text.append(message)
        if page.name == "student":
            student.note_typed_message(message)

    def wait_visible(page: FakePage, text: str, _timeout: float) -> None:
        page.visible_text.append(text)

    recorder = DemoRecorder(
        student=student,
        pi=pi,
        ledger=ledger,
        channel_id="room-1",
        student_page=student_page,
        pi_page=pi_page,
        output_dir=tmp_path,
        proposal_only=proposal_only,
        request_date=date(2026, 11, 6),
        step_timeout=10,
        poll_interval=0.5,
        typing_delay_ms=45,
        type_message=type_message,
        wait_visible=wait_visible,
        click_approval=lambda *_args: None,
        audit_tail=lambda _path, _limit: "[verified audit tail]",
        monotonic=clock.monotonic,
        utc_now=clock.now,
        end_card_hold_seconds=0,
    )
    return recorder, student, pi, ledger, student_page, pi_page


def _proposal_snapshot() -> LedgerSnapshot:
    decision = {
        "action": "commit_booking",
        "requester": "maya",
        "resource": "INS-01",
        "interval": {
            "start_utc": "2026-11-06T10:15:00Z",
            "end_utc": "2026-11-06T11:15:00Z",
        },
        "project": "egcg",
        "request_id": "AR-0042",
        "revision": 1,
    }
    digest = content_hash(decision)
    request = RequestRecord(
        request_id="AR-0042",
        status="pending",
        revision=1,
        content_hash=digest,
        decision=decision,
        requester="maya",
        resource="INS-01",
        resource_timezone="Asia/Kolkata",
        start_utc="2026-11-06T10:15:00Z",
        end_utc="2026-11-06T11:15:00Z",
        project="egcg",
    )
    booking = BookingRecord(
        booking_id="BK-0042",
        request_id="AR-0042",
        status="proposed",
        person_id="maya",
        instrument_id="INS-01",
        start_utc=request.start_utc,
        end_utc=request.end_utc,
    )
    return LedgerSnapshot((request,), (booking,), (), True)


def _committed_snapshot() -> LedgerSnapshot:
    snapshot = _proposal_snapshot()
    request = snapshot.requests[0]
    committed_request = RequestRecord(
        request_id=request.request_id,
        status="committed",
        revision=request.revision,
        content_hash=request.content_hash,
        decision=request.decision,
        requester=request.requester,
        resource=request.resource,
        resource_timezone=request.resource_timezone,
        start_utc=request.start_utc,
        end_utc=request.end_utc,
        project=request.project,
    )
    proposed_booking = snapshot.bookings[0]
    committed_booking = BookingRecord(
        booking_id=proposed_booking.booking_id,
        request_id=proposed_booking.request_id,
        status="committed",
        person_id=proposed_booking.person_id,
        instrument_id=proposed_booking.instrument_id,
        start_utc=proposed_booking.start_utc,
        end_utc=proposed_booking.end_utc,
    )
    event = AuditEvent(
        seq=1,
        actor_agent="pi-desk",
        tool="commit_booking",
        args={
            "request_id": request.request_id,
            "revision": request.revision,
            "content_hash": request.content_hash,
            "decision": request.decision,
        },
        result={"request_id": request.request_id, "status": "committed"},
        hash="audit-hash",
    )
    return LedgerSnapshot((committed_request,), (committed_booking,), (event,), True)


def _approval_card() -> ApprovalCard:
    request = _proposal_snapshot().requests[0]
    message = "\n".join(
        (
            "action: commit_booking",
            f"request_id: {request.request_id}",
            f"revision: {request.revision}",
            f"content_hash: {request.content_hash}",
            f"requester_handle: {request.requester}",
            f"instrument_id: {request.resource}",
            f"project_untrusted_text: {request.project}",
            f"start_utc: {request.start_utc}",
            f"end_utc: {request.end_utc}",
            "Reply with A1 and your choice",
            "1. Allow once",
        )
    )
    return ApprovalCard(
        handle="A1",
        post_id="card-1",
        channel_id="room-1",
        user_id="switch",
        message=message,
        options=((1, "Allow once"),),
    )
