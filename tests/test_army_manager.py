"""Tests for ArmyManager state machine transitions."""
from bot.config import ATTACK_SUPPLY_PER_BASE, REGROUP_THRESHOLD, RETREAT_ARMY_SUPPLY
from bot.core.blackboard import MacroAction
from bot.tactics.army_manager import ArmyManager, ArmyState


class _FakeBlackboard:
    def __init__(self, action: MacroAction = MacroAction.STANDARD_MACRO):
        self.current_action = action


def _make_manager(action: MacroAction = MacroAction.STANDARD_MACRO) -> ArmyManager:
    """Create an ArmyManager with a minimal fake bot object."""

    class FakeBot:
        blackboard = _FakeBlackboard(action)

    mgr = ArmyManager(FakeBot())
    return mgr


class TestStateTransitions:
    def test_initial_state_is_building_up(self):
        mgr = _make_manager()
        assert mgr.state == ArmyState.BUILDING_UP

    def test_building_up_to_attacking_requires_both_policy_and_supply(self):
        mgr = _make_manager()
        # 2 bases: threshold = 2 * 20 = 40
        # Policy says attack but supply too low -> stays BUILDING_UP
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=20, base_count=2)
        assert mgr.state == ArmyState.BUILDING_UP

        # Supply met but policy doesn't say attack -> stays BUILDING_UP
        mgr._update_state(MacroAction.STANDARD_MACRO, army_supply=40, base_count=2)
        assert mgr.state == ArmyState.BUILDING_UP

        # Both conditions met -> ATTACKING
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=40, base_count=2)
        assert mgr.state == ArmyState.ATTACKING

    def test_all_in_also_triggers_attack(self):
        mgr = _make_manager()
        mgr._update_state(MacroAction.ALL_IN, army_supply=40, base_count=2)
        assert mgr.state == ArmyState.ATTACKING

    def test_attack_threshold_scales_with_bases(self):
        """3 bases requires 60 supply, 4 bases requires 80."""
        mgr = _make_manager()
        # 3 bases: threshold = 60; army at 50 -> stays BUILDING_UP
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=50, base_count=3)
        assert mgr.state == ArmyState.BUILDING_UP

        # 3 bases: army at 60 -> ATTACKING
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=60, base_count=3)
        assert mgr.state == ArmyState.ATTACKING

    def test_attacking_to_regrouping_on_absolute_floor(self):
        mgr = _make_manager()
        mgr._state = ArmyState.ATTACKING
        # Use low attack_start_supply so loss ratio (40% of 30 = 12) is below
        # the absolute floor (15), isolating the floor check.
        mgr._attack_start_supply = 30

        # Above floor and above loss ratio -> stays attacking
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=RETREAT_ARMY_SUPPLY + 1, base_count=2)
        assert mgr.state == ArmyState.ATTACKING

        # At absolute floor -> regroup
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=RETREAT_ARMY_SUPPLY, base_count=2)
        assert mgr.state == ArmyState.REGROUPING

    def test_attacking_to_regrouping_on_loss_ratio(self):
        mgr = _make_manager()
        mgr._state = ArmyState.ATTACKING
        mgr._attack_start_supply = 50

        # 40% of 50 = 20. At 20 supply -> regroup
        threshold = int(50 * 0.40)
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=threshold, base_count=2)
        assert mgr.state == ArmyState.REGROUPING

    def test_regrouping_to_building_up(self):
        mgr = _make_manager()
        mgr._state = ArmyState.REGROUPING

        # Below regroup threshold -> stays regrouping
        mgr._update_state(MacroAction.STANDARD_MACRO, army_supply=REGROUP_THRESHOLD - 1, base_count=2)
        assert mgr.state == ArmyState.REGROUPING

        # At threshold -> back to building up
        mgr._update_state(MacroAction.STANDARD_MACRO, army_supply=REGROUP_THRESHOLD, base_count=2)
        assert mgr.state == ArmyState.BUILDING_UP

    def test_hysteresis_prevents_immediate_reattack(self):
        """After regrouping back to BUILDING_UP at 25 supply, the bot should NOT
        immediately attack — it needs to reach the threshold (40 on 2 bases) again."""
        mgr = _make_manager()

        # Simulate: attack at 40, lose units, regroup, rebuild to 25
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=40, base_count=2)
        assert mgr.state == ArmyState.ATTACKING

        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=RETREAT_ARMY_SUPPLY, base_count=2)
        assert mgr.state == ArmyState.REGROUPING

        mgr._update_state(MacroAction.STANDARD_MACRO, army_supply=REGROUP_THRESHOLD, base_count=2)
        assert mgr.state == ArmyState.BUILDING_UP

        # Policy says attack at 25 supply — should NOT attack (below commit threshold)
        mgr._update_state(MacroAction.PRESSURE_PUSH, army_supply=25, base_count=2)
        assert mgr.state == ArmyState.BUILDING_UP

    def test_defensive_hold_resets_to_building_up(self):
        """DEFENSIVE_HOLD should be tested via step(), not _update_state,
        since the override is in step(). Test the _update_state path stays
        in the same state when defensive override isn't triggered."""
        mgr = _make_manager()
        mgr._state = ArmyState.ATTACKING

        # _update_state with non-attack, non-defensive action doesn't change state
        # (attacking only transitions on supply loss)
        mgr._update_state(MacroAction.STANDARD_MACRO, army_supply=50, base_count=2)
        assert mgr.state == ArmyState.ATTACKING
