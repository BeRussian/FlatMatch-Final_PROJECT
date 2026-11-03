"""
Unit tests for Threaded Room Inventory and Lock-based Race Condition Prevention
"""

import pytest
from flatmatch.threaded_processing import (
    SharedRoomInventory,
    UnsafeSharedRoomInventory,
    run_concurrent_room_bookings,
)


def test_shared_room_inventory_sequential_booking():
    """Verifies that room inventory tracks bookings and rejections accurately in single-thread."""
    inv = SharedRoomInventory(apartment_id="APT-01", available_rooms=2)
    assert inv.attempt_room_booking("Alice") is True
    assert inv.available_rooms == 1
    assert inv.attempt_room_booking("Bob") is True
    assert inv.available_rooms == 0
    assert inv.attempt_room_booking("Charlie") is False
    assert inv.available_rooms == 0
    assert inv.booked_seekers == ["Alice", "Bob"]
    assert inv.rejected_seekers == ["Charlie"]


def test_concurrent_room_bookings_guarantees_no_overbooking():
    """Verifies that concurrent threads synchronized with Lock never overbook rooms."""
    available_rooms = 3
    seeker_names = [f"Seeker-{i}" for i in range(1, 16)]  # 15 concurrent applicants for 3 rooms

    inventory = run_concurrent_room_bookings(
        available_rooms=available_rooms,
        seeker_names=seeker_names,
        apartment_id="APT-POPULAR-01",
        artificial_delay=0.001,
    )

    assert len(inventory.booked_seekers) == available_rooms
    assert len(inventory.rejected_seekers) == len(seeker_names) - available_rooms
    assert inventory.available_rooms == 0
    assert inventory.total_attempts == len(seeker_names)


def test_zero_capacity_inventory_rejects_all():
    """Verifies that an apartment with 0 rooms rejects all concurrent applicants safely."""
    inventory = run_concurrent_room_bookings(
        available_rooms=0,
        seeker_names=["User-1", "User-2", "User-3"],
    )
    assert len(inventory.booked_seekers) == 0
    assert len(inventory.rejected_seekers) == 3
    assert inventory.available_rooms == 0
