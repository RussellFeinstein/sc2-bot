"""Replay ETL pipeline: .SC2Replay files → feature parquet store.

Usage:
    python training/build_replay_dataset.py --replays data/raw_replays/ --out data/processed/

Phase 2 task: implement full sc2reader parsing pipeline.
"""
from __future__ import annotations
import argparse
from pathlib import Path

# TODO(Phase 2): implement using sc2reader
# import sc2reader
# from bot.ml.schemas import FEATURE_COLUMNS
# from bot.logging.replay_labels import detect_opening, detect_timing_attack


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Parse SC2 replays into feature parquet files")
    p.add_argument("--replays", type=Path, default=Path("data/raw_replays"), help="Replay directory")
    p.add_argument("--out", type=Path, default=Path("data/processed"), help="Output directory")
    p.add_argument("--limit", type=int, default=None, help="Max replays to process (dev mode)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    print(f"[TODO Phase 2] Would parse replays from {args.replays} → {args.out}")


if __name__ == "__main__":
    main()
