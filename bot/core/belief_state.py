"""Belief state: hidden-state estimates under partial information.

Humans play StarCraft from beliefs, not certainties.  This module maintains
probability distributions over the opponent's hidden tech and intent.

Example beliefs maintained:
  - P(enemy has cloaked tech)
  - P(enemy is fast-expanding)
  - P(enemy attack within 2 min)
  - enemy opening label + confidence
  - our current strategic position (ahead / even / behind)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.core.game_state import GameStateSnapshot


@dataclass
class BeliefState:
    """Maintained and updated each step.  Consumed by StrategicPolicy."""

    # Enemy plan
    enemy_opening: str = "unknown"
    enemy_opening_confidence: float = 0.0

    # Hidden-tech probabilities (0.0–1.0)
    p_cloak_tech: float = 0.0
    p_mech_tech: float = 0.0
    p_air_tech: float = 0.0
    p_fast_expand: float = 0.0
    p_all_in: float = 0.0

    # Attack timing window
    p_attack_within_2min: float = 0.0

    # Strategic position
    position: str = "even"          # "ahead" | "even" | "behind"
    position_confidence: float = 0.0

    # Per-step evidence list (human-readable, used by decision_logger)
    evidence: list[str] = field(default_factory=list)

    def update(self, snapshot: "GameStateSnapshot", features: object) -> None:
        """Update beliefs given the latest game state snapshot and feature vector.

        Phase 1: rule-based heuristics only.
        Phase 3: integrate ML opening classifier and attack timing model outputs.
        """
        self.evidence.clear()

        # TODO(Phase 1): implement rule-based heuristics
        # e.g. if enemy_structures_visible > 0 and snapshot.time < 120:
        #          self.enemy_opening = "early_aggression"

        # TODO(Phase 3): call ML models via inference.py
