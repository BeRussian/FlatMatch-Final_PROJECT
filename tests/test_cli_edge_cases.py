"""
Automated Pytest Suite for CLI Edge Cases, Validation, and Extreme Scenarios
"""

import sys
import subprocess
import pytest
from flatmatch import (
    Apartment,
    ApartmentSeeker,
    RoommateSeeker,
    Preferences,
    AddressNormalizer,
    NominatimGeocodingClient,
    CommuteAPIClient,
    FlatMatchRepository,
)


def test_edge_case_unfamiliar_or_garbage_address_fallback():
    """Edge Case: Completely weird or non-existent address string should not crash geocoder or normalizer."""
    garbage_input = "@@##$$ Strange Place 123456 Nowhere"
    normalized = AddressNormalizer.normalize(garbage_input)
    assert isinstance(normalized, str)

    geocoder = NominatimGeocodingClient(use_live_network=False)
    coords = geocoder.geocode(normalized)
    assert isinstance(coords, tuple)
    assert len(coords) == 2
    # Verify fallback coordinates returned safely
    assert coords == (34.7818, 32.0853)


def test_edge_case_extreme_low_budget_filters_all_apartments():
    """Edge Case: Seeker with tiny budget (500 NIS) should have 0 matches and 30 rejections."""
    repo = FlatMatchRepository("data/sample_data.jsonl")
    owners = repo.get_roommate_seekers()
    
    seeker = ApartmentSeeker(
        name="Penniless Seeker",
        age=20,
        phone="050-0000001",
        max_budget=500.0,
        destination_address="Kiryat Ono",
        max_commute_minutes=60.0,
        preferences=Preferences(cleanliness=4, allows_pets=True, is_smoker=False)
    )

    matches = [o for o in owners if not seeker.evaluate_dealbreakers(o)]
    assert len(matches) == 0  # 100% filtered out by budget dealbreaker!


def test_edge_case_strict_smoker_dealbreaker():
    """Edge Case: Smoker seeker should be rejected by all non-smoking apartment hosts."""
    repo = FlatMatchRepository("data/sample_data.jsonl")
    owners = repo.get_roommate_seekers()

    seeker = ApartmentSeeker(
        name="Heavy Smoker",
        age=28,
        phone="050-0000002",
        max_budget=5000.0,
        destination_address="Tel Aviv",
        max_commute_minutes=60.0,
        preferences=Preferences(cleanliness=3, allows_pets=True, is_smoker=True)
    )

    non_smoking_hosts = [o for o in owners if not o.preferences.is_smoker]
    for host in non_smoking_hosts:
        assert seeker.evaluate_dealbreakers(host) is True  # Must be rejected


def test_edge_case_super_short_commute_threshold():
    """Edge Case: Max commute of 5 minutes should filter out all distant cities."""
    client = CommuteAPIClient()
    # Haifa to Tel Aviv
    commute = client.fetch_commute_metrics(
        origin_coords=(34.9896, 32.794),
        dest_coords=(34.7818, 32.0853),
        origin_address="Haifa",
        dest_address="Tel Aviv",
    )
    assert commute.duration_minutes > 5.0


def test_edge_case_city_validation_resilience():
    """Edge Case: City names with hyphens, apostrophes, lower case, extra spaces."""
    assert Apartment.is_valid_city("tel aviv")
    assert Apartment.is_valid_city("be'er sheva")
    assert Apartment.is_valid_city("beersheva")
    assert Apartment.is_valid_city("beer-sheva")
    assert Apartment.is_valid_city("modi'in")
    assert Apartment.is_valid_city("modiin")
    assert Apartment.is_valid_city("kiryat ono")
    assert Apartment.is_valid_city("kiryat-ono")
    assert Apartment.is_valid_city("Qiryat Ono")
    assert Apartment.is_valid_city("   Haifa   ")
    # Non-existent fictional cities must be rejected
    assert not Apartment.is_valid_city("Gotham City")
    assert not Apartment.is_valid_city("Atlantis")
    assert not Apartment.is_valid_city("")
    assert not Apartment.is_valid_city(None)


def test_cli_execution_with_malformed_inputs_and_recovery():
    """
    Subprocess simulation of CLI handling bad inputs:
    - Bad age string ('notanage'), then negative ('-5'), then valid '25'
    - Bad budget string ('free'), then negative ('-500'), then valid '3600'
    - Bad destination number ('99'), then valid preset '1'
    - Bad cleanliness ('9'), then valid '4'
    """
    inputs = (
        "Fault Tolerant User\n"
        "notanage\n-5\n25\n"      # Age recovery
        "050-7778899\n"
        "free\n-500\n3600\n"      # Budget recovery
        "99\n1\n"                 # Destination: invalid preset 99, then preset 1
        "30\n"                    # Max commute
        "\n\n"                    # Smoking, pets defaults
        "9\n4\n"                  # Cleanliness: invalid 9, then 4
        "\n\n\n"                  # Sleep, kashrut, shabbat defaults
    )

    res = subprocess.run(
        [sys.executable, "interactive_matcher.py", "--mock"],
        input=inputs,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    assert res.returncode == 0
    assert "Invalid input. Expected an integer number." in res.stdout
    assert "Please enter a whole number between 18 and 120." in res.stdout
    assert "Please enter a number greater than or equal to 500.0." in res.stdout
    assert "USER REGISTERED SUCCESSFULLY" in res.stdout
    assert "SUCCESS:" in res.stdout and "Found" in res.stdout


def test_preferences_three_way_conflict_and_flexible_logic():
    """Verify 3-way smoking and pets logic: flexible never conflicts with True or False."""
    p_strict_yes = Preferences(is_smoker=True, allows_pets=True)
    p_strict_no = Preferences(is_smoker=False, allows_pets=False)
    p_flexible = Preferences(is_smoker="flexible", allows_pets="flexible")

    # Strict True vs Strict False must conflict
    assert p_strict_yes.has_conflict(p_strict_no) is True
    assert p_strict_no.has_conflict(p_strict_yes) is True

    # Same values never conflict
    assert p_strict_yes.has_conflict(p_strict_yes) is False
    assert p_strict_no.has_conflict(p_strict_no) is False
    assert p_flexible.has_conflict(p_flexible) is False

    # Flexible NEVER conflicts with True or False
    assert p_flexible.has_conflict(p_strict_yes) is False
    assert p_flexible.has_conflict(p_strict_no) is False
    assert p_strict_yes.has_conflict(p_flexible) is False
    assert p_strict_no.has_conflict(p_flexible) is False


def test_interactive_host_cli_execution():
    """Subprocess simulation of interactive_host.py finding compatible seekers."""
    inputs = (
        "Sarah Host\n"
        "29\n"
        "054-9998877\n"
        "Tel Aviv\n"
        "Dizengoff 100\n"
        "7000\n"             # Total rent (3,500 per room)
        "2\n"                # 2 rooms
        "\n\n\n\n\n"         # Amenities defaults
        "3\n"                # Smoking: 3 (flexible)
        "3\n"                # Pets: 3 (flexible)
        "4\n"                # Cleanliness: 4
        "morning_person\n"
        "1\n"                # Kashrut: 1 (secular)
        "n\n"                # Shabbat: n
    )

    res = subprocess.run(
        [sys.executable, "interactive_host.py", "--mock"],
        input=inputs,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    assert res.returncode == 0
    assert "HOST APARTMENT REGISTERED SUCCESSFULLY" in res.stdout
    assert "ROOMMATE MATCH RESULTS FOR HOST SARAH HOST" in res.stdout
    assert "Found" in res.stdout
    assert "Match Score:" in res.stdout
    assert "HOST MATCHING SESSION COMPLETED" in res.stdout


