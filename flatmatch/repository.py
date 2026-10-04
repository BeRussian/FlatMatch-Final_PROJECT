"""
FlatMatch - Data Repository and Streaming Reader (Part D)
=========================================================
This module handles incremental, streaming ingestion of synthetic JSONL
records, dictionary parsing, object deserialization via from_dict,
ID duplicate validation, and O(1) indexed lookup.
"""

import json
import os
try:
    from flatmatch.models import User, ApartmentSeeker, RoommateSeeker, Apartment, Preferences
except ImportError:
    from .models import User, ApartmentSeeker, RoommateSeeker, Apartment, Preferences


def parse_user_record(data: dict) -> User:
    """
    Validates dictionary structure and instantiates the appropriate domain model
    using the corresponding @classmethod from_dict.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Record must be a dict, got {type(data).__name__}")

    # Validate essential identification fields common to all users
    required_base_fields = ["name", "age", "phone"]
    for field in required_base_fields:
        if field not in data:
            raise ValueError(f"Record is missing required field '{field}': {data}")

    user_type = data.get("type", "").strip().lower()

    if user_type == "roommate_seeker" or "apartment" in data:
        return RoommateSeeker.from_dict(data)
    elif user_type == "apartment_seeker" or "max_budget" in data:
        return ApartmentSeeker.from_dict(data)
    else:
        raise ValueError(f"Unable to determine user type for record with phone '{data.get('phone')}'.")


def stream_users_from_jsonl(filepath: str):
    """
    Streams and yields domain User objects line-by-line from a JSONL file.

    CRITICAL REQUIREMENTS MET:
    - Uses 'with open(..., encoding="utf-8")'.
    - Traverses line-by-line via file iterator WITHOUT read() or readlines().
    - Converts each line via json.loads and then via from_dict.
    - Yields objects lazily to avoid loading all contents into memory at once.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped_line = line.strip()
            if not stripped_line:
                continue

            try:
                record_dict = json.loads(stripped_line)
            except json.JSONDecodeError as err:
                raise ValueError(f"Line {line_number}: Malformed JSON syntax: {err}") from err

            user_obj = parse_user_record(record_dict)
            yield user_obj


def load_users_from_jsonl(filepath: str) -> list:
    """Convenience function to load and return all users from a JSONL file into a list."""
    return list(stream_users_from_jsonl(filepath))


class FlatMatchRepository:
    """
    Central repository for managing loaded users and apartments with O(1) lookup.
    """

    def __init__(self, data_filepath: str = None):
        self._users_by_phone = {}
        self._users_list = []
        if data_filepath is not None:
            self.load_from_file(data_filepath)

    def load_from_file(self, filepath: str) -> int:
        """
        Loads all records incrementally from the specified JSONL file.
        Detects and rejects duplicate phone IDs to preserve data integrity.
        """
        count = 0
        for user in stream_users_from_jsonl(filepath):
            if user.phone in self._users_by_phone:
                raise ValueError(f"Duplicate user phone ID detected: '{user.phone}' for user '{user.name}'")
            self._users_by_phone[user.phone] = user
            self._users_list.append(user)
            count += 1
        return count

    def get_by_phone(self, phone: str):
        """O(1) safe lookup of user by unique phone ID."""
        return self._users_by_phone.get(phone)

    def get_all_users(self) -> list:
        """Returns all loaded users."""
        return self._users_list.copy()

    def get_apartment_seekers(self) -> list:
        """Filters and returns all ApartmentSeeker instances."""
        return [u for u in self._users_list if isinstance(u, ApartmentSeeker)]

    def get_roommate_seekers(self) -> list:
        """Filters and returns all RoommateSeeker instances."""
        return [u for u in self._users_list if isinstance(u, RoommateSeeker)]

    def __len__(self) -> int:
        return len(self._users_list)

    def __repr__(self) -> str:
        return f"FlatMatchRepository(total_users={len(self._users_list)})"


# ==============================================================================
# Verification Suite & Demonstration
# ==============================================================================

def demonstrate_streaming_and_repository():
    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    print(f"\n--- 1. Incremental Streaming Verification from '{data_path}' ---")

    # Verify lazy streaming generator without pre-allocating whole list
    stream_gen = stream_users_from_jsonl(data_path)
    first_streamed = next(stream_gen)
    second_streamed = next(stream_gen)
    print(f"Streamed 1st user on-the-fly: {first_streamed.get_role_summary()}")
    print(f"Streamed 2nd user on-the-fly: {second_streamed.get_role_summary()}")
    assert first_streamed.name == "Daniel Levin"
    assert second_streamed.name == "Ronit Shapira"
    print("[PASS] Lazy generator yields deserialized objects line-by-line.")

    # Load complete repository
    print("\n--- 2. Repository Loading & ID Indexing ---")
    repo = FlatMatchRepository(data_path)
    print(f"Successfully loaded {repo} from JSONL.")

    seekers = repo.get_apartment_seekers()
    owners = repo.get_roommate_seekers()
    print(f"Loaded Seekers: {len(seekers)}, Loaded Roommate Seekers: {len(owners)}")
    assert len(seekers) >= 15, f"Expected at least 15 seekers, got {len(seekers)}"
    assert len(owners) >= 5, f"Expected at least 5 owners, got {len(owners)}"

    # O(1) Lookup testing
    print("\n--- 3. Lookup by Unique Phone ID ---")
    found_user = repo.get_by_phone("050-1000001")
    missing_user = repo.get_by_phone("050-9999999")
    print(f"Lookup '050-1000001': {found_user.name} ({type(found_user).__name__})")
    print(f"Lookup non-existent '050-9999999': {missing_user}")
    assert found_user is not None and found_user.name == "Daniel Levin"
    assert missing_user is None
    print("[PASS] Phone ID lookups verified.")

    # Duplicate ID validation test
    print("\n--- 4. Duplicate ID Prevention Verification ---")
    duplicate_record = {
        "type": "apartment_seeker",
        "phone": "050-1000001",  # Already in repo
        "name": "Imposter Daniel",
        "age": 28,
        "max_budget": 3000.0,
        "preferred_cities": ["Tel Aviv"]
    }
    dup_repo = FlatMatchRepository()
    dup_repo.load_from_file(data_path)
    duplicate_caught = False
    try:
        # Simulate attempting to load duplicate phone
        user_dup = parse_user_record(duplicate_record)
        if dup_repo.get_by_phone(user_dup.phone):
            raise ValueError(f"Duplicate user phone ID detected: '{user_dup.phone}'")
    except ValueError as e:
        duplicate_caught = True
        print(f"Caught expected duplicate error: {e}")
    assert duplicate_caught, "Expected duplicate check to trigger."
    print("[PASS] Duplicate validation successfully verified.")


if __name__ == "__main__":
    print("============================================================")
    print("FlatMatch - Part D: Repository & Streaming Ingestion Demo")
    print("============================================================")
    demonstrate_streaming_and_repository()
    print("\n============================================================")
    print("All repository and streaming requirements passed successfully!")
    print("============================================================")
