"""Tests for the Blackboard and MacroAction enum."""
from __future__ import annotations

from bot.core.blackboard import Blackboard, MacroAction


def test_default_action() -> None:
    bb = Blackboard()
    assert bb.current_action == MacroAction.STANDARD_MACRO


def test_all_macro_actions_unique() -> None:
    values = [a.value for a in MacroAction]
    assert len(values) == len(set(values))


def test_notes_cleared() -> None:
    bb = Blackboard()
    bb.add_note("test")
    assert len(bb.notes) == 1
    bb.clear_notes()
    assert len(bb.notes) == 0
