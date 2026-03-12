# sc2-bot Project Roadmap

## Phase 1: Scripted Bot (DONE — merged to `main` at v0.1.4)

Get the bot running end-to-end and beating Easy AI with pure scripted logic. No ML.

**Completed:**
- Project scaffold, all module stubs wired in `main.py`
- `GameState` snapshot, `FeatureExtractor`, `BeliefState`, `Blackboard`
- `BuildOrderExecutor`, `EconomyManager` (using `distribute_workers()`), `ProductionManager`
- `UpgradeManager`, `ArmyManager`, `ScoutingManager`, `DecisionLogger`
- Full `on_step` loop validated, bot beats Easy/Medium AI
- `ladderbots.json` for AI Arena submission

---

## Phase 1.5: Bot Tuning (current — `feature/01.5-bot-tuning`)

Tune the scripted bot to beat Very Hard AI with roach-based play. No ML.

**Completed (v0.1.5–v0.1.8):**
- Army state machine with hysteresis (attack/retreat/regroup)
- Strategic policy rework: 8-step rule-based decision tree
- Roach tech path: roach warren -> lair -> evo chamber
- Queens: 2 per hatchery, nearest-idle inject logic with pending-inject tracking
- Dynamic overlord production (buffer = 5 + 2 per extra base, max 2 pending)
- Building placement away from mineral line (`placement.py`)
- Fix duplicate builds, queen inject wandering
- Expansion logic: saturation-based with army safety checks, mineral reservation
- Attack threshold scales with base count (20 supply per base)
- Tech-based gas management: cumulative gas cap (pool +1, RW +2, evo +1)
- Smart attack targeting: defend home -> chase structures -> enemy start
- Three-base droning in strategic policy
- 31 tests across 5 test files

**Deferred to later phase:**
- Ling runby/poke scouting (4-6 lings to enemy natural)
- Xel'Naga watchtower control
- Map control lings at key intersections

**Remaining:**
- Upgrades (roach speed, +1 missile, carapace)
- Engagement evaluation (when to take fights vs retreat)
- Better scouting (ling scouts, overlord positioning)
- Basic micro (roach kiting, focus fire)
- Queen cap: add a global MAX_QUEENS (6-9 depending on matchup) so we stop building queens on 4+ bases. Current `QUEENS_PER_HATCHERY=2` has no ceiling — 5 bases = 10 queens which is too many supply.

---

## Phase 2: Creep Spread Strategy (`feature/02-creep-spread`)

Replace `map_center` placeholder with strategic tumor placement:
- Base connection paths (main, natural, third)
- Choke-point watch positions for vision
- Defensive arcs toward likely attack paths

---

## Phase 3: Speed Mining Optimization (`feature/03-speed-mining`)

**When**: After creep spread is functional.
**Why**: ~10-12% mineral income boost. No pip-installable module exists — must build from scratch.

Replace `distribute_workers()` in `EconomyManager` with a custom `SpeedMiner` class implementing:

1. **Initial worker split** — frame 0, split 12 drones across 8 patches (close-first)
2. **Close-patch prioritization** — 2 workers on close patches before far patches
3. **Mineral stacking** — `move` to offset position + queued `gather` to skip deceleration
4. **Return cargo optimization** — immediate `HARVEST_RETURN` to skip idle frames

**Files:** new `bot/macro/speed_mining.py`, `tests/test_speed_mining.py`. Modify `config.py`, `economy.py`, `main.py`.

**Config constants:**
```python
MINERAL_CLOSE_DISTANCE = 5.0
MINERAL_WORKERS_PER_CLOSE_PATCH = 2
MINERAL_WORKERS_PER_FAR_PATCH = 2
MINERAL_WORKERS_PER_BASE_MAX = 16
MINERAL_WALK_OFFSET = 2.375
MINERAL_OWNERSHIP_RADIUS = 10.0
GAS_WORKERS_PER_EXTRACTOR = 3
```

**SpeedMiner data structures:**
```python
@dataclass
class TownhallInfo:
    tag: int
    position: Point2
    close_patches: list[int]
    far_patches: list[int]

class SpeedMiner:
    _worker_to_patch: dict[int, int]
    _patch_to_workers: dict[int, set[int]]
    _gas_workers: set[int]
    _townhall_info: dict[int, TownhallInfo]
    _worker_returning: set[int]
```

**Per-step logic:** cleanup dead workers/depleted patches, handle base changes, manage gas, assign new drones, issue mining commands (worker state machine).

**Worker state machine:**

| State | Detection | Action |
|-------|-----------|--------|
| IDLE | `worker.is_idle` | `_speed_mine_gather(worker, patch)` |
| CARRYING | `is_carrying_minerals`, not in `_worker_returning` | `HARVEST_RETURN`, add to set |
| JUST RETURNED | was in set, not carrying now | `_speed_mine_gather()` |
| GATHERING (correct) | `order_target == patch.tag` | no-op |
| GATHERING (wrong) | mismatched target | re-issue gather |
| MOVING | has move order | no-op (mineral walk in progress) |

**Mineral stacking trick:** compute offset position (`patch.position` toward townhall by 2.375 units), `worker.move(offset)`, then `worker.gather(patch, queue=True)`.

**Edge cases:** drone dies/morphs — cleanup removes from maps. Patch depletes — workers reassigned same frame. Base lost — orphaned workers redistribute. Workers with BUILD/ATTACK orders — skip.

---

## Phase 4: ML Model Training (`feature/04-ml-model-training`)

- Opening classifier (enemy opening from partial game state, T <= 3 min)
- Attack timing predictor (P(attack within 2 min))
- Engagement win probability (army comp + upgrades + positioning)
- Strategic policy model (full belief state to macro action enum)

---

## Phase 5: ML Integration (`feature/05-ml-inference-integration`)

- Wire trained models into `inference.py`
- `StrategicPolicy` switches from heuristic to model-based decisions
- `OpponentModel` uses opening classifier for belief state updates

---

## Phase 6: Opponent Adaptation (`feature/06-opponent-adaptation`)

- Per-opponent memory across games
- Adaptation of strategic policy based on opponent history
- AI Arena ladder submission (`ladderbots.json`)
