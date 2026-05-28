"""Tests for the build_kwargs helper."""

from ecosystems_cli.helpers.build_kwargs import build_kwargs


def test_drops_none_values():
    assert build_kwargs(a=1, b=None, c="x") == {"a": 1, "c": "x"}


def test_empty_when_all_none():
    assert build_kwargs(a=None, b=None) == {}


def test_empty_when_no_args():
    assert build_kwargs() == {}


def test_keeps_falsy_non_none_values():
    """0, False, and "" are real values and must be preserved."""
    assert build_kwargs(page=0, flag=False, name="") == {"page": 0, "flag": False, "name": ""}


def test_keeps_all_when_nothing_is_none():
    assert build_kwargs(page=1, per_page=10) == {"page": 1, "per_page": 10}
