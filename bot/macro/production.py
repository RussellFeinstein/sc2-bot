"""Production manager: tech buildings, queens, overlords, and larva spending."""
from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

from bot.config import (
    DRONE_TARGET_FOUR_BASE,
    DRONE_TARGET_THREE_BASE,
    DRONE_TARGET_TWO_BASE,
    EXPAND_ARMY_PER_BASE,
    EXPAND_SATURATION_THRESHOLD,
    GAS_PER_EVO_CHAMBER,
    GAS_PER_ROACH_WARREN,
    GAS_PER_SPAWNING_POOL,
    MAX_PENDING_OVERLORDS,
    OVERLORD_SUPPLY_BUFFER,
    OVERLORD_SUPPLY_BUFFER_PER_BASE,
    QUEEN_HATCHERY_DISTANCE,
    QUEENS_PER_HATCHERY,
)
from bot.core.blackboard import MacroAction
from bot.macro.placement import tech_placement

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
        self._evo_ordered = False
        self._rw_ordered = False
        self._wants_expand = False

    async def step(self) -> None:
        bot = self._bot
        blackboard = getattr(bot, "blackboard", None)
        action = blackboard.current_action if blackboard else MacroAction.STANDARD_MACRO
        self._wants_expand = False

        # Non-larva production first (uses hatchery build queue)
        await self._train_queens()

        # Take a new base when saturated and army can defend it
        await self._check_expand()

        # Tech buildings (uses drone + minerals)
        await self._ensure_tech_buildings(action)

        # Gas buildings (cumulative cap based on tech)
        await self._ensure_gas_buildings()

        if not bot.larva:
            return

        # Overlords before anything else
        self._build_overlords()

        if not bot.larva:
            return

        # Reserve minerals for pending expansion — only spend on drones, not army
        if self._wants_expand:
            for larva in bot.larva:
                if bot.workers.amount < self._drone_target() and bot.can_afford(UnitTypeId.DRONE):
                    larva.train(UnitTypeId.DRONE)
            return

        # Larva spending
        pool_ready = bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists
        rw_ready = bot.structures(UnitTypeId.ROACHWARREN).ready.exists
        army_action = action in _ARMY_PRIORITY_ACTIONS
        wants_roaches = rw_ready and action in (
            MacroAction.TECH_TO_ROACH,
            MacroAction.STANDARD_MACRO,
            MacroAction.PRESSURE_PUSH,
            MacroAction.ALL_IN,
        )

        for larva in bot.larva:
            if army_action:
                if wants_roaches and bot.can_afford(UnitTypeId.ROACH):
                    larva.train(UnitTypeId.ROACH)
                elif pool_ready and bot.can_afford(UnitTypeId.ZERGLING):
                    larva.train(UnitTypeId.ZERGLING)
            elif bot.workers.amount < self._drone_target():
                if bot.can_afford(UnitTypeId.DRONE):
                    larva.train(UnitTypeId.DRONE)
            elif wants_roaches and bot.can_afford(UnitTypeId.ROACH):
                larva.train(UnitTypeId.ROACH)
            elif pool_ready and bot.can_afford(UnitTypeId.ZERGLING):
                larva.train(UnitTypeId.ZERGLING)

    # ── Expansion ─────────────────────────────────────────────────────────

    async def _check_expand(self) -> None:
        bot = self._bot

        if bot.already_pending(UnitTypeId.HATCHERY):
            return

        # Need roach warren before expanding beyond natural
        if bot.townhalls.amount >= 2 and not bot.structures(UnitTypeId.ROACHWARREN).exists:
            return

        # Check mineral saturation across ready bases
        ideal = sum(th.ideal_harvesters for th in bot.townhalls.ready)
        if ideal <= 0:
            return
        saturation = bot.workers.amount / ideal
        if saturation < EXPAND_SATURATION_THRESHOLD:
            return

        # Army must be sufficient: more bases need more army to defend
        next_base = bot.townhalls.amount + 1
        required_army = next_base * EXPAND_ARMY_PER_BASE
        if bot.supply_army < required_army:
            return

        # Signal that we want to expand — reserve minerals by skipping
        # army production this step (handled via _wants_expand flag)
        self._wants_expand = True

        if not bot.can_afford(UnitTypeId.HATCHERY):
            return

        await bot.expand_now()
        self._wants_expand = False
        logger.info(f"Production: expanding to base {next_base} (saturation={saturation:.0%}, army={bot.supply_army})")

    # ── Queens ──────────────────────────────────────────────────────────────

    async def _train_queens(self) -> None:
        bot = self._bot
        if not bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists:
            return

        queens = bot.units(UnitTypeId.QUEEN)
        desired = bot.townhalls.ready.amount * QUEENS_PER_HATCHERY
        current = queens.amount + bot.already_pending(UnitTypeId.QUEEN)

        if current >= desired:
            return
        if not bot.can_afford(UnitTypeId.QUEEN):
            return

        for th in bot.townhalls.ready.idle:
            nearby = queens.closer_than(QUEEN_HATCHERY_DISTANCE, th.position).amount
            if nearby < QUEENS_PER_HATCHERY:
                th.train(UnitTypeId.QUEEN)
                return  # one per step to avoid mineral drain

    # ── Tech buildings ──────────────────────────────────────────────────────

    async def _ensure_tech_buildings(self, action: MacroAction) -> None:
        bot = self._bot

        # Roach warren: build when policy says TECH_TO_ROACH
        if bot.structures(UnitTypeId.ROACHWARREN).exists or bot.already_pending(UnitTypeId.ROACHWARREN):
            self._rw_ordered = False
        elif (
            not self._rw_ordered
            and action == MacroAction.TECH_TO_ROACH
            and bot.can_afford(UnitTypeId.ROACHWARREN)
            and bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists
        ):
            await bot.build(UnitTypeId.ROACHWARREN, near=tech_placement(bot, bot.townhalls.first))
            self._rw_ordered = True
            logger.info("Production: building roach warren")

        # Evolution chamber: once we have 2 bases and a roach warren
        if bot.structures(UnitTypeId.EVOLUTIONCHAMBER).exists or bot.already_pending(UnitTypeId.EVOLUTIONCHAMBER):
            self._evo_ordered = False  # reset flag once the engine sees it
        elif (
            not self._evo_ordered
            and bot.townhalls.ready.amount >= 2
            and bot.structures(UnitTypeId.ROACHWARREN).exists
            and bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER)
        ):
            await bot.build(UnitTypeId.EVOLUTIONCHAMBER, near=tech_placement(bot, bot.townhalls.first))
            self._evo_ordered = True
            logger.info("Production: building evolution chamber")

        # Lair: morph from main hatchery once roach warren + pool are ready
        if (
            bot.structures(UnitTypeId.ROACHWARREN).ready.exists
            and bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists
            and not bot.structures(UnitTypeId.LAIR).exists
            and not bot.structures(UnitTypeId.HIVE).exists
            and not bot.already_pending(UnitTypeId.LAIR)
            and bot.can_afford(UnitTypeId.LAIR)
        ):
            main_hatch = bot.townhalls.ready.idle
            if main_hatch:
                main_hatch.first(AbilityId.UPGRADETOLAIR_LAIR)
                logger.info("Production: morphing lair")

    # ── Gas buildings ───────────────────────────────────────────────────────

    async def _ensure_gas_buildings(self) -> None:
        """Build extractors based on what tech is spending gas.

        Gas cap is cumulative: each tech building adds extractors.
        No tech = 0 extractors. Pool = 1. Pool + RW = 3. Etc.
        """
        bot = self._bot

        gas_cap = self._gas_cap()
        if gas_cap <= 0:
            return

        current_gas = bot.gas_buildings.amount + bot.already_pending(UnitTypeId.EXTRACTOR)
        if current_gas >= gas_cap:
            return

        for th in bot.townhalls.ready:
            geysers = bot.vespene_geyser.closer_than(10.0, th.position)
            for geyser in geysers:
                if current_gas >= gas_cap:
                    return
                if not bot.gas_buildings.closer_than(1.0, geyser.position).exists:
                    if bot.can_afford(UnitTypeId.EXTRACTOR):
                        await bot.build(UnitTypeId.EXTRACTOR, geyser)
                        current_gas += 1

    def _gas_cap(self) -> int:
        """Cumulative gas cap based on existing tech buildings."""
        bot = self._bot
        cap = 0
        if bot.structures(UnitTypeId.SPAWNINGPOOL).exists:
            cap += GAS_PER_SPAWNING_POOL
        if bot.structures(UnitTypeId.ROACHWARREN).exists:
            cap += GAS_PER_ROACH_WARREN
        if bot.structures(UnitTypeId.EVOLUTIONCHAMBER).exists:
            cap += GAS_PER_EVO_CHAMBER
        return cap

    # ── Overlords ───────────────────────────────────────────────────────────

    def _build_overlords(self) -> None:
        bot = self._bot
        if bot.supply_cap >= 200:
            return

        pending = bot.already_pending(UnitTypeId.OVERLORD)
        buffer = OVERLORD_SUPPLY_BUFFER + max(0, bot.townhalls.ready.amount - 1) * OVERLORD_SUPPLY_BUFFER_PER_BASE

        if bot.supply_left <= buffer and pending < MAX_PENDING_OVERLORDS:
            needed = min(MAX_PENDING_OVERLORDS - pending, MAX_PENDING_OVERLORDS)
            for _ in range(needed):
                if bot.larva and bot.can_afford(UnitTypeId.OVERLORD):
                    bot.larva.first.train(UnitTypeId.OVERLORD)
                else:
                    break

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _drone_target(self) -> int:
        base_count = self._bot.townhalls.ready.amount
        if base_count >= 4:
            return DRONE_TARGET_FOUR_BASE
        if base_count >= 3:
            return DRONE_TARGET_THREE_BASE
        return DRONE_TARGET_TWO_BASE
