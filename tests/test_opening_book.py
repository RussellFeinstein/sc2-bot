"""Tests for the opening book."""
from __future__ import annotations

import pytest

from bot.strategy.opening_book import get_opening, OPENING_BOOK, BuildStep


def test_all_openings_loadable() -> None:
    for name in OPENING_BOOK:
        steps = get_opening(name)
        assert len(steps) > 0, f"Opening '{name}' is empty"


def test_build_steps_are_typed() -> None:
    for name, steps in OPENING_BOOK.items():
        for step in steps:
            assert isinstance(step, BuildStep)
            assert isinstance(step.supply, int)
            assert isinstance(step.action, str)


def test_unknown_opening_raises() -> None:
    with pytest.raises(ValueError, match="Unknown opening"):
        get_opening("not_a_real_opening")


def test_build_steps_supply_non_decreasing() -> None:
    """Steps should be ordered by supply (each step at or after the previous)."""
    for name, steps in OPENING_BOOK.items():
        supplies = [s.supply for s in steps]
        assert supplies == sorted(supplies), f"Opening '{name}' has out-of-order supply steps"
