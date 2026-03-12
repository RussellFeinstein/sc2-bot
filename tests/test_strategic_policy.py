"""Tests for StrategicPolicy decision tree."""
from bot.config import ATTACK_SUPPLY_PER_BASE, DRONE_TARGET_THREE_BASE, DRONE_TARGET_TWO_BASE
from bot.core.belief_state import BeliefState
from bot.core.blackboard import Blackboard, MacroAction
from bot.core.game_state import GameStateSnapshot
from bot.strategy.strategic_policy import StrategicPolicy


def _snapshot(**overrides) -> GameStateSnapshot:
    """Create a GameStateSnapshot with sensible defaults, overridden by kwargs."""
    defaults = dict(
        time=120.0,
        minerals=300,
        vespene=100,
        supply_used=40,
        supply_cap=44,
        supply_left=4,
        worker_count=24,
        army_supply=10,
        base_count=2,
        larva_count=3,
        queen_count=2,
        ling_count=0,
        bane_count=0,
        roach_count=0,
        ravager_count=0,
        hydra_count=0,
        muta_count=0,
        ultra_count=0,
        spawning_pool_exists=True,
        roach_warren_exists=False,
        evo_chamber_exists=False,
        lair_exists=False,
        hive_exists=False,
        spire_exists=False,
        gas_buildings=1,
        mineral_saturation=1.0,
        enemy_base_location_known=True,
        enemy_units_visible=0,
        enemy_structures_visible=0,
    )
    defaults.update(overrides)
    return GameStateSnapshot(**defaults)


def _policy() -> StrategicPolicy:
    return StrategicPolicy(Blackboard())


class TestDecisionTree:
    def test_defensive_hold_on_detected_all_in(self):
        belief = BeliefState(p_all_in=0.70)
        result = _policy().choose(_snapshot(), belief)
        assert result == MacroAction.DEFENSIVE_HOLD

    def test_drone_greed_early_game(self):
        snap = _snapshot(worker_count=12, base_count=1)
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.DRONE_GREED

    def test_no_drone_greed_if_attack_imminent(self):
        snap = _snapshot(worker_count=12, base_count=1)
        belief = BeliefState(p_attack_within_2min=0.8)
        result = _policy().choose(snap, belief)
        assert result != MacroAction.DRONE_GREED

    def test_fast_expand_when_one_base_saturated(self):
        snap = _snapshot(worker_count=16, base_count=1)
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.FAST_EXPAND

    def test_drone_greed_two_base_unsaturated(self):
        snap = _snapshot(worker_count=20, base_count=2)
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.DRONE_GREED

    def test_tech_to_roach_when_two_base_saturated(self):
        snap = _snapshot(
            worker_count=DRONE_TARGET_TWO_BASE,
            base_count=2,
            roach_warren_exists=False,
        )
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.TECH_TO_ROACH

    def test_drone_greed_three_base_unsaturated(self):
        snap = _snapshot(
            worker_count=DRONE_TARGET_TWO_BASE + 2,
            base_count=3,
            roach_warren_exists=True,
            army_supply=20,
        )
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.DRONE_GREED

    def test_standard_macro_when_building_army(self):
        snap = _snapshot(
            worker_count=DRONE_TARGET_TWO_BASE,
            base_count=2,
            roach_warren_exists=True,
            army_supply=20,
        )
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.STANDARD_MACRO

    def test_pressure_push_at_attack_threshold(self):
        # 2 bases: threshold = 2 * ATTACK_SUPPLY_PER_BASE = 40
        snap = _snapshot(
            worker_count=DRONE_TARGET_TWO_BASE,
            base_count=2,
            roach_warren_exists=True,
            army_supply=2 * ATTACK_SUPPLY_PER_BASE,
        )
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.PRESSURE_PUSH

    def test_standard_macro_below_scaled_threshold_three_base(self):
        # 3 bases: threshold = 3 * 20 = 60; army at 50 should still be STANDARD_MACRO
        snap = _snapshot(
            worker_count=DRONE_TARGET_THREE_BASE,
            base_count=3,
            roach_warren_exists=True,
            army_supply=50,
        )
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.STANDARD_MACRO

    def test_pressure_push_at_scaled_threshold_three_base(self):
        # 3 bases: threshold = 3 * 20 = 60
        snap = _snapshot(
            worker_count=DRONE_TARGET_THREE_BASE,
            base_count=3,
            roach_warren_exists=True,
            army_supply=3 * ATTACK_SUPPLY_PER_BASE,
        )
        result = _policy().choose(snap, BeliefState())
        assert result == MacroAction.PRESSURE_PUSH
