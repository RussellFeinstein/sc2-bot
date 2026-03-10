"""Feature extraction: GameStateSnapshot → ML feature vector.

The feature vector is defined by bot.ml.schemas.FEATURE_COLUMNS.
This module is the single place where raw game state becomes ML inputs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from bot.ml.schemas import FEATURE_COLUMNS

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI
    from bot.core.game_state import GameStateSnapshot


class FeatureExtractor:
    """Converts a GameStateSnapshot into a fixed-length numpy feature vector."""

    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    def extract(self, snapshot: "GameStateSnapshot") -> np.ndarray:
        """Return a float32 array aligned with FEATURE_COLUMNS order."""
        # TODO(Phase 2): implement full feature engineering
        # For now, return a zero vector of the correct length.
        return np.zeros(len(FEATURE_COLUMNS), dtype=np.float32)

    def extract_dict(self, snapshot: "GameStateSnapshot") -> dict[str, float]:
        """Return features as a named dict (used for logging and debugging)."""
        vec = self.extract(snapshot)
        return dict(zip(FEATURE_COLUMNS, vec.tolist()))
