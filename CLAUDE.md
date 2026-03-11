# CLAUDE.md — sc2-bot

## Project Overview

A human-modeling StarCraft II **Zerg** ladder bot targeting the [AI Arena](https://aiarena.net/) online ladder.
The bot learns strategic abstractions from human and bot replays and uses belief-based decision-making under
partial information. It is not an end-to-end neural policy — it combines reliable scripted macro/micro with
ML models that operate over a finite strategic action space.

## Architecture

Three explicit layers:

```
Perception layer      game state → human-like abstractions (openings, army comp, threat, map control)
Decision layer        abstractions → strategic macro action (EXPAND, ATTACK, DRONE_GREED, ...)
Execution layer       strategic action → unit commands (scripted build orders, micro, production)
```

Directory layout:

```
sc2-bot/
  bot/
    main.py               # Entry point — BotAI subclass wired to all layers
    config.py             # Centralized config (race, thresholds, model paths)
    runner.py             # Local game launch helpers

    core/
      game_state.py       # Typed snapshot of current game state
      feature_extractor.py  # Raw state → ML feature vector
      belief_state.py     # Hidden-state estimates (cloaked tech, likely enemy plan)
      blackboard.py       # Shared mutable state across modules

    strategy/
      opening_book.py     # Named Zerg openings and build-order tables
      opponent_model.py   # Wraps ML model for enemy plan inference
      strategic_policy.py # Chooses macro action from finite enum
      tech_switches.py    # Heuristics for mid-game tech transitions
      expansion_logic.py  # When to take a new base

    tactics/
      army_manager.py     # Army grouping, attack/defend routing
      engagement_eval.py  # Fight confidence estimation (rule-based + ML)
      harassment.py       # Ling/bane/muta harass routines
      scouting.py         # Drone/overlord/ling scouting logic

    macro/
      build_order.py      # Build-order executor (supply, timings)
      economy.py          # Drone saturation, gas management
      production.py       # Larva spending, unit mix decisions
      upgrades.py         # Upgrade priority tables

    micro/
      unit_controllers/   # Per-unit-type micro (banelings, roaches, etc.)
      spellcasters/       # Infestor, viper, queen spell logic
      retreats.py         # Retreat conditions and pathing

    ml/
      models/             # Serialized model files (gitignored except .gitkeep)
      inference.py        # Load and call all models; cached per-game
      schemas.py          # Feature column definitions — single source of truth

    logging/
      decision_logger.py  # Per-decision structured log for replay analysis
      replay_labels.py    # Label extraction helpers used by training pipeline

  data/
    raw_replays/          # .SC2Replay files (gitignored)
    processed/            # Parsed per-frame parquet files (gitignored)
    features/             # Feature-engineered parquet files (gitignored)
    labels/               # Label parquet files for supervised training (gitignored)

  training/
    build_replay_dataset.py   # sc2reader pipeline: replays → processed parquet
    train_opening_classifier.py
    train_engagement_model.py
    evaluate_models.py

  experiments/
    notebooks/            # Jupyter exploration (gitignored checkpoints)
    ablations/            # Scripts for controlled ablation experiments

  tests/
    test_feature_extractor.py
    test_belief_state.py
    test_strategic_policy.py
    test_build_order.py
```

## Strategic Action Space (finite enum — key design decision)

The ML decision layer selects from:

- `DRONE_GREED` — keep droning, skip military investment
- `STANDARD_MACRO` — balanced drone/military growth
- `PRESSURE_PUSH` — build army, attack before opponent peaks
- `FAST_EXPAND` — take third/fourth base ahead of schedule
- `TECH_TO_ROACH` / `TECH_TO_LING_BANE` / `TECH_TO_MUTA` / `TECH_TO_ULTRA`
- `DEFENSIVE_HOLD` — spine crawlers, queens, minimal army while droning
- `ALL_IN` — spend everything, attack immediately
- `SEND_SCOUT` — priority scouting action
- `HOLD_AND_WAIT` — preserve army, wait for upgrade or reinforcement timing

## ML Model Targets (Phase 3+)

| Model | Input | Output |
|---|---|---|
| Opening classifier | partial game-state features (T ≤ 3 min) | enemy opening label |
| Attack timing predictor | game-state features | P(attack within 2 min) |
| Expand-now probability | economy features | P(expand is correct) |
| Engagement win probability | army composition, upgrades, positioning | P(win fight) |
| Strategic policy | full belief state | macro action enum |

## Development Commands

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate        # Windows
pip install -e ".[dev]"

# Run local game (requires SC2 installed)
python -m bot.runner

# Tests
pytest

# Lint
ruff check .
ruff format .

# Type check
mypy bot/ training/
```

## External Dependencies

- **StarCraft II** — must be installed locally for development (free Starter Edition works on Mac/Linux;
  Windows requires retail license or using the headless Linux build for CI).
- **burnysc2** — actively maintained fork of python-sc2. Use `pip install burnysc2` not `pip install sc2`.
- **AI Arena** — ladder submission requires a `ladder.zip` with `bot/` and `ladderbots.json`.
  See [AI Arena docs](https://aiarena.net/wiki/bot-development/).
- **Replays** — download human/bot replays from AI Arena or Spawning Tool for offline training.

## Version File

`pyproject.toml` — current: `0.1.4`

## Key Decisions

- **Zerg only** — one race keeps scripted logic manageable; Zerg's larva mechanic and macro-first style
  maps naturally to the greedy/defensive policy axes.
- **burnysc2 over vanilla python-sc2** — better maintained, async-native, works with current SC2 patches.
- **Tabular ML first** — LightGBM/XGBoost before any neural nets; faster iteration, better interpretability,
  lower data requirements.
- **Finite strategic action space** — ML picks from ~10 named macro actions; scripted execution handles
  unit commands. This keeps the learned policy tractable and debuggable.
- **sc2reader for replay ETL** — battle-tested parser; avoids reinventing replay parsing.
- **DuckDB + Parquet for feature store** — zero-server local analytics; handles millions of game-state rows.

## Known Issues / TODO

- Phase 1: Only scripted bot exists; no ML models trained yet.
- SC2 headless server setup for CI/automated testing not configured.
- `ladderbots.json` format for AI Arena submission not yet written.
- No opponent memory or per-opponent adaptation (Phase 5).

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the full phased development plan including speed mining design, creep spread strategy, ML model targets, and AI Arena submission.
