"""
FlatMatch - Match Event Observers (Observer Pattern - Part 3)
==============================================================
Implements the Observer pattern for event-driven updates, auditing,
statistical tracking, applicant notifications, and subsystem synchronization.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from flatmatch.config import get_logger

logger = get_logger("observers")


class MatchEventListener(ABC):
    """
    Abstract Observer listening to match evaluation lifecycle events.
    """

    @abstractmethod
    def on_match_evaluated(self, event_data: dict) -> None:
        """
        Receives dictionary payload when a candidate match is evaluated.
        Expected keys: seeker_phone, owner_phone, city, rent_per_room,
        score, commute_metrics, status, is_approved.
        """
        pass


class MatchStatisticsObserver(MatchEventListener):
    """
    Observer 1: Tracks cumulative statistics, approval counts by city,
    and API reliability metrics.
    """

    def __init__(self) -> None:
        self.total_evaluated: int = 0
        self.verified_commutes: int = 0
        self.api_fallbacks: int = 0
        self.approved_by_city: Dict[str, int] = {}
        self.rejected_by_reason: Dict[str, int] = {}

    def on_match_evaluated(self, event_data: dict) -> None:
        self.total_evaluated += 1
        city = event_data.get("city", "Unknown")
        status = event_data.get("status", "UNKNOWN")
        is_approved = event_data.get("is_approved", False)
        commute = event_data.get("commute_metrics")

        if commute and getattr(commute, "is_verified", False):
            self.verified_commutes += 1
        else:
            self.api_fallbacks += 1

        if is_approved:
            self.approved_by_city[city] = self.approved_by_city.get(city, 0) + 1
        else:
            self.rejected_by_reason[status] = self.rejected_by_reason.get(status, 0) + 1

        logger.debug(f"[StatsObserver] Total: {self.total_evaluated}, Approved: {sum(self.approved_by_city.values())}")


class ApplicantNotificationObserver(MatchEventListener):
    """
    Observer 2: Logs and collects real-time notifications for applicants.
    """

    def __init__(self) -> None:
        self.notifications: List[str] = []

    def on_match_evaluated(self, event_data: dict) -> None:
        seeker_name = event_data.get("seeker_name", event_data.get("seeker_phone"))
        owner_name = event_data.get("owner_name", event_data.get("owner_phone"))
        status = event_data.get("status")
        score = event_data.get("score", 0.0)

        if event_data.get("is_approved"):
            msg = (
                f"MATCH APPROVED for {seeker_name} with {owner_name} "
                f"in {event_data.get('city')} (Score: {score:.1f}/100)"
            )
            self.notifications.append(msg)
            logger.info(f"[Notification] {msg}")
        elif status == "FALLBACK_UNVERIFIED":
            msg = f"ACTION REQUIRED: Match between {seeker_name} and {owner_name} pending manual verification."
            self.notifications.append(msg)
            logger.warning(f"[Notification] {msg}")
        else:
            msg = f"Match not approved between {seeker_name} and {owner_name} ({status})."
            self.notifications.append(msg)
