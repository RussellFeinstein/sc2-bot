"""Upgrade manager: research priority tables."""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sc2.bot_ai import BotAI

class UpgradeManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        # TODO(Phase 1): research metabolic boost, carapace, melee as appropriate
        pass
