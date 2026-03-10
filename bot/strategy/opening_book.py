"""Zerg opening book.

Defines named opening build-order sequences.
The BuildOrderExecutor reads the active opening and executes it step by step.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BuildStep:
    """A single step in a build order."""
    supply: int             # Execute at or after this supply count
    action: str             # Human-readable action label
    unit_id: int | None = None    # sc2.ids.UnitTypeId if applicable
    upgrade_id: int | None = None

    def __str__(self) -> str:
        return f"[{self.supply}] {self.action}"


# ── Opening: Pool First Expand ─────────────────────────────────────────────────
# Safe general-purpose Zerg opener; good against most strategies.
#  13 - Overlord
#  13 - Spawning Pool
#  16 - Hatchery (natural)
#  16 - Extractor
#  17 - Overlord
#  18 - Queen × 2
#  ... macro from here
POOL_FIRST_EXPAND: list[BuildStep] = [
    BuildStep(supply=13, action="build_overlord"),
    BuildStep(supply=13, action="build_spawning_pool"),
    BuildStep(supply=16, action="build_hatchery_natural"),
    BuildStep(supply=16, action="build_extractor"),
    BuildStep(supply=17, action="build_overlord"),
    BuildStep(supply=18, action="train_queen"),
    BuildStep(supply=20, action="train_queen"),
    BuildStep(supply=20, action="research_metabolic_boost"),
]

# ── Opening: Hatch First ───────────────────────────────────────────────────────
# Greedy opener; vulnerable to early aggression.
HATCH_FIRST: list[BuildStep] = [
    BuildStep(supply=17, action="build_hatchery_natural"),
    BuildStep(supply=18, action="build_spawning_pool"),
    BuildStep(supply=18, action="build_extractor"),
    BuildStep(supply=19, action="build_overlord"),
    BuildStep(supply=20, action="train_queen"),
    BuildStep(supply=22, action="train_queen"),
]

# ── Opening registry ───────────────────────────────────────────────────────────
OPENING_BOOK: dict[str, list[BuildStep]] = {
    "pool_first_expand": POOL_FIRST_EXPAND,
    "hatch_first": HATCH_FIRST,
}


def get_opening(name: str) -> list[BuildStep]:
    if name not in OPENING_BOOK:
        raise ValueError(f"Unknown opening '{name}'. Available: {list(OPENING_BOOK)}")
    return OPENING_BOOK[name]
