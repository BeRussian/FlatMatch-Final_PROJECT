"""
FlatMatch - TDD Unit Tests for Commute-Adjusted Budget Ceiling (Part 6)
========================================================================
Test Suite developed strictly before the implementation (TDD Red-Green-Refactor).
Tests the feature:
calculate_commute_adjusted_budget(base_budget: float, commute: CommuteMetrics) -> float
"""

import pytest
from flatmatch.models import CommuteMetrics
from flatmatch.services import calculate_commute_adjusted_budget


def test_commute_within_threshold_retains_full_budget():
    """Commute duration <= 20 minutes incurs zero financial deduction."""
    commute = CommuteMetrics(
        origin_address="Tel Aviv",
        dest_address="Givatayim",
        distance_km=4.5,
        duration_minutes=15.0,
        is_verified=True,
    )
    adjusted = calculate_commute_adjusted_budget(base_budget=3500.0, commute=commute)
    assert adjusted == 3500.0


def test_commute_exact_threshold_retains_full_budget():
    """Commute duration exactly equal to 20 minutes incurs zero financial deduction."""
    commute = CommuteMetrics(
        origin_address="Tel Aviv",
        dest_address="Ramat Gan",
        distance_km=6.0,
        duration_minutes=20.0,
        is_verified=True,
    )
    adjusted = calculate_commute_adjusted_budget(base_budget=3000.0, commute=commute)
    assert adjusted == 3000.0


def test_commute_exceeding_threshold_applies_linear_penalty():
    """Every minute over 20 reduces budget ceiling by 15.0 ILS."""
    # 30 min commute -> 10 minutes over threshold -> 10 * 15 = 150 ILS deduction
    commute = CommuteMetrics(
        origin_address="Rishon LeZion",
        dest_address="Tel Aviv University",
        distance_km=22.0,
        duration_minutes=30.0,
        is_verified=True,
    )
    adjusted = calculate_commute_adjusted_budget(base_budget=4000.0, commute=commute)
    assert adjusted == 3850.0


def test_commute_penalty_floors_at_zero():
    """Budget ceiling cannot become negative; floored at 0.0."""
    # Base budget 100 ILS, 40 min commute -> 20 min over * 15 = 300 ILS deduction
    commute = CommuteMetrics(
        origin_address="Haifa",
        dest_address="Beer Sheva",
        distance_km=150.0,
        duration_minutes=40.0,
        is_verified=True,
    )
    adjusted = calculate_commute_adjusted_budget(base_budget=100.0, commute=commute)
    assert adjusted == 0.0


def test_unverified_commute_retains_full_budget():
    """Unverified commute does not penalize seeker's financial budget."""
    commute = CommuteMetrics(
        origin_address="Unknown",
        dest_address="Unknown",
        distance_km=0.0,
        duration_minutes=0.0,
        is_verified=False,
    )
    adjusted = calculate_commute_adjusted_budget(base_budget=2800.0, commute=commute)
    assert adjusted == 2800.0


def test_negative_base_budget_raises_value_error():
    """Negative base budget is invalid and must raise ValueError."""
    commute = CommuteMetrics(
        origin_address="Tel Aviv",
        dest_address="Tel Aviv",
        distance_km=2.0,
        duration_minutes=10.0,
        is_verified=True,
    )
    with pytest.raises(ValueError, match="Base budget must be non-negative"):
        calculate_commute_adjusted_budget(base_budget=-500.0, commute=commute)


def test_invalid_commute_type_raises_type_error():
    """Invalid commute argument must raise TypeError."""
    with pytest.raises(TypeError, match="Expected CommuteMetrics"):
        calculate_commute_adjusted_budget(base_budget=3000.0, commute="not_a_commute_object")
