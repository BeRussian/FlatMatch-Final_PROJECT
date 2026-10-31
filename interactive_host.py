"""
FlatMatch - Interactive Host & Roommate Finder (CLI)
====================================================
Interactive console application allowing Apartment Owners / Primary Tenants
(RoommateSeekers) to register their shared apartment and find compatible
roommates from the seeker candidate pool based on lifestyle harmony, budget,
and verified commute times to the candidate's university or workplace.

Usage:
    python interactive_host.py          (Default: Uses live OSRM routing with offline fallback)
    python interactive_host.py --mock   (Deterministic offline mode)
"""

import os
import sys
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 I/O encoding across Windows consoles to seamlessly handle all characters
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flatmatch import (
    Apartment,
    ApartmentSeeker,
    RoommateSeeker,
    Preferences,
    FlatMatchRepository,
    AddressNormalizer,
    NominatimGeocodingClient,
    CommuteAPIClient,
)


def get_input(prompt: str, default: str = "") -> str:
    """Helper to get user input with an optional default value."""
    if default:
        raw = input(f"{prompt} [{default}]: ").strip()
        return raw if raw else default
    return input(f"{prompt}: ").strip()


def get_int_input(prompt: str, default: int, min_val: int, max_val: int) -> int:
    """Safely prompt for an integer within a specified range."""
    while True:
        raw = get_input(prompt, str(default))
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  [!] Please enter a whole number between {min_val} and {max_val}.")
        except ValueError:
            print("  [!] Invalid input. Expected an integer number.")


def get_float_input(prompt: str, default: float, min_val: float) -> float:
    """Safely prompt for a positive floating point number."""
    while True:
        raw = get_input(prompt, str(default))
        try:
            val = float(raw)
            if val >= min_val:
                return val
            print(f"  [!] Please enter a number greater than or equal to {min_val}.")
        except ValueError:
            print("  [!] Invalid input. Expected a valid number.")


def get_bool_input(prompt: str, default: bool) -> bool:
    """Prompt for a yes/no boolean value."""
    default_str = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} ({default_str}): ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes", "true", "1"):
            return True
        if raw in ("n", "no", "false", "0"):
            return False
        print("  [!] Please answer 'y' for Yes or 'n' for No.")


def get_kashrut_input() -> str:
    """Prompt for kashrut category with numbered presets or direct names."""
    print("\nSelect apartment Kashrut standard:")
    print("  [1] secular       (חילוני)")
    print("  [2] traditional   (מסורתי)")
    print("  [3] religious     (דתי)")
    print("  [4] ultra_orthodox (חרדי)")

    mapping = {
        "1": "secular",
        "2": "traditional",
        "3": "religious",
        "4": "ultra_orthodox",
        "secular": "secular",
        "traditional": "traditional",
        "religious": "religious",
        "ultra_orthodox": "ultra_orthodox",
    }
    raw = input("Enter choice [1-4, default: 1 (secular)]: ").strip().lower()
    return mapping.get(raw, "secular")


def run_host_interactive_session():
    print("=" * 80)
    print("   FLATMATCH - APARTMENT OWNER / HOST ROOMMATE MATCHER (CLI)")
    print("=" * 80)
    print("Welcome Host! Register your apartment and find ideal roommates from our")
    print("active candidate pool based on budget, lifestyle, and verified commute.")
    print("-" * 80)

    # --------------------------------------------------------------------------
    # Step 1: Host Personal Details
    # --------------------------------------------------------------------------
    print("\n[STEP 1: HOST PERSONAL DETAILS]")
    name = ""
    while not name:
        name = get_input("Enter your full name", default="Daniel Host")
        if not name:
            print("  [!] Name cannot be blank.")

    age = get_int_input("Enter your age", default=28, min_val=18, max_val=120)
    phone = get_input("Enter your contact phone", default="052-8889900")

    # --------------------------------------------------------------------------
    # Step 2: Apartment Details & Location
    # --------------------------------------------------------------------------
    print("\n[STEP 2: APARTMENT DETAILS & ADDRESS]")

    # Validate city against supported Israeli cities/settlements
    city = ""
    while not city:
        candidate_city = get_input("Enter apartment city (e.g. Kiryat Ono, Tel Aviv, Ramat Gan)", default="Kiryat Ono")
        if Apartment.is_valid_city(candidate_city):
            city = candidate_city
        else:
            print(f"  [!] City '{candidate_city}' was not recognized. Please enter a valid Israeli city or settlement.")

    street_address = get_input("Enter specific street address", default=f"Levi Eshkol 14, {city}")
    rent = get_float_input("Enter total apartment monthly rent (NIS)", default=3400.0, min_val=1000.0)
    rooms = get_int_input("Enter total number of rooms in apartment", default=2, min_val=1, max_val=10)

    print("\nSelect apartment amenities (press Enter for defaults):")
    has_ac = get_bool_input("Air Conditioner?", default=True)
    has_mamad = get_bool_input("Mamad (Secure Room)?", default=True)
    has_balcony = get_bool_input("Balcony?", default=True)
    has_elevator = get_bool_input("Elevator?", default=True)
    has_parking = get_bool_input("Private Parking?", default=False)

    amenities = set()
    if has_ac:
        amenities.add("Air Conditioner")
    if has_mamad:
        amenities.add("Mamad")
    if has_balcony:
        amenities.add("Balcony")
    if has_elevator:
        amenities.add("Elevator")
    if has_parking:
        amenities.add("Parking")

    # Create Apartment Object
    apartment = Apartment(
        city=city,
        rent=rent,
        rooms=rooms,
        amenities=amenities,
        address=street_address,
    )

    # --------------------------------------------------------------------------
    # Step 3: Lifestyle & Living Rules
    # --------------------------------------------------------------------------
    print("\n[STEP 3: APARTMENT LIFESTYLE & ROOMMATE RULES]")
    is_smoker = get_bool_input("Is smoking allowed in the apartment?", default=False)
    allows_pets = get_bool_input("Are pets allowed in the apartment?", default=True)
    cleanliness = get_int_input("Apartment cleanliness standard (1=relaxed, 5=spotless)", default=4, min_val=1, max_val=5)
    sleep_sched = get_input("Apartment sleep routine (morning_person / night_owl / flexible)", default="morning_person")
    if sleep_sched not in ("morning_person", "night_owl", "flexible"):
        sleep_sched = "flexible"

    kashrut_level = get_kashrut_input()
    shabbat = get_bool_input("Do you observe Shabbat in the apartment?", default=False)

    host_prefs = Preferences(
        cleanliness=cleanliness,
        allows_pets=allows_pets,
        is_smoker=is_smoker,
        sleep_schedule=sleep_sched,
        kashrut_level=kashrut_level,
        shabbat_observant=shabbat,
    )

    host = RoommateSeeker(
        name=name,
        age=age,
        phone=phone,
        apartment=apartment,
        preferences=host_prefs,
    )

    rent_per_room = apartment.rent_per_room

    print("\n" + "=" * 80)
    print("  HOST APARTMENT REGISTERED SUCCESSFULLY")
    print(f"  Host: {host.name} (Phone: {host.phone}) | Location: {apartment.address}")
    print(f"  Rent: {apartment.rent:,.0f} NIS total | {rent_per_room:,.0f} NIS per room ({apartment.rooms} rooms)")
    print(f"  Rules: Pets: {host_prefs.allows_pets} | Smoking: {host_prefs.is_smoker} | Kashrut: {host_prefs.kashrut_level}")
    print(f"  Perks: {', '.join(sorted(apartment.amenities)) if apartment.amenities else 'Standard'}")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # Step 4: Search Active Seeker Pool & Verify Commute
    # --------------------------------------------------------------------------
    print("\n[MATCHING CANDIDATES FROM ACTIVE SEEKER POOL VIA OSRM API...]")

    use_mock = "--mock" in sys.argv
    geocoder = NominatimGeocodingClient(use_live_network=not use_mock)

    apt_normalized = AddressNormalizer.normalize(apartment.address)
    apt_coords = geocoder.geocode(apt_normalized)
    print(f"  [1/3] Apartment coordinates resolved: lon={apt_coords[0]:.4f}, lat={apt_coords[1]:.4f}")

    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    repo = FlatMatchRepository(data_path)
    registered_seekers: List[ApartmentSeeker] = repo.get_apartment_seekers()
    print(f"  [2/3] Evaluating {len(registered_seekers)} registered room seekers in database...")

    commute_client = CommuteAPIClient(max_retries=3)

    matching_candidates: List[Dict[str, Any]] = []
    rejected_candidates: List[Dict[str, Any]] = []

    for seeker in registered_seekers:
        # 1. Budget and Dealbreakers Check
        if seeker.max_budget < rent_per_room:
            rejected_candidates.append({
                "seeker": seeker,
                "reason": f"Budget ({seeker.max_budget:,.0f} NIS) is below room rent ({rent_per_room:,.0f} NIS)",
            })
            continue

        if seeker.preferences.has_conflict(host.preferences):
            if seeker.preferences.is_smoker != host.preferences.is_smoker:
                reason = "Smoking policy conflict"
            elif seeker.preferences.allows_pets != host.preferences.allows_pets:
                reason = "Pet policy conflict"
            else:
                reason = "Lifestyle conflict"
            rejected_candidates.append({
                "seeker": seeker,
                "reason": reason,
            })
            continue

        # 2. External Commute Query: From this apartment to Seeker's destination
        seeker_dest_normalized = AddressNormalizer.normalize(seeker.destination_address)
        seeker_coords = geocoder.geocode(seeker_dest_normalized)

        try:
            commute = commute_client.fetch_commute_metrics(
                origin_coords=apt_coords,
                dest_coords=seeker_coords,
                origin_address=apartment.address,
                dest_address=seeker_dest_normalized,
            )
        except Exception:
            commute = None

        if commute and commute.duration_minutes > seeker.max_commute_minutes:
            rejected_candidates.append({
                "seeker": seeker,
                "reason": f"Commute to candidate's goal ({commute.duration_minutes:.1f} min) exceeds candidate limit ({seeker.max_commute_minutes:.0f} min)",
            })
            continue

        duration_min = commute.duration_minutes if commute else 0.0
        distance_km = commute.distance_km if commute else 0.0
        budget_surplus = seeker.max_budget - rent_per_room

        matching_candidates.append({
            "seeker": seeker,
            "duration_minutes": duration_min,
            "distance_km": distance_km,
            "budget_surplus": budget_surplus,
            "is_verified": commute.is_verified if commute else False,
        })

    # Sort matching candidates: shortest commute first, then highest budget surplus
    matching_candidates.sort(key=lambda item: (item["duration_minutes"], -item["budget_surplus"]))

    # --------------------------------------------------------------------------
    # Step 5: Results Display
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"  ROOMMATE MATCH RESULTS FOR HOST {host.name.upper()} ({apartment.address})")
    print(f"  Room Rent: {rent_per_room:,.0f} NIS / month | Total Evaluated: {len(registered_seekers)} Candidates")
    print("=" * 80)

    if matching_candidates:
        print(f"\nSUCCESS: Found {len(matching_candidates)} compatible roommate candidate(s) for your apartment:\n")
        for idx, match in enumerate(matching_candidates, start=1):
            seeker = match["seeker"]
            print(f"#{idx} [CANDIDATE: {seeker.name.upper()}] (Age: {seeker.age}, Phone: {seeker.phone})")
            print(f"   Destination:     {seeker.destination_address}")
            print(f"   Commute Time:    {match['duration_minutes']:.1f} min ({match['distance_km']:.1f} km drive) [Verified: {match['is_verified']}]")
            print(f"   Candidate Limit: Accepts up to {seeker.max_commute_minutes:.0f} min commute")
            print(f"   Budget Capacity: {seeker.max_budget:,.0f} NIS (Surplus: +{match['budget_surplus']:,.0f} NIS above room rent)")
            print(f"   Lifestyle:       Cleanliness {seeker.preferences.cleanliness}/5, Pets: {seeker.preferences.allows_pets}, Smoking: {seeker.preferences.is_smoker}, Kashrut: {seeker.preferences.kashrut_level}")
            print("   " + "-" * 74)
    else:
        print("\nNo registered seekers currently match your apartment's room rent, location, and lifestyle rules.")

    if rejected_candidates:
        print("\n[FILTERED OUT CANDIDATES]")
        for rej in rejected_candidates:
            cand = rej["seeker"]
            print(f"  * {cand.name} (Phone: {cand.phone}): Filtered out -> {rej['reason']}")

    print("\n" + "=" * 80)
    print("  HOST MATCHING SESSION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    try:
        run_host_interactive_session()
    except KeyboardInterrupt:
        print("\n\nHost matching session aborted by user. Goodbye!")
