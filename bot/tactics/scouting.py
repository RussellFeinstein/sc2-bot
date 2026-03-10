"""Scouting manager: drone/overlord/ling scouting logic."""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sc2.bot_ai import BotAI

class ScoutingManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        # TODO(Phase 1): send overlord to watch natural; drone-scout at ~14 supply
        pass
