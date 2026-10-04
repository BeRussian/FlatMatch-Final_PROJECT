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
