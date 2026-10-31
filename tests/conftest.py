"""
Shared Pytest Fixtures for FlatMatch Test Suite
"""

import pytest
from unittest.mock import MagicMock
from flatmatch.models import (
    Preferences,
    Apartment,
    ApartmentSeeker,
    RoommateSeeker,
    CommuteMetrics,
)
from flatmatch.api_client import CommuteAPIClient


@pytest.fixture
def sample_preferences():
    return Preferences(
        cleanliness=4,
        allows_pets=True,
        is_smoker=False,
        sleep_schedule="morning_person",
        kashrut_level="hiloni",
        shabbat_observant=False,
    )


@pytest.fixture
def sample_apartment():
    return Apartment(
        city="Tel Aviv",
        rent=3400.0,
        rooms=2,
        amenities={"Air Conditioner", "Balcony", "Elevator"},
        address="Dizengoff 100, Tel Aviv",
    )


@pytest.fixture
def sample_seeker():
    return ApartmentSeeker(
        name="Noa Bar",
        age=24,
        phone="050-9990001",
        max_budget=3800.0,
        destination_address="אוניברסיטת תל אביב",
        preferences=Preferences(
            cleanliness=4,
            allows_pets=True,
            is_smoker=False,
            sleep_schedule="morning_person",
            kashrut_level="hiloni",
            shabbat_observant=False,
        ),
        max_commute_minutes=35.0,
    )


@pytest.fixture
def sample_owner(sample_apartment):
    return RoommateSeeker(
        name="Omer Cohen",
        age=26,
        phone="050-9990002",
        apartment=sample_apartment,
        preferences=Preferences(
            cleanliness=4,
            allows_pets=True,
            is_smoker=False,
            sleep_schedule="morning_person",
            kashrut_level="hiloni",
            shabbat_observant=False,
        ),
    )


@pytest.fixture
def mock_successful_http_get():
    """Mock returning successful OSRM route payload."""
    def _mock_get(url, params=None, timeout=None):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 8500.0,   # 8.5 km
                    "duration": 1080.0,   # 18.0 min
                }
            ],
        }
        return resp
    return _mock_get


@pytest.fixture
def mock_api_client(mock_successful_http_get):
    return CommuteAPIClient(
        http_get=mock_successful_http_get,
        sleep_func=lambda s: None,
        max_retries=3,
        retry_delay=0.0,
    )
