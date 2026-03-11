"""Scouting manager: overlord and drone scouting logic."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


class ScoutingManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot
        self._overlord_scouted: bool = False

    async def step(self) -> None:
        bot = self._bot

        # Send the first overlord toward the enemy start location immediately.
        # Standard Zerg practice — the initial overlord reveals the spawn and
        # gives early warning of aggression.
        #
        # NOTE: long-term, overlords should patrol choke points and creep edges
        # rather than walking into the enemy main (where they will be sniped).
        if not self._overlord_scouted and bot.enemy_start_locations:
            overlords = bot.units(UnitTypeId.OVERLORD)
            if overlords:
                overlords.first.move(bot.enemy_start_locations[0])
                self._overlord_scouted = True

                blackboard = getattr(bot, "blackboard", None)
                if blackboard is not None:
                    blackboard.add_note("overlord scout dispatched")
