"""P1 pure domain behavior, named after the planning catalogue."""

from __future__ import annotations

from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from labquorum.domain.approvals import RequestStatus, transition_status
from labquorum.domain.booking import (
    Booking,
    InstrumentPolicy,
    Interval,
    Training,
    check_booking,
    intervals_conflict,
    nearest_free_slot,
)
from labquorum.domain.canonical import canonical_json, content_hash
from labquorum.domain.errors import ErrorCode, LabQuorumError, error_codes_markdown
from labquorum.domain.guards import RateGuard
from labquorum.domain.policy import PolicyCheck, policy_check
from labquorum.domain.timeutil import FixedClock, SystemClock, format_interval, parse_iso_datetime
from tests.conftest import ANCHOR_DATE, BASE_NOW, at, make_policy


def _training(start_hour: int = 8, expiry_hour: int = 20) -> Training:
    return Training(
        granted_at=at(ANCHOR_DATE, start_hour),
        expires_at=at(ANCHOR_DATE, expiry_hour),
    )


def test_U_B01_non_overlapping_proposals_are_both_valid() -> None:
    policy = make_policy()
    first = Interval(at(ANCHOR_DATE, 10), at(ANCHOR_DATE, 11))
    second = Interval(at(ANCHOR_DATE, 11, 15), at(ANCHOR_DATE, 12))
    check_booking(policy, first, now=BASE_NOW, training=_training())
    check_booking(policy, second, now=BASE_NOW, training=_training())


def test_U_B02_conflict_names_committed_booking() -> None:
    candidate = Interval(at(ANCHOR_DATE, 15), at(ANCHOR_DATE, 16))
    existing = Booking("BK-0041", Interval(at(ANCHOR_DATE, 14), at(ANCHOR_DATE, 15, 30)))
    with pytest.raises(LabQuorumError) as error:
        check_booking(
            make_policy(),
            candidate,
            now=BASE_NOW,
            training=_training(),
            existing_bookings=[existing],
        )
    assert error.value.code is ErrorCode.CONFLICT
    assert error.value.details["booking_id"] == "BK-0041"


def test_U_B03_half_open_intervals_allow_start_at_end_plus_gap() -> None:
    previous = Interval(at(ANCHOR_DATE, 14), at(ANCHOR_DATE, 15, 30))
    next_slot = Interval(at(ANCHOR_DATE, 15, 45), at(ANCHOR_DATE, 16, 45))
    assert not intervals_conflict(next_slot, previous, gap_minutes=15)


def test_U_B04_nearest_free_slot_is_earliest_within_opening_hours() -> None:
    existing = Booking("BK-0041", Interval(at(ANCHOR_DATE, 14), at(ANCHOR_DATE, 15, 30)))
    slot = nearest_free_slot(
        make_policy(),
        at(ANCHOR_DATE, 14),
        duration_minutes=60,
        now=BASE_NOW,
        existing_bookings=[existing],
    )
    assert slot == Interval(at(ANCHOR_DATE, 15, 45), at(ANCHOR_DATE, 16, 45))


def test_U_B05_down_instrument_fails_with_down_until_time() -> None:
    down_until = at(ANCHOR_DATE, 17)
    with pytest.raises(LabQuorumError) as error:
        check_booking(
            make_policy(status="down_until", down_until=down_until),
            Interval(at(ANCHOR_DATE, 16), at(ANCHOR_DATE, 17)),
            now=BASE_NOW,
            training=_training(),
        )
    assert error.value.code is ErrorCode.INSTRUMENT_DOWN
    assert error.value.details["down_until"]


def test_U_B06_training_must_be_valid_at_booking_start() -> None:
    with pytest.raises(LabQuorumError) as error:
        check_booking(
            make_policy(),
            Interval(at(ANCHOR_DATE, 16), at(ANCHOR_DATE, 17)),
            now=BASE_NOW,
            training=_training(expiry_hour=15),
        )
    assert error.value.code is ErrorCode.TRAINING_REQUIRED
    assert error.value.details["expires_at"]


def test_U_B07_long_block_fails_with_split_suggestion() -> None:
    with pytest.raises(LabQuorumError) as error:
        check_booking(
            make_policy(),
            Interval(at(ANCHOR_DATE, 9), at(ANCHOR_DATE, 14)),
            now=BASE_NOW,
            training=_training(),
        )
    assert error.value.code is ErrorCode.TOO_LONG
    assert error.value.details["suggested_split_minutes"]


def test_U_B08_past_and_outside_booking_window_fail() -> None:
    policy = make_policy()
    with pytest.raises(LabQuorumError) as past:
        check_booking(
            policy,
            Interval(BASE_NOW - timedelta(hours=2), BASE_NOW - timedelta(hours=1)),
            now=BASE_NOW,
            training=None,
        )
    assert past.value.code is ErrorCode.IN_PAST
    with pytest.raises(LabQuorumError) as outside:
        check_booking(
            policy,
            Interval(
                at(ANCHOR_DATE + timedelta(days=31), 10), at(ANCHOR_DATE + timedelta(days=31), 11)
            ),
            now=BASE_NOW,
            training=_training(),
        )
    assert outside.value.code is ErrorCode.OUTSIDE_WINDOW


def test_U_B10_dst_offset_round_trip_on_fall_back_day() -> None:
    first = parse_iso_datetime("2026-11-01T01:30:00-04:00")
    second = parse_iso_datetime("2026-11-01T01:30:00-05:00")
    zone = ZoneInfo("America/New_York")
    first_local = first.astimezone(zone)
    second_local = second.astimezone(zone)
    assert first_local.hour == second_local.hour == 1
    assert first_local.fold == 0
    assert second_local.fold == 1
    assert second - first == timedelta(hours=1)


def test_U_B11_non_iso_time_returns_needs_iso_datetime() -> None:
    with pytest.raises(LabQuorumError) as error:
        parse_iso_datetime("Thursday 2 to 5 pm")
    assert error.value.code is ErrorCode.NEEDS_ISO_DATETIME
    with pytest.raises(LabQuorumError) as naive:
        parse_iso_datetime("2026-11-06T15:45:00")
    assert naive.value.code is ErrorCode.NEEDS_ISO_DATETIME


def test_booking_outside_instrument_hours_fails() -> None:
    with pytest.raises(LabQuorumError) as error:
        check_booking(
            make_policy(),
            Interval(at(ANCHOR_DATE, 19), at(ANCHOR_DATE, 21)),
            now=BASE_NOW,
            training=_training(),
        )
    assert error.value.code is ErrorCode.OUTSIDE_HOURS


def test_nearest_free_slot_returns_none_when_no_day_is_open() -> None:
    policy = make_policy()
    closed = InstrumentPolicy(
        instrument_id=policy.instrument_id,
        timezone=policy.timezone,
        opening_hours={},
        max_block_minutes=policy.max_block_minutes,
        min_gap_minutes=policy.min_gap_minutes,
        booking_window_days=policy.booking_window_days,
    )
    assert (
        nearest_free_slot(
            closed,
            at(ANCHOR_DATE, 10),
            duration_minutes=60,
            now=BASE_NOW,
        )
        is None
    )


def test_U_A04_policy_check_returns_structured_results() -> None:
    checks = policy_check(
        [
            PolicyCheck("training", True, None, "Training is valid at start."),
            PolicyCheck("availability", False, ErrorCode.CONFLICT, "Conflicts with BK-0041."),
        ]
    )
    assert checks == [
        {"name": "training", "passed": True, "code": None, "reason": "Training is valid at start."},
        {
            "name": "availability",
            "passed": False,
            "code": "CONFLICT",
            "reason": "Conflicts with BK-0041.",
        },
    ]


def test_U_L03_display_includes_weekday_date_time_and_zone() -> None:
    rendered = format_interval(
        at(ANCHOR_DATE, 15, 45),
        at(ANCHOR_DATE, 16, 45),
        "Asia/Kolkata",
    )
    assert rendered == "Fri 6 Nov 2026, 15:45-16:45 IST"


def test_U_L04_clock_is_injected_and_system_clock_is_aware() -> None:
    fixed = FixedClock(BASE_NOW)
    assert fixed.now() == BASE_NOW
    assert SystemClock().now().utcoffset() is not None


def test_U_G01_rate_guard_limits_each_profile_after_thirty_calls() -> None:
    clock = FixedClock(BASE_NOW)
    guard = RateGuard(clock=clock)
    for _ in range(30):
        guard.check("labops")
    with pytest.raises(LabQuorumError) as error:
        guard.check("labops")
    assert error.value.code is ErrorCode.RATE_LIMITED
    guard.check("scout")
    clock.set(BASE_NOW + timedelta(minutes=1))
    guard.check("labops")


def test_U_G06_error_codes_are_closed_and_render_as_markdown() -> None:
    table = error_codes_markdown()
    assert "| Code | Meaning |" in table
    assert all(code.value in table for code in ErrorCode)


@settings(max_examples=35, deadline=None)
@given(
    start_minute=st.integers(min_value=8 * 60, max_value=18 * 60),
    duration=st.integers(min_value=1, max_value=120),
)
def test_P_02_nearest_free_slot_never_conflicts(start_minute: int, duration: int) -> None:
    requested = at(ANCHOR_DATE, start_minute // 60, start_minute % 60)
    occupied = Booking("BK-0041", Interval(at(ANCHOR_DATE, 14), at(ANCHOR_DATE, 15, 30)))
    slot = nearest_free_slot(
        make_policy(),
        requested,
        duration_minutes=duration,
        now=BASE_NOW,
        existing_bookings=[occupied],
    )
    if slot is not None:
        assert slot.duration_minutes == duration
        assert not intervals_conflict(slot, occupied.interval, gap_minutes=15)


@settings(max_examples=40, deadline=None)
@given(
    actions=st.lists(
        st.sampled_from([RequestStatus.COMMITTED, RequestStatus.DECLINED, RequestStatus.EXPIRED]),
        max_size=10,
    )
)
def test_P_05_no_path_reaches_committed_from_declined_or_expired(
    actions: list[RequestStatus],
) -> None:
    status = RequestStatus.PENDING
    terminal = False
    for target in actions:
        if status in {RequestStatus.DECLINED, RequestStatus.EXPIRED}:
            with pytest.raises(LabQuorumError):
                transition_status(status, target)
            continue
        if status is RequestStatus.COMMITTED:
            with pytest.raises(LabQuorumError):
                transition_status(status, target)
            continue
        try:
            status = transition_status(status, target)
        except LabQuorumError:
            continue
        if status in {RequestStatus.DECLINED, RequestStatus.EXPIRED}:
            terminal = True
    if terminal:
        assert status is not RequestStatus.COMMITTED


@settings(max_examples=50, deadline=None)
@given(
    left=st.dictionaries(st.text(min_size=1, max_size=8), st.integers(), max_size=8),
    right=st.dictionaries(st.text(min_size=1, max_size=8), st.integers(), max_size=8),
)
def test_P_08_canonical_json_hash_is_stable_under_key_order_and_whitespace(
    left: dict[str, int], right: dict[str, int]
) -> None:
    combined = {**left, **right}
    assert content_hash(combined) == content_hash(dict(reversed(list(combined.items()))))
    assert canonical_json(combined).startswith("{")


def test_canonical_json_rejects_non_integer_quantities() -> None:
    with pytest.raises(LabQuorumError) as error:
        canonical_json({"quantity": 1.5})
    assert error.value.code is ErrorCode.INVALID_ARGUMENT


def test_canonical_json_is_compact_sorted_utf8_with_utc_z_times() -> None:
    encoded = canonical_json(
        {
            "z": "µ",
            "when": parse_iso_datetime("2026-11-06T10:15:00+05:30"),
            "a": 1,
        }
    )
    assert encoded == '{"a":1,"when":"2026-11-06T04:45:00Z","z":"µ"}'


def test_I_34_windows_zoneinfo_rejects_gap_and_fold_and_accepts_kolkata() -> None:
    with pytest.raises(LabQuorumError) as gap:
        parse_iso_datetime("2026-03-29T02:30:00", timezone="Europe/Berlin")
    assert gap.value.code is ErrorCode.NONEXISTENT_LOCAL_TIME
    with pytest.raises(LabQuorumError) as fold:
        parse_iso_datetime("2026-10-25T02:30:00", timezone="Europe/Berlin")
    assert fold.value.code is ErrorCode.AMBIGUOUS_LOCAL_TIME
    resolved = parse_iso_datetime(
        "2026-10-25T02:30:00+01:00",
        timezone="Europe/Berlin",
    )
    assert resolved.utcoffset() == timedelta(hours=1)
    local = parse_iso_datetime("2026-11-06T15:45:00", timezone="Asia/Kolkata")
    assert local.utcoffset() == timedelta(hours=5, minutes=30)
