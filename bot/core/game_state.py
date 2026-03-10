"""Typed snapshot of the current game state.

GameState wraps the raw BotAI object and exposes human-readable named properties.
All other modules consume a GameState snapshot rather than BotAI directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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
        # TODO(Phase 1): fill in all fields using bot.units, bot.structures, etc.
        return GameStateSnapshot(
            time=bot.time,
            minerals=bot.minerals,
            vespene=bot.vespene,
            supply_used=bot.supply_used,
            supply_cap=bot.supply_cap,
            supply_left=bot.supply_left,
            worker_count=bot.workers.amount,
            army_supply=bot.supply_army,
            base_count=0,       # placeholder
            larva_count=0,
            queen_count=0,
            ling_count=0,
            bane_count=0,
            roach_count=0,
            ravager_count=0,
            hydra_count=0,
            muta_count=0,
            ultra_count=0,
            spawning_pool_exists=False,
            roach_warren_exists=False,
            lair_exists=False,
            hive_exists=False,
            spire_exists=False,
            gas_buildings=0,
            mineral_saturation=0.0,
            enemy_base_location_known=False,
            enemy_units_visible=0,
            enemy_structures_visible=0,
        )
