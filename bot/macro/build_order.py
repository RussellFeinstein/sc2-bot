"""Build order executor.

Reads the active opening from the opening book and issues the appropriate
build/train commands at the correct supply counts.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

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
            if await self._execute(current_step):
                self._step_index += 1

    async def _execute(self, step: BuildStep) -> bool:
        """Dispatch a build step to the appropriate sc2 action.

        Returns True when the action was issued (or is already done) so the
        caller can advance to the next step.  Returns False when prerequisites
        are not yet met (no larva, insufficient minerals, etc.) so the step is
        retried next frame.
        """
        bot = self._bot
        action = step.action

        if action == "build_overlord":
            if not bot.larva or not bot.can_afford(UnitTypeId.OVERLORD):
                return False
            bot.larva.random.train(UnitTypeId.OVERLORD)
            return True

        if action == "build_spawning_pool":
            if bot.structures(UnitTypeId.SPAWNINGPOOL).exists:
                return True  # already built or under construction
            if not bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                return False
            await bot.build(UnitTypeId.SPAWNINGPOOL, near=bot.townhalls.first)
            return True

        if action == "build_hatchery_natural":
            if bot.townhalls.amount >= 2:
                return True  # second hatchery already exists or is building
            if not bot.can_afford(UnitTypeId.HATCHERY):
                return False
            await bot.expand_now()
            return True

        if action == "build_extractor":
            if bot.gas_buildings.exists:
                return True  # extractor already built or under construction
            if not bot.can_afford(UnitTypeId.EXTRACTOR):
                return False
            for th in bot.townhalls.ready:
                geysers = bot.vespene_geyser.closer_than(10.0, th.position)
                for geyser in geysers:
                    if not bot.gas_buildings.closer_than(1.0, geyser.position):
                        await bot.build(UnitTypeId.EXTRACTOR, geyser)
                        return True
            return False

        if action == "train_queen":
            if not bot.can_afford(UnitTypeId.QUEEN):
                return False
            idle_hatcheries = bot.townhalls.idle
            if not idle_hatcheries:
                return False
            idle_hatcheries.first.train(UnitTypeId.QUEEN)
            return True

        if action == "research_metabolic_boost":
            if bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) > 0:
                return True  # already researching or done
            sp = bot.structures(UnitTypeId.SPAWNINGPOOL).ready.idle
            if not sp:
                return False
            if bot.minerals < 100 or bot.vespene < 100:
                return False
            sp.first.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
            return True

        logger.warning(f"Unknown build order action: {action!r} — skipping")
        return True
