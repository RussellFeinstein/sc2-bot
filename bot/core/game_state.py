"""Typed snapshot of the current game state.

GameState wraps the raw BotAI object and exposes human-readable named properties.
All other modules consume a GameState snapshot rather than BotAI directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sc2.ids.unit_typeid import UnitTypeId

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI


@dataclass
class GameStateSnapshot:
    """Immutable snapshot captured once per step."""
    time: float                     # Game time in seconds
    minerals: int
    vespene: int
    supply_used: int
    supply_cap: int
    supply_left: int
    worker_count: int
    army_supply: int
    base_count: int                 # Completed Hatcheries/Lairs/Hives
    larva_count: int
    queen_count: int
    # Unit counts by category
    ling_count: int
    bane_count: int
    roach_count: int
    ravager_count: int
    hydra_count: int
    muta_count: int
    ultra_count: int
    # Structures
    spawning_pool_exists: bool
    roach_warren_exists: bool
    evo_chamber_exists: bool
    lair_exists: bool
    hive_exists: bool
    spire_exists: bool
    # Economy
    gas_buildings: int
    mineral_saturation: float       # workers / ideal; >1.0 means oversaturated
    # Visibility / scouting
    enemy_base_location_known: bool
    enemy_units_visible: int
    enemy_structures_visible: int


class GameState:
    """Captures a typed snapshot of the current game state from BotAI."""

    def __init__(self, bot: "BotAI") -> None:
        self._bot = bot

    def snapshot(self) -> GameStateSnapshot:
        bot = self._bot

        # Bases: completed hatcheries, lairs, and hives
        base_count = bot.townhalls.ready.amount

        # Mineral saturation: actual workers / optimal workers across all ready bases
        ideal_workers = sum(th.ideal_harvesters for th in bot.townhalls.ready)
        mineral_saturation = bot.workers.amount / max(1, ideal_workers)

        return GameStateSnapshot(
            time=bot.time,
            minerals=bot.minerals,
            vespene=bot.vespene,
            supply_used=bot.supply_used,
            supply_cap=bot.supply_cap,
            supply_left=bot.supply_left,
            worker_count=bot.workers.amount,
            army_supply=bot.supply_army,
            base_count=base_count,
            larva_count=bot.larva.amount,
            queen_count=bot.units(UnitTypeId.QUEEN).amount,
            ling_count=bot.units(UnitTypeId.ZERGLING).amount,
            bane_count=bot.units(UnitTypeId.BANELING).amount,
            roach_count=bot.units(UnitTypeId.ROACH).amount,
            ravager_count=bot.units(UnitTypeId.RAVAGER).amount,
            hydra_count=bot.units(UnitTypeId.HYDRALISK).amount,
            muta_count=bot.units(UnitTypeId.MUTALISK).amount,
            ultra_count=bot.units(UnitTypeId.ULTRALISK).amount,
            spawning_pool_exists=bot.structures(UnitTypeId.SPAWNINGPOOL).exists,
            roach_warren_exists=bot.structures(UnitTypeId.ROACHWARREN).exists,
            evo_chamber_exists=bot.structures(UnitTypeId.EVOLUTIONCHAMBER).exists,
            lair_exists=bot.structures(UnitTypeId.LAIR).ready.exists,
            hive_exists=bot.structures(UnitTypeId.HIVE).ready.exists,
            spire_exists=bot.structures(UnitTypeId.SPIRE).ready.exists,
            gas_buildings=bot.gas_buildings.amount,
            mineral_saturation=mineral_saturation,
            enemy_base_location_known=bot.enemy_structures.amount > 0,
            enemy_units_visible=bot.enemy_units.amount,
            enemy_structures_visible=bot.enemy_structures.amount,
        )
