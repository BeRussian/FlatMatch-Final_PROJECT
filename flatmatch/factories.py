"""
FlatMatch - User Domain Factory (Factory Pattern - Part 3)
===========================================================
Implements the Factory Pattern for encapsulating polymorphic instantiation
of domain users (ApartmentSeeker vs RoommateSeeker).
"""

from flatmatch.models import User, ApartmentSeeker, RoommateSeeker

VALID_USER_TYPES = {"apartment_seeker", "roommate_seeker"}


class UserFactory:
    """
    Factory class responsible for instantiating concrete User subclasses
    based on record metadata.
    """

    @staticmethod
    def create_user(data: dict) -> User:
        """
        Instantiates and returns the appropriate User subclass from a raw dict.
        Raises TypeError if data is not a dict.
        Raises ValueError if 'type' is missing, unknown, or if record is malformed.
        """
        if not isinstance(data, dict):
            raise TypeError(f"User record must be a dict, got {type(data).__name__}")

        raw_type = data.get("type")
        if not raw_type or not isinstance(raw_type, str):
            # Check structural fallback if type key is missing
            has_apt = "apartment" in data
            has_budget = "max_budget" in data
            if has_apt and not has_budget:
                return RoommateSeeker.from_dict(data)
            elif has_budget and not has_apt:
                return ApartmentSeeker.from_dict(data)
            raise ValueError(f"Record is missing valid 'type' key: {data}")

        clean_type = raw_type.strip().lower()
        if clean_type not in VALID_USER_TYPES:
            raise ValueError(
                f"Unknown or unsupported user type '{raw_type}'. "
                f"Supported types are: {', '.join(sorted(VALID_USER_TYPES))}."
            )

        if clean_type == "apartment_seeker":
            return ApartmentSeeker.from_dict(data)
        elif clean_type == "roommate_seeker":
            return RoommateSeeker.from_dict(data)
        else:
            raise ValueError(f"Unsupported user type: '{clean_type}'")
