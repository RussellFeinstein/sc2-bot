# sc2-bot

A human-modeling StarCraft II Zerg ladder bot. Combines reliable scripted macro/micro with ML models
trained on human replays to make belief-based strategic decisions under partial information.
Targets the [AI Arena](https://aiarena.net/) online bot ladder.

## Architecture

```
Perception  →  Decision  →  Execution
(abstractions)  (ML policy)  (scripted units)
```

The ML policy chooses from a finite set of strategic actions (DRONE_GREED, PRESSURE_PUSH, TECH_TO_MUTA, …).
Scripted modules handle all unit commands, build orders, and micro.

## Setup

```bash
# 1. Clone
git clone https://github.com/<your-handle>/sc2-bot.git
cd sc2-bot

# 2. Create virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate     # Mac/Linux

# 3. Install
pip install -e ".[dev]"

# 4. Requires StarCraft II installed locally
#    Free Starter Edition works on Mac/Linux.
#    Windows requires retail license.
```

## Running a Local Game

```bash
python -m bot.runner
```

This launches a game against the built-in AI using the SC2 installed on your machine.

## Running Tests

```bash
pytest
```

## Lint / Format

```bash
ruff check .
ruff format .
```

## AI Arena Submission

AI Arena requires a `ladder.zip` containing `bot/` and `ladderbots.json`.
See [AI Arena wiki](https://aiarena.net/wiki/bot-development/) for submission instructions.

## Project Phases

| Phase | Goal | Status |
|-------|------|--------|
| 1 — Scripted bot | End-to-end Zerg bot with pool-first opening | Done (v0.1.4) |
| 1.5 — Bot tuning | Roach tech, army state machine, beat Very Hard AI | **In Progress** |
| 2 — Creep spread | Strategic tumor placement and base connection | Planned |
| 3 — Speed mining | Custom worker micro for ~10% mineral income boost | Planned |
| 4 — ML models | Opening classifier, fight confidence, strategic policy | Planned |
| 5 — ML integration | Models plugged into decision layer | Planned |
| 6 — Adaptation | Per-opponent memory, best-of-N meta | Planned |

## Tech Stack

- [burnysc2](https://github.com/BurnySc2/python-sc2) — SC2 bot client
- [sc2reader](https://github.com/ggtracker/sc2reader) — replay parsing
- [LightGBM](https://lightgbm.readthedocs.io/) / [XGBoost](https://xgboost.readthedocs.io/) — tabular ML
- [PyTorch](https://pytorch.org/) — neural components (Phase 3+)
- [DuckDB](https://duckdb.org/) + [Parquet](https://parquet.apache.org/) — feature store
