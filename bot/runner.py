"""Local game launcher for development.

Usage:
    python -m bot.runner
    python -m bot.runner --difficulty VeryHard
    python -m bot.runner --map AcropolisLE
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.maps import Map
from sc2.player import Bot, Computer

from bot.main import ZergBot


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run sc2-bot locally")
    p.add_argument("--map", default="PylonAIE", help="SC2 map name (must exist in SC2/Maps/)")
    p.add_argument(
        "--difficulty",
        default="Medium",
        choices=["VeryEasy", "Easy", "Medium", "Hard", "Harder", "VeryHard", "CheatVision", "CheatMoney", "CheatInsane"],
        help="Built-in AI difficulty",
    )
    p.add_argument("--realtime", action="store_true", help="Run in real-time mode")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    difficulty = Difficulty[args.difficulty]
    run_game(
        Map(Path(f"{args.map}.SC2Map")),
        [
            Bot(Race.Zerg, ZergBot()),
            Computer(Race.Random, difficulty),
        ],
        realtime=args.realtime,
    )


if __name__ == "__main__":
    main()
