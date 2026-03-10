"""Strategic policy: selects a MacroAction each decision cycle.

Phase 1: rule-based policy using heuristics and game state.
Phase 4: ML model plugged in to override or guide rule-based defaults.

The policy always selects from the finite MacroAction enum.
Scripted execution modules interpret the active action.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from bot.core.blackboard import Blackboard, MacroAction
from bot.config import STRATEGY_OVERRIDE_THRESHOLD

if TYPE_CHECKING:
    from bot.core.belief_state import BeliefState
    from bot.core.game_state import GameStateSnapshot


class StrategicPolicy:
    """Chooses a MacroAction given the current game snapshot and belief state."""

    def __init__(self, blackboard: Blackboard) -> None:
        self._blackboard = blackboard

    def choose(self, snapshot: "GameStateSnapshot", belief: "BeliefState") -> MacroAction:
        """Return the strategic action for this step.

        Phase 1 heuristics:
          - Drone to saturation before building army
          - Scout early; respond to detected aggression
          - Expand when saturated
          - Hold defensively when behind
        """
        # TODO(Phase 1): implement full heuristic decision tree
        # TODO(Phase 4): call ML policy model; override if confidence >= threshold

        if belief.p_all_in >= STRATEGY_OVERRIDE_THRESHOLD:
            return MacroAction.DEFENSIVE_HOLD

        if snapshot.worker_count < 16 and not belief.enemy_attack_imminent:
            return MacroAction.DRONE_GREED

        if snapshot.base_count < 2 and snapshot.worker_count >= 16:
            return MacroAction.FAST_EXPAND

        return MacroAction.STANDARD_MACRO

    @property
    def _enemy_attack_imminent(self) -> bool:
        return self._blackboard.enemy_attack_imminent
