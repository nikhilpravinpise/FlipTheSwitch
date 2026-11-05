"""Small authenticated Mattermost REST v4 client for the P4 harness."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import quote, urljoin

import httpx

from labquorum.e2e.cards import (
    ApprovalCard,
    find_approval_cards,
    post_text,
    settled_by,
    visible_action_names,
)


class MattermostError(RuntimeError):
    """Base exception for sanitized Mattermost API failures."""


class MattermostAuthenticationError(MattermostError):
    """Raised when a persona cannot log in."""


class ReplyTimeout(MattermostError):
    """Raised when no matching agent reply arrives before the timeout."""


class MattermostTimeout(MattermostError):
    """Raised when a REST request exceeds its configured timeout."""


@dataclass(frozen=True)
class MattermostPost:
    post_id: str
    channel_id: str
    user_id: str
    message: str
    create_at: int
    root_id: str | None = None
    props: dict[str, Any] | None = None


class MattermostClient:
    """Log in one persona and keep its bearer token in memory only."""

    def __init__(
        self,
        base_url: str,
        login_id: str,
        password: str,
        *,
        timeout: float = 10.0,
    ) -> None:
        if timeout <= 0:
            raise ValueError("Mattermost timeout must be positive.")
        self._base_url = base_url.rstrip("/")
        api_root = f"{base_url.rstrip('/')}/api/v4"
        self._http = httpx.Client(
            base_url=api_root,
            timeout=httpx.Timeout(timeout),
            follow_redirects=False,
            headers={"Accept": "application/json"},
        )
        self._usernames: dict[str, str] = {}
        try:
            response = self._request(
                "POST",
                "/users/login",
                json={"login_id": login_id, "password": password},
                login=True,
            )
            token = response.headers.get("Token")
            body = self._json_object(response)
            user_id = body.get("id")
            username = body.get("username")
            if not isinstance(token, str) or not token or not isinstance(user_id, str):
                raise MattermostAuthenticationError(
                    "Mattermost login did not return a usable persona session."
                )
            self._session_token = token
            self.user_id = user_id
            self.username = username if isinstance(username, str) else login_id
            self._usernames[user_id] = self.username
            self._http.headers["Authorization"] = f"Bearer {token}"
        except BaseException:
            self._http.close()
            raise

    def __enter__(self) -> MattermostClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    @property
    def session_token(self) -> str:
        """Return the in-memory login token for an authenticated browser cookie."""
        return self._session_token

    def room_url(self, channel_id: str) -> str:
        """Resolve a channel ID to Mattermost's team and channel deep link."""
        encoded_channel_id = quote(channel_id, safe="")
        channel = self._json_object(self._request("GET", f"/channels/{encoded_channel_id}"))
        team_id = channel.get("team_id")
        channel_name = channel.get("name")
        if not isinstance(team_id, str) or not team_id:
            raise MattermostError("Configured Mattermost room is not attached to a team.")
        if not isinstance(channel_name, str) or not channel_name:
            raise MattermostError("Mattermost room lookup returned no channel name.")
        encoded_team_id = quote(team_id, safe="")
        team = self._json_object(self._request("GET", f"/teams/{encoded_team_id}"))
        team_name = team.get("name")
        if not isinstance(team_name, str) or not team_name:
            raise MattermostError("Mattermost team lookup returned no team name.")
        path = f"{quote(team_name, safe='')}/channels/{quote(channel_name, safe='')}"
        return urljoin(f"{self._base_url}/", path)

    def post(
        self,
        channel_id: str,
        message: str,
        *,
        root_id: str | None = None,
    ) -> MattermostPost:
        payload: dict[str, str] = {"channel_id": channel_id, "message": message}
        if root_id:
            payload["root_id"] = root_id
        response = self._request("POST", "/posts", json=payload)
        return self._parse_post(self._json_object(response))

    def get_channel_posts(
        self,
        channel_id: str,
        *,
        include_deleted: bool = False,
    ) -> list[MattermostPost]:
        params: dict[str, str | int] = {"per_page": 100}
        if include_deleted:
            params["include_deleted"] = "true"
        response = self._request("GET", f"/channels/{channel_id}/posts", params=params)
        body = self._json_object(response)
        raw_posts = body.get("posts")
        if not isinstance(raw_posts, dict):
            raise MattermostError("Mattermost channel posts response is malformed.")
        posts_by_id = cast(dict[str, Any], raw_posts)
        parsed = [
            self._parse_post(cast(dict[str, Any], post))
            for post in posts_by_id.values()
            if isinstance(post, dict)
        ]
        return sorted(parsed, key=lambda post: post.create_at)

    def wait_for_post(  # noqa: PLR0913
        self,
        channel_id: str,
        *,
        from_user: str,
        message: str,
        after_ms: int,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> MattermostPost:
        """Poll for an exact message from a persona after a recorded UI send."""
        if timeout < 0:
            raise ValueError("Post timeout cannot be negative.")
        if poll_interval <= 0:
            raise ValueError("Post poll interval must be positive.")
        deadline = time.monotonic() + timeout
        while True:
            posts = self.get_channel_posts(channel_id)
            for post in reversed(posts):
                if post.create_at < after_ms or post.message != message:
                    continue
                if self._username_for(post.user_id).casefold() == from_user.casefold():
                    return post
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReplyTimeout(f"Post from {from_user} timed out after {timeout:g} seconds.")
            time.sleep(min(max(poll_interval, 0.001), remaining, 2.0))

    def username_for(self, user_id: str) -> str:
        """Resolve a post author with the Mattermost user lookup endpoint."""
        return self._username_for(user_id)

    def wait_for_reply(  # noqa: PLR0913
        self,
        channel_id: str,
        *,
        from_agent: str,
        after_ms: int,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
        root_id: str | None = None,
    ) -> MattermostPost:
        """Poll channel posts until a named agent replies or the deadline passes."""
        if timeout < 0:
            raise ValueError("Reply timeout cannot be negative.")
        deadline = time.monotonic() + timeout
        while True:
            posts = self.get_channel_posts(channel_id)
            for post in reversed(posts):
                if post.create_at < after_ms:
                    continue
                if root_id and root_id not in (post.root_id, post.post_id):
                    continue
                if self._username_for(post.user_id).casefold() == from_agent.casefold():
                    return post
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReplyTimeout(f"Reply from {from_agent} timed out after {timeout:g} seconds.")
            time.sleep(min(max(poll_interval, 0.001), remaining))

    def wait_for_approval_card(
        self,
        channel_id: str,
        *,
        after_ms: int,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
        root_id: str | None = None,
    ) -> ApprovalCard:
        """Poll posts for a Switch card with its typed-answer instruction."""
        deadline = time.monotonic() + timeout
        while True:
            posts = self.get_channel_posts(channel_id)
            cards = find_approval_cards(
                post
                for post in posts
                if post.create_at >= after_ms
                and (root_id is None or root_id in (post.root_id, post.post_id))
            )
            if cards:
                return cards[-1]
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReplyTimeout(f"No approval card arrived within {timeout:g} seconds.")
            time.sleep(min(max(poll_interval, 0.001), remaining))

    def answer_card(self, card: ApprovalCard, choice: str | int) -> MattermostPost:
        """Answer a Switch bridge card using its displayed A<n> text grammar."""
        value = str(choice).strip()
        if not value:
            raise ValueError("An approval card choice is required.")
        root_id = card.root_id or card.post_id
        return self.post(card.channel_id, f"{card.handle} {value}", root_id=root_id)

    def wait_for_settled_card(
        self,
        card: ApprovalCard,
        *,
        expected_settler: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> tuple[str, str | None]:
        """Return the updated card text and actor once Switch names its settler."""
        deadline = time.monotonic() + timeout
        while True:
            posts = self.get_channel_posts(card.channel_id, include_deleted=True)
            updated = next((post for post in posts if post.post_id == card.post_id), None)
            if updated is not None:
                message = post_text(updated)
                actor = settled_by(message)
                if actor is not None:
                    if actor != expected_settler.casefold():
                        raise MattermostError(
                            f"Approval card was settled by {actor}, expected {expected_settler}."
                        )
                    return message, actor
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReplyTimeout(f"Approval card was not shown as settled by {expected_settler}.")
            time.sleep(min(max(poll_interval, 0.001), remaining))

    def _username_for(self, user_id: str) -> str:
        cached = self._usernames.get(user_id)
        if cached is not None:
            return cached
        response = self._request("GET", f"/users/{user_id}")
        body = self._json_object(response)
        username = body.get("username")
        if not isinstance(username, str) or not username:
            raise MattermostError("Mattermost user lookup returned no username.")
        self._usernames[user_id] = username
        return username

    def _request(
        self,
        method: str,
        path: str,
        *,
        login: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        try:
            response = self._http.request(method, path, **kwargs)
        except httpx.TimeoutException as exc:
            raise MattermostTimeout("Mattermost API request timed out.") from exc
        except httpx.HTTPError as exc:
            raise MattermostError("Mattermost API request failed.") from exc
        if login and response.status_code in (401, 403):
            raise MattermostAuthenticationError(
                f"Mattermost persona login failed (HTTP {response.status_code})."
            )
        if response.is_error:
            raise MattermostError(f"Mattermost API request failed (HTTP {response.status_code}).")
        return response

    @staticmethod
    def _json_object(response: httpx.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError as exc:
            raise MattermostError("Mattermost API returned invalid JSON.") from exc
        if not isinstance(body, dict):
            raise MattermostError("Mattermost API returned an unexpected JSON shape.")
        return cast(dict[str, Any], body)

    @staticmethod
    def _parse_post(value: dict[str, Any]) -> MattermostPost:
        post_id = value.get("id")
        channel_id = value.get("channel_id")
        user_id = value.get("user_id")
        message = value.get("message")
        create_at = value.get("create_at")
        if not isinstance(post_id, str) or not post_id:
            raise MattermostError("Mattermost post response is missing its identity fields.")
        if not isinstance(channel_id, str) or not channel_id:
            raise MattermostError("Mattermost post response is missing its identity fields.")
        if not isinstance(user_id, str) or not user_id:
            raise MattermostError("Mattermost post response is missing its identity fields.")
        if not isinstance(message, str) or not isinstance(create_at, int):
            raise MattermostError("Mattermost post response is missing its message or timestamp.")
        root = value.get("root_id")
        action_names = visible_action_names(value.get("props"))
        safe_props = (
            {"attachments": [{"actions": [{"name": name} for name in action_names]}]}
            if action_names
            else {}
        )
        return MattermostPost(
            post_id=post_id,
            channel_id=channel_id,
            user_id=user_id,
            message=message,
            create_at=create_at,
            root_id=root if isinstance(root, str) and root else None,
            props=safe_props,
        )
