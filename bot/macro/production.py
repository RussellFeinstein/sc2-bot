"""Production manager: larva spending and unit mix decisions."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId

from bot.core.blackboard import MacroAction
from bot.config import DRONE_TARGET_TWO_BASE

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


# MacroActions that want fighting units over drones
_ARMY_PRIORITY_ACTIONS = frozenset({
    MacroAction.PRESSURE_PUSH,
    MacroAction.ALL_IN,
})


class ProductionManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        bot = self._bot
        if not bot.larva:
            return

        blackboard = getattr(bot, "blackboard", None)
        action = blackboard.current_action if blackboard else MacroAction.STANDARD_MACRO
        pool_ready = bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists
        army_action = action in _ARMY_PRIORITY_ACTIONS

        # Spend every affordable larva this step — never let larvae accumulate.
        # Sitting at the 3-per-hatchery cap pauses natural larva generation entirely.
        #
        # NOTE: intentional larva banking (holding larvae for a timing attack/all-in burst)
        # is a valid advanced technique but requires a named "bank mode" from the strategic
        # layer.  Phase 1 always spends.  See memory/planning.md for the future design.
        for larva in bot.larva:
            if army_action and pool_ready:
                if bot.can_afford(UnitTypeId.ZERGLING):
                    larva.train(UnitTypeId.ZERGLING)
            elif bot.workers.amount < DRONE_TARGET_TWO_BASE:
                if bot.can_afford(UnitTypeId.DRONE):
                    larva.train(UnitTypeId.DRONE)
            elif pool_ready:
                # Drone target met — bleed excess larva into zerglings
                if bot.can_afford(UnitTypeId.ZERGLING):
                    larva.train(UnitTypeId.ZERGLING)
