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
        # Maps hatch tag → queen tag for in-flight inject commands
        self._pending_injects: dict[int, int] = {}

    async def step(self) -> None:
        bot = self._bot

        # Redistribute idle/oversaturated drones across bases and extractors
        await bot.distribute_workers()

        # Queen inject assignment (only ready hatcheries can receive inject)
        hatcheries_needing_inject = bot.townhalls.ready.filter(
            lambda th: not th.has_buff(BuffId.QUEENSPAWNLARVATIMER)
        )

        # Clear pending when: buff appeared, hatch died, queen died,
        # or queen went idle (inject completed or failed)
        idle_queen_tags = {q.tag for q in bot.units(UnitTypeId.QUEEN).idle}
        all_queen_tags = {q.tag for q in bot.units(UnitTypeId.QUEEN)}
        needing_tags = {th.tag for th in hatcheries_needing_inject}
        self._pending_injects = {
            h: q
            for h, q in self._pending_injects.items()
            if h in needing_tags and q in all_queen_tags
            and q not in idle_queen_tags
        }

        idle_queens = bot.units(UnitTypeId.QUEEN).idle.filter(
            lambda q: q.energy >= 25
        )
        assigned_queen_tags: set[int] = set(self._pending_injects.values())

        for hatch in hatcheries_needing_inject:
            if hatch.tag in self._pending_injects:
                continue  # a queen is already on the way
            candidates = idle_queens.filter(
                lambda q: q.tag not in assigned_queen_tags
            )
            if not candidates:
                break
            queen = min(
                candidates,
                key=lambda q: (q.distance_to(hatch.position), -q.energy),
            )
            queen(AbilityId.EFFECT_INJECTLARVA, hatch)
            assigned_queen_tags.add(queen.tag)
            self._pending_injects[hatch.tag] = queen.tag
