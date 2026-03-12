"""Strategic policy: selects a MacroAction each decision cycle.

Phase 1.5: rule-based policy with tech transitions and smarter thresholds.
Phase 4: ML model plugged in to override or guide rule-based defaults.

The policy always selects from the finite MacroAction enum.
Scripted execution modules interpret the active action.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from bot.config import (
    ATTACK_SUPPLY_PER_BASE,
    DRONE_TARGET_THREE_BASE,
    DRONE_TARGET_TWO_BASE,
    STRATEGY_OVERRIDE_THRESHOLD,
)
from bot.core.blackboard import Blackboard, MacroAction

if TYPE_CHECKING:
    from bot.core.belief_state import BeliefState
    from bot.core.game_state import GameStateSnapshot


class StrategicPolicy:
    """Chooses a MacroAction given the current game snapshot and belief state."""

    def __init__(self, blackboard: Blackboard) -> None:
        self._blackboard = blackboard

    def choose(self, snapshot: "GameStateSnapshot", belief: "BeliefState") -> MacroAction:
        """Return the strategic action for this step.

        Decision tree (evaluated top to bottom, first match wins):
          1. Emergency: detected all-in → DEFENSIVE_HOLD
          2. Early game: drone up to 16 workers
          3. Need natural hatchery → FAST_EXPAND
          4. Two bases: drone up to saturation
          5. Two-base saturated, no roach warren → TECH_TO_ROACH
          6. Three+ bases: drone up to saturation
          7. Army below attack threshold → STANDARD_MACRO
          8. Army ready → PRESSURE_PUSH
        """
        # TODO(Phase 4): call ML policy model; override if confidence >= threshold

        # 1. Emergency: detected all-in
        if belief.p_all_in >= STRATEGY_OVERRIDE_THRESHOLD:
            return MacroAction.DEFENSIVE_HOLD

        # 2. Early game: drone greed until minimum economy
        if snapshot.worker_count < 16 and not belief.enemy_attack_imminent:
            return MacroAction.DRONE_GREED

        # 3. Need natural expansion
        if snapshot.base_count < 2 and snapshot.worker_count >= 16:
            return MacroAction.FAST_EXPAND

        # 4. Two bases running: drone up to saturation before teching
        if snapshot.base_count >= 2 and snapshot.worker_count < DRONE_TARGET_TWO_BASE:
            return MacroAction.DRONE_GREED

        # 5. Two-base saturated: transition to roach tech
        if snapshot.base_count >= 2 and not snapshot.roach_warren_exists:
            return MacroAction.TECH_TO_ROACH

        # 6. Three+ bases: drone up to three-base saturation
        if snapshot.base_count >= 3 and snapshot.worker_count < DRONE_TARGET_THREE_BASE:
            return MacroAction.DRONE_GREED

        # 7. Have tech, building up army (threshold scales with bases)
        attack_threshold = max(snapshot.base_count, 2) * ATTACK_SUPPLY_PER_BASE
        if snapshot.army_supply < attack_threshold:
            return MacroAction.STANDARD_MACRO

        # 8. Army threshold reached: attack
        return MacroAction.PRESSURE_PUSH
