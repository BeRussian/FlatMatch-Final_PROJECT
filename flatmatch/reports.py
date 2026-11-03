"""
FlatMatch - Subsystem Integration & Integrated Business Reports (Part 5)
==========================================================================
Integrates FlatMatchRepository with the LeaseInspectionSubsystem, synchronized
via observer events, and produces executive business reports.
"""

from typing import Dict, Any, Optional, Tuple
from flatmatch.config import get_logger
from flatmatch.repository import FlatMatchRepository
from flatmatch.observers import MatchEventListener

logger = get_logger("reports")


class LeaseInspectionSubsystem:
    """
    Subsystem responsible for validating candidate contracts, ensuring
    all parties exist in the registered repository, and tracking readiness
    for formal lease signing.
    """

    def __init__(self, repository: Optional[FlatMatchRepository] = None) -> None:
        self.repository = repository
        # Maps (seeker_phone, owner_phone) -> inspection record dict
        self.inspections: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def inspect_candidate_match(
        self,
        seeker_phone: str,
        owner_phone: str,
        match_status: str,
        score: float = 0.0,
        city: str = "",
    ) -> Dict[str, Any]:
        """
        Inspects and registers a match evaluation outcome:
        - Validates that both parties exist in repository (if repository is attached).
        - Assigns lifecycle status: READY_FOR_LEASE, PENDING_MANUAL_VERIFICATION,
          REJECTED_HIGH_COMMUTE, REJECTED_DEALBREAKER, or REJECTED_UNKNOWN_PARTY.
        """
        seeker_phone = str(seeker_phone)
        owner_phone = str(owner_phone)

        # Cross-system validation: Check repository registration
        if self.repository is not None:
            seeker_exists = self.repository.find_by_phone(seeker_phone) is not None
            owner_exists = self.repository.find_by_phone(owner_phone) is not None
            if not (seeker_exists and owner_exists):
                inspection = {
                    "seeker_phone": seeker_phone,
                    "owner_phone": owner_phone,
                    "status": "REJECTED_UNKNOWN_PARTY",
                    "reason": "One or both parties not found in registered repository",
                    "score": score,
                    "city": city,
                    "is_ready_for_lease": False,
                }
                self.inspections[(seeker_phone, owner_phone)] = inspection
                return inspection

        # Translate matching status into lease lifecycle status
        if match_status == "APPROVED":
            lease_status = "READY_FOR_LEASE"
            is_ready = True
        elif match_status == "FALLBACK_UNVERIFIED":
            lease_status = "PENDING_MANUAL_VERIFICATION"
            is_ready = False
        elif match_status == "REJECTED_COMMUTE_EXCEEDED":
            lease_status = "REJECTED_HIGH_COMMUTE"
            is_ready = False
        elif match_status == "REJECTED_DEALBREAKER":
            lease_status = "REJECTED_DEALBREAKER"
            is_ready = False
        else:
            lease_status = f"INSPECTED_{match_status}"
            is_ready = False

        inspection = {
            "seeker_phone": seeker_phone,
            "owner_phone": owner_phone,
            "status": lease_status,
            "score": score,
            "city": city,
            "is_ready_for_lease": is_ready,
        }
        self.inspections[(seeker_phone, owner_phone)] = inspection
        return inspection

    def get_inspection(self, seeker_phone: str, owner_phone: str) -> Optional[Dict[str, Any]]:
        return self.inspections.get((seeker_phone, owner_phone))

    @property
    def ready_for_lease_count(self) -> int:
        return sum(1 for rec in self.inspections.values() if rec.get("is_ready_for_lease"))

    @property
    def pending_verification_count(self) -> int:
        return sum(1 for rec in self.inspections.values() if rec.get("status") == "PENDING_MANUAL_VERIFICATION")


class SubsystemSyncObserver(MatchEventListener):
    """
    Observer listening to match evaluation events and automatically
    synchronizing them with the LeaseInspectionSubsystem.
    """

    def __init__(self, subsystem: LeaseInspectionSubsystem) -> None:
        self.subsystem = subsystem

    def on_match_evaluated(self, event_data: dict) -> None:
        seeker_phone = event_data.get("seeker_phone", "")
        owner_phone = event_data.get("owner_phone", "")
        status = event_data.get("status", "UNKNOWN")
        score = event_data.get("score", 0.0)
        city = event_data.get("city", "")

        self.subsystem.inspect_candidate_match(
            seeker_phone=seeker_phone,
            owner_phone=owner_phone,
            match_status=status,
            score=score,
            city=city,
        )


def generate_integrated_business_report(
    repository: FlatMatchRepository,
    subsystem: LeaseInspectionSubsystem,
) -> Dict[str, Any]:
    """
    Generates an integrated business report combining repository statistics
    with lease inspection subsystem results.
    """
    total_users = repository.total_users()
    inspections = list(subsystem.inspections.values())
    total_inspected = len(inspections)
    ready_count = subsystem.ready_for_lease_count
    pending_count = subsystem.pending_verification_count

    # Status distribution
    status_distribution: Dict[str, int] = {}
    for record in inspections:
        st = record.get("status", "UNKNOWN")
        status_distribution[st] = status_distribution.get(st, 0) + 1

    verified_ready_ratio = (
        round(ready_count / total_inspected, 2) if total_inspected > 0 else 0.0
    )

    report = {
        "total_seekers_and_owners": total_users,
        "total_inspected_pairs": total_inspected,
        "ready_for_lease_count": ready_count,
        "pending_manual_verification_count": pending_count,
        "verified_ready_ratio": verified_ready_ratio,
        "status_distribution": status_distribution,
    }

    logger.info(
        f"[IntegratedReport] Users: {total_users}, Inspected: {total_inspected}, "
        f"Ready: {ready_count}, Pending: {pending_count}, Ratio: {verified_ready_ratio}"
    )
    return report
