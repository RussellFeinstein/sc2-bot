"""Model inference wrapper.

Loads serialized models once at game start and provides a clean interface
for the decision layer.  All model calls go through this module.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from loguru import logger

from bot.config import OPENING_CLASSIFIER_PATH, ENGAGEMENT_MODEL_PATH
from bot.ml.schemas import OPENING_LABELS


class ModelInference:
    """Loads and wraps all trained ML models for in-game inference."""

    def __init__(self) -> None:
        self._opening_clf = self._load_model(OPENING_CLASSIFIER_PATH, "opening_classifier")
        self._engagement_model = self._load_model(ENGAGEMENT_MODEL_PATH, "engagement_model")

    @staticmethod
    def _load_model(path: Path, name: str) -> object | None:
        if not path.exists():
            logger.warning(f"Model not found: {path} — {name} will use heuristic fallback")
            return None
        try:
            import lightgbm as lgb
            return lgb.Booster(model_file=str(path))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as exc:
            logger.error(f"Failed to load {name}: {exc}")
            return None

    def predict_opening(self, features: np.ndarray) -> tuple[str, float]:
        """Return (opening_label, confidence) for the current feature vector."""
        if self._opening_clf is None:
            return "unknown", 0.0
        probs: np.ndarray = self._opening_clf.predict(features.reshape(1, -1))[0]
        idx = int(np.argmax(probs))
        return OPENING_LABELS[idx], float(probs[idx])

    def predict_engagement_win(self, features: np.ndarray) -> float:
        """Return P(win fight) ∈ [0, 1] for a potential engagement."""
        if self._engagement_model is None:
            return 0.5
        prob: float = float(self._engagement_model.predict(features.reshape(1, -1))[0])
        return prob
