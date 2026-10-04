"""
FlatMatch - Smart Apartment & Roommate Matching Package
========================================================
This package encapsulates:
- Domain Models & Polymorphism (models.py)
- Data Ingestion & Repository (repository.py)
- Collection Processing, Queues & Sorting (processing.py)
- Iterators, Generators & Lazy Pipeline (iterators.py)
- Resource & Lifecycle Context Managers (context_managers.py)
"""

from .models import (
    Preferences,
    Apartment,
    User,
    ApartmentSeeker,
    RoommateSeeker,
    sample_apartment_seekers,
    sample_roommate_seekers,
)
from .repository import (
    FlatMatchRepository,
    stream_users_from_jsonl,
    load_users_from_jsonl,
    parse_user_record,
)
from .processing import (
    create_match_record,
    partition_candidates,
    compare_amenities,
    demonstrate_set_mutation,
    build_user_lookup,
    add_user_to_lookup,
    find_user_by_id,
    group_seekers_by_city,
    count_seekers_by_city,
    format_grouped_summary,
    RoommateApplicationQueue,
    PriorityCandidate,
    UrgentCandidateQueue,
    filter_seekers_by_budget,
    extract_unique_preferred_cities,
    map_seeker_phones_to_budgets,
    get_seeker_budget,
    sort_seekers_by_budget_descending,
    sort_seekers_by_age,
    sort_apartments_by_city_and_rent,
)
from .iterators import (
    SeekerCollection,
    SeekerIterator,
    stream_budget_candidates,
    build_lazy_seeker_pipeline,
)
from .context_managers import (
    SearchSessionContext,
    ApartmentHoldContext,
)

__all__ = [
    "Preferences",
    "Apartment",
    "User",
    "ApartmentSeeker",
    "RoommateSeeker",
    "sample_apartment_seekers",
    "sample_roommate_seekers",
    "FlatMatchRepository",
    "stream_users_from_jsonl",
    "load_users_from_jsonl",
    "parse_user_record",
    "create_match_record",
    "partition_candidates",
    "compare_amenities",
    "demonstrate_set_mutation",
    "build_user_lookup",
    "add_user_to_lookup",
    "find_user_by_id",
    "group_seekers_by_city",
    "count_seekers_by_city",
    "format_grouped_summary",
    "RoommateApplicationQueue",
    "PriorityCandidate",
    "UrgentCandidateQueue",
    "filter_seekers_by_budget",
    "extract_unique_preferred_cities",
    "map_seeker_phones_to_budgets",
    "get_seeker_budget",
    "sort_seekers_by_budget_descending",
    "sort_seekers_by_age",
    "sort_apartments_by_city_and_rent",
    "SeekerCollection",
    "SeekerIterator",
    "stream_budget_candidates",
    "build_lazy_seeker_pipeline",
    "SearchSessionContext",
    "ApartmentHoldContext",
]
