"""
FlatMatch - Part D Comprehensive Validation Suite
==================================================
Runs and verifies all components of Part D:
- Iterators and Iterables (iterators.py)
- Generator with yield and Lazy Pipeline (iterators.py)
- Streaming JSONL Ingestion and Repository (repository.py)
- SearchSessionContext and ApartmentHoldContext (context_managers.py)
"""

import os
from flatmatch.models import Apartment, ApartmentSeeker, Preferences
from flatmatch.iterators import (
    SeekerCollection,
    SeekerIterator,
    stream_budget_candidates,
    build_lazy_seeker_pipeline
)
from flatmatch.repository import stream_users_from_jsonl, FlatMatchRepository
from flatmatch.context_managers import SearchSessionContext, ApartmentHoldContext


def test_custom_iterators():
    print("Testing Custom Iterable and Independent Iterators...")
    seekers = [
        ApartmentSeeker("User A", 24, "050-0000001", 3000, ["Tel Aviv"]),
        ApartmentSeeker("User B", 26, "050-0000002", 3500, ["Haifa"]),
        ApartmentSeeker("User C", 28, "050-0000003", 4000, ["Jerusalem"])
    ]
    col = SeekerCollection(seekers)
    assert len(col) == 3

    it1 = iter(col)
    it2 = iter(col)

    assert next(it1).name == "User A"
    assert next(it1).name == "User B"
    assert next(it2).name == "User A"
    assert it1.cursor == 2
    assert it2.cursor == 1
    assert next(it1).name == "User C"

    try:
        next(it1)
        assert False, "Should raise StopIteration"
    except StopIteration:
        pass
    print(" -> Custom Iterators test passed.")


def test_generator_lifecycle():
    print("Testing Generator with yield Lifecycle...")
    seekers = [
        ApartmentSeeker("Low", 22, "050-0000011", 2500, ["Tel Aviv"]),
        ApartmentSeeker("High", 24, "050-0000012", 4500, ["Tel Aviv"]),
        ApartmentSeeker("Mid", 25, "050-0000013", 3000, ["Tel Aviv"])
    ]
    gen = stream_budget_candidates(seekers, 3200)
    first = next(gen)
    assert first.name == "Low"

    resumed = list(gen)
    assert len(resumed) == 1
    assert resumed[0].name == "Mid"

    # Exhausted generator test
    assert list(gen) == []
    print(" -> Generator lifecycle test passed.")


def test_lazy_pipeline():
    print("Testing 3-Stage Lazy Pipeline...")
    pref_high = Preferences(cleanliness=5)
    pref_low = Preferences(cleanliness=2)
    seekers = [
        ApartmentSeeker("Cand 1", 22, "050-0000021", 3000, ["Tel Aviv"], pref_high),
        ApartmentSeeker("Cand 2", 23, "050-0000022", 3200, ["Haifa"], pref_high),     # Filtered by city
        ApartmentSeeker("Cand 3", 24, "050-0000023", 3100, ["Tel Aviv"], pref_low),      # Filtered by cleanliness
        ApartmentSeeker("Cand 4", 25, "050-0000024", 3300, ["Tel Aviv"], pref_high),
        ApartmentSeeker("Cand 5", 26, "050-0000025", 3400, ["Tel Aviv"], pref_high)
    ]
    pipeline = build_lazy_seeker_pipeline(seekers, "Tel Aviv", min_cleanliness=4)
    item1 = next(pipeline)
    item2 = next(pipeline)

    assert "Cand 1" in item1
    assert "Cand 4" in item2
    print(" -> Lazy pipeline test passed.")


def test_streaming_and_repository():
    print("Testing Streaming JSONL Reader and FlatMatchRepository...")
    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    repo = FlatMatchRepository(data_path)
    assert len(repo) == 20
    assert len(repo.get_apartment_seekers()) == 15
    assert len(repo.get_roommate_seekers()) == 5

    user = repo.get_by_phone("050-1000001")
    assert user is not None
    assert user.name == "Daniel Levin"
    assert repo.get_by_phone("050-0000000") is None
    print(" -> Repository streaming and lookup test passed.")


def test_context_managers():
    print("Testing Context Managers...")
    # SearchSessionContext normal
    with SearchSessionContext("Alice", "SES-T1") as session:
        session.record_evaluation(3)
        session.record_match("Match 1")
    assert session.status == "COMPLETED"

    # SearchSessionContext exception handling
    err_propagated = False
    try:
        with SearchSessionContext("Alice", "SES-T2") as session:
            raise KeyError("Simulated key error")
    except KeyError:
        err_propagated = True
    assert err_propagated
    assert session.status == "ABORTED_WITH_ERROR"

    # ApartmentHoldContext normal
    apt = Apartment("Tel Aviv", 3000, rooms=2)
    apt.status = "AVAILABLE"
    with ApartmentHoldContext(apt, "Candidate 1"):
        assert apt.status == "ON_HOLD"
    assert apt.status == "AVAILABLE"

    # ApartmentHoldContext exception rollback
    err_propagated = False
    try:
        with ApartmentHoldContext(apt, "Candidate 2"):
            assert apt.status == "ON_HOLD"
            raise ValueError("Invalid document")
    except ValueError:
        err_propagated = True
    assert err_propagated
    assert apt.status == "AVAILABLE"
    print(" -> Context managers test passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING ALL PART D VERIFICATION TESTS")
    print("==================================================")
    test_custom_iterators()
    test_generator_lifecycle()
    test_lazy_pipeline()
    test_streaming_and_repository()
    test_context_managers()
    print("==================================================")
    print("ALL PART D TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")
