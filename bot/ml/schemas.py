"""ML feature column definitions — single source of truth.

Every column used by any model must be listed here.
FeatureExtractor, training scripts, and model evaluation all import from this file.
Adding/removing columns here requires retraining all affected models.
"""

from __future__ import annotations

# ── Economic features ──────────────────────────────────────────────────────────
ECONOMIC_FEATURES = [
    "minerals",
    "vespene",
    "supply_used",
    "supply_cap",
    "worker_count",
    "base_count",
    "gas_buildings",
    "mineral_saturation",
    "larva_count",
]

# ── Army features ──────────────────────────────────────────────────────────────
ARMY_FEATURES = [
    "army_supply",
    "ling_count",
    "bane_count",
    "roach_count",
    "ravager_count",
    "hydra_count",
    "muta_count",
    "ultra_count",
    "queen_count",
]

# ── Tech structure features ───────────────────────────────────────────────────
TECH_FEATURES = [
    "spawning_pool_exists",
    "roach_warren_exists",
    "evo_chamber_exists",
    "lair_exists",
    "hive_exists",
    "spire_exists",
]

# ── Scouting / visibility features ───────────────────────────────────────────
SCOUTING_FEATURES = [
    "enemy_base_location_known",
    "enemy_units_visible",
    "enemy_structures_visible",
]

# ── Time features ─────────────────────────────────────────────────────────────
TIME_FEATURES = [
    "game_time",
]

# ── Composite list (order must be stable — never remove from middle) ──────────
FEATURE_COLUMNS: list[str] = (
    TIME_FEATURES
    + ECONOMIC_FEATURES
    + ARMY_FEATURES
    + TECH_FEATURES
    + SCOUTING_FEATURES
)

# Labels for supervised models
OPENING_LABELS = [
    "pool_first",
    "hatch_first",
    "gaspool",
    "fast_lair",
    "unknown",
]

MACRO_ACTION_LABELS = [
    "DRONE_GREED",
    "STANDARD_MACRO",
    "PRESSURE_PUSH",
    "FAST_EXPAND",
    "TECH_TO_ROACH",
    "TECH_TO_LING_BANE",
    "TECH_TO_MUTA",
    "TECH_TO_ULTRA",
    "DEFENSIVE_HOLD",
    "ALL_IN",
    "SEND_SCOUT",
    "HOLD_AND_WAIT",
]
