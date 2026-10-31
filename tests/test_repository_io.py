"""
Unit tests for Repository File I/O and Streaming using tmp_path
"""

import json
import pytest
from flatmatch.repository import FlatMatchRepository, stream_users_from_jsonl


def test_repository_load_from_jsonl_tmp_path(tmp_path):
    """Verifies repository loads valid records from temporary JSONL file."""
    test_file = tmp_path / "test_data.jsonl"
    records = [
        {
            "name": "User One",
            "age": 22,
            "phone": "050-1001",
            "type": "apartment_seeker",
            "max_budget": 3000.0,
            "destination_address": "Tel Aviv",
            "preferences": {"cleanliness": 4, "is_smoker": False, "allows_pets": True},
        },
        {
            "name": "User Two",
            "age": 26,
            "phone": "050-1002",
            "type": "roommate_seeker",
            "apartment": {
                "city": "Tel Aviv",
                "rent": 3000.0,
                "rooms": 2,
                "amenities": ["Air Conditioner"],
            },
            "preferences": {"cleanliness": 4, "is_smoker": False, "allows_pets": True},
        },
    ]

    with open(test_file, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    repo = FlatMatchRepository(str(test_file))
    assert repo.total_users() == 2
    assert repo.find_by_phone("050-1001").name == "User One"
    assert repo.find_by_phone("050-1002").name == "User Two"


def test_repository_duplicate_phone_rejected_tmp_path(tmp_path):
    """Verifies that duplicate phone IDs are detected and rejected during file loading."""
    dup_file = tmp_path / "duplicates.jsonl"
    records = [
        {"name": "Original", "age": 24, "phone": "050-DUP-01", "type": "apartment_seeker", "max_budget": 3000.0},
        {"name": "Imposter", "age": 25, "phone": "050-DUP-01", "type": "apartment_seeker", "max_budget": 3200.0},
    ]
    with open(dup_file, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    repo = FlatMatchRepository()
    with pytest.raises(ValueError, match="Duplicate user phone ID detected"):
        repo.load_from_file(str(dup_file))
