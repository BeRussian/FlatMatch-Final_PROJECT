"""
FlatMatch - Threaded Operations & Race Condition Prevention (Part 4)
=====================================================================
Demonstrates multi-threading with explicit thread synchronization using
threading.Lock to protect critical Check-Then-Act sections from race conditions
during concurrent apartment room booking.
"""

import threading
import time
from typing import List
from flatmatch.config import get_logger

logger = get_logger("threading")


class SharedRoomInventory:
    """
    Thread-safe inventory for an apartment's available rooms.
    Guarantees thread safety on the Check-Then-Act booking pattern
    using an internal threading.Lock.
    """

    def __init__(self, apartment_id: str, available_rooms: int) -> None:
        self.apartment_id = str(apartment_id)
        self.available_rooms = max(0, int(available_rooms))
        self.initial_capacity = self.available_rooms
        self.booked_seekers: List[str] = []
        self.rejected_seekers: List[str] = []
        self._lock = threading.Lock()

    def attempt_room_booking(self, seeker_name: str, artificial_delay: float = 0.0) -> bool:
        """
        Safely attempts to book an available room for a seeker.
        Guards the critical check-then-act section with self._lock.
        """
        with self._lock:
            if artificial_delay > 0:
                time.sleep(artificial_delay)

            if self.available_rooms > 0:
                self.available_rooms -= 1
                self.booked_seekers.append(seeker_name)
                logger.debug(
                    f"[Thread-Safe Booking SUCCESS] {seeker_name} reserved room in {self.apartment_id}. "
                    f"Remaining rooms: {self.available_rooms}"
                )
                return True
            else:
                self.rejected_seekers.append(seeker_name)
                logger.debug(
                    f"[Thread-Safe Booking REJECTED] {seeker_name} could not book {self.apartment_id}: "
                    f"No rooms available."
                )
                return False

    @property
    def total_attempts(self) -> int:
        return len(self.booked_seekers) + len(self.rejected_seekers)

    def __repr__(self) -> str:
        return (
            f"SharedRoomInventory(apt='{self.apartment_id}', remaining={self.available_rooms}, "
            f"booked={len(self.booked_seekers)}, rejected={len(self.rejected_seekers)})"
        )


class UnsafeSharedRoomInventory:
    """
    Intentionally unsynchronized room inventory to demonstrate race conditions
    and overbooking when no lock is applied.
    """

    def __init__(self, apartment_id: str, available_rooms: int) -> None:
        self.apartment_id = str(apartment_id)
        self.available_rooms = max(0, int(available_rooms))
        self.initial_capacity = self.available_rooms
        self.booked_seekers: List[str] = []
        self.rejected_seekers: List[str] = []

    def attempt_room_booking(self, seeker_name: str, artificial_delay: float = 0.001) -> bool:
        """Unprotected Check-Then-Act vulnerable to context switches."""
        # Check
        if self.available_rooms > 0:
            if artificial_delay > 0:
                time.sleep(artificial_delay)  # Yield CPU to trigger race condition
            # Act
            self.available_rooms -= 1
            self.booked_seekers.append(seeker_name)
            return True
        else:
            self.rejected_seekers.append(seeker_name)
            return False


def run_concurrent_room_bookings(
    available_rooms: int,
    seeker_names: List[str],
    apartment_id: str = "APT-SHARED-01",
    artificial_delay: float = 0.0,
) -> SharedRoomInventory:
    """
    Spawns concurrent worker threads, each attempting to book a room.
    
    Adheres strictly to proper thread lifecycle management:
    - Loop 1: Starts all threads with t.start().
    - Loop 2: Joins all threads with t.join().
    Never calls join inside the start loop.
    """
    inventory = SharedRoomInventory(apartment_id=apartment_id, available_rooms=available_rooms)
    threads: List[threading.Thread] = []

    for name in seeker_names:
        t = threading.Thread(
            target=inventory.attempt_room_booking,
            args=(name, artificial_delay),
            name=f"BookingThread-{name}",
        )
        threads.append(t)

    # Loop 1: Start all worker threads concurrently
    for t in threads:
        t.start()

    # Loop 2: Await completion of all worker threads
    for t in threads:
        t.join()

    return inventory
