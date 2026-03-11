"""Army manager: state-machine-based attack routing with hysteresis.

The army manager decouples from the per-frame strategic policy once an attack
is committed.  The state machine prevents the "build 20 lings → attack → die →
repeat" loop by requiring meaningful army thresholds for transitions.
"""
from __future__ import annotations

from enum import auto, Enum
from typing import TYPE_CHECKING

from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId

from bot.config import (
    ATTACK_COMMIT_SUPPLY,
    REGROUP_THRESHOLD,
    RETREAT_ARMY_SUPPLY,
    RETREAT_LOSS_RATIO,
)
from bot.core.blackboard import MacroAction

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


class ArmyState(Enum):
    """Internal state for the army manager's state machine."""
    BUILDING_UP = auto()   # Accumulating army at rally point
    ATTACKING = auto()     # Committed to attack — moving toward enemy
    REGROUPING = auto()    # Post-attack retreat; rebuilding before next attempt


_COMBAT_UNIT_TYPES = frozenset({
    UnitTypeId.ZERGLING,
    UnitTypeId.BANELING,
    UnitTypeId.ROACH,
    UnitTypeId.RAVAGER,
    UnitTypeId.HYDRALISK,
    UnitTypeId.MUTALISK,
    UnitTypeId.ULTRALISK,
})

_ATTACK_ACTIONS = frozenset({
    MacroAction.PRESSURE_PUSH,
    MacroAction.ALL_IN,
})

_DEFENSIVE_ACTIONS = frozenset({
    MacroAction.DEFENSIVE_HOLD,
    MacroAction.HOLD_AND_WAIT,
})


class ArmyManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot
        self._state = ArmyState.BUILDING_UP
        self._attack_start_supply: int = 0

    @property
    def state(self) -> ArmyState:
        return self._state

    async def step(self) -> None:
        bot = self._bot
        blackboard = getattr(bot, "blackboard", None)
        action = blackboard.current_action if blackboard else MacroAction.STANDARD_MACRO

        army = bot.units.filter(lambda u: u.type_id in _COMBAT_UNIT_TYPES)
        if not army:
            return

        army_supply = bot.supply_army

        # Defensive override: always retreat regardless of state machine
        if action in _DEFENSIVE_ACTIONS:
            if self._state != ArmyState.BUILDING_UP:
                logger.info(f"Army: defensive override → BUILDING_UP (was {self._state.name})")
            self._state = ArmyState.BUILDING_UP
            self._rally_to_ramp(army)
            return

        # State transitions
        self._update_state(action, army_supply)

        # Execute current state behavior
        if self._state == ArmyState.ATTACKING:
            if bot.enemy_start_locations:
                target = bot.enemy_start_locations[0]
                for unit in army.idle:
                    unit.attack(target)

        elif self._state == ArmyState.REGROUPING:
            self._rally_to_ramp(army)

        else:  # BUILDING_UP
            self._rally_to_ramp(army)

    def _update_state(self, action: MacroAction, army_supply: int) -> None:
        prev = self._state

        if self._state == ArmyState.BUILDING_UP:
            if action in _ATTACK_ACTIONS and army_supply >= ATTACK_COMMIT_SUPPLY:
                self._state = ArmyState.ATTACKING
                self._attack_start_supply = army_supply

        elif self._state == ArmyState.ATTACKING:
            if army_supply <= RETREAT_ARMY_SUPPLY:
                self._state = ArmyState.REGROUPING
            elif (
                self._attack_start_supply > 0
                and army_supply <= self._attack_start_supply * RETREAT_LOSS_RATIO
            ):
                self._state = ArmyState.REGROUPING

        elif self._state == ArmyState.REGROUPING:
            if army_supply >= REGROUP_THRESHOLD:
                self._state = ArmyState.BUILDING_UP

        if self._state != prev:
            logger.info(f"Army: {prev.name} → {self._state.name} (supply={army_supply})")

    def _rally_to_ramp(self, army) -> None:
        bot = self._bot
        rally = bot.main_base_ramp.top_center if bot.main_base_ramp else bot.start_location
        for unit in army.idle:
            if unit.distance_to(rally) > 15:
                unit.move(rally)
