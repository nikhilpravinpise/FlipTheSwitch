from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from labquorum.domain.canonical import content_hash
from labquorum.e2e.config import load_config
from labquorum.e2e.assertions import (
    assert_approval,
    assert_decline,
    assert_injection_no_commit,
    assert_read_propose_smoke,
    assert_refusal,
    assert_repeat_second_commit,
    assert_restart_safe,
)
from labquorum.e2e.cards import find_approval_cards
from labquorum.e2e.evidence import write_evidence
from labquorum.e2e.ledger import LedgerInspector
from labquorum.e2e.mattermost import (
    MattermostAuthenticationError,
    MattermostClient,
    ReplyTimeout,
)
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
            self.wfile.write(body)

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
            if self.path.startswith("/api/v4/channels/") and self.path.endswith(
                "/posts?per_page=100"
            ):
                if state.delay_channel_posts:
                    time.sleep(state.delay_channel_posts)
                channel_id = self.path.split("/")[4]
                posts = {
                    post_id: post
                    for post_id, post in state.posts.items()
                    if post["channel_id"] == channel_id
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


def test_mattermost_client_auth_failure_does_not_expose_password(
    fake_mattermost: tuple[str, FakeMattermostState],
) -> None:
    base_url, state = fake_mattermost
    state.auth_failure = True
    password = "never-print-this-password"
    with pytest.raises(MattermostAuthenticationError) as error:
        MattermostClient(base_url, "maya", password, timeout=1)

    assert password not in str(error.value)


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


def test_ledger_inspector_reads_pending_rows_and_audit_chain(tmp_path: Path) -> None:
    ledger_path = _make_ledger(tmp_path / "ledger.sqlite")
    inspector = LedgerInspector(ledger_path)
    snapshot = inspector.snapshot()

    assert snapshot.audit_valid
    assert snapshot.bad_audit_sequence is None
    assert snapshot.requests[0].request_id == "AR-0042"
    assert snapshot.requests[0].status == "pending"
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


def test_E2E_05_pi_decline_leaves_domain_request_pending(tmp_path: Path) -> None:
    snapshot = LedgerInspector(_make_ledger(tmp_path / "ledger.sqlite")).snapshot()

    assert_decline(snapshot, "AR-0042", "prof-rao")


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
        "start_utc": "2026-11-06T10:15:00Z",
        "end_utc": "2026-11-06T11:15:00Z",
        "project": "egcg",
        "request_id": "AR-0042",
        "revision": 1,
    }
    digest = content_hash(decision)
    request_status = "committed" if committed else "pending"
    booking_status = "committed" if committed else "proposed"
    connection.execute(
        "INSERT INTO approval_request VALUES (?, 'booking', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "AR-0042",
            "maya",
            "INS-01",
            decision["start_utc"],
            decision["end_utc"],
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
            decision["start_utc"],
            decision["end_utc"],
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
    values = json.dumps(request.decision, sort_keys=True)
    return f"Decision: {values}\ncontent_hash: {request.content_hash}"


@dataclass(frozen=True)
class FixedClock:
    value: str = "2026-11-05T10:01:00+00:00"

    def now(self) -> Any:
        return datetime.fromisoformat(self.value)
