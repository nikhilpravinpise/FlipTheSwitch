"""Scaffold smoke test."""

import labquorum


def test_package_version_is_string() -> None:
    assert isinstance(labquorum.__version__, str)
