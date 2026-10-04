"""
FlatMatch - Data Structures and Collections Processing (Part C)
================================================================
This module implements collection processing, data structures,
filtering, queuing, and sorting mechanisms for the FlatMatch platform.
"""

from collections import deque
import heapq

from models import (
    sample_apartment_seekers,
    sample_roommate_seekers
)


# ==============================================================================
# 1. Lists, Tuples, and Extended Unpacking (*)
# ==============================================================================

def create_match_record(seeker, owner) -> tuple:
    """
    Creates an immutable, fixed record (tuple) representing a potential match.
    Tuples are ideal for heterogeneous records that should not be mutated.
    """
    return (seeker.name, owner.name, owner.apartment.city, owner.apartment.rent)


def partition_candidates(candidates: list) -> tuple:
    """
    Partitions an ordered mutable list of candidates using * (extended unpacking).
    Extracts the top pick, runner-up, and collects the remaining candidates into a list.
    """
    if len(candidates) < 2:
        raise ValueError("At least 2 candidates are required to partition.")
    
    # Extended unpacking (*) to collect remaining values
    top_pick, runner_up, *remaining = candidates
    return top_pick, runner_up, remaining


# ==============================================================================
# 2. Advanced Set Operations
# ==============================================================================

def compare_amenities(desired_amenities: set, available_amenities: set) -> dict:
    """
    Demonstrates set operations for matching seeker requirements with apartment amenities:
    - Membership testing using 'in'
    - Intersection (&): matching amenities
    - Difference (-): missing required amenities
    - Union (|): total unique amenities combined
    """
    # Membership testing using 'in'
    has_air_conditioner = "Air Conditioner" in available_amenities

    # Set operations
    matching = desired_amenities & available_amenities
    missing = desired_amenities - available_amenities
    all_combined = desired_amenities | available_amenities

    return {
        "has_air_conditioner": has_air_conditioner,
        "matching": matching,
        "missing": missing,
        "all_combined": all_combined
    }


def demonstrate_set_mutation(amenities: set) -> dict:
    """
    Demonstrates set mutation operations:
    - add: adds a unique element
    - discard: safely removes an element without raising KeyError if absent
    - remove: removes an element, raising KeyError if absent
    """
    s = amenities.copy()

    # 1. add
    s.add("Gym")

    # 2. discard (safe - does not raise error if item is not found)
    s.discard("NonExistentItem")

    # 3. remove (strict - raises KeyError if item is not found)
    s.remove("Gym")

    # Verify that remove on absent item raises KeyError
    key_error_caught = False
    try:
        s.remove("NonExistentItem")
    except KeyError:
        key_error_caught = True

    return {
        "final_set": s,
        "key_error_caught": key_error_caught
    }


# ==============================================================================
# 3. Dictionaries (Lookup, Grouping, and Counting)
# ==============================================================================

def build_user_lookup(users: list) -> dict:
    """
    Builds a primary dictionary for O(1) lookup of a User object by their unique ID (phone number).
    """
    lookup = {}
    for user in users:
        add_user_to_lookup(lookup, user.phone, user, allow_overwrite=False)
    return lookup


def add_user_to_lookup(user_dict: dict, user_id: str, user_obj, allow_overwrite: bool = False) -> None:
    """
    Explicit handling of duplicate keys when adding a user:
    - If allow_overwrite is False and the ID exists, raises ValueError.
    - If allow_overwrite is True, updates the entry.
    """
    if user_id in user_dict and not allow_overwrite:
        raise ValueError(f"Registration Error: User ID '{user_id}' already exists in registry.")
    user_dict[user_id] = user_obj


def find_user_by_id(user_dict: dict, user_id: str):
    """
    Demonstrates safe lookup with .get() when the absence of a key is an expected condition.
    Returns None if the key does not exist.
    """
    return user_dict.get(user_id, None)


def group_seekers_by_city(seekers: list) -> dict:
    """
    Secondary dictionary purpose: Grouping items (seekers) by category (city).
    """
    city_groups = {}
    for seeker in seekers:
        for city in seeker.preferred_cities:
            if city not in city_groups:
                city_groups[city] = []
            city_groups[city].append(seeker)
    return city_groups


def count_seekers_by_city(seekers: list) -> dict:
    """
    Secondary dictionary purpose: Counting occurrences per category (seekers per city).
    """
    counts = {}
    for seeker in seekers:
        for city in seeker.preferred_cities:
            counts[city] = counts.get(city, 0) + 1
    return counts


def format_grouped_summary(grouped: dict) -> list:
    """
    Demonstrates iterating over dictionary items using .items() with tuple unpacking:
    'for key, value in dictionary.items():'
    """
    summaries = []
    # Loop over .items() with unpacking of key and value
    for city, seekers_list in grouped.items():
        names = ", ".join(s.name for s in seekers_list)
        summaries.append(f"{city}: {len(seekers_list)} seekers ({names})")
    return summaries


# ==============================================================================
# 4. FIFO Queue using collections.deque
# ==============================================================================

class RoommateApplicationQueue:
    """
    FIFO Queue for processing incoming roommate applications by arrival order.
    
    Business rationale:
    In a high-demand shared rental market, applications must be reviewed strictly
    in the order they arrive (First-In, First-Out) to ensure transparency, fairness,
    and prevent bias towards applicants.
    """

    def __init__(self):
        self._queue = deque()

    def enqueue_application(self, applicant_name: str, apartment_id: str, timestamp: str) -> None:
        """
        Adds a new application to the back of the queue using append().
        """
        self._queue.append((applicant_name, apartment_id, timestamp))

    def process_next_application(self):
        """
        Removes and returns the oldest application using popleft().
        Gracefully handles empty queue state without crashing or raising IndexError.
        """
        if not self._queue:
            return None
        return self._queue.popleft()

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def __len__(self) -> int:
        return len(self._queue)


# ==============================================================================
# 5. Priority Queue using heapq
# ==============================================================================

class PriorityCandidate:
    """
    Encapsulates a candidate with an explicit priority level and tie-breaker.

    Priority Convention:
    LOWER number represents HIGHER priority (standard min-heap behavior):
    - Priority 1: Emergency / Immediate Move-In (Urgent)
    - Priority 2: High Priority (Flexible within 2 weeks)
    - Priority 3: Standard Priority (Planning ahead / Next month)

    Tie-breaking:
    When priorities are equal, entry_id ensures deterministic ordering
    without attempting to compare User objects directly.
    """

    def __init__(self, priority: int, entry_id: int, seeker, reason: str = ""):
        self.priority = priority
        self.entry_id = entry_id
        self.seeker = seeker
        self.reason = reason

    def __lt__(self, other: "PriorityCandidate") -> bool:
        if not isinstance(other, PriorityCandidate):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority < other.priority
        # Tie-breaker by chronological insertion order
        return self.entry_id < other.entry_id

    def __str__(self) -> str:
        return f"[Priority {self.priority}] {self.seeker.name} ({self.reason})"


class UrgentCandidateQueue:
    """
    Priority Queue managing candidates where urgency supersedes arrival time.
    Note: The internal list of a heap maintains the heap invariant, but is NOT fully sorted.
    """

    def __init__(self):
        self._heap = []
        self._counter: int = 0

    def push_candidate(self, seeker, priority: int, reason: str = "") -> None:
        """
        Pushes a candidate into the priority queue using heapq.heappush().
        """
        candidate = PriorityCandidate(priority, self._counter, seeker, reason)
        self._counter += 1
        heapq.heappush(self._heap, candidate)

    def pop_candidate(self):
        """
        Pops and returns the highest priority candidate using heapq.heappop().
        Handles empty queue gracefully without crashing.
        """
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def __len__(self) -> int:
        return len(self._heap)


# ==============================================================================
# 6. Comprehensions (List, Set, Dict)
# ==============================================================================

def filter_seekers_by_budget(seekers: list, min_budget: float) -> list:
    """
    List comprehension for filtering and formatting:
    Filters seekers with at least min_budget and formats their name and budget.
    """
    return [f"{s.name} ({s.max_budget:.0f} NIS)" for s in seekers if s.max_budget >= min_budget]


def extract_unique_preferred_cities(seekers: list) -> set:
    """
    Set comprehension for extracting unique values:
    Flattens preferred cities from all seekers into a set of unique city names.
    """
    return {city for s in seekers for city in s.preferred_cities}


def map_seeker_phones_to_budgets(seekers: list) -> dict:
    """
    Dict comprehension for creating an index/mapping:
    Maps each seeker's unique phone number to their maximum budget.
    """
    return {s.phone: s.max_budget for s in seekers}


# ==============================================================================
# 7. Sorting and Functions as Values
# ==============================================================================

def get_seeker_budget(seeker) -> float:
    """
    Regular named function used as the 'key' argument in sorted().
    """
    return seeker.max_budget


def sort_seekers_by_budget_descending(seekers: list) -> list:
    """
    Demonstrates sorted() using a regular named function as key.
    Sorts seekers by budget in descending order.
    """
    return sorted(seekers, key=get_seeker_budget, reverse=True)


def sort_seekers_by_age(seekers: list) -> list:
    """
    Demonstrates sorted() using a concise lambda function as key.
    Sorts seekers by age in ascending order.
    """
    return sorted(seekers, key=lambda s: s.age)


def sort_apartments_by_city_and_rent(owners: list) -> list:
    """
    Demonstrates sorted() by TWO fields using a tuple:
    First by city alphabetically, then by monthly rent in ascending order.
    """
    return sorted(owners, key=lambda o: (o.apartment.city, o.apartment.rent))


# ==============================================================================
# Comprehensive Demonstration & Verification Runner
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FlatMatch - Part C: Data Structures & Collections Demo")
    print("=" * 60)

    seekers = sample_apartment_seekers
    owners = sample_roommate_seekers

    # 1. Lists, Tuples, and Unpacking (*)
    print("\n--- 1. Lists, Tuples, and Unpacking (*) ---")
    record = create_match_record(seekers[0], owners[0])
    print(f"Sample Immutable Match Tuple: {record}")
    assert isinstance(record, tuple) and len(record) == 4

    top_pick, runner_up, remaining = partition_candidates(seekers)
    print(f"Top Pick: {top_pick.name}")
    print(f"Runner-up: {runner_up.name}")
    print(f"Remaining Candidates ({len(remaining)}): {[s.name for s in remaining]}")
    assert len(remaining) == len(seekers) - 2

    # 2. Advanced Set Operations
    print("\n--- 2. Advanced Set Operations ---")
    desired = {"Air Conditioner", "Balcony", "Elevator", "Parking"}
    available = owners[0].apartment.amenities
    print(f"Desired Amenities: {desired}")
    print(f"Apartment Available Amenities: {available}")

    comparison = compare_amenities(desired, available)
    print(f"Has Air Conditioner (in test): {comparison['has_air_conditioner']}")
    print(f"Matching Amenities (&): {comparison['matching']}")
    print(f"Missing Amenities (-): {comparison['missing']}")
    print(f"Total Unique Combined (|): {comparison['all_combined']}")
    assert "Air Conditioner" in comparison["matching"]

    mutation_res = demonstrate_set_mutation(available)
    print(f"Safe discard & remove demonstration successful (KeyError caught: {mutation_res['key_error_caught']})")
    assert mutation_res["key_error_caught"] is True

    # 3. Dictionaries (Lookup, Grouping, Counting)
    print("\n--- 3. Dictionaries (Lookup, Grouping, Counting) ---")
    all_users = seekers + owners
    directory = build_user_lookup(all_users)
    print(f"Indexed {len(directory)} users by unique phone ID.")

    # Safe retrieval with .get()
    found = find_user_by_id(directory, "050-1112233")
    not_found = find_user_by_id(directory, "000-0000000")
    print(f"Found User with .get(): {found.name if found else 'None'}")
    print(f"Missing User with .get() (safe return): {not_found}")
    assert found is not None and not_found is None

    # Duplicate key collision check
    duplicate_caught = False
    try:
        add_user_to_lookup(directory, seekers[0].phone, seekers[0], allow_overwrite=False)
    except ValueError as e:
        duplicate_caught = True
        print(f"Explicit duplicate prevention caught: {e}")
    assert duplicate_caught is True

    # Grouping and counting
    grouped = group_seekers_by_city(seekers)
    counts = count_seekers_by_city(seekers)
    print(f"Seeker Counts per City: {counts}")
    print("Grouped Summary (.items() loop with unpacking):")
    for summary_line in format_grouped_summary(grouped):
        print(f"  * {summary_line}")

    # 4. FIFO Queue with deque
    print("\n--- 4. FIFO Queue (collections.deque) ---")
    app_queue = RoommateApplicationQueue()
    app_queue.enqueue_application("Alice Cohen", "Apt-TLV-101", "10:00 AM")
    app_queue.enqueue_application("Ben Levi", "Apt-TLV-101", "10:15 AM")
    app_queue.enqueue_application("Dana Mizrahi", "Apt-TLV-101", "10:30 AM")
    print(f"Queued {len(app_queue)} applications based on arrival order (FIFO fairness).")

    app1 = app_queue.process_next_application()
    app2 = app_queue.process_next_application()
    app3 = app_queue.process_next_application()
    empty_app = app_queue.process_next_application()
    print(f"Processed 1st: {app1[0]} (Arrival: {app1[2]})")
    print(f"Processed 2nd: {app2[0]} (Arrival: {app2[2]})")
    print(f"Processed 3rd: {app3[0]} (Arrival: {app3[2]})")
    print(f"Processing on empty queue returns safely: {empty_app}")
    assert app1[0] == "Alice Cohen" and empty_app is None

    # 5. Priority Queue with heapq
    print("\n--- 5. Priority Queue (heapq) ---")
    urgent_queue = UrgentCandidateQueue()
    # Explicit convention: Lower number = Higher priority
    urgent_queue.push_candidate(seekers[2], priority=3, reason="Next month move-in")
    urgent_queue.push_candidate(seekers[0], priority=1, reason="Emergency / Immediate move-in")
    urgent_queue.push_candidate(seekers[1], priority=2, reason="Flexible within 2 weeks (First)")
    urgent_queue.push_candidate(seekers[3], priority=2, reason="Flexible within 2 weeks (Second)")

    print(f"Enqueued {len(urgent_queue)} candidates into min-heap with urgency priorities.")
    first_served = urgent_queue.pop_candidate()
    second_served = urgent_queue.pop_candidate()
    third_served = urgent_queue.pop_candidate()
    fourth_served = urgent_queue.pop_candidate()
    empty_popped = urgent_queue.pop_candidate()

    print(f"1st served: {first_served}")
    print(f"2nd served: {second_served}")
    print(f"3rd served: {third_served}")
    print(f"4th served: {fourth_served}")
    print(f"Popping from empty priority queue returns safely: {empty_popped}")
    assert first_served.priority == 1 and first_served.seeker.name == "Alice Cohen"
    assert second_served.priority == 2 and second_served.seeker.name == "Ben Levi"
    assert third_served.priority == 2 and third_served.seeker.name == "Eitan Sharon"
    assert fourth_served.priority == 3 and fourth_served.seeker.name == "Dana Mizrahi"
    assert empty_popped is None

    # 6. Comprehensions
    print("\n--- 6. Comprehensions (List, Set, Dict) ---")
    budget_filtered = filter_seekers_by_budget(seekers, min_budget=3500)
    print(f"List Comprehension (Budget >= 3500): {budget_filtered}")
    assert len(budget_filtered) == 3

    unique_cities = extract_unique_preferred_cities(seekers)
    print(f"Set Comprehension (Unique Cities): {sorted(unique_cities)}")
    assert "Tel Aviv" in unique_cities and "Jerusalem" in unique_cities

    phone_to_budget = map_seeker_phones_to_budgets(seekers)
    print(f"Dict Comprehension (Phone -> Budget): {phone_to_budget}")
    assert phone_to_budget["050-1112233"] == 3200.0

    # 7. Sorting and Functions as Values
    print("\n--- 7. Sorting & Functions as Values ---")
    by_budget = sort_seekers_by_budget_descending(seekers)
    print(f"Sorted by budget (named function 'get_seeker_budget'): {[f'{s.name}: {s.max_budget}' for s in by_budget]}")
    assert by_budget[0].max_budget >= by_budget[1].max_budget

    by_age = sort_seekers_by_age(seekers)
    print(f"Sorted by age (lambda function): {[f'{s.name}: {s.age}' for s in by_age]}")
    assert by_age[0].age <= by_age[-1].age

    by_city_and_rent = sort_apartments_by_city_and_rent(owners)
    print("Sorted apartments by (City, Rent) using 2-field tuple:")
    for o in by_city_and_rent:
        print(f"  * {o.apartment.city} - Rent: {o.apartment.rent} NIS (Host: {o.name})")
    assert by_city_and_rent[0].apartment.city <= by_city_and_rent[-1].apartment.city

    print("\n" + "=" * 60)
    print("All Part C requirements verified and passed successfully!")
    print("=" * 60)
