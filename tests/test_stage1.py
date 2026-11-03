"""
FlatMatch - Stage 1 Test Suite (10 Simple, Direct Tests)
=========================================================
These tests verify the core requirements defined in TASKS.md (Stage 1):
- Object-Oriented Models (Apartment, Preferences, ApartmentSeeker, RoommateSeeker)
- Data Validation and Dealbreaker Evaluation
- Collection Processing and Set Operations
- Context Managers and Rollback
- Repository Streaming and Lookup
"""

import pytest
from flatmatch.models import Preferences, Apartment, ApartmentSeeker, RoommateSeeker
from flatmatch.processing import compare_amenities
from flatmatch.context_managers import ApartmentHoldContext
from flatmatch.repository import FlatMatchRepository, parse_user_record


# ------------------------------------------------------------------------------
# Test 1: Apartment creation and computed rent_per_room
# ------------------------------------------------------------------------------
def test_apartment_creation_and_computed_rent_per_room():
    apt = Apartment(city="Tel Aviv", rent=4000.0, rooms=2)
    assert apt.city == "Tel Aviv"
    assert apt.rent == 4000.0
    assert apt.rooms == 2
    assert apt.rent_per_room == 2000.0


# ------------------------------------------------------------------------------
# Test 2: Apartment amenities operations (add, check, remove)
# ------------------------------------------------------------------------------
def test_apartment_amenities_operations():
    apt = Apartment(city="Haifa", rent=3000.0, rooms=1, amenities={"Balcony"})
    assert apt.has_amenity("Balcony") is True
    assert apt.has_amenity("Elevator") is False

    apt.add_amenity("Elevator")
    assert apt.has_amenity("Elevator") is True

    apt.remove_amenity("Balcony")
    assert apt.has_amenity("Balcony") is False


# ------------------------------------------------------------------------------
# Test 3: Preferences validation and lifestyle conflict detection
# ------------------------------------------------------------------------------
def test_preferences_validation_and_conflict_detection():
    # Cleanliness must be between 1 and 5
    with pytest.raises(ValueError):
        Preferences(cleanliness=6)

    # Conflict between smoker and non-smoker
    pref_smoker = Preferences(is_smoker=True)
    pref_non_smoker = Preferences(is_smoker=False)
    assert pref_smoker.has_conflict(pref_non_smoker) is True


# ------------------------------------------------------------------------------
# Test 4: User validation rejects underage applicants and invalid budget
# ------------------------------------------------------------------------------
def test_user_validation_rejects_underage_and_negative_budget():
    # Age under 18 must raise ValueError
    with pytest.raises(ValueError):
        ApartmentSeeker(
            name="Young Applicant",
            age=16,
            phone="050-0000001",
            max_budget=3000.0,
            preferred_cities=["Tel Aviv"]
        )

    # Budget <= 0 must raise ValueError
    with pytest.raises(ValueError):
        ApartmentSeeker(
            name="Valid Age",
            age=25,
            phone="050-0000002",
            max_budget=-500.0,
            preferred_cities=["Tel Aviv"]
        )


# ------------------------------------------------------------------------------
# Test 5: Dealbreakers evaluate to True (rejected) when rent exceeds budget
# ------------------------------------------------------------------------------
def test_dealbreakers_rejected_when_rent_exceeds_budget():
    seeker = ApartmentSeeker(
        name="Budget Seeker",
        age=24,
        phone="050-1111111",
        max_budget=2500.0,
        preferred_cities=["Tel Aviv"]
    )
    expensive_apt = Apartment(city="Tel Aviv", rent=4500.0, rooms=1)
    owner = RoommateSeeker(
        name="Apartment Owner",
        age=27,
        phone="050-2222222",
        apartment=expensive_apt
    )

    # Seeker budget (2500) < Rent (4500) -> Dealbreaker triggered (True)
    assert seeker.evaluate_dealbreakers(owner) is True


# ------------------------------------------------------------------------------
# Test 6: Dealbreakers evaluate to False (compatible) when criteria match
# ------------------------------------------------------------------------------
def test_dealbreakers_accepted_when_budget_and_city_match():
    pref = Preferences(is_smoker=False, allows_pets=False)
    seeker = ApartmentSeeker(
        name="Matching Seeker",
        age=26,
        phone="050-3333333",
        max_budget=3500.0,
        preferred_cities=["Tel Aviv"],
        preferences_OBJ=pref
    )
    matching_apt = Apartment(city="Tel Aviv", rent=3000.0, rooms=1)
    owner = RoommateSeeker(
        name="Matching Owner",
        age=28,
        phone="050-4444444",
        apartment=matching_apt,
        preferences_OBJ=pref
    )

    # Rent is within budget, city matches, and no preferences conflict
    assert seeker.evaluate_dealbreakers(owner) is False


# ------------------------------------------------------------------------------
# Test 7: ApartmentSeeker sorting by max_budget (__lt__)
# ------------------------------------------------------------------------------
def test_apartment_seeker_sorting_by_budget():
    seeker_low = ApartmentSeeker("Low", 22, "050-1000001", max_budget=2000.0, preferred_cities=["Haifa"])
    seeker_high = ApartmentSeeker("High", 29, "050-1000002", max_budget=4500.0, preferred_cities=["Tel Aviv"])

    assert seeker_low < seeker_high
    assert sorted([seeker_high, seeker_low]) == [seeker_low, seeker_high]


# ------------------------------------------------------------------------------
# Test 8: Set operations for amenities comparison
# ------------------------------------------------------------------------------
def test_compare_amenities_set_operations():
    desired = {"WiFi", "Balcony", "Elevator"}
    available = {"WiFi", "Balcony", "Parking"}

    result = compare_amenities(desired, available)
    assert result["matching"] == {"WiFi", "Balcony"}
    assert result["missing"] == {"Elevator"}


# ------------------------------------------------------------------------------
# Test 9: ApartmentHoldContext rolls back apartment status upon error
# ------------------------------------------------------------------------------
def test_apartment_hold_context_rolls_back_status_on_error():
    apt = Apartment(city="Jerusalem", rent=3200.0, rooms=1)
    apt.status = "AVAILABLE"

    with pytest.raises(RuntimeError):
        with ApartmentHoldContext(apt, "Applicant"):
            assert apt.status == "ON_HOLD"
            raise RuntimeError("Application processing error")

    # Guaranteed rollback
    assert apt.status == "AVAILABLE"


# ------------------------------------------------------------------------------
# Test 10: Repository loading and O(1) lookup by phone
# ------------------------------------------------------------------------------
def test_repository_load_and_get_by_phone():
    repo = FlatMatchRepository("data/sample_data.jsonl")
    users = repo.get_all_users()

    assert len(users) >= 15
    first_user = users[0]
    fetched_user = repo.get_by_phone(first_user.phone)

    assert fetched_user is not None
    assert fetched_user.name == first_user.name


# ------------------------------------------------------------------------------
# Test 11: Lecturer Feedback 1 - __repr__ implementation in central domain models
# ------------------------------------------------------------------------------
def test_lecturer_feedback_models_repr_implementation():
    pref = Preferences(cleanliness=4, allows_pets=True, is_smoker=False)
    assert "Preferences(" in repr(pref)
    assert "cleanliness=4" in repr(pref)

    apt = Apartment(city="Tel Aviv", rent=3500.0, rooms=2, amenities={"Balcony"})
    apt_repr = repr(apt)
    assert "Apartment(" in apt_repr
    assert "city='Tel Aviv'" in apt_repr
    assert "rent=3500.0" in apt_repr
    assert "rooms=2" in apt_repr

    seeker = ApartmentSeeker(
        name="Daniel Levin",
        age=25,
        phone="050-1000001",
        max_budget=3500.0,
        preferred_cities=["Tel Aviv"],
        preferences_OBJ=pref,
    )
    seeker_repr = repr(seeker)
    assert "ApartmentSeeker(" in seeker_repr
    assert "name='Daniel Levin'" in seeker_repr
    assert "phone='050-1000001'" in seeker_repr
    assert "max_budget=3500.0" in seeker_repr

    owner = RoommateSeeker(
        name="Doron Sela",
        age=27,
        phone="050-2000001",
        apartment=apt,
        preferences_OBJ=pref,
    )
    owner_repr = repr(owner)
    assert "RoommateSeeker(" in owner_repr
    assert "name='Doron Sela'" in owner_repr
    assert "phone='050-2000001'" in owner_repr
    assert "apartment=Apartment(" in owner_repr


# ------------------------------------------------------------------------------
# Test 12: Lecturer Feedback 2 - parse_user_record rejects unknown user types
# ------------------------------------------------------------------------------
def test_lecturer_feedback_parse_user_record_unknown_type():
    # 1. Unknown user type must raise ValueError
    unknown_record = {
        "name": "Alex",
        "age": 28,
        "phone": "050-9999999",
        "type": "guest_investor",
        "apartment": {"city": "Tel Aviv", "rent": 3000.0},
    }
    with pytest.raises(ValueError, match="Unknown or unsupported user type 'guest_investor'"):
        parse_user_record(unknown_record)

    # 2. Missing type with ambiguous fields must raise ValueError
    ambiguous_record = {
        "name": "Alex",
        "age": 28,
        "phone": "050-9999999",
    }
    with pytest.raises(ValueError, match="Record is missing valid 'type' key"):
        parse_user_record(ambiguous_record)

    # 3. Non-dict input must raise TypeError
    with pytest.raises(TypeError, match="Record must be a dict"):
        parse_user_record(["not", "a", "dict"])


