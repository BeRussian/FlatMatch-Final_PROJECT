"""
FlatMatch - Context Managers for Resource and Session Lifecycle (Part D)
========================================================================
This module implements custom context managers using __enter__ and __exit__:
1. SearchSessionContext: Manages active search sessions, metrics, timing, and graceful cleanup.
2. ApartmentHoldContext: Manages temporary status locks/holds on apartments during application review,
   guaranteeing state rollback even upon exceptions without suppressing errors.
"""

import time
try:
    from flatmatch.models import Apartment, ApartmentSeeker
except ImportError:
    from .models import Apartment, ApartmentSeeker


class SearchSessionContext:
    """
    Context manager managing a seeker's active search session lifecycle.

    Guarantees:
    - Automatically activates and timestamps the session on __enter__.
    - Tracks operations and candidate evaluations during the session.
    - Accurately measures execution time.
    - In __exit__, gracefully marks the session as COMPLETED or ABORTED_WITH_ERROR.
    - Never suppresses exceptions (returns False) so caller can handle errors properly.
    """

    def __init__(self, seeker_name: str, session_id: str):
        if not seeker_name or not session_id:
            raise ValueError("seeker_name and session_id must be non-empty strings")
        self.seeker_name = seeker_name
        self.session_id = session_id
        self.status = "PENDING"
        self.start_time = None
        self.end_time = None
        self.duration_seconds = 0.0
        self.evaluated_count = 0
        self.matches_found = []
        self.error_info = None

    def record_evaluation(self, count: int = 1):
        """Records the number of candidates evaluated during this session."""
        self.evaluated_count += count

    def record_match(self, match_summary: str):
        """Records a successful match candidate found during this session."""
        self.matches_found.append(match_summary)

    def __enter__(self):
        self.status = "ACTIVE"
        self.start_time = time.perf_counter()
        print(f"[SearchSessionContext] Started Session '{self.session_id}' for Seeker '{self.seeker_name}'. Status: {self.status}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        if self.start_time is not None:
            self.duration_seconds = round(self.end_time - self.start_time, 4)

        if exc_type is not None:
            # An exception occurred inside the with block
            self.status = "ABORTED_WITH_ERROR"
            self.error_info = {
                "exception_type": exc_type.__name__,
                "exception_message": str(exc_val)
            }
            print(f"[SearchSessionContext] Session '{self.session_id}' failed due to {exc_type.__name__}: {exc_val}. Cleaned up state (Status: {self.status}, Duration: {self.duration_seconds}s).")
            # Do NOT suppress exception! Return False to allow exception propagation
            return False

        # Successful completion
        self.status = "COMPLETED"
        print(f"[SearchSessionContext] Closed Session '{self.session_id}' successfully. Evaluated: {self.evaluated_count}, Matches: {len(self.matches_found)}, Duration: {self.duration_seconds}s.")
        return False


class ApartmentHoldContext:
    """
    Context manager that temporarily locks an apartment into an 'ON_HOLD' status
    while an application is being evaluated or processed.

    Guarantees:
    - Marks the apartment as held upon entry.
    - Reverts apartment status back to 'AVAILABLE' upon exit, even if an exception occurs.
    - Returns False from __exit__ so errors are not silenced.
    """

    def __init__(self, apartment: Apartment, applicant_name: str):
        if not isinstance(apartment, Apartment):
            raise TypeError("apartment must be an instance of Apartment")
        if not applicant_name:
            raise ValueError("applicant_name must be a non-empty string")
        self.apartment = apartment
        self.applicant_name = applicant_name
        self.previous_status = getattr(apartment, "status", "AVAILABLE")

    def __enter__(self):
        if getattr(self.apartment, "status", "AVAILABLE") == "ON_HOLD":
            raise ValueError(f"Apartment in '{self.apartment.city}' is already ON_HOLD by another process.")
        
        self.apartment.status = "ON_HOLD"
        print(f"[ApartmentHoldContext] Placed apartment in '{self.apartment.city}' ON_HOLD for applicant '{self.applicant_name}'.")
        return self.apartment

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Guaranteed rollback to previous status
        self.apartment.status = self.previous_status
        if exc_type is not None:
            print(f"[ApartmentHoldContext] Exception caught during application processing ({exc_type.__name__}). Rollback apartment status to '{self.previous_status}'.")
            return False
        
        print(f"[ApartmentHoldContext] Application review finalized. Restored apartment status to '{self.previous_status}'.")
        return False


# ==============================================================================
# Verification Suite & Demonstration
# ==============================================================================

def demonstrate_session_context():
    print("\n--- 1. SearchSessionContext Normal Execution ---")
    with SearchSessionContext("Alice Cohen", "SES-101") as session:
        session.record_evaluation(5)
        session.record_match("Apartment in Tel Aviv (3500 NIS)")
        time.sleep(0.01)  # Simulate brief search work
        print(f"  Inside with-block: Status={session.status}, Matches={len(session.matches_found)}")

    assert session.status == "COMPLETED"
    assert session.duration_seconds > 0
    assert len(session.matches_found) == 1
    print("[PASS] Normal session lifecycle verified.")

    print("\n--- 2. SearchSessionContext Error Handling Verification ---")
    exception_propagated = False
    try:
        with SearchSessionContext("Alice Cohen", "SES-102") as session:
            session.record_evaluation(2)
            # Simulate unexpected business logic failure
            raise RuntimeError("Database connection timeout during search")
    except RuntimeError as err:
        exception_propagated = True
        print(f"  Caught expected error outside with-block: {err}")

    assert exception_propagated, "Exception should have propagated out of context manager."
    assert session.status == "ABORTED_WITH_ERROR"
    assert session.error_info["exception_type"] == "RuntimeError"
    print("[PASS] Error handling verified: state cleaned up and exception re-raised without suppression.")


def demonstrate_apartment_hold_context():
    print("\n--- 3. ApartmentHoldContext Normal Lifecycle ---")
    apt = Apartment("Tel Aviv", 3500, rooms=2, amenities={"Balcony"})
    apt.status = "AVAILABLE"

    with ApartmentHoldContext(apt, "Ben Levi") as held_apt:
        assert held_apt.status == "ON_HOLD"
        print(f"  Inside with-block: Apartment status={held_apt.status}")

    assert apt.status == "AVAILABLE"
    print(f"  After with-block: Apartment status successfully reverted to '{apt.status}'.")
    print("[PASS] Normal hold lifecycle verified.")

    print("\n--- 4. ApartmentHoldContext Exception Rollback Verification ---")
    error_caught = False
    try:
        with ApartmentHoldContext(apt, "Dana Mizrahi"):
            assert apt.status == "ON_HOLD"
            raise ValueError("Application documents rejected")
    except ValueError as err:
        error_caught = True
        print(f"  Caught expected error outside with-block: {err}")

    assert error_caught
    assert apt.status == "AVAILABLE"
    print(f"  After error: Apartment status successfully rolled back to '{apt.status}'.")
    print("[PASS] Exception rollback verified.")


if __name__ == "__main__":
    print("============================================================")
    print("FlatMatch - Part D: Context Managers Demo")
    print("============================================================")
    demonstrate_session_context()
    demonstrate_apartment_hold_context()
    print("\n============================================================")
    print("All context manager requirements passed successfully!")
    print("============================================================")
