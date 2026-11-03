"""
FlatMatch - Smart Apartment & Roommate Matching Package
========================================================
This package encapsulates:
- Domain Models & Polymorphism (models.py)
- Data Ingestion & Repository (repository.py)
- Collection Processing, Queues & Sorting (processing.py)
- Iterators, Generators & Lazy Pipeline (iterators.py)
- Resource & Lifecycle Context Managers (context_managers.py)
- Strategy, Factory, Observer Design Patterns & Services (strategies.py, factories.py, observers.py, services.py)
- Smart Location, Address Normalizer & OSRM Routing Client (address_normalizer.py, geocoding.py, api_client.py)
- Concurrency: Async Rate-Limited Ingestion & Thread-Safe Room Inventory (async_processing.py, threaded_processing.py)
- Lease Inspection Subsystem & Integrated Reports (reports.py)
"""

from .models import (
    Preferences,
    Apartment,
    User,
    ApartmentSeeker,
    RoommateSeeker,
    CommuteMetrics,
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
    group_seekers_by_destination,
    count_seekers_by_destination,
    extract_unique_destinations,
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
from .factories import (
    UserFactory,
    VALID_USER_TYPES,
)
from .strategies import (
    MatchingStrategy,
    BudgetFocusedStrategy,
    CommuteAndLifestyleStrategy,
)
from .observers import (
    MatchEventListener,
    MatchStatisticsObserver,
    ApplicantNotificationObserver,
)
from .services import (
    FlatMatchService,
    MatchEvaluationResult,
    calculate_commute_adjusted_budget,
)
from .address_normalizer import (
    AddressNormalizer,
    normalize_address,
)
from .geocoding import (
    Coordinates,
    NominatimGeocodingClient,
)
from .api_client import (
    CommuteAPIClient,
    APIConnectionError,
    APIHTTPError,
    APIResponseFormatError,
    APIDataValidationError,
)
from .async_processing import (
    fetch_apartment_verification_async,
    collect_verifications_sequential,
    collect_verifications_concurrent,
)
from .threaded_processing import (
    SharedRoomInventory,
    UnsafeSharedRoomInventory,
    run_concurrent_room_bookings,
)
from .reports import (
    LeaseInspectionSubsystem,
    SubsystemSyncObserver,
    generate_integrated_business_report,
)

__all__ = [
    # Stage 1 Domain Models
    "Preferences",
    "Apartment",
    "User",
    "ApartmentSeeker",
    "RoommateSeeker",
    "CommuteMetrics",
    "sample_apartment_seekers",
    "sample_roommate_seekers",
    # Stage 1 Ingestion & Repository
    "FlatMatchRepository",
    "stream_users_from_jsonl",
    "load_users_from_jsonl",
    "parse_user_record",
    # Stage 1 Collections, Queues, Sets, Sorting
    "create_match_record",
    "partition_candidates",
    "compare_amenities",
    "demonstrate_set_mutation",
    "build_user_lookup",
    "add_user_to_lookup",
    "find_user_by_id",
    "group_seekers_by_city",
    "count_seekers_by_city",
    "group_seekers_by_destination",
    "count_seekers_by_destination",
    "extract_unique_destinations",
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
    # Stage 1 Iterables & Context Managers
    "SeekerCollection",
    "SeekerIterator",
    "stream_budget_candidates",
    "build_lazy_seeker_pipeline",
    "SearchSessionContext",
    "ApartmentHoldContext",
    # Stage 2 Design Patterns & Services
    "UserFactory",
    "VALID_USER_TYPES",
    "MatchingStrategy",
    "BudgetFocusedStrategy",
    "CommuteAndLifestyleStrategy",
    "MatchEventListener",
    "MatchStatisticsObserver",
    "ApplicantNotificationObserver",
    "FlatMatchService",
    "MatchEvaluationResult",
    "calculate_commute_adjusted_budget",
    # Stage 2 Smart Location & External API Pipeline
    "AddressNormalizer",
    "normalize_address",
    "Coordinates",
    "NominatimGeocodingClient",
    "CommuteAPIClient",
    "APIConnectionError",
    "APIHTTPError",
    "APIResponseFormatError",
    "APIDataValidationError",
    "fetch_apartment_verification_async",
    "collect_verifications_sequential",
    "collect_verifications_concurrent",
    # Stage 2 Threaded Processing with Lock
    "SharedRoomInventory",
    "UnsafeSharedRoomInventory",
    "run_concurrent_room_bookings",
    # Stage 2 Subsystem Integration & Integrated Reports
    "LeaseInspectionSubsystem",
    "SubsystemSyncObserver",
    "generate_integrated_business_report",
]
