"""
FlatMatch - Data Structures and Collections Processing (Part C)
================================================================
This module implements collection processing, data structures,
filtering, queuing, and sorting mechanisms for the FlatMatch platform.
"""

from collections import deque
import heapq
from typing import List, Tuple, Dict, Set, Optional, Any

from models import (
    Preferences,
    Apartment,
    User,
    ApartmentSeeker,
    RoommateSeeker,
    sample_apartment_seekers,
    sample_roommate_seekers
)


# ==============================================================================
# 1. Lists, Tuples, and Extended Unpacking (*)
# ==============================================================================

def create_match_record(seeker: ApartmentSeeker, owner: RoommateSeeker) -> Tuple[str, str, str, float]:
    """
    Creates an immutable, fixed record (tuple) representing a potential match.
    Tuples are ideal for heterogeneous records that should not be mutated.
    """
    return (seeker.name, owner.name, owner.apartment.city, owner.apartment.rent)


def partition_candidates(candidates: List[Any]) -> Tuple[Any, Any, List[Any]]:
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

def compare_amenities(desired_amenities: Set[str], available_amenities: Set[str]) -> Dict[str, Any]:
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


def demonstrate_set_mutation(amenities: Set[str]) -> Dict[str, Any]:
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
    removed_item = "Gym"
    s.remove(removed_item)

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

def build_user_lookup(users: List[User]) -> Dict[str, User]:
    """
    Builds a primary dictionary for O(1) lookup of a User object by their unique ID (phone number).
    """
    lookup: Dict[str, User] = {}
    for user in users:
        add_user_to_lookup(lookup, user.phone, user, allow_overwrite=False)
    return lookup


def add_user_to_lookup(
    user_dict: Dict[str, User],
    user_id: str,
    user_obj: User,
    allow_overwrite: bool = False
) -> None:
    """
    Explicit handling of duplicate keys when adding a user:
    - If allow_overwrite is False and the ID exists, raises ValueError.
    - If allow_overwrite is True, updates the entry.
    """
    if user_id in user_dict and not allow_overwrite:
        raise ValueError(f"Registration Error: User ID '{user_id}' already exists in registry.")
    user_dict[user_id] = user_obj


def find_user_by_id(user_dict: Dict[str, User], user_id: str) -> Optional[User]:
    """
    Demonstrates safe lookup with .get() when the absence of a key is an expected condition.
    Returns None if the key does not exist.
    """
    return user_dict.get(user_id, None)


def group_seekers_by_city(seekers: List[ApartmentSeeker]) -> Dict[str, List[ApartmentSeeker]]:
    """
    Secondary dictionary purpose: Grouping items (seekers) by category (city).
    """
    city_groups: Dict[str, List[ApartmentSeeker]] = {}
    for seeker in seekers:
        for city in seeker.preferred_cities:
            if city not in city_groups:
                city_groups[city] = []
            city_groups[city].append(seeker)
    return city_groups


def count_seekers_by_city(seekers: List[ApartmentSeeker]) -> Dict[str, int]:
    """
    Secondary dictionary purpose: Counting occurrences per category (seekers per city).
    """
    counts: Dict[str, int] = {}
    for seeker in seekers:
        for city in seeker.preferred_cities:
            counts[city] = counts.get(city, 0) + 1
    return counts


def format_grouped_summary(grouped: Dict[str, List[ApartmentSeeker]]) -> List[str]:
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

