"""
Unit tests for Domain Models and Address Normalizer
"""

import pytest
from flatmatch.models import ApartmentSeeker, RoommateSeeker, Apartment, CommuteMetrics
from flatmatch.address_normalizer import normalize_address, AddressNormalizer


@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        ('ת"א', "תל אביב"),
        ("אונו", "הקריה האקדמית אונו, קרית אונו"),
        ("טכניון", "הטכניון, חיפה"),
        ("עברית", "האוניברסיטה העברית, ירושלים"),
        ("בן גוריון", "אוניברסיטת בן-גוריון, באר שבע"),
        ("רחוב רוטשילד 10, תל אביב", "רחוב רוטשילד 10, תל אביב"),  # unfamiliar string passes safely
    ],
)
def test_address_normalizer_parametrized(raw_input, expected_output):
    """Verifies that address normalizer handles acronyms and safely preserves raw addresses."""
    assert normalize_address(raw_input) == expected_output
    assert AddressNormalizer.normalize(raw_input) == expected_output


def test_apartment_seeker_destination_and_commute_properties(sample_seeker):
    """Verifies ApartmentSeeker destination address and commute minutes."""
    assert sample_seeker.destination_address == "אוניברסיטת תל אביב"
    assert sample_seeker.max_commute_minutes == 35.0
    # Backward compatibility check
    assert "אוניברסיטת תל אביב" in sample_seeker.preferred_cities


def test_commute_metrics_formatting():
    """Verifies CommuteMetrics attributes and string representations."""
    metrics = CommuteMetrics(
        origin_address="Dizengoff, Tel Aviv",
        dest_address="TAU",
        distance_km=7.2,
        duration_minutes=22.5,
        is_verified=True,
    )
    assert metrics.distance_km == 7.2
    assert metrics.duration_minutes == 22.5
    assert metrics.is_verified is True
    assert "22.5 min" in str(metrics)
    assert "7.2 km" in str(metrics)


def test_apartment_model_default_address(sample_apartment):
    """Verifies Apartment address initialization and rent calculations."""
    assert sample_apartment.address == "Dizengoff 100, Tel Aviv"
    assert sample_apartment.rent_per_room == 1700.0
    assert "Air Conditioner" in sample_apartment.amenities
