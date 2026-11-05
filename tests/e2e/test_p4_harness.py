from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field, replace
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from urllib.parse import parse_qs, urlsplit

import pytest

from labquorum.domain.canonical import content_hash
from labquorum.e2e.__main__ import build_parser
from labquorum.e2e.assertions import (
    assert_approval,
    assert_card_matches_request,
    assert_decline,
    assert_injection_no_commit,
    assert_read_propose_smoke,
    assert_refusal,
    assert_repeat_second_commit,
    assert_restart_safe,
)
from labquorum.e2e.cards import ApprovalCard, find_approval_cards
from labquorum.e2e.config import load_config
from labquorum.e2e.evidence import write_evidence
from labquorum.e2e.ledger import LedgerInspector
from labquorum.e2e.mattermost import (
    MattermostAuthenticationError,
    MattermostClient,
    MattermostPost,
    MattermostTimeout,
    ReplyTimeout,
)
from labquorum.e2e.runner import INJECTION_PROMPTS, ScenarioOptions, ScenarioRunner
from labquorum.store.audit import append_event


@dataclass
class FakeMattermostState:
    users: dict[str, str] = field(
        default_factory=lambda: {"maya": "maya-id", "prof-rao": "rao-id", "labops": "labops-id"}
    )
    tokens: dict[str, str] = field(default_factory=dict)
    posts: dict[str, dict[str, Any]] = field(default_factory=dict)
    counter: int = 0
    auth_failure: bool = False
    delay_channel_posts: float = 0.0
    auto_reply: tuple[str, str] | None = None
    deleted_post_ids: set[str] = field(default_factory=set)

    def add_post(
        self,
        *,
        channel_id: str,
        user_id: str,
        message: str,
        root_id: str | None = None,
        create_at: int | None = None,
    ) -> dict[str, Any]:
        self.counter += 1
        post_id = f"post-{self.counter}"
        post = {
            "id": post_id,
            "channel_id": channel_id,
            "user_id": user_id,
            "message": message,
            "create_at": create_at if create_at is not None else self.counter * 1000,
            "root_id": root_id or "",
            "props": {},
        }
        self.posts[post_id] = post
        return post


@pytest.fixture
def fake_mattermost() -> Any:
    state = FakeMattermostState()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def _send(
            self, status: int, payload: object, headers: dict[str, str] | None = None
        ) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            try:
                self.wfile.write(body)
            except OSError:
                return

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/api/v4/users/login":
                if state.auth_failure:
                    self._send(401, {"message": "login failed"})
                    return
                login_id = str(body["login_id"])
                token = f"fake-token-{login_id}"
                state.tokens[token] = login_id
                self._send(
                    200,
                    {"id": state.users[login_id], "username": login_id},
                    {"Token": token},
                )
                return
            if self.path == "/api/v4/posts":
                token = self.headers.get("Authorization", "").removeprefix("Bearer ")
                username = state.tokens[token]
                user_id = state.users[username]
                post = state.add_post(
                    channel_id=str(body["channel_id"]),
                    user_id=user_id,
                    message=str(body["message"]),
                    root_id=str(body["root_id"]) if body.get("root_id") else None,
                )
                if state.auto_reply is not None and username == "maya":
                    agent_username, reply = state.auto_reply
                    state.add_post(
                        channel_id=str(body["channel_id"]),
                        user_id=state.users[agent_username],
                        message=reply,
                        root_id=post["id"],
                    )
                self._send(201, post)
                return
            self._send(404, {"message": "not found"})

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            if parsed.path.startswith("/api/v4/channels/") and parsed.path.endswith("/posts"):
                if state.delay_channel_posts:
                    time.sleep(state.delay_channel_posts)
                channel_id = parsed.path.split("/")[4]
                include_deleted = parse_qs(parsed.query).get("include_deleted") == ["true"]
                if include_deleted:
                    token = self.headers.get("Authorization", "").removeprefix("Bearer ")
                    if state.tokens.get(token) != "prof-rao":
                        self._send(403, {"message": "system admin required"})
                        return
                posts = {
                    post_id: post
                    for post_id, post in state.posts.items()
                    if post["channel_id"] == channel_id
                    and (include_deleted or post_id not in state.deleted_post_ids)
                }
                self._send(200, {"order": list(reversed(posts)), "posts": posts})
                return
            if self.path.startswith("/api/v4/users/"):
                user_id = self.path.removeprefix("/api/v4/users/")
                username = next(
                    (name for name, candidate_id in state.users.items() if candidate_id == user_id),
                    None,
                )
                if username is None:
                    self._send(404, {"message": "user not found"})
                else:
                    self._send(200, {"id": user_id, "username": username})
                return
            self._send(404, {"message": "not found"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.block_network(allowed_hosts=[r"^127\.0\.0\.1$"])
def test_mattermost_client_posts_and_finds_agent_authored_reply(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, state = fake_mattermost
    state.auto_reply = (
        "labops",
        "Lena conflicts 14:00-15:30. Proposed 15:45-16:45. Request AR-0042.",
    )
    with MattermostClient(base_url, "maya", "fake-password", timeout=1) as client:
        sent = client.post("channel-1", "@labops, propose the next open slot")
        reply = client.wait_for_reply(
            "channel-1",
            from_agent="labops",
            after_ms=sent.create_at,
            root_id=sent.post_id,
            timeout=0.25,
            poll_interval=0.005,
        )

    assert reply.message.startswith("Lena conflicts")
    assert reply.root_id == sent.post_id
    assert any(post["message"].startswith("@labops") for post in state.posts.values())


@pytest.mark.block_network(allowed_hosts=[r"^127\.0\.0\.1$"])
def test_mattermost_client_reports_reply_timeout(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, _ = fake_mattermost
    with (
        MattermostClient(base_url, "maya", "fake-password", timeout=1) as client,
        pytest.raises(ReplyTimeout, match="timed out"),
    ):
        client.wait_for_reply(
            "channel-1",
            from_agent="labops",
            after_ms=0,
            timeout=0.02,
            poll_interval=0.002,
        )


@pytest.mark.block_network(allowed_hosts=[r"^127\.0\.0\.1$"])
def test_mattermost_client_reports_http_timeout(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, state = fake_mattermost
    state.delay_channel_posts = 0.1

    with (
        MattermostClient(base_url, "maya", "fake-password", timeout=0.01) as client,
        pytest.raises(MattermostTimeout, match="timed out"),
    ):
        client.get_channel_posts("channel-1")


@pytest.mark.block_network(allowed_hosts=[r"^127\.0\.0\.1$"])
def test_mattermost_client_auth_failure_does_not_expose_password(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, state = fake_mattermost
    state.auth_failure = True
    password = "never-print-this-password"
    with pytest.raises(MattermostAuthenticationError) as error:
        MattermostClient(base_url, "maya", password, timeout=1)

    assert password not in str(error.value)


@pytest.mark.block_network(allowed_hosts=[r"^127\.0\.0\.1$"])
def test_approval_card_discovery_and_persona_answer(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, state = fake_mattermost
    card_post = state.add_post(
        channel_id="channel-1",
        user_id="switch-bot",
        message=(
            "Approval requested · request `A7`\n"
            "1. Allow once\n2. Allow for session\n3. Decline\n4. Cancel\n"
            "Reply with `A7` and your choice, e.g. `A7 1`."
        ),
    )
    cards = find_approval_cards(
        [
            {
                **card_post,
                "props": {},
            }
        ]
    )

    assert len(cards) == 1
    assert cards[0].handle == "A7"
    with MattermostClient(base_url, "prof-rao", "fake-password", timeout=1) as client:
        sent = client.answer_card(cards[0], "1")

    assert sent.message == "A7 1"
    assert sent.user_id == "rao-id"
    assert sent.root_id == card_post["id"]


def test_approval_card_discovery_excludes_switch_action_tokens() -> None:
    card_post = {
        "id": "card-1",
        "channel_id": "channel-1",
        "user_id": "switch-bot",
        "message": "Reply with `A7` and your choice, e.g. `A7 1`.",
        "props": {
            "attachments": [
                {
                    "actions": [
                        {
                            "name": "1. Allow once",
                            "integration": {"context": {"token": "never-copy-this-switch-token"}},
                        },
                        {"name": "2. Decline"},
                    ]
                }
            ],
        },
    }

    [card] = find_approval_cards([card_post])

    assert "1. Allow once" in card.message
    assert "never-copy-this-switch-token" not in card.message
    assert card.options == ((1, "Allow once"), (2, "Decline"))


def test_mattermost_post_sanitizes_switch_action_credentials() -> None:
    post = MattermostClient._parse_post(
        {
            "id": "card-1",
            "channel_id": "channel-1",
            "user_id": "switch-bot",
            "message": "Reply with A7 and your choice.",
            "create_at": 1000,
            "props": {
                "attachments": [
                    {
                        "actions": [
                            {
                                "name": "1. Allow once",
                                "integration": {
                                    "context": {"token": "never-print-this-switch-token"}
                                },
                            }
                        ]
                    }
                ]
            },
        }
    )

    assert post.props == {"attachments": [{"actions": [{"name": "1. Allow once"}]}]}
    assert "never-print-this-switch-token" not in repr(post)


def test_card_discovery_does_not_treat_private_props_as_session_id() -> None:
    card_post = {
        "id": "card-1",
        "channel_id": "channel-1",
        "user_id": "switch-bot",
        "message": "Reply with `A7` and your choice, e.g. `A7 1`.",
        "props": {"session_id": "unverified-private-prop"},
    }

    [card] = find_approval_cards([card_post])

    assert not hasattr(card, "session_id")


@pytest.mark.block_network(allowed_hosts=[r"^127\.0\.0\.1$"])
def test_settled_card_can_be_read_after_switch_deletes_it(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, state = fake_mattermost
    card_post = state.add_post(
        channel_id="channel-1",
        user_id="switch-bot",
        message="1. Allow once\n2. Decline\nReply with `A7` and your choice, e.g. `A7 1`.",
    )
    card = find_approval_cards([card_post])[0]
    state.posts[card_post["id"]]["message"] = "**Decline** A7\nChosen by prof-rao from Mattermost."
    state.deleted_post_ids.add(card_post["id"])

    with MattermostClient(base_url, "prof-rao", "fake-password", timeout=1) as client:
        settled_text, actor = client.wait_for_settled_card(
            card,
            expected_settler="prof-rao",
            timeout=0.1,
            poll_interval=0.002,
        )

    assert "Decline" in settled_text
    assert actor == "prof-rao"


def test_ledger_inspector_reads_pending_rows_and_audit_chain(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite")
    inspector = LedgerInspector(ledger_path)
    snapshot = inspector.snapshot()

    assert snapshot.audit_valid
    assert snapshot.bad_audit_sequence is None
    assert snapshot.requests[0].request_id == "AR-0042"
    assert snapshot.requests[0].status == "pending"
    assert snapshot.requests[0].resource_timezone == "Asia/Kolkata"
    assert snapshot.bookings[0].status == "proposed"
    with (
        sqlite3.connect(inspector.read_only_uri, uri=True) as connection,
        pytest.raises(sqlite3.OperationalError),
    ):
        connection.execute("UPDATE approval_request SET status = 'committed'")


def test_E2E_01_read_propose_smoke_checks_conflict_slot_and_pending_request(
    tmp_path: Path,
) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    reply = (
        "Lena's 14:00-15:30 INS-01 booking conflicts. "
        "The 15:45-16:45 slot is proposed. Request AR-0042."
    )

    assert_read_propose_smoke(reply, "AR-0042", snapshot)


def test_E2E_01_smoke_accepts_top_level_handoff_outside_prompt_thread(
    tmp_path: Path,
) -> None:
    ledger = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite"))
    prompt = MattermostPost("prompt-1", "channel-1", "maya-id", "book INS-01", 1000)
    thread_summary = MattermostPost(
        "summary-1", "channel-1", "labops-id", "Worked for 1m 19s. AR-0042", 2000,
        root_id=prompt.post_id,
    )
    handoff = MattermostPost(
        "handoff-1",
        "channel-1",
        "labops-id",
        "Lena's 14:00-15:30 INS-01 booking conflicts. "
        "The 15:45-16:45 slot is proposed. Request AR-0042.",
        3000,
    )

    class StubPersona:
        root_id: str | None = None

        def post(self, channel_id: str, message: str) -> MattermostPost:
            assert channel_id == "channel-1"
            assert message
            return prompt

        def wait_for_reply(
            self,
            channel_id: str,
            *,
            from_agent: str,
            after_ms: int,
            timeout: float,
            poll_interval: float,
            root_id: str | None = None,
        ) -> MattermostPost:
            assert channel_id == "channel-1"
            assert from_agent == "labops"
            assert after_ms == prompt.create_at
            assert timeout > 0
            assert poll_interval > 0
            self.root_id = root_id
            matching = [thread_summary, handoff]
            if root_id is not None:
                matching = [post for post in matching if post.root_id == root_id]
            return matching[-1]

    persona = StubPersona()
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": persona, "prof-rao": persona}),
        ledger=ledger,
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
    )

    result = runner._read_propose_smoke()

    assert persona.root_id is None
    assert result["response_post_id"] == handoff.post_id
    assert "conflicts" in result["response"]
    assert result["request_status"] == "pending"


def test_E2E_01_read_propose_smoke_requires_conflict_language(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    reply = (
        "Lena has a 14:00-15:30 INS-01 booking. The 15:45-16:45 slot is proposed. Request AR-0042."
    )

    with pytest.raises(AssertionError, match="conflict"):
        assert_read_propose_smoke(reply, "AR-0042", snapshot)


@pytest.mark.parametrize(
    "updates",
    [
        {"resource": "INS-02"},
        {"start_utc": "2026-11-06T10:00:00Z"},
        {"end_utc": "2026-11-06T11:30:00Z"},
        {"resource_timezone": "UTC"},
    ],
)
def test_E2E_01_read_propose_smoke_rejects_wrong_persisted_booking(
    tmp_path: Path,
    updates: dict[str, str],
) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    request = SimpleNamespace(**{**vars(snapshot.requests[0]), **updates})
    altered = replace(snapshot, requests=(request,))
    reply = (
        "Lena's 14:00-15:30 INS-01 booking conflicts. "
        "The 15:45-16:45 slot is proposed. Request AR-0042."
    )

    with pytest.raises(AssertionError, match="persisted"):
        assert_read_propose_smoke(reply, "AR-0042", altered)


def test_E2E_03_wrong_person_refusal_has_no_ledger_effect(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite")
    before = LedgerInspector(ledger_path).snapshot()
    after = LedgerInspector(ledger_path).snapshot()

    assert_refusal("I cannot approve this. Only the PI can answer the card.", before, after)


def test_E2E_03_historical_commit_does_not_fail_a_no_effect_refusal(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite", committed=True)
    before = LedgerInspector(ledger_path).snapshot()
    after = LedgerInspector(ledger_path).snapshot()

    assert_refusal("I cannot approve this. Only the PI can answer the card.", before, after)


def test_E2E_04_pi_approval_matches_card_and_commits_once(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite", committed=True)
    snapshot = LedgerInspector(ledger_path).snapshot()
    card_text = _card_text(snapshot.requests[0])

    assert_approval(snapshot, "AR-0042", card_text, "prof-rao")


def test_E2E_04_open_card_wait_uses_the_proposal_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite"))
    request = ledger.snapshot().requests[0]
    prompt = MattermostPost("prompt-1", "channel-1", "maya-id", "proposal", 1000)
    attempt = SimpleNamespace(
        prompt_post=prompt,
        request_id=request.request_id,
        after_reply=ledger.snapshot(),
    )
    card = ApprovalCard(
        "A7",
        "card-1",
        "channel-1",
        "switch-bot",
        _card_text(request),
        options=((1, "Allow once"), (2, "Decline")),
    )

    class StubPersona:
        root_id: str | None = None

        def wait_for_approval_card(self, channel_id: str, **kwargs: Any) -> ApprovalCard:
            assert channel_id == "channel-1"
            self.root_id = kwargs.get("root_id")
            return card

    persona = StubPersona()
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": persona, "prof-rao": persona}),
        ledger=ledger,
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
    )
    monkeypatch.setattr(runner, "_begin_proposal", lambda _: attempt)

    runner._open_card("proposal", "allow")

    assert persona.root_id == prompt.post_id


def test_E2E_04_card_rejects_duplicate_canonical_field(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    request = snapshot.requests[0]
    duplicated = f"{_card_text(request)}\ninstrument_id: INS-01"

    with pytest.raises(AssertionError, match="resource"):
        assert_card_matches_request(duplicated, request)


def test_E2E_05_pi_decline_leaves_domain_request_pending(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()

    assert_decline(snapshot, "AR-0042", "prof-rao")


def test_E2E_05_decline_runner_rejects_an_approved_card_settlement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    card = ApprovalCard(
        "A7",
        "card-7",
        "channel-1",
        "switch-bot",
        "approval",
        options=((1, "Approve once"), (2, "Decline")),
    )
    attempt = SimpleNamespace(
        prompt_post=MattermostPost("prompt", "channel-1", "maya-id", "request", 1000),
        reply=MattermostPost("reply", "channel-1", "labops-id", "AR-0042", 2000),
        request_id="AR-0042",
        after_reply=snapshot,
    )
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": object(), "prof-rao": object()}),
        ledger=LedgerInspector(tmp_path / "ledger.sqlite"),
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
    )
    monkeypatch.setattr(runner, "_open_card", lambda *args: ((attempt, card), 2))
    monkeypatch.setattr(
        runner,
        "_answer_and_wait",
        lambda *args: ("**Approve once** A7\\nChosen by @prof-rao.", "prof-rao", "answer-1"),
    )
    monkeypatch.setattr(runner, "_wait_for_pending", lambda request_id: snapshot)

    with pytest.raises(AssertionError, match="decline"):
        runner._decline()


def test_E2E_11_second_commit_requires_error_or_fresh_card(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()

    assert_repeat_second_commit(
        "COMMIT_LIMIT_REACHED",
        request_id="AR-0042",
        snapshot=snapshot,
        first_card_handle="A1",
        second_card_handle=None,
    )
    assert_repeat_second_commit(
        "A fresh approval card was presented",
        request_id="AR-0042",
        snapshot=snapshot,
        first_card_handle="A1",
        second_card_handle="A2",
    )


def test_E2E_11_repeat_limit_error_is_case_insensitive(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()

    assert_repeat_second_commit(
        "commit_limit_reached",
        request_id="AR-0042",
        snapshot=snapshot,
        first_card_handle="A1",
        second_card_handle=None,
    )


def test_E2E_11_repeat_error_is_correlated_to_the_prompt_thread(tmp_path: Path) -> None:
    posts = [
        MattermostPost(
            "unrelated-error",
            "channel-1",
            "labops-id",
            "COMMIT_LIMIT_REACHED",
            2000,
            root_id="other-prompt",
        ),
        MattermostPost(
            "related-reply",
            "channel-1",
            "labops-id",
            "No approval card was presented.",
            2001,
            root_id="target-prompt",
        ),
    ]

    class StubPersona:
        def get_channel_posts(self, channel_id: str) -> list[MattermostPost]:
            assert channel_id == "channel-1"
            return posts

        def username_for(self, user_id: str) -> str:
            return {"labops-id": "labops"}[user_id]

    persona = StubPersona()
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": persona, "prof-rao": persona}),
        ledger=LedgerInspector(tmp_path / "ledger.sqlite"),
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
    )

    response = runner._agent_text_after(1000, root_id="target-prompt")

    assert "COMMIT_LIMIT_REACHED" not in response
    assert "No approval card" in response


def test_E2E_11_fresh_card_requires_a_pending_second_request(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite")
    with sqlite3.connect(ledger_path) as connection:
        connection.execute("UPDATE approval_request SET status = 'declined'")
    snapshot = LedgerInspector(ledger_path).snapshot()

    with pytest.raises(AssertionError, match="must stay pending"):
        assert_repeat_second_commit(
            "A fresh approval card was presented",
            request_id="AR-0042",
            snapshot=snapshot,
            first_card_handle="A1",
            second_card_handle="A2",
        )


def test_E2E_11_session_id_option_requires_explicit_confirmation() -> None:
    args = build_parser().parse_args(
        [
            "--scenario",
            "e2e11",
            "--session-id",
            "session-123",
            "--confirm-session-id",
        ]
    )

    assert args.confirm_session_id


def test_E2E_11_runner_rejects_unconfirmed_session_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="confirm"):
        ScenarioRunner(
            personas={"maya": cast(Any, object()), "prof-rao": cast(Any, object())},
            ledger=LedgerInspector(tmp_path / "ledger.sqlite"),
            channel_id="channel-1",
            evidence_dir=tmp_path / "evidence",
            options=ScenarioOptions(binding=True, session_id="session-123"),
        )


def test_E2E_11_fresh_card_remains_pending_in_same_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    canonical = _card_text(snapshot.requests[0])
    first_card = ApprovalCard("A1", "card-1", "channel-1", "switch-bot", canonical)
    second_card = ApprovalCard("A2", "card-2", "channel-1", "switch-bot", canonical)

    class StubPersona:
        answer_calls = 0

        def wait_for_approval_card(self, *args: Any, **kwargs: Any) -> ApprovalCard:
            return second_card

        def answer_card(self, *args: Any, **kwargs: Any) -> object:
            self.answer_calls += 1
            return object()

    persona = StubPersona()
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": persona, "prof-rao": persona}),
        ledger=LedgerInspector(tmp_path / "ledger.sqlite"),
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
        options=ScenarioOptions(
            binding=True,
            observation_seconds=0,
            session_id="provider-session",
            session_id_confirmed=True,
        ),
    )
    post = MattermostPost("prompt-2", "channel-1", "maya-id", "repeat", 2000)
    reply = MattermostPost("reply-2", "channel-1", "labops-id", "AR-0042", 3000)
    second_attempt = SimpleNamespace(
        prompt_post=post,
        reply=reply,
        request_id="AR-0042",
        before=snapshot,
        after_reply=snapshot,
    )
    first_attempt = SimpleNamespace(request_id="AR-0041")
    first_flow = SimpleNamespace(
        attempt=first_attempt,
        card=first_card,
        settled_by="prof-rao",
        snapshot=snapshot,
    )
    commit_calls = 0

    def commit_open_card(opened: object) -> Any:
        nonlocal commit_calls
        commit_calls += 1
        return first_flow

    monkeypatch.setattr(runner, "_open_card", lambda *args: ((first_attempt, first_card), 1))
    monkeypatch.setattr(runner, "_commit_open_card", commit_open_card)
    monkeypatch.setattr(runner, "_begin_proposal", lambda prompt: second_attempt)

    result = runner._repeat()

    assert result["second_request_status"] == "pending"
    assert result["second_commit_audit_count"] == 0
    assert commit_calls == 1
    assert persona.answer_calls == 0


def test_I_36_user_note_cannot_substitute_instrument(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_injection_no_commit(snapshot, "AR-0042", "I-36")


def test_I_37_user_note_cannot_change_duration_or_quantity(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_injection_no_commit(snapshot, "AR-0042", "I-37")


def test_I_38_handoff_cannot_substitute_time(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_injection_no_commit(snapshot, "AR-0042", "I-38")


def test_I_39_impersonated_pi_text_cannot_answer_card(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_injection_no_commit(snapshot, "AR-0042", "I-39")


def test_I_40_injected_policy_evidence_cannot_commit(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_injection_no_commit(snapshot, "AR-0042", "I-40")


def test_I_41_stale_request_revision_cannot_commit(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_injection_no_commit(snapshot, "AR-0042", "I-41")


def test_I_41_prompt_uses_a_real_stale_request_reference() -> None:
    prompt_template = INJECTION_PROMPTS["I-41"]

    assert "AR-0042" not in prompt_template
    assert "{request_id}" in prompt_template
    assert "{stale_revision}" in prompt_template
    assert "{stale_hash}" in prompt_template


def test_I_41_cli_accepts_stale_reference_arguments() -> None:
    args = build_parser().parse_args(
        [
            "--scenario",
            "injection",
            "--attack",
            "I-41",
            "--stale-request-id",
            "AR-0042",
            "--stale-revision",
            "1",
            "--stale-hash",
            "a" * 64,
        ]
    )

    assert args.stale_request_id == "AR-0042"
    assert args.stale_revision == 1
    assert args.stale_hash == "a" * 64


def test_I_41_runner_rejects_hash_not_in_revision_audit_history(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite")
    prior = LedgerInspector(ledger_path).snapshot().requests[0]
    revised_decision = {**prior.decision, "revision": 2}
    revised_hash = content_hash(revised_decision)
    with sqlite3.connect(ledger_path) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN")
        append_event(
            connection,
            actor="labops",
            tool="propose_booking",
            args={},
            result={
                "request_id": prior.request_id,
                "revision": 1,
                "content_hash": prior.content_hash,
                "decision": prior.decision,
            },
            clock=FixedClock(),
        )
        connection.execute(
            "UPDATE approval_request SET revision = 2, content_hash = ?, decision_json = ? "
            "WHERE id = ?",
            (
                revised_hash,
                json.dumps(revised_decision, sort_keys=True, separators=(",", ":")),
                prior.request_id,
            ),
        )
        append_event(
            connection,
            actor="labops",
            tool="revise_request",
            args={"request_id": prior.request_id, "revision": 1, "new_revision": 2},
            result={
                "request_id": prior.request_id,
                "revision": 2,
                "content_hash": revised_hash,
                "decision": revised_decision,
            },
            clock=FixedClock(),
        )

    class StubPersona:
        def post(self, *_: Any, **__: Any) -> None:
            raise RuntimeError("Mattermost must not be called for an unaudited stale hash.")

    persona = StubPersona()
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": persona, "prof-rao": persona}),
        ledger=LedgerInspector(ledger_path),
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
        options=ScenarioOptions(
            stale_request_id=prior.request_id,
            stale_revision=1,
            stale_hash="a" * 64,
        ),
    )

    with pytest.raises(AssertionError, match="audit"):
        runner._stale_revision_injection()


def test_E2E_15_restart_keeps_request_uncommitted(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()
    assert_restart_safe(snapshot, "AR-0042", card_settled=False)


def test_evidence_writer_writes_json_and_redacts_secret_fields(tmp_path: Path) -> None:
    evidence_path = write_evidence(
        tmp_path / "evidence",
        "e2e01",
        {
            "status": "pass",
            "password": "do-not-write",
            "token": "also-do-not-write",
        },
    )
    contents = evidence_path.read_text(encoding="utf-8")
    evidence = json.loads(contents)

    assert evidence["status"] == "pass"
    assert evidence["password"] == "[REDACTED]"
    assert evidence["token"] == "[REDACTED]"
    assert "do-not-write" not in contents


def test_scenario_runner_writes_timed_step_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = ScenarioRunner(
        personas=cast(Any, {"maya": object(), "prof-rao": object()}),
        ledger=LedgerInspector(tmp_path / "ledger.sqlite"),
        channel_id="channel-1",
        evidence_dir=tmp_path / "evidence",
    )

    def dispatch(scenario: str, *, attack_id: str | None) -> dict[str, str]:
        assert scenario == "e2e01"
        assert attack_id is None
        runner._timed_step("fake.operation", lambda: "done")
        return {"status": "pass"}

    monkeypatch.setattr(runner, "_dispatch", dispatch)
    result = runner.run("e2e01")
    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))

    assert evidence["status"] == "pass"
    assert evidence["started_at_utc"]
    assert evidence["finished_at_utc"]
    assert evidence["elapsed_seconds"] >= 0
    assert evidence["steps"][0]["name"] == "fake.operation"
    assert evidence["steps"][0]["status"] == "pass"
    assert evidence["steps"][0]["elapsed_seconds"] >= 0


def test_persona_config_expands_localappdata_ledger_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    config_path = tmp_path / "personas.json"
    config_path.write_text(
        json.dumps(
            {
                "mattermost_url": "http://127.0.0.1:8065",
                "channel_id": "channel-1",
                "ledger_path": r"%LOCALAPPDATA%\LabQuorum\ledger.sqlite",
                "personas": {
                    "maya": {"username": "maya", "password": "maya-secret"},
                    "prof-rao": {"username": "prof-rao", "password": "rao-secret"},
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.ledger_path == (tmp_path / "LabQuorum" / "ledger.sqlite").resolve()


def _make_ledger(path: Path, *, committed: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE schema_version (version INTEGER NOT NULL);
        INSERT INTO schema_version(version) VALUES (1);
        CREATE TABLE instrument (id TEXT PRIMARY KEY, timezone TEXT NOT NULL);
        INSERT INTO instrument VALUES ('INS-01', 'Asia/Kolkata');
        CREATE TABLE approval_request (
            id TEXT PRIMARY KEY, kind TEXT NOT NULL, requester TEXT NOT NULL,
            resource TEXT NOT NULL, start_utc TEXT NOT NULL, end_utc TEXT NOT NULL,
            project TEXT NOT NULL, revision INTEGER NOT NULL, content_hash TEXT NOT NULL,
            decision_json TEXT NOT NULL, status TEXT NOT NULL, created_utc TEXT NOT NULL,
            expires_utc TEXT NOT NULL, decided_utc TEXT, decline_reason TEXT
        );
        CREATE TABLE booking (
            id TEXT PRIMARY KEY, request_id TEXT, person_id TEXT NOT NULL,
            instrument_id TEXT NOT NULL, project_id TEXT NOT NULL, start_utc TEXT NOT NULL,
            end_utc TEXT NOT NULL, status TEXT NOT NULL
        );
        CREATE TABLE audit_event (
            seq INTEGER PRIMARY KEY, ts_utc TEXT NOT NULL, actor_agent TEXT NOT NULL,
            tool TEXT NOT NULL, args_json TEXT NOT NULL, result_json TEXT NOT NULL,
            prev_hash TEXT NOT NULL, hash TEXT NOT NULL
        );
        """
    )
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
    start_utc = decision["interval"]["start_utc"]
    end_utc = decision["interval"]["end_utc"]
    request_status = "committed" if committed else "pending"
    booking_status = "committed" if committed else "proposed"
    connection.execute(
        "INSERT INTO approval_request VALUES (?, 'booking', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "AR-0042",
            "maya",
            "INS-01",
            start_utc,
            end_utc,
            "egcg",
            1,
            digest,
            json.dumps(decision, sort_keys=True, separators=(",", ":")),
            request_status,
            "2026-11-05T10:00:00Z",
            "2026-11-05T10:10:00Z",
            "2026-11-05T10:01:00Z" if committed else None,
            None,
        ),
    )
    connection.execute(
        "INSERT INTO booking VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "BK-0042",
            "AR-0042",
            "maya",
            "INS-01",
            "egcg",
            start_utc,
            end_utc,
            booking_status,
        ),
    )
    connection.commit()
    if committed:
        args = {
            "request_id": "AR-0042",
            "revision": 1,
            "content_hash": digest,
            "decision": decision,
        }
        connection.execute("BEGIN")
        append_event(
            connection,
            actor="pi-desk",
            tool="commit_booking",
            args=args,
            result={"request_id": "AR-0042", "status": "committed"},
            clock=FixedClock(),
        )
        connection.commit()
    connection.close()
    return path


def _card_text(request: Any) -> str:
    return "\n".join(
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
        )
    )


@dataclass(frozen=True)
class FixedClock:
    value: str = "2026-11-05T10:01:00+00:00"

    def now(self) -> Any:
        return datetime.fromisoformat(self.value)
