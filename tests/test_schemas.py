"""Tests for ML feature schema consistency."""
from __future__ import annotations

from bot.ml.schemas import (
    FEATURE_COLUMNS,
    OPENING_LABELS,
    MACRO_ACTION_LABELS,
)


def test_feature_columns_unique() -> None:
    assert len(FEATURE_COLUMNS) == len(set(FEATURE_COLUMNS))


def test_feature_columns_non_empty() -> None:
    assert len(FEATURE_COLUMNS) > 0


def test_opening_labels_non_empty() -> None:
    assert "unknown" in OPENING_LABELS


def test_macro_action_labels_match_enum() -> None:
    from bot.core.blackboard import MacroAction
    enum_names = {a.name for a in MacroAction}
    label_names = set(MACRO_ACTION_LABELS)
    assert enum_names == label_names, f"Mismatch: {enum_names.symmetric_difference(label_names)}"
