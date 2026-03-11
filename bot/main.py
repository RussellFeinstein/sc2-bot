"""Main bot entry point.

ZergBot subclasses BotAI (burnysc2) and wires together the three layers:
  Perception  → GameState + FeatureExtractor + BeliefState
  Decision    → StrategicPolicy
  Execution   → macro/tactics/micro modules
"""

from __future__ import annotations

import asyncio

from loguru import logger
from sc2.bot_ai import BotAI
from sc2.data import Race, Result
from sc2.main import run_game
from sc2.maps import Map
from sc2.player import Bot, Computer

from bot.config import RACE
from bot.core.blackboard import Blackboard
from bot.core.belief_state import BeliefState
from bot.core.feature_extractor import FeatureExtractor
from bot.core.game_state import GameState
from bot.macro.build_order import BuildOrderExecutor
from bot.macro.economy import EconomyManager
from bot.macro.production import ProductionManager
from bot.macro.upgrades import UpgradeManager
from bot.strategy.strategic_policy import StrategicPolicy
from bot.tactics.army_manager import ArmyManager
from bot.tactics.scouting import ScoutingManager
from bot.logging.decision_logger import DecisionLogger


class ZergBot(BotAI):
    """Human-modeling Zerg bot for the AI Arena ladder."""

    NAME = "ZergBot"
    RACE = Race.Zerg

    async def on_start(self) -> None:
        logger.info("Game started — initializing bot modules")
        self.blackboard = Blackboard()
        self.game_state = GameState(self)
        self.feature_extractor = FeatureExtractor(self)
        self.belief_state = BeliefState()
        self.strategic_policy = StrategicPolicy(self.blackboard)
        self.build_order = BuildOrderExecutor(self)
        self.economy = EconomyManager(self)
        self.production = ProductionManager(self)
        self.upgrades = UpgradeManager(self)
        self.army = ArmyManager(self)
        self.scouting = ScoutingManager(self)
        self.decision_logger = DecisionLogger()
        self._gg_sent = False

    async def on_step(self, iteration: int) -> None:
        await self._handle_chat()

        # 1. Perception
        snapshot = self.game_state.snapshot()
        features = self.feature_extractor.extract(snapshot)
        self.belief_state.update(snapshot, features)

        # 2. Decision
        action = self.strategic_policy.choose(snapshot, self.belief_state)
        self.decision_logger.log(iteration, snapshot, self.belief_state, action)
        self.blackboard.current_action = action

        # 3. Execution
        await self.build_order.step()
        await self.economy.step()
        await self.production.step()
        await self.upgrades.step()
        await self.scouting.step()
        await self.army.step()

    async def _handle_chat(self) -> None:
        """Respond 'gg' when the opponent sends 'gg'."""
        if self._gg_sent:
            return
        for msg in self.state.chat:
            if msg.player_id != self.player_id and "gg" in msg.message.lower():
                await self.chat_send("gg")
                self._gg_sent = True
                logger.info("Opponent said gg — responded gg")
                break

    async def on_end(self, game_result: Result) -> None:
        logger.info(f"Game ended: {game_result}")
        self.decision_logger.flush()


def create_bot() -> ZergBot:
    return ZergBot()
