"""
Unit tests for Core Services, Strategy Pattern, Factory Pattern, and Observers
"""

import pytest
from unittest.mock import MagicMock
from flatmatch.factories import UserFactory
from flatmatch.models import ApartmentSeeker, RoommateSeeker, CommuteMetrics
from flatmatch.strategies import BudgetFocusedStrategy, CommuteAndLifestyleStrategy
from flatmatch.observers import MatchStatisticsObserver, ApplicantNotificationObserver
from flatmatch.services import FlatMatchService
from flatmatch.api_client import CommuteAPIClient, APIConnectionError


def test_factory_creates_apartment_seeker():
    """Verifies UserFactory instantiates an ApartmentSeeker correctly."""
    data = {
        "name": "Dana Levi",
        "age": 23,
        "phone": "052-1110001",
        "type": "apartment_seeker",
        "max_budget": 3200.0,
        "destination_address": "Tel Aviv University",
        "max_commute_minutes": 30.0,
        "preferences": {
            "cleanliness": 4,
            "allows_pets": True,
            "is_smoker": False,
            "sleep_schedule": "morning_person",
            "kashrut_level": "hiloni",
            "shabbat_observant": False,
        },
    }
    user = UserFactory.create_user(data)
    assert isinstance(user, ApartmentSeeker)
    assert user.name == "Dana Levi"
    assert user.max_budget == 3200.0
    assert user.destination_address == "Tel Aviv University"


def test_factory_creates_roommate_seeker():
    """Verifies UserFactory instantiates a RoommateSeeker correctly."""
    data = {
        "name": "Eyal Golan",
        "age": 28,
        "phone": "052-1110002",
        "type": "roommate_seeker",
        "apartment": {
            "city": "Tel Aviv",
            "rent": 4000.0,
            "rooms": 2,
            "amenities": ["Air Conditioner"],
            "address": "Gordon 12, Tel Aviv",
        },
        "preferences": {
            "cleanliness": 3,
            "allows_pets": False,
            "is_smoker": False,
            "sleep_schedule": "flexible",
            "kashrut_level": "hiloni",
            "shabbat_observant": False,
        },
    }
    user = UserFactory.create_user(data)
    assert isinstance(user, RoommateSeeker)
    assert user.name == "Eyal Golan"
    assert user.apartment.city == "Tel Aviv"


def test_factory_invalid_inputs_raise_errors():
    """Verifies UserFactory validates input types and schema."""
    with pytest.raises(TypeError):
        UserFactory.create_user(["not_a_dict"])

    with pytest.raises(ValueError, match="Unknown or unsupported user type"):
        UserFactory.create_user({"type": "invalid_type", "name": "A", "age": 20, "phone": "050-1"})


def test_strategies_produce_distinct_evaluation_scores(sample_seeker, sample_owner):
    """Verifies that interchangeable strategies compute distinct normalized scores."""
    commute = CommuteMetrics(
        origin_address="Tel Aviv",
        dest_address="TAU",
        distance_km=5.0,
        duration_minutes=15.0,
        is_verified=True,
    )
    budget_strat = BudgetFocusedStrategy()
    lifestyle_strat = CommuteAndLifestyleStrategy()

    score_budget = budget_strat.calculate_score(sample_seeker, sample_owner, commute)
    score_lifestyle = lifestyle_strat.calculate_score(sample_seeker, sample_owner, commute)

    assert 0.0 <= score_budget <= 100.0
    assert 0.0 <= score_lifestyle <= 100.0
    assert score_budget != score_lifestyle


def test_service_evaluates_candidate_approved(mock_api_client, budget_strategy, sample_seeker, sample_owner):
    """Verifies FlatMatchService coordinates evaluation, returning APPROVED status."""
    stats_observer = MatchStatisticsObserver()
    notification_observer = ApplicantNotificationObserver()

    service = FlatMatchService(
        api_client=mock_api_client,
        strategy=budget_strategy,
        observers=[stats_observer, notification_observer],
        max_commute_minutes=40.0,
    )

    result = service.evaluate_candidate_match(sample_seeker, sample_owner)
    assert result.is_approved is True
    assert result.status == "APPROVED"
    assert result.score > 0.0

    # Verify observers were notified
    assert stats_observer.total_evaluated == 1
    assert stats_observer.verified_commutes == 1
    assert len(notification_observer.notifications) == 1
    assert "MATCH APPROVED" in notification_observer.notifications[0]


def test_service_graceful_fallback_on_api_error(budget_strategy, sample_seeker, sample_owner):
    """Verifies that API connection failures engage Graceful Fallback without crashing."""
    def failing_http_get(*args, **kwargs):
        raise APIConnectionError("Network disconnected")

    failing_client = CommuteAPIClient(http_get=failing_http_get, max_retries=1)
    stats_observer = MatchStatisticsObserver()

    service = FlatMatchService(
        api_client=failing_client,
        strategy=budget_strategy,
        observers=[stats_observer],
    )

    result = service.evaluate_candidate_match(sample_seeker, sample_owner)
    assert result.is_approved is False
    assert result.status == "FALLBACK_UNVERIFIED"
    assert result.commute_metrics.is_verified is False
    assert stats_observer.api_fallbacks == 1


def test_service_dealbreaker_rejection(mock_api_client, budget_strategy, sample_seeker, sample_owner):
    """Verifies that lifestyle dealbreakers reject match immediately with score 0.0."""
    # Introduce dealbreaker: seeker demands no smoking, owner is a heavy smoker
    sample_owner.preferences.is_smoker = True
    sample_seeker.preferences.is_smoker = False

    service = FlatMatchService(api_client=mock_api_client, strategy=budget_strategy)
    result = service.evaluate_candidate_match(sample_seeker, sample_owner)

    assert result.is_approved is False
    assert result.status == "REJECTED_DEALBREAKER"
    assert result.score == 0.0
