"""Decision logger: records per-step strategic decisions for post-game analysis.

Every MacroAction the bot takes is logged with:
  - game time
  - belief state summary
  - evidence that led to the decision
  - alternative actions considered

This log is the primary tool for understanding and improving the bot's strategy.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from loguru import logger as _logger

from bot.config import LOG_DIR

if TYPE_CHECKING:
    from bot.core.blackboard import MacroAction
    from bot.core.belief_state import BeliefState
    from bot.core.game_state import GameStateSnapshot


class DecisionLogger:
    """Accumulates decision records during a game and flushes to JSON on game end."""

    def __init__(self) -> None:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self._path = LOG_DIR / f"decisions_{timestamp}.jsonl"
        self._records: list[dict] = []

    def log(
        self,
        iteration: int,
        snapshot: "GameStateSnapshot",
        belief: "BeliefState",
        action: "MacroAction",
    ) -> None:
        record = {
            "iteration": iteration,
            "time": snapshot.time,
            "action": action.name,
            "enemy_opening": belief.enemy_opening,
            "enemy_opening_confidence": belief.enemy_opening_confidence,
            "position": belief.position,
            "p_all_in": belief.p_all_in,
            "p_attack_within_2min": belief.p_attack_within_2min,
            "evidence": list(belief.evidence),
            "worker_count": snapshot.worker_count,
            "army_supply": snapshot.army_supply,
            "base_count": snapshot.base_count,
            "minerals": snapshot.minerals,
        }
        self._records.append(record)

    def flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            for record in self._records:
                f.write(json.dumps(record) + "\n")
        _logger.info(f"Decision log written: {self._path} ({len(self._records)} records)")
