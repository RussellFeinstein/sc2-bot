"""Economy manager: drone saturation, gas management, and queen macro."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


class EconomyManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        bot = self._bot

        # Redistribute idle/oversaturated drones across bases and extractors
        await bot.distribute_workers()

        # Queen macro: inject is highest priority; spare energy goes to creep spread.
        # NOTE: creep tumor targeting uses map_center as a Phase 1 placeholder.
        # Long-term, tumors should be placed strategically — base connection paths,
        # choke-point watch positions, and defensive arcs.  See memory/planning.md.
        hatcheries_needing_inject = bot.townhalls.filter(
            lambda th: not th.has_buff(BuffId.QUEENSPAWNLARVATIMER)
        )

        for queen in bot.units(UnitTypeId.QUEEN).idle:
            if queen.energy < 25:
                continue

            if hatcheries_needing_inject:
                target = hatcheries_needing_inject.closest_to(queen.position)
                queen(AbilityId.EFFECT_INJECTLARVA, target)
            else:
                # All bases injected — spread creep toward map center (placeholder)
                queen(AbilityId.BUILD_CREEPTUMOR_QUEEN, bot.game_info.map_center)
