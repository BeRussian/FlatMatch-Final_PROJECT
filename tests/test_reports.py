"""
Unit tests for LeaseInspectionSubsystem and Integrated Business Reports
"""

import pytest
from flatmatch.repository import FlatMatchRepository
from flatmatch.reports import (
    LeaseInspectionSubsystem,
    SubsystemSyncObserver,
    generate_integrated_business_report,
)


def test_subsystem_inspects_approved_and_fallback_matches():
    """Verifies lifecycle status mapping for approved vs unverified matches."""
    subsystem = LeaseInspectionSubsystem()

    rec_approved = subsystem.inspect_candidate_match(
        seeker_phone="050-1",
        owner_phone="050-2",
        match_status="APPROVED",
        score=85.0,
        city="Tel Aviv",
    )
    assert rec_approved["status"] == "READY_FOR_LEASE"
    assert rec_approved["is_ready_for_lease"] is True

    rec_unverified = subsystem.inspect_candidate_match(
        seeker_phone="050-3",
        owner_phone="050-4",
        match_status="FALLBACK_UNVERIFIED",
        score=65.0,
        city="Ramat Gan",
    )
    assert rec_unverified["status"] == "PENDING_MANUAL_VERIFICATION"
    assert rec_unverified["is_ready_for_lease"] is False


def test_subsystem_cross_validates_repository_parties(sample_seeker, sample_owner):
    """Verifies that unknown party phones are rejected by the inspection subsystem."""
    repo = FlatMatchRepository()
    repo.add_user(sample_seeker)
    # Note: sample_owner is NOT added to repo

    subsystem = LeaseInspectionSubsystem(repository=repo)
    rec = subsystem.inspect_candidate_match(
        seeker_phone=sample_seeker.phone,
        owner_phone="050-UNREGISTERED",
        match_status="APPROVED",
    )

    assert rec["status"] == "REJECTED_UNKNOWN_PARTY"
    assert rec["is_ready_for_lease"] is False


def test_subsystem_sync_observer_updates_inspections():
    """Verifies that SubsystemSyncObserver synchronizes event payloads to subsystem."""
    subsystem = LeaseInspectionSubsystem()
    observer = SubsystemSyncObserver(subsystem)

    payload = {
        "seeker_phone": "050-111",
        "owner_phone": "050-222",
        "status": "APPROVED",
        "score": 90.0,
        "city": "Herzliya",
    }
    observer.on_match_evaluated(payload)

    record = subsystem.get_inspection("050-111", "050-222")
    assert record is not None
    assert record["status"] == "READY_FOR_LEASE"
    assert record["city"] == "Herzliya"


def test_generate_integrated_business_report(sample_seeker, sample_owner):
    """Verifies computation of executive metrics and verification ratio."""
    repo = FlatMatchRepository()
    repo.add_user(sample_seeker)
    repo.add_user(sample_owner)

    subsystem = LeaseInspectionSubsystem(repository=repo)
    # Inspect 1 approved and 1 unverified
    subsystem.inspect_candidate_match(sample_seeker.phone, sample_owner.phone, "APPROVED")
    subsystem.inspect_candidate_match(sample_seeker.phone, sample_owner.phone, "FALLBACK_UNVERIFIED")

    report = generate_integrated_business_report(repo, subsystem)
    assert report["total_seekers_and_owners"] == 2
    assert report["total_inspected_pairs"] == 1  # Keyed by (seeker, owner), so updated to latest
    assert "status_distribution" in report
