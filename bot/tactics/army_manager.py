"""Army manager: grouping, attack routing, and defend-at-home logic."""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sc2.bot_ai import BotAI

class ArmyManager:
    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    async def step(self) -> None:
        # TODO(Phase 1): move army based on MacroAction (attack/defend/hold)
        pass
