"""
FlatMatch - Core Business Services (Part 3)
============================================
Coordinates domain models, routing API clients, scoring strategies,
and observers through constructor-based Dependency Injection (DI).
"""

from typing import List, Optional, Dict, Any
from flatmatch.config import get_logger
from flatmatch.models import ApartmentSeeker, RoommateSeeker, CommuteMetrics
from flatmatch.api_client import (
    CommuteAPIClient,
    APIConnectionError,
    APIHTTPError,
    APIResponseFormatError,
    APIDataValidationError,
)
from flatmatch.strategies import MatchingStrategy, CommuteAndLifestyleStrategy
from flatmatch.observers import MatchEventListener
from flatmatch.geocoding import NominatimGeocodingClient

logger = get_logger("services")


class MatchEvaluationResult:
    """
    Structured outcome of a candidate match evaluation.
    """

    def __init__(
        self,
        seeker_phone: str,
        owner_phone: str,
        city: str,
        rent_per_room: float,
        score: float,
        commute_metrics: Optional[CommuteMetrics],
        status: str,
        is_approved: bool,
        seeker_name: str = "",
        owner_name: str = "",
    ) -> None:
        self.seeker_phone = seeker_phone
        self.owner_phone = owner_phone
        self.city = city
        self.rent_per_room = rent_per_room
        self.score = round(float(score), 2)
        self.commute_metrics = commute_metrics
        self.status = status
        self.is_approved = is_approved
        self.seeker_name = seeker_name
        self.owner_name = owner_name

    def to_event_data(self) -> Dict[str, Any]:
        """Converts result object to dictionary payload for observers."""
        return {
            "seeker_phone": self.seeker_phone,
            "owner_phone": self.owner_phone,
            "seeker_name": self.seeker_name,
            "owner_name": self.owner_name,
            "city": self.city,
            "rent_per_room": self.rent_per_room,
            "score": self.score,
            "commute_metrics": self.commute_metrics,
            "status": self.status,
            "is_approved": self.is_approved,
        }

    def __repr__(self) -> str:
        return (
            f"MatchEvaluationResult(seeker='{self.seeker_name}', owner='{self.owner_name}', "
            f"score={self.score}, status='{self.status}', is_approved={self.is_approved})"
        )


class FlatMatchService:
    """
    Central orchestrator for roommate matching, integrating API routing,
    strategy scoring, observer notifications, and graceful fallbacks.
    """

    def __init__(
        self,
        api_client: CommuteAPIClient,
        strategy: MatchingStrategy,
        observers: Optional[List[MatchEventListener]] = None,
        max_commute_minutes: float = 45.0,
        geocoding_client: Optional[NominatimGeocodingClient] = None,
    ) -> None:
        self.api_client = api_client
        self.strategy = strategy
        self.observers = observers or []
        self.max_commute_minutes = float(max_commute_minutes)
        self.geocoding_client = geocoding_client or NominatimGeocodingClient(use_live_network=False)

    def evaluate_candidate_match(
        self,
        seeker: ApartmentSeeker,
        owner: RoommateSeeker,
    ) -> MatchEvaluationResult:
        """
        Executes end-to-end evaluation between a seeker and an apartment host:
        1. Checks hard dealbreakers (budget & lifestyle conflicts).
        2. Resolves coordinates and fetches commute metrics via API.
        3. Handles API failures with controlled graceful fallback.
        4. Calculates final polymorphic score and determines approval status.
        5. Dispatches event data to all registered observers.
        """
        # Step 1: Base Dealbreaker check
        if seeker.evaluate_dealbreakers(owner):
            result = MatchEvaluationResult(
                seeker_phone=seeker.phone,
                owner_phone=owner.phone,
                city=owner.apartment.city,
                rent_per_room=owner.apartment.rent_per_room,
                score=0.0,
                commute_metrics=None,
                status="REJECTED_DEALBREAKER",
                is_approved=False,
                seeker_name=seeker.name,
                owner_name=owner.name,
            )
            self._notify_observers(result)
            return result

        # Step 2: Resolve coordinates for routing
        origin_address = owner.apartment.address or owner.apartment.city
        dest_address = seeker.destination_address
        origin_coords = self.geocoding_client.geocode(origin_address)
        dest_coords = self.geocoding_client.geocode(dest_address)

        # Step 3: Fetch commute metrics with error handling / fallback
        try:
            commute = self.api_client.fetch_commute_metrics(
                origin_coords=origin_coords,
                dest_coords=dest_coords,
                origin_address=origin_address,
                dest_address=dest_address,
            )
        except (
            APIConnectionError,
            APIHTTPError,
            APIResponseFormatError,
            APIDataValidationError,
            Exception,
        ) as err:
            logger.warning(
                f"Commute lookup failed for {origin_address} -> {dest_address}: {err}. "
                f"Engaging Graceful Fallback mode."
            )
            commute = CommuteMetrics(
                origin_address=origin_address,
                dest_address=dest_address,
                distance_km=0.0,
                duration_minutes=0.0,
                is_verified=False,
            )

        # Step 4: Business Decision Logic & Scoring
        effective_max_commute = getattr(seeker, "max_commute_minutes", self.max_commute_minutes)

        if commute.is_verified and commute.duration_minutes > effective_max_commute:
            status = "REJECTED_COMMUTE_EXCEEDED"
            is_approved = False
            score = 0.0
        elif not commute.is_verified:
            status = "FALLBACK_UNVERIFIED"
            is_approved = False  # Protect seeker from unverified contract
            score = self.strategy.calculate_score(seeker, owner, commute)
        else:
            status = "APPROVED"
            is_approved = True
            score = self.strategy.calculate_score(seeker, owner, commute)

        result = MatchEvaluationResult(
            seeker_phone=seeker.phone,
            owner_phone=owner.phone,
            city=owner.apartment.city,
            rent_per_room=owner.apartment.rent_per_room,
            score=score,
            commute_metrics=commute,
            status=status,
            is_approved=is_approved,
            seeker_name=seeker.name,
            owner_name=owner.name,
        )

        # Step 5: Notify Observers
        self._notify_observers(result)
        return result

    def _notify_observers(self, result: MatchEvaluationResult) -> None:
        """Helper to broadcast event payload to all registered observers."""
        payload = result.to_event_data()
        for observer in self.observers:
            try:
                observer.on_match_evaluated(payload)
            except Exception as obs_err:
                logger.error(f"Observer {type(observer).__name__} failed: {obs_err}")
