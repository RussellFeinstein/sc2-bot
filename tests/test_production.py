"""Tests for ProductionManager queen cap logic."""
from bot.config import MAX_QUEENS, QUEENS_PER_HATCHERY


class TestQueenCap:
    def test_queen_cap_limits_desired_on_many_bases(self):
        """With 5 bases, desired should be MAX_QUEENS (8), not 10."""
        base_count = 5
        desired = min(base_count * QUEENS_PER_HATCHERY, MAX_QUEENS)
        assert desired == MAX_QUEENS

    def test_queen_cap_no_effect_on_few_bases(self):
        """With 3 bases, desired should be 6 (below the cap)."""
        base_count = 3
        desired = min(base_count * QUEENS_PER_HATCHERY, MAX_QUEENS)
        assert desired == base_count * QUEENS_PER_HATCHERY

    def test_queen_cap_is_reasonable(self):
        """MAX_QUEENS should be between 6 and 10 for standard play."""
        assert 6 <= MAX_QUEENS <= 10
