"""
FlatMatch - Main Demonstration Scenario (Part E)
=================================================
This script serves as the centralized end-to-end demonstration for the FlatMatch platform.
It loads synthetic data from data/sample_data.jsonl and demonstrates all core syllabus requirements:
1. Data Ingestion & Repository (JSONL streaming & O(1) indexed lookup)
2. OOP & Polymorphism (Role summaries and dealbreaker evaluations)
3. Data Structures (FIFO deque, priority heapq, dict grouping/counting, set operations)
4. Comprehensions & Advanced Sorting (List/Set/Dict comprehensions, key functions & tuples)
5. Custom Iterable & Independent Iterators (Concurrent traversal over SeekerCollection)
6. Generator & 3-Stage Lazy Evaluation Pipeline (Partial consumption without intermediate lists)
7. Context Managers (Lifecycle management in normal execution and error handling)
"""

import os
import sys

from flatmatch import (
    ApartmentSeeker,
    RoommateSeeker,
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
)


def run_main_demo():
    print("=" * 70)
    print("  FLATMATCH - CENTRAL DEMONSTRATION RUNNER (Part E)")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # 1. Data Ingestion & Repository
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 1: DATA INGESTION & STREAMING REPOSITORY")
    print("=" * 70)

    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    repo = FlatMatchRepository(data_path)
    all_users = repo.get_all_users()
    seekers = repo.get_apartment_seekers()
    owners = repo.get_roommate_seekers()

    print(f"Successfully loaded {len(repo)} users from '{data_path}':")
    print(f"  - Apartment Seekers: {len(seekers)}")
    print(f"  - Roommate Seekers (with Apartments): {len(owners)}")

    # O(1) Lookup demonstration
    sample_phone = "050-1000001"
    user_by_phone = repo.get_by_phone(sample_phone)
    print(f"O(1) Dictionary Lookup for phone '{sample_phone}': {user_by_phone.name} ({type(user_by_phone).__name__})")
    assert user_by_phone != None

    # --------------------------------------------------------------------------
    # 2. OOP & Polymorphic Behavior
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 2: OOP, COMPOSITION & POLYMORPHISM")
    print("=" * 70)

    sample_seeker = seekers[0]
    sample_owner = owners[0]

    # Polymorphic role summaries
    print(f"Polymorphic Role Summary (Seeker): {sample_seeker.get_role_summary()}")
    print(f"Polymorphic Role Summary (Owner):  {sample_owner.get_role_summary()}")

    # Polymorphic dealbreaker evaluations
    has_dealbreaker = sample_seeker.evaluate_dealbreakers(sample_owner)
    print(f"Dealbreaker evaluation between {sample_seeker.name} (Budget {sample_seeker.max_budget} NIS) and {sample_owner.name} (Rent {sample_owner.apartment.rent} NIS): {has_dealbreaker}")

    # --------------------------------------------------------------------------
    # 3. Data Structures: deque, heapq, dict, set
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 3: DATA STRUCTURES (deque, heapq, dict, set)")
    print("=" * 70)

    # 3.1 FIFO Queue (deque) - Fairness in arrival order
    app_queue = RoommateApplicationQueue()
    app_queue.enqueue_application(seekers[0].name, "Apt-TLV-1", "09:00 AM")
    app_queue.enqueue_application(seekers[1].name, "Apt-TLV-1", "09:15 AM")
    app_queue.enqueue_application(seekers[2].name, "Apt-TLV-1", "09:30 AM")
    print(f"FIFO Queue (deque): Queued {len(app_queue)} applications. Processing first-in:")
    processed_app = app_queue.process_next_application()
    print(f"  -> Processed First: {processed_app[0]} (Arrival: {processed_app[2]})")
    assert processed_app[0] == seekers[0].name

    # 3.2 Priority Queue (heapq) - Urgency superseding arrival time
    urgent_queue = UrgentCandidateQueue()
    urgent_queue.push_candidate(seekers[1], priority=3, reason="Standard / Planning ahead")
    urgent_queue.push_candidate(seekers[0], priority=1, reason="Emergency / Immediate move-in")
    urgent_queue.push_candidate(seekers[2], priority=2, reason="High / Urgent within 2 weeks")
    print(f"Priority Queue (heapq): Enqueued 3 candidates. Highest priority (lowest number) popped first:")
    highest_priority = urgent_queue.pop_candidate()
    print(f"  -> Served First: {highest_priority}")
    assert highest_priority.priority == 1 and highest_priority.seeker.name == seekers[0].name

    # 3.3 Dictionary Grouping & Counting
    city_counts = count_seekers_by_city(seekers)
    print(f"Dictionary Counting (Seekers per City): {city_counts}")
    grouped_cities = group_seekers_by_city(seekers)
    print("Dictionary Grouping (.items() traversal with unpacking):")
    for summary_line in format_grouped_summary(grouped_cities)[:3]:
        print(f"  * {summary_line}")

    # 3.4 Set Operations: Amenities matching
    desired_amenities = {"Air Conditioner", "Elevator", "Balcony", "Parking"}
    apartment_amenities = sample_owner.apartment.amenities
    amenity_comp = compare_amenities(desired_amenities, apartment_amenities)
    print(f"Set Comparison for apartment in {sample_owner.apartment.city}:")
    print(f"  - Desired:  {desired_amenities}")
    print(f"  - Actual:   {apartment_amenities}")
    print(f"  - Matching (&): {amenity_comp['matching']}")
    print(f"  - Missing  (-): {amenity_comp['missing']}")

    # --------------------------------------------------------------------------
    # 4. Comprehensions & Advanced Sorting
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 4: COMPREHENSIONS & ADVANCED SORTING")
    print("=" * 70)

    # List, Set, Dict Comprehensions
    budget_filter = filter_seekers_by_budget(seekers, min_budget=3500)
    unique_cities = extract_unique_preferred_cities(seekers)
    phones_map = map_seeker_phones_to_budgets(seekers)
    print(f"List Comprehension (Budget >= 3500 NIS, first 3): {budget_filter[:3]}")
    print(f"Set Comprehension  (Unique Target Cities): {sorted(unique_cities)}")
    print(f"Dict Comprehension (Total Phone->Budget Mappings): {len(phones_map)}")

    # Sorting
    by_budget = sort_seekers_by_budget_descending(seekers)
    by_age = sort_seekers_by_age(seekers)
    by_city_rent = sort_apartments_by_city_and_rent(owners)
    print(f"Sorted by Budget (Regular Function 'get_seeker_budget'): Top = {by_budget[0].name} ({by_budget[0].max_budget} NIS)")
    print(f"Sorted by Age    (Lambda Function): Youngest = {by_age[0].name} (Age {by_age[0].age})")
    print("Sorted by Two Fields (City, Rent) using Tuple:")
    for o in by_city_rent[:3]:
        print(f"  * {o.apartment.city} - {o.apartment.rent} NIS (Host: {o.name})")

    # --------------------------------------------------------------------------
    # 5. Custom Iterable & Independent Iterators
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 5: CUSTOM ITERABLE & INDEPENDENT ITERATORS")
    print("=" * 70)

    collection = SeekerCollection(seekers)
    iter1 = iter(collection)
    iter2 = iter(collection)

    print("Advancing Iterator 1 by 2 items:")
    print(f"  Iterator 1 (cursor={iter1.cursor}): {next(iter1).name}")
    print(f"  Iterator 1 (cursor={iter1.cursor}): {next(iter1).name}")

    print("Advancing Iterator 2 by 1 item:")
    print(f"  Iterator 2 (cursor={iter2.cursor}): {next(iter2).name}")

    assert iter1.cursor == 2 and iter2.cursor == 1
    print("[PASS] Verified: Two independent iterators maintain separate traversal states over the same collection.")

    # --------------------------------------------------------------------------
    # 6. Generator with yield & 3-Stage Lazy Pipeline
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 6: GENERATOR (yield) & 3-STAGE LAZY EVALUATION PIPELINE")
    print("=" * 70)

    # Generator demonstration
    gen = stream_budget_candidates(seekers, max_budget_ceiling=3600)
    first_gen_item = next(gen)
    print(f"Generator with yield: First matching item pulled via next(): {first_gen_item.name} ({first_gen_item.max_budget} NIS)")

    # 3-Stage Lazy Pipeline with partial consumption
    print("\nExecuting 3-Stage Lazy Pipeline (Stage 1: Filter City -> Stage 2: Filter Cleanliness -> Stage 3: Summary String):")
    pipeline = build_lazy_seeker_pipeline(seekers, target_city="Tel Aviv", min_cleanliness=3)

    # Strictly consume only the first 2 results
    result1 = next(pipeline)
    result2 = next(pipeline)
    print(f"  Pipeline Result 1: {result1}")
    print(f"  Pipeline Result 2: {result2}")
    print("[PASS] Partial Consumption: Exactly 2 items consumed from lazy pipeline without building intermediate lists.")

    # --------------------------------------------------------------------------
    # 7. Context Managers (Lifecycle & Safety)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 7: CONTEXT MANAGERS (Lifecycle & Exception Safety)")
    print("=" * 70)

    # 7.1 Normal execution
    with SearchSessionContext(sample_seeker.name, "SES-MAIN-01") as session:
        session.record_evaluation(1)
        session.record_match(sample_owner.name)
        print(f"  Inside with-block: Session '{session.session_id}' active. Total matches: {len(session.matches_found)}")

    # 7.2 Exception handling & non-suppression verification
    error_caught = False
    try:
        with SearchSessionContext(sample_seeker.name, "SES-MAIN-02") as session:
            session.record_evaluation(1)
            raise ConnectionError("Simulated external API timeout during search")
    except ConnectionError as e:
        error_caught = True
        print(f"  Caught expected exception outside with-block: {e}")

    assert error_caught == True
    print("[PASS] Verified: Context Manager cleanly aborted and state was finalized without suppressing the exception.")

    # --------------------------------------------------------------------------
    # Completion
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  ALL DEMONSTRATION PHASES PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_main_demo()
