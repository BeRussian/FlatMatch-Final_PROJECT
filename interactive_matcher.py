"""
FlatMatch - Interactive Terminal Matching System (CLI)
======================================================
Interactive console application allowing users to register as an ApartmentSeeker,
specify their workplace/study destination, budget ceiling, and lifestyle habits,
and receive real-time commute and compatibility matches across all available apartments.

Usage:
    python interactive_matcher.py          (Default: Uses live OSRM routing with offline fallback)
    python interactive_matcher.py --mock   (Deterministic offline mode)
"""

import os
import sys
from typing import List, Tuple, Dict, Any

# Ensure UTF-8 I/O encoding across Windows consoles
if sys.platform.startswith("win"):
    try:
        os.system("")  # Enable native ANSI VT100 colors in Windows console
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GRAY = "\033[90m"
    CYAN = "\033[36m"
    BOLD_CYAN = "\033[1;36m"
    GREEN = "\033[32m"
    BOLD_GREEN = "\033[1;32m"
    YELLOW = "\033[33m"
    BOLD_YELLOW = "\033[1;33m"
    BLUE = "\033[34m"
    BOLD_BLUE = "\033[1;34m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"
    BOLD_RED = "\033[1;31m"


from flatmatch import (
    ApartmentSeeker,
    RoommateSeeker,
    Preferences,
    FlatMatchRepository,
    AddressNormalizer,
    NominatimGeocodingClient,
    CommuteAPIClient,
    APIConnectionError,
    APIHTTPError,
    APIResponseFormatError,
    APIDataValidationError,
)

PRESET_DESTINATIONS = [
    "Ono Academic College (Kiryat Ono)",
    "Tel Aviv University - TAU (Tel Aviv)",
    "Bar-Ilan University - BIU (Ramat Gan)",
    "Reichman University (Herzliya)",
    "Technion - Institute of Technology (Haifa)",
    "Hebrew University of Jerusalem (Jerusalem)",
    "Ben-Gurion University (Beer Sheva)",
    "Azrieli Business Towers (Tel Aviv)",
    "Bursa High-Tech District (Ramat Gan)",
    "Herzliya Pituach Business Park (Herzliya)",
    "Tel Aviv City Center (Tel Aviv)",
    "Jerusalem City Center (Jerusalem)",
]


def get_input(prompt: str, default: str = "") -> str:
    """Helper to get user input with an optional default value."""
    if default:
        raw = input(f"{prompt} [{Color.CYAN}{default}{Color.RESET}]: ").strip()
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
            print(f"  {Color.YELLOW}[!] Please enter a whole number between {min_val} and {max_val}.{Color.RESET}")
        except ValueError:
            print(f"  {Color.RED}[!] Invalid input. Expected an integer number.{Color.RESET}")


def get_float_input(prompt: str, default: float, min_val: float) -> float:
    """Safely prompt for a positive floating point number."""
    while True:
        raw = get_input(prompt, str(default))
        try:
            val = float(raw)
            if val >= min_val:
                return val
            print(f"  {Color.YELLOW}[!] Please enter a number greater than or equal to {min_val}.{Color.RESET}")
        except ValueError:
            print(f"  {Color.RED}[!] Invalid input. Expected a valid number.{Color.RESET}")


def get_bool_input(prompt: str, default: bool) -> bool:
    """Prompt for a yes/no boolean value."""
    default_str = f"{Color.CYAN}Y/n{Color.RESET}" if default else f"{Color.CYAN}y/N{Color.RESET}"
    while True:
        raw = input(f"{prompt} ({default_str}): ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes", "true", "1"):
            return True
        if raw in ("n", "no", "false", "0"):
            return False
        print(f"  {Color.YELLOW}[!] Please answer 'y' for Yes or 'n' for No.{Color.RESET}")


def get_destination_input() -> str:
    """
    Seamless hybrid destination selection.
    User can enter a preset number (1-12) or directly type any custom address/city.
    """
    print(f"\n{Color.BOLD_BLUE}Select your workplace, campus, or study destination:{Color.RESET}")
    for idx, preset in enumerate(PRESET_DESTINATIONS, start=1):
        print(f"  {Color.CYAN}[{idx:2d}]{Color.RESET} {preset}")
    print(f"  {Color.GRAY}Or type any custom street address or city (e.g. Rothschild 10, Tel Aviv){Color.RESET}")

    raw = input(f"\nEnter preset number [1-{len(PRESET_DESTINATIONS)}] OR custom address [{Color.CYAN}{PRESET_DESTINATIONS[0]}{Color.RESET}]: ").strip()
    if not raw:
        return PRESET_DESTINATIONS[0]

    # Check if user entered a valid preset number
    if raw.isdigit():
        choice_idx = int(raw)
        if 1 <= choice_idx <= len(PRESET_DESTINATIONS):
            chosen = PRESET_DESTINATIONS[choice_idx - 1]
            print(f"  {Color.GREEN}-> Selected preset:{Color.RESET} {Color.BOLD}{chosen}{Color.RESET}")
            return chosen

    # Otherwise, treat raw text directly as custom destination
    print(f"  {Color.GREEN}-> Custom destination entered:{Color.RESET} '{Color.BOLD}{raw}{Color.RESET}'")
    return raw


def get_kashrut_input() -> str:
    """Prompt for kashrut category with numbered presets or direct names."""
    print(f"\n{Color.BOLD_BLUE}Select your Kashrut preference:{Color.RESET}")
    print(f"  {Color.CYAN}[1]{Color.RESET} secular")
    print(f"  {Color.CYAN}[2]{Color.RESET} traditional")
    print(f"  {Color.CYAN}[3]{Color.RESET} religious")
    print(f"  {Color.CYAN}[4]{Color.RESET} ultra_orthodox")

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
    raw = input(f"Enter choice [1-4, default: {Color.CYAN}1 (secular){Color.RESET}]: ").strip().lower()
    return mapping.get(raw, "secular")


def get_sleep_schedule_input() -> str:
    """Prompt for sleep schedule with numbered presets or direct names."""
    mapping = {
        "1": "morning_person",
        "2": "night_owl",
        "3": "flexible",
        "morning_person": "morning_person",
        "night_owl": "night_owl",
        "flexible": "flexible",
    }
    raw = input(f"Sleep schedule: [{Color.CYAN}1{Color.RESET}] morning_person, [{Color.CYAN}2{Color.RESET}] night_owl, [{Color.CYAN}3{Color.RESET}] flexible [default: {Color.CYAN}1{Color.RESET}]: ").strip().lower()
    return mapping.get(raw, "morning_person")


def run_interactive_session():
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print(f"      {Color.BOLD_CYAN}FLATMATCH - SMART APARTMENT & ROOMMATE FINDER (CLI){Color.RESET}")
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print("Welcome! Let's find your ideal shared apartment based on real commute times")
    print("and lifestyle compatibility.")
    print(f"{Color.GRAY}{'-' * 80}{Color.RESET}")

    # --------------------------------------------------------------------------
    # Step 1: User Profile & Budget
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[STEP 1: PERSONAL DETAILS & BUDGET]{Color.RESET}")
    name = ""
    while not name:
        name = get_input("Enter your full name")
        if not name:
            print(f"  {Color.RED}[!] Name cannot be blank.{Color.RESET}")

    age = get_int_input("Enter your age", default=24, min_val=18, max_val=120)
    phone = get_input("Enter your contact phone", default="050-1234567")
    max_budget = get_float_input("Enter your maximum monthly budget (NIS)", default=3500.0, min_val=500.0)

    # --------------------------------------------------------------------------
    # Step 2: Workplace / Study Destination & Max Commute
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[STEP 2: DESTINATION & COMMUTE GOAL]{Color.RESET}")
    destination = get_destination_input()
    max_commute = get_float_input("Enter your maximum acceptable commute time (minutes)", default=35.0, min_val=5.0)

    # --------------------------------------------------------------------------
    # Step 3: Lifestyle & Compatibility Preferences
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[STEP 3: LIFESTYLE & COMPATIBILITY PREFERENCES]{Color.RESET}")
    print(f"{Color.GRAY}Press [Enter] to accept the recommended default values:{Color.RESET}")
    is_smoker = get_bool_input("Do you smoke (or allow smoking in the apartment)?", default=False)
    allows_pets = get_bool_input("Do you have (or love living with) pets?", default=True)
    cleanliness = get_int_input("Cleanliness standard (1=relaxed, 5=spotless)", default=4, min_val=1, max_val=5)
    sleep_sched = get_sleep_schedule_input()
    kashrut_level = get_kashrut_input()
    shabbat = get_bool_input("Do you keep Shabbat?", default=False)

    # Create Seeker Instance
    seeker_prefs = Preferences(
        cleanliness=cleanliness,
        allows_pets=allows_pets,
        is_smoker=is_smoker,
        sleep_schedule=sleep_sched,
        kashrut_level=kashrut_level,
        shabbat_observant=shabbat,
    )
    seeker = ApartmentSeeker(
        name=name,
        age=age,
        phone=phone,
        max_budget=max_budget,
        destination_address=destination,
        max_commute_minutes=max_commute,
        preferences=seeker_prefs,
    )

    print(f"\n{Color.BOLD_GREEN}{'=' * 80}{Color.RESET}")
    print(f"  {Color.BOLD_GREEN}USER REGISTERED SUCCESSFULLY{Color.RESET}")
    print(f"  Seeker: {Color.BOLD}{seeker.name}{Color.RESET} (Age: {seeker.age}, Phone: {Color.CYAN}{seeker.phone}{Color.RESET})")
    print(f"  Target: '{Color.BOLD}{seeker.destination_address}{Color.RESET}' (Max Commute: {Color.YELLOW}{seeker.max_commute_minutes:.0f} min{Color.RESET})")
    print(f"  Budget Cap: {Color.GREEN}{seeker.max_budget:,.0f} NIS{Color.RESET} | Pets: {seeker_prefs.allows_pets} | Smoking: {seeker_prefs.is_smoker}")
    print(f"  Kashrut: {seeker_prefs.kashrut_level} | Shabbat: {seeker_prefs.shabbat_observant} | Cleanliness: {seeker_prefs.cleanliness}/5")
    print(f"{Color.BOLD_GREEN}{'=' * 80}{Color.RESET}")

    # --------------------------------------------------------------------------
    # Step 4: Routing & Commute Analysis
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[PROCESSING COMMUTE METRICS VIA EXTERNAL ROUTING API...]{Color.RESET}")

    # 4.1 Address Normalization
    normalized_dest = AddressNormalizer.normalize(seeker.destination_address)
    print(f"  {Color.CYAN}[1/3]{Color.RESET} Normalizing destination: '{seeker.destination_address}' -> '{Color.BOLD}{normalized_dest}{Color.RESET}'")

    # 4.2 Geocoding
    use_mock = "--mock" in sys.argv
    geocoder = NominatimGeocodingClient(use_live_network=not use_mock)
    dest_coords = geocoder.geocode(normalized_dest)
    print(f"  {Color.CYAN}[2/3]{Color.RESET} Geographic coordinates resolved: {Color.YELLOW}lon={dest_coords[0]:.4f}, lat={dest_coords[1]:.4f}{Color.RESET}")

    # 4.3 Load Available Apartments
    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    repo = FlatMatchRepository(data_path)
    available_owners: List[RoommateSeeker] = repo.get_roommate_seekers()
    print(f"  {Color.CYAN}[3/3]{Color.RESET} Querying OSRM Route Service for {Color.BOLD}{len(available_owners)}{Color.RESET} candidate apartments in database...")

    commute_client = CommuteAPIClient(max_retries=3)

    matching_apartments: List[Dict[str, Any]] = []
    rejected_apartments: List[Dict[str, Any]] = []

    for owner in available_owners:
        apt = owner.apartment
        apt_address = apt.address if apt.address else f"Center, {apt.city}"
        apt_normalized = AddressNormalizer.normalize(apt_address)
        apt_coords = geocoder.geocode(apt_normalized)

        # 1. Lifestyle & Hard Dealbreaker Check
        is_dealbreaker = seeker.evaluate_dealbreakers(owner)
        if is_dealbreaker:
            reason = "Lifestyle conflict"
            if apt.rent > seeker.max_budget:
                reason = f"Rent ({apt.rent:,.0f} NIS) exceeds budget ({seeker.max_budget:,.0f} NIS)"
            elif seeker.preferences.has_conflict(owner.preferences):
                if seeker.preferences.is_smoker != owner.preferences.is_smoker:
                    reason = "Smoking policy mismatch"
                elif seeker.preferences.allows_pets != owner.preferences.allows_pets:
                    reason = "Pet tolerance mismatch"
            rejected_apartments.append({
                "owner": owner,
                "city": apt.city,
                "reason": reason,
            })
            continue

        # 2. External Commute Query
        try:
            commute = commute_client.fetch_commute_metrics(
                origin_coords=apt_coords,
                dest_coords=dest_coords,
                origin_address=apt_address,
                dest_address=normalized_dest,
            )
        except Exception:
            commute = None

        if commute and commute.duration_minutes > seeker.max_commute_minutes:
            rejected_apartments.append({
                "owner": owner,
                "city": apt.city,
                "reason": f"Commute too long ({commute.duration_minutes:.1f} min > {seeker.max_commute_minutes:.0f} min)",
            })
            continue

        duration_min = commute.duration_minutes if commute else 0.0
        distance_km = commute.distance_km if commute else 0.0
        rent_per_room = apt.rent_per_room
        savings = seeker.max_budget - rent_per_room

        matching_apartments.append({
            "owner": owner,
            "apt": apt,
            "city": apt.city,
            "address": apt_address,
            "rent_per_room": rent_per_room,
            "total_rent": apt.rent,
            "rooms": apt.rooms,
            "savings": savings,
            "duration_minutes": duration_min,
            "distance_km": distance_km,
            "is_verified": commute.is_verified if commute else False,
            "amenities": sorted(list(apt.amenities)),
        })

    # Sort matching apartments by shortest commute duration first
    matching_apartments.sort(key=lambda item: item["duration_minutes"])

    # --------------------------------------------------------------------------
    # Step 5: Results Display
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print(f"  {Color.BOLD_CYAN}MATCH RESULTS FOR {seeker.name.upper()} (Target: {normalized_dest}){Color.RESET}")
    print(f"  Budget Ceiling: {Color.GREEN}{seeker.max_budget:,.0f} NIS{Color.RESET} | Max Travel Time: {Color.YELLOW}{seeker.max_commute_minutes:.0f} minutes{Color.RESET}")
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")

    if matching_apartments:
        print(f"\n{Color.BOLD_GREEN}SUCCESS:{Color.RESET} Found {Color.BOLD}{len(matching_apartments)}{Color.RESET} relevant apartment(s) within your commute & budget limits:\n")
        for idx, match in enumerate(matching_apartments, start=1):
            owner = match["owner"]
            apt = match["apt"]
            verified_tag = f"{Color.GREEN}[Verified: True]{Color.RESET}" if match["is_verified"] else f"{Color.GRAY}[Fallback]{Color.RESET}"
            savings_tag = f"{Color.GREEN}+{match['savings']:,.0f} NIS{Color.RESET}" if match['savings'] >= 0 else f"{Color.RED}{match['savings']:,.0f} NIS{Color.RESET}"
            
            print(f"{Color.BOLD_YELLOW}#{idx}{Color.RESET} [{Color.BOLD_CYAN}{match['city'].upper()}{Color.RESET}] - Host: {Color.BOLD}{owner.name}{Color.RESET} (Phone: {Color.CYAN}{owner.phone}{Color.RESET})")
            print(f"   Address:          {match['address']}")
            print(f"   Rent per Room:    {Color.BOLD}{match['rent_per_room']:,.0f} NIS{Color.RESET} / month (Savings: {savings_tag} under your budget)")
            print(f"   Total Flat Rent:  {match['total_rent']:,.0f} NIS for {match['rooms']} rooms")
            print(f"   Commute Time:     {Color.BOLD_YELLOW}{match['duration_minutes']:.1f} minutes{Color.RESET} ({match['distance_km']:.1f} km drive) {verified_tag}")
            print(f"   Apartment Perks:  {Color.CYAN}{', '.join(match['amenities']) if match['amenities'] else 'Standard amenities'}{Color.RESET}")
            print(f"   Host Lifestyle:   Cleanliness {owner.preferences.cleanliness}/5, Pets: {owner.preferences.allows_pets}, Smoking: {owner.preferences.is_smoker}, Kashrut: {owner.preferences.kashrut_level}")
            print(f"   {Color.GRAY}{'-' * 74}{Color.RESET}")
    else:
        print(f"\n{Color.YELLOW}No apartments currently match all your criteria (budget, lifestyle, and commute threshold).{Color.RESET}")

    if rejected_apartments:
        print(f"\n{Color.GRAY}[FILTERED OUT CANDIDATES]{Color.RESET}")
        for rej in rejected_apartments:
            owner = rej["owner"]
            print(f"  {Color.GRAY}* {rej['city']} (Host: {owner.name}): Filtered out ->{Color.RESET} {Color.RED}{rej['reason']}{Color.RESET}")

    print(f"\n{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print(f"  {Color.BOLD_CYAN}SEARCH SESSION COMPLETED{Color.RESET}")
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")


if __name__ == "__main__":
    try:
        run_interactive_session()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Session aborted by user. Goodbye!{Color.RESET}")
