"""Build order executor.

Reads the active opening from the opening book and issues the appropriate
build/train commands at the correct supply counts.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from bot.strategy.opening_book import get_opening, BuildStep
from bot.config import DEFAULT_OPENING

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


class BuildOrderExecutor:
    """Executes the active build order opening step by step."""

    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot
        self._steps: list[BuildStep] = get_opening(DEFAULT_OPENING)
        self._step_index: int = 0

    async def step(self) -> None:
        """Execute the next pending build step if supply threshold is met."""
        if self._step_index >= len(self._steps):
            return  # Opening complete; macro modules take over

        current_step = self._steps[self._step_index]
        if self._bot.supply_used >= current_step.supply:
            logger.debug(f"Build order step: {current_step}")
            await self._execute(current_step)
            self._step_index += 1

    async def _execute(self, step: BuildStep) -> None:
        """Dispatch a build step to the appropriate sc2 action."""
        # TODO(Phase 1): implement each action case
        # e.g. "build_spawning_pool" → self._bot.build(SPAWNINGPOOL, ...)
        logger.debug(f"[TODO] execute: {step.action}")
