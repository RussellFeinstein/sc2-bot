"""Centralized bot configuration.

All magic numbers, thresholds, and file paths live here.
Code reads from Config — never hardcode values inline.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# ── Race ──────────────────────────────────────────────────────────────────────
RACE = "Zerg"

# ── SC2 connection ─────────────────────────────────────────────────────────────
SC2_HOST = "127.0.0.1"
SC2_PORT = 8168

# ── Model paths ───────────────────────────────────────────────────────────────
MODELS_DIR = ROOT_DIR / "bot" / "ml" / "models"
OPENING_CLASSIFIER_PATH = MODELS_DIR / "opening_classifier.lgbm"
ENGAGEMENT_MODEL_PATH = MODELS_DIR / "engagement_model.lgbm"

# ── Feature store ─────────────────────────────────────────────────────────────
DATA_DIR = ROOT_DIR / "data"
FEATURES_DIR = DATA_DIR / "features"
LABELS_DIR = DATA_DIR / "labels"

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Economy thresholds ────────────────────────────────────────────────────────
# Drone counts at which macro transitions are considered
DRONE_TARGET_TWO_BASE = 28
DRONE_TARGET_THREE_BASE = 44
DRONE_TARGET_FOUR_BASE = 60

# ── Opening ───────────────────────────────────────────────────────────────────
# Which scripted opening to use when no ML model is loaded
DEFAULT_OPENING = "pool_first_expand"

# ── Supply management ────────────────────────────────────────────────────────
# Build an overlord when free supply drops to or below this value
OVERLORD_SUPPLY_BUFFER = 5
# Additional buffer per extra base beyond the first
OVERLORD_SUPPLY_BUFFER_PER_BASE = 2
# Max overlords building simultaneously
MAX_PENDING_OVERLORDS = 2

# ── Gas management ──────────────────────────────────────────────────────────
# Max extractors when teching to roach (keeps mineral economy strong)
GAS_CAP_ROACH_TECH = 3

# ── Queen management ────────────────────────────────────────────────────────
# Target queen count per hatchery (inject + defense/creep)
QUEENS_PER_HATCHERY = 2
# How close a queen must be to a hatchery to count as "covering" it
QUEEN_HATCHERY_DISTANCE = 8.0

# ── Army state machine ──────────────────────────────────────────────────────
# Minimum army supply to commit to an attack
ATTACK_COMMIT_SUPPLY = 40
# Retreat if army supply drops below this absolute floor during an attack
RETREAT_ARMY_SUPPLY = 15
# After regrouping, must rebuild to this supply before attacking again
REGROUP_THRESHOLD = 25
# Retreat if army drops to this fraction of the supply when the attack started
RETREAT_LOSS_RATIO = 0.40

# ── Strategic action confidence thresholds ────────────────────────────────────
# Minimum ML model probability to override the default action
STRATEGY_OVERRIDE_THRESHOLD = 0.65
ENGAGEMENT_CONFIDENCE_THRESHOLD = 0.55
