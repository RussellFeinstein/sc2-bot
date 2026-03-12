"""Building placement helpers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sc2.position import Point2

if TYPE_CHECKING:
    from sc2.bot_ai import BotAI
    from sc2.unit import Unit


def tech_placement(bot: "BotAI", townhall: "Unit", distance: float = 8.0) -> Point2:
    """Return a position near *townhall* away from its mineral line.

    Finds the centroid of nearby mineral patches and places the building
    on the opposite side of the townhall so it never blocks mining.
    """
    minerals = bot.mineral_field.closer_than(10, townhall.position)
    if minerals:
        mineral_center = minerals.center
        # Move away from minerals, past the townhall
        return townhall.position.towards(mineral_center, -distance)
    # Fallback: toward map center
    return townhall.position.towards(bot.game_info.map_center, distance)
