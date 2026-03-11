"""Army manager: grouping, attack routing, and defend-at-home logic."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId

from bot.core.blackboard import MacroAction

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


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

_RETREAT_ACTIONS = frozenset({
    MacroAction.DEFENSIVE_HOLD,
    MacroAction.HOLD_AND_WAIT,
})


class ArmyManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        bot = self._bot
        blackboard = getattr(bot, "blackboard", None)
        action = blackboard.current_action if blackboard else MacroAction.STANDARD_MACRO

        army = bot.units.filter(lambda u: u.type_id in _COMBAT_UNIT_TYPES)
        if not army:
            return

        if action in _ATTACK_ACTIONS and bot.enemy_start_locations:
            target = bot.enemy_start_locations[0]
            for unit in army.idle:
                unit.attack(target)

        elif action in _RETREAT_ACTIONS:
            rally = bot.start_location
            for unit in army.idle:
                unit.move(rally)

        # All other actions: hold position near start location
        else:
            rally = bot.start_location
            for unit in army.idle:
                if unit.distance_to(rally) > 20:
                    unit.move(rally)
