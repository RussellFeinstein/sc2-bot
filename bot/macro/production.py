"""Production manager: larva spending and unit mix decisions."""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sc2.bot_ai import BotAI

class ProductionManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        # TODO(Phase 1): spend larva based on current MacroAction and supply
        pass
