"""Discover and inspect Switch session activity cards in Mattermost posts."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from labquorum.e2e.mattermost import MattermostPost

_CARD_INSTRUCTION = re.compile(r"\breply with\s+[`*_~]*([Aa][1-9][0-9]*)", re.IGNORECASE)
_OPTION_LINE = re.compile(r"^\s*(\d+)[.)]\s+(.+?)\s*$")


@dataclass(frozen=True)
class ApprovalCard:
    handle: str
    post_id: str
    channel_id: str
    user_id: str
    message: str
    root_id: str | None = None
    options: tuple[tuple[int, str], ...] = ()

    def option_number(self, label: str) -> int:
        """Return the displayed number for an option label, case-insensitively."""
        normalized = label.strip().casefold()
        for number, offered in self.options:
            if offered.strip().casefold() == normalized:
                return number
        matches = [
            number for number, offered in self.options if normalized in offered.strip().casefold()
        ]
        if len(matches) == 1:
            return matches[0]
        raise ValueError("Approval card does not expose one unambiguous matching option.")


def find_approval_cards(
    posts: Iterable[MattermostPost | Mapping[str, Any]],
) -> list[ApprovalCard]:
    """Find open approval cards by their source-backed typed-answer instruction."""
    cards: list[ApprovalCard] = []
    for post in posts:
        post_id = _post_value(post, "post_id", "id")
        channel_id = _post_value(post, "channel_id")
        user_id = _post_value(post, "user_id")
        message = _post_message(post)
        match = _CARD_INSTRUCTION.search(message)
        if not post_id or not channel_id or not user_id or match is None:
            continue
        handle = match.group(1).upper()
        options = tuple(
            (int(option_match.group(1)), _strip_markup(option_match.group(2)))
            for line in message.splitlines()
            if (option_match := _OPTION_LINE.match(line)) is not None
        )
        root_id = _post_value(post, "root_id") or None
        cards.append(
            ApprovalCard(
                handle=handle,
                post_id=post_id,
                channel_id=channel_id,
                user_id=user_id,
                message=message,
                root_id=root_id,
                options=options,
            )
        )
    return cards


def settled_by(message: str) -> str | None:
    """Read the named actor from Switch's settled card rendering."""
    match = re.search(
        r"\b(?:Chosen|Answered|Decided)\s+by\s+@?([A-Za-z0-9_.-]+)",
        message,
        re.IGNORECASE,
    )
    return match.group(1).casefold() if match else None


def post_text(post: MattermostPost | Mapping[str, Any]) -> str:
    """Return visible post text and visible action labels, without action credentials."""
    return _post_message(post)


def _post_message(post: MattermostPost | Mapping[str, Any]) -> str:
    """Read only visible message and button text; props also contain action tokens."""
    chunks = [
        _post_value(post, "message"),
        *visible_action_names(_post_value_object(post, "props")),
    ]
    return "\n".join(chunk for chunk in chunks if chunk)


def _post_value(post: MattermostPost | Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = post.get(key) if isinstance(post, Mapping) else getattr(post, key, None)
        if value is not None and value != "":
            return str(value)
    return ""


def _post_value_object(post: MattermostPost | Mapping[str, Any], key: str) -> Any:
    if isinstance(post, Mapping):
        return post.get(key)
    return getattr(post, key, None)


def visible_action_names(props: Any) -> list[str]:
    """Read Mattermost's user-visible action names and ignore integration context."""
    if not isinstance(props, Mapping):
        return []
    props_mapping = cast(Mapping[str, Any], props)
    attachments = props_mapping.get("attachments")
    if not isinstance(attachments, list):
        return []
    names: list[str] = []
    for raw_attachment in cast(list[Any], attachments):
        if not isinstance(raw_attachment, Mapping):
            continue
        attachment = cast(Mapping[str, Any], raw_attachment)
        actions = attachment.get("actions")
        if not isinstance(actions, list):
            continue
        for raw_action in cast(list[Any], actions):
            if not isinstance(raw_action, Mapping):
                continue
            action = cast(Mapping[str, Any], raw_action)
            name = action.get("name")
            if isinstance(name, str) and name:
                names.append(name)
    return names


def _strip_markup(value: str) -> str:
    return value.strip().strip("*_`~ ").rstrip(". ")
