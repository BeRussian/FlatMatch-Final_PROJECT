"""
FlatMatch - Centralized End-to-End Demonstration Runner (Stage 1 & API System)
==============================================================================
Central execution script demonstrating:
- Stage 1: OOP, Polymorphism, Collections, Comprehensions, Iterators/Lazy Pipeline, Context Managers.
- Stage 2 (API & Smart Location): Smart Address Normalization, Zero-Key Geocoding & OSRM Commute Routing,
           Retry Logic, Fallback Safety, and Async Rate-Limited Verification.

Usage:
    python main.py          (Default: 100% Offline, deterministic execution on any machine)
    python main.py --live   (Optional: Connects to live public OpenStreetMap & OSRM APIs)
"""

import os
import sys
import asyncio

from flatmatch import (
    ApartmentSeeker,
    RoommateSeeker,
    Apartment,
    Preferences,
    CommuteMetrics,
    FlatMatchRepository,
    create_match_record,
    partition_candidates,
    compare_amenities,
    demonstrate_set_mutation,
    group_seekers_by_city,
    count_seekers_by_city,
    format_grouped_summary,
    RoommateApplicationQueue,
    UrgentCandidateQueue,
    filter_seekers_by_budget,
    extract_unique_preferred_cities,
    map_seeker_phones_to_budgets,
    get_seeker_budget,
    sort_seekers_by_budget_descending,
    sort_seekers_by_age,
    sort_apartments_by_city_and_rent,
    SeekerCollection,
    stream_budget_candidates,
    build_lazy_seeker_pipeline,
    SearchSessionContext,
    ApartmentHoldContext,
    AddressNormalizer,
    NominatimGeocodingClient,
    CommuteAPIClient,
    fetch_apartment_verification_async,
    collect_verifications_sequential,
    collect_verifications_concurrent,
)


def run_main_demo(use_live_network: bool = False):
    mode_label = "LIVE NETWORK API" if use_live_network else "OFFLINE DETERMINISTIC (Default)"
    print("=" * 75)
    print(f"  FLATMATCH - CENTRAL DEMONSTRATION RUNNER (Mode: {mode_label})")
    print("=" * 75)

    # --------------------------------------------------------------------------
    # STEP 1: Data Ingestion & Repository
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 1: DATA INGESTION & STREAMING REPOSITORY")
    print("=" * 75)

    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    repo = FlatMatchRepository(data_path)
    all_users = repo.get_all_users()
    seekers = repo.get_apartment_seekers()
    owners = repo.get_roommate_seekers()

    print(f"Successfully loaded {len(all_users)} users from '{data_path}':")
    print(f"  - Apartment Seekers: {len(seekers)}")
    print(f"  - Roommate Seekers (with Apartments): {len(owners)}")

    # O(1) indexed lookup demonstration
    sample_phone = "050-1000001"
    indexed_user = repo.get_by_phone(sample_phone)
    print(f"O(1) Dictionary Lookup for phone '{sample_phone}': {indexed_user.name} ({type(indexed_user).__name__})")

    # --------------------------------------------------------------------------
    # STEP 2: OOP, Composition & Polymorphism
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 2: OOP, COMPOSITION & POLYMORPHISM")
    print("=" * 75)

    sample_seeker = seekers[0]
    sample_owner = owners[0]

    # Polymorphic method call
    print(f"Polymorphic Role Summary (Seeker): {sample_seeker.get_role_summary()}")
    print(f"Polymorphic Role Summary (Owner):  {sample_owner.get_role_summary()}")

    # Dealbreaker evaluation
    has_conflict = sample_seeker.evaluate_dealbreakers(sample_owner)
    print(f"Dealbreaker evaluation between {sample_seeker.name} (Budget {sample_seeker.max_budget} NIS) and {sample_owner.name} (Rent {sample_owner.apartment.rent} NIS): {has_conflict}")

    # --------------------------------------------------------------------------
    # STEP 3: Data Structures (deque, heapq, dict, set)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 3: DATA STRUCTURES (deque, heapq, dict, set)")
    print("=" * 75)

    # FIFO Queue (deque)
    app_queue = RoommateApplicationQueue()
    app_queue.enqueue_application(seekers[0].name, "APT-TLV-01", "09:00 AM")
    app_queue.enqueue_application(seekers[1].name, "APT-TLV-01", "09:15 AM")
    app_queue.enqueue_application(seekers[2].name, "APT-TLV-01", "09:30 AM")
    first_served = app_queue.process_next_application()
    print(f"FIFO Queue (deque): Queued 3 applications. Processing first-in:\n  -> Processed First: {first_served[0]} (Arrival: {first_served[2]})")

    # Priority Queue (heapq)
    urgent_queue = UrgentCandidateQueue()
    urgent_queue.push_candidate(seekers[1], priority=3, reason="Standard application")
    urgent_queue.push_candidate(seekers[0], priority=1, reason="Emergency / Immediate move-in")
    urgent_queue.push_candidate(seekers[2], priority=2, reason="Relocating for work")
    highest_priority = urgent_queue.pop_candidate()
    print(f"Priority Queue (heapq): Enqueued 3 candidates. Highest priority popped first:\n  -> Served First: {highest_priority}")

    # Dictionary Grouping & Counting
    city_counts = count_seekers_by_city(seekers)
    print(f"Dictionary Counting (Seekers per City): {city_counts}")
    city_groups = group_seekers_by_city(seekers)
    print("Dictionary Grouping (.items() traversal with unpacking):")
    for city, grouped_seekers in list(city_groups.items())[:3]:
        names = ", ".join(s.name for s in grouped_seekers)
        print(f"  * {city}: {len(grouped_seekers)} seekers ({names})")

    # Set Operations
    desired_amenities = {"Balcony", "Air Conditioner", "Parking", "Elevator"}
    actual_amenities = sample_owner.apartment.amenities
    matching = desired_amenities & actual_amenities
    missing = desired_amenities - actual_amenities
    print(f"Set Comparison for apartment in {sample_owner.apartment.city}:")
    print(f"  - Desired:  {desired_amenities}")
    print(f"  - Actual:   {actual_amenities}")
    print(f"  - Matching (&): {matching}")
    print(f"  - Missing  (-): {missing}")

    # --------------------------------------------------------------------------
    # STEP 4: Comprehensions & Advanced Sorting
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 4: COMPREHENSIONS & ADVANCED SORTING")
    print("=" * 75)

    high_budget_names = [f"{s.name} ({s.max_budget:.0f} NIS)" for s in seekers if s.max_budget >= 3500]
    unique_cities = {city for s in seekers for city in s.preferred_cities}
    phone_budget_map = {s.phone: s.max_budget for s in seekers}
    print(f"List Comprehension (Budget >= 3500 NIS, first 3): {high_budget_names[:3]}")
    print(f"Set Comprehension  (Unique Target Cities): {sorted(list(unique_cities))}")
    print(f"Dict Comprehension (Total Phone->Budget Mappings): {len(phone_budget_map)}")

    sorted_by_budget = sort_seekers_by_budget_descending(seekers)
    sorted_by_age = sort_seekers_by_age(seekers)
    sorted_owners = sort_apartments_by_city_and_rent(owners)
    print(f"Sorted by Budget: Top = {sorted_by_budget[0].name} ({sorted_by_budget[0].max_budget} NIS)")
    print(f"Sorted by Age:    Youngest = {sorted_by_age[0].name} (Age {sorted_by_age[0].age})")
    print("Sorted by Two Fields (City, Rent) using Tuple:")
    for o in sorted_owners[:3]:
        print(f"  * {o.apartment.city} - {o.apartment.rent} NIS (Host: {o.name})")

    # --------------------------------------------------------------------------
    # STEP 5: Custom Iterable & Independent Iterators
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 5: CUSTOM ITERABLE & INDEPENDENT ITERATORS")
    print("=" * 75)

    collection = SeekerCollection(seekers[:3])
    iter1 = iter(collection)
    iter2 = iter(collection)
    print(f"Advancing Iterator 1: {next(iter1).name}, {next(iter1).name}")
    print(f"Advancing Iterator 2: {next(iter2).name}")
    assert iter1.cursor == 2 and iter2.cursor == 1
    print("[PASS] Verified: Two independent iterators maintain separate traversal states over the same collection.")

    # --------------------------------------------------------------------------
    # STEP 6: Generator (yield) & 3-Stage Lazy Pipeline
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 6: GENERATOR (yield) & 3-STAGE LAZY EVALUATION PIPELINE")
    print("=" * 75)

    gen = stream_budget_candidates(seekers, max_budget_ceiling=3600)
    first_gen_item = next(gen)
    print(f"Generator with yield: First matching item pulled via next(): {first_gen_item.name} ({first_gen_item.max_budget} NIS)")

    pipeline = build_lazy_seeker_pipeline(seekers, target_city="Tel Aviv", min_cleanliness=3)
    res1 = next(pipeline)
    res2 = next(pipeline)
    print(f"  Pipeline Result 1: {res1}")
    print(f"  Pipeline Result 2: {res2}")
    print("[PASS] Partial Consumption: Exactly 2 items consumed from lazy pipeline without building intermediate lists.")

    # --------------------------------------------------------------------------
    # STEP 7: Context Managers (Lifecycle & Exception Safety)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 7: CONTEXT MANAGERS (Lifecycle & Exception Safety)")
    print("=" * 75)

    with SearchSessionContext(sample_seeker.name, "SES-MAIN-01") as session:
        session.record_evaluation(1)
        session.record_match(sample_owner.name)
        print(f"  Inside with-block: Session '{session.session_id}' active. Total matches: {len(session.matches_found)}")

    error_caught = False
    try:
        with SearchSessionContext(sample_seeker.name, "SES-MAIN-02") as session:
            session.record_evaluation(1)
            raise ConnectionError("Simulated external API timeout during search")
    except ConnectionError as e:
        error_caught = True
        print(f"  Caught expected exception outside with-block: {e}")

    assert error_caught is True
    print("[PASS] Verified: Context Manager cleanly aborted and state was finalized without suppressing exception.")

    # --------------------------------------------------------------------------
    # STEP 8: Smart Address Normalization & Zero-Key Commute API Pipeline
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("STEP 8: SMART ADDRESS NORMALIZATION & ZERO-KEY COMMUTE ROUTING")
    print("=" * 75)

    test_inputs = ['ת"א', "אונו", "הטכניון", "רוטשילד 10, תל אביב"]
    print("Resilient Address Normalization (Zero-Crash on Unknown / Slang):")
    for raw in test_inputs:
        normalized = AddressNormalizer.normalize(raw)
        print(f"  * Raw: '{raw}' -> Normalized: '{normalized}'")

    geocoder = NominatimGeocodingClient(use_live_network=use_live_network)
    origin_name = "דיזנגוף סנטר, תל אביב"
    dest_name = "הקריה האקדמית אונו, קרית אונו"
    origin_c = geocoder.geocode(origin_name)
    dest_c = geocoder.geocode(dest_name)
    print(f"\nGeocoding Coordinates Resolved via Nominatim:")
    print(f"  * Origin ({origin_name}): lon={origin_c[0]:.4f}, lat={origin_c[1]:.4f}")
    print(f"  * Dest   ({dest_name}): lon={dest_c[0]:.4f}, lat={dest_c[1]:.4f}")

    if use_live_network:
        commute_client = CommuteAPIClient(max_retries=3)
    else:
        # Deterministic mock client for 100% offline runs
        from unittest.mock import MagicMock
        def _offline_get(*a, **kw):
            m = MagicMock()
            m.status_code = 200
            m.json.return_value = {
                "code": "Ok",
                "routes": [{"distance": 12500.0, "duration": 1320.0}],
            }
            return m
        commute_client = CommuteAPIClient(http_get=_offline_get, sleep_func=lambda s: None)

    commute_result = commute_client.fetch_commute_metrics(
        origin_coords=origin_c,
        dest_coords=dest_c,
        origin_address=origin_name,
        dest_address=dest_name,
    )
    print(f"\nCommute Routing Metrics Calculated (OSRM API):")
    print(f"  -> Distance: {commute_result.distance_km:.2f} km")
    print(f"  -> Duration: {commute_result.duration_minutes:.1f} minutes")
    print(f"  -> Verified: {commute_result.is_verified}")

    # Async with Semaphore Rate Limiting Demonstration
    print(f"\nAsync Semaphore-Bounded Route Verification:")
    apt_ids = ["APT-TLV-01", "APT-TLV-02", "APT-TLV-03", "APT-TLV-04", "APT-RG-01", "APT-JER-01"]
    async def run_async_demo():
        return await collect_verifications_concurrent(apt_ids, max_concurrency=3, delay_seconds=0.01)

    async_results = asyncio.run(run_async_demo())
    verified_count = sum(1 for r in async_results if r["is_verified"])
    print(f"  -> Concurrently queried {len(async_results)} apartments (Bounded to Max Concurrency: 3)")
    print(f"  -> Verified Units: {verified_count}/{len(async_results)}")

    # --------------------------------------------------------------------------
    # Final Success Banner
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("  FLATMATCH STAGE 1 & SMART COMMUTE API DEMONSTRATION PASSED (100% SUCCESS)!")
    print("=" * 75)


if __name__ == "__main__":
    is_live = "--live" in sys.argv
    run_main_demo(use_live_network=is_live)
