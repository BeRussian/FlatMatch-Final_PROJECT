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


def get_kashrut_input() -> str:
    """Prompt for kashrut category with numbered presets or direct names."""
    print(f"\n{Color.BOLD_BLUE}Select apartment Kashrut standard:{Color.RESET}")
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


def get_smoking_preference(prompt: str = "Smoking policy in the apartment:") -> Any:
    """3-way smoking preference input: yes, no, or flexible."""
    print(f"\n{Color.BOLD_BLUE}{prompt}{Color.RESET}")
    print(f"  {Color.CYAN}[1]{Color.RESET} yes       (Smoking allowed)")
    print(f"  {Color.CYAN}[2]{Color.RESET} no        (Strictly smoke-free)")
    print(f"  {Color.CYAN}[3]{Color.RESET} flexible  (Doesn't matter / tolerant)")
    mapping = {
        "1": True, "yes": True, "y": True,
        "2": False, "no": False, "n": False,
        "3": "flexible", "flexible": "flexible",
    }
    raw = input(f"Enter choice [1-3, default: {Color.CYAN}2 (no){Color.RESET}]: ").strip().lower()
    return mapping.get(raw, False)


def get_pets_preference(prompt: str = "Pet policy in the apartment:") -> Any:
    """3-way pets preference input: yes, no, or flexible."""
    print(f"\n{Color.BOLD_BLUE}{prompt}{Color.RESET}")
    print(f"  {Color.CYAN}[1]{Color.RESET} yes       (Pets allowed / welcome)")
    print(f"  {Color.CYAN}[2]{Color.RESET} no        (No pets)")
    print(f"  {Color.CYAN}[3]{Color.RESET} flexible  (Doesn't matter / tolerant)")
    mapping = {
        "1": True, "yes": True, "y": True,
        "2": False, "no": False, "n": False,
        "3": "flexible", "flexible": "flexible",
    }
    raw = input(f"Enter choice [1-3, default: {Color.CYAN}1 (yes){Color.RESET}]: ").strip().lower()
    return mapping.get(raw, True)


def calculate_match_score(
    commute_duration: float,
    max_commute: float,
    budget_headroom: float,
    max_budget: float,
    seeker_prefs: Preferences,
    host_prefs: Preferences,
) -> int:
    """
    Computes an aggregated composite compatibility score (0 - 100%):
    - Commute / Travel Time:  30%
    - Budget / Headroom:      25%
    - Cleanliness Alignment:  15%
    - Sleep Schedule Harmony: 15%
    - Kashrut & Shabbat:      15%
    """
    # 1. Commute Score (up to 30 pts)
    if max_commute > 0:
        ratio = min(1.0, max(0.0, commute_duration / max_commute))
        commute_score = round((1.0 - ratio) * 30)
    else:
        commute_score = 15

    # 2. Budget Score (up to 25 pts)
    if max_budget > 0:
        savings_ratio = max(0.0, budget_headroom / max_budget)
        budget_score = min(25, round(12 + savings_ratio * 30))
    else:
        budget_score = 15

    # 3. Cleanliness Alignment (up to 15 pts)
    diff = abs(seeker_prefs.cleanliness - host_prefs.cleanliness)
    clean_score = max(0, 15 - diff * 3)

    # 4. Sleep Schedule Harmony (up to 15 pts)
    if seeker_prefs.sleep_schedule == host_prefs.sleep_schedule:
        sleep_score = 15
    elif seeker_prefs.sleep_schedule == "flexible" or host_prefs.sleep_schedule == "flexible":
        sleep_score = 12
    else:
        sleep_score = 6

    # 5. Kashrut & Shabbat Harmony (up to 15 pts)
    shabbat_score = 5 if seeker_prefs.shabbat_observant == host_prefs.shabbat_observant else 2
    kashrut_weights = {
        ("secular", "secular"): 10,
        ("traditional", "traditional"): 10,
        ("religious", "religious"): 10,
        ("ultra_orthodox", "ultra_orthodox"): 10,
        ("secular", "traditional"): 8,
        ("traditional", "secular"): 8,
        ("traditional", "religious"): 8,
        ("religious", "traditional"): 8,
        ("religious", "ultra_orthodox"): 8,
        ("ultra_orthodox", "religious"): 8,
    }
    kashrut_pair = (seeker_prefs.kashrut_level, host_prefs.kashrut_level)
    spiritual_score = shabbat_score + kashrut_weights.get(kashrut_pair, 4)

    return min(100, max(1, commute_score + budget_score + clean_score + sleep_score + spiritual_score))


def format_score_badge(score: int) -> str:
    """Format compatibility score with aesthetic color and rating label."""
    if score >= 85:
        return f"{Color.BOLD_GREEN}{score}% [Top Match]{Color.RESET}"
    if score >= 70:
        return f"{Color.GREEN}{score}% [Good Match]{Color.RESET}"
    if score >= 55:
        return f"{Color.YELLOW}{score}% [Fair Match]{Color.RESET}"
    return f"{Color.RED}{score}% [Weak Match]{Color.RESET}"


def run_host_interactive_session():
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print(f"   {Color.BOLD_CYAN}FLATMATCH - APARTMENT OWNER / HOST ROOMMATE MATCHER (CLI){Color.RESET}")
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print("Welcome Host! Register your apartment and find ideal roommates from our")
    print("active candidate pool based on budget, lifestyle, and verified commute.")
    print(f"{Color.GRAY}{'-' * 80}{Color.RESET}")

    # --------------------------------------------------------------------------
    # Step 1: Host Personal Details
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[STEP 1: HOST PERSONAL DETAILS]{Color.RESET}")
    name = ""
    while not name:
        name = get_input("Enter your full name", default="Daniel Host")
        if not name:
            print(f"  {Color.RED}[!] Name cannot be blank.{Color.RESET}")

    age = get_int_input("Enter your age", default=28, min_val=18, max_val=120)
    phone = get_input("Enter your contact phone", default="052-8889900")

    # --------------------------------------------------------------------------
    # Step 2: Apartment Details & Location
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[STEP 2: APARTMENT DETAILS & ADDRESS]{Color.RESET}")

    # Validate city against supported Israeli cities/settlements
    city = ""
    while not city:
        candidate_city = get_input("Enter apartment city (e.g. Kiryat Ono, Tel Aviv, Ramat Gan)", default="Kiryat Ono")
        if Apartment.is_valid_city(candidate_city):
            city = candidate_city
        else:
            print(f"  {Color.YELLOW}[!] City '{candidate_city}' was not recognized. Please enter a valid Israeli city or settlement.{Color.RESET}")

    street_address = get_input("Enter specific street address", default=f"Levi Eshkol 14, {city}")
    rent = get_float_input("Enter total apartment monthly rent (NIS)", default=3400.0, min_val=1000.0)
    rooms = get_int_input("Enter total number of rooms in apartment", default=2, min_val=1, max_val=10)

    print(f"\n{Color.BOLD_BLUE}Select apartment amenities (press Enter for defaults):{Color.RESET}")
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
    print(f"\n{Color.BOLD_BLUE}[STEP 3: APARTMENT LIFESTYLE & ROOMMATE RULES]{Color.RESET}")
    is_smoker = get_smoking_preference("Smoking policy in the apartment:")
    allows_pets = get_pets_preference("Pet policy in the apartment:")
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

    print(f"\n{Color.BOLD_GREEN}{'=' * 80}{Color.RESET}")
    print(f"  {Color.BOLD_GREEN}HOST APARTMENT REGISTERED SUCCESSFULLY{Color.RESET}")
    print(f"  Host: {Color.BOLD}{host.name}{Color.RESET} (Phone: {Color.CYAN}{host.phone}{Color.RESET}) | Location: {Color.BOLD}{apartment.address}{Color.RESET}")
    print(f"  Rent: {Color.GREEN}{apartment.rent:,.0f} NIS total{Color.RESET} | {Color.BOLD_GREEN}{rent_per_room:,.0f} NIS per room{Color.RESET} ({apartment.rooms} rooms)")
    print(f"  Rules: Pets: {host_prefs.allows_pets} | Smoking: {host_prefs.is_smoker} | Kashrut: {host_prefs.kashrut_level}")
    print(f"  Perks: {Color.CYAN}{', '.join(sorted(apartment.amenities)) if apartment.amenities else 'Standard'}{Color.RESET}")
    print(f"{Color.BOLD_GREEN}{'=' * 80}{Color.RESET}")

    # --------------------------------------------------------------------------
    # Step 4: Search Active Seeker Pool & Verify Commute
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_BLUE}[MATCHING CANDIDATES FROM ACTIVE SEEKER POOL VIA OSRM API...]{Color.RESET}")

    use_mock = "--mock" in sys.argv
    geocoder = NominatimGeocodingClient(use_live_network=not use_mock)

    apt_normalized = AddressNormalizer.normalize(apartment.address)
    apt_coords = geocoder.geocode(apt_normalized)
    print(f"  {Color.CYAN}[1/3]{Color.RESET} Apartment coordinates resolved: {Color.YELLOW}lon={apt_coords[0]:.4f}, lat={apt_coords[1]:.4f}{Color.RESET}")

    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.jsonl")
    repo = FlatMatchRepository(data_path)
    registered_seekers: List[ApartmentSeeker] = repo.get_apartment_seekers()
    print(f"  {Color.CYAN}[2/3]{Color.RESET} Evaluating {Color.BOLD}{len(registered_seekers)}{Color.RESET} registered room seekers in database...")

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

        match_score = calculate_match_score(
            commute_duration=duration_min,
            max_commute=seeker.max_commute_minutes,
            budget_headroom=budget_surplus,
            max_budget=seeker.max_budget,
            seeker_prefs=seeker.preferences,
            host_prefs=host.preferences,
        )

        matching_candidates.append({
            "seeker": seeker,
            "duration_minutes": duration_min,
            "distance_km": distance_km,
            "budget_surplus": budget_surplus,
            "is_verified": commute.is_verified if commute else False,
            "match_score": match_score,
        })

    # Sort matching candidates: highest compatibility score first, then shortest commute
    matching_candidates.sort(key=lambda item: (-item["match_score"], item["duration_minutes"]))

    # --------------------------------------------------------------------------
    # Step 5: Results Display
    # --------------------------------------------------------------------------
    print(f"\n{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print(f"  {Color.BOLD_CYAN}ROOMMATE MATCH RESULTS FOR HOST {host.name.upper()} ({apartment.address}){Color.RESET}")
    print(f"  Room Rent: {Color.BOLD_GREEN}{rent_per_room:,.0f} NIS / month{Color.RESET} | Total Evaluated: {Color.BOLD}{len(registered_seekers)}{Color.RESET} Candidates")
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")

    if matching_candidates:
        print(f"\n{Color.BOLD_GREEN}SUCCESS:{Color.RESET} Found {Color.BOLD}{len(matching_candidates)}{Color.RESET} compatible roommate candidate(s) for your apartment:\n")
        for idx, match in enumerate(matching_candidates, start=1):
            seeker = match["seeker"]
            verified_tag = f"{Color.GREEN}[Verified: True]{Color.RESET}" if match["is_verified"] else f"{Color.GRAY}[Fallback]{Color.RESET}"
            surplus_tag = f"{Color.GREEN}+{match['budget_surplus']:,.0f} NIS{Color.RESET}" if match['budget_surplus'] >= 0 else f"{Color.RED}{match['budget_surplus']:,.0f} NIS{Color.RESET}"
            score_badge = format_score_badge(match["match_score"])

            print(f"{Color.BOLD_YELLOW}#{idx}{Color.RESET} [CANDIDATE: {Color.BOLD_CYAN}{seeker.name.upper()}{Color.RESET}] {score_badge} (Age: {seeker.age}, Phone: {Color.CYAN}{seeker.phone}{Color.RESET})")
            print(f"   Match Score:     {score_badge}")
            print(f"   Destination:     {seeker.destination_address}")
            print(f"   Commute Time:    {Color.BOLD_YELLOW}{match['duration_minutes']:.1f} min{Color.RESET} ({match['distance_km']:.1f} km drive) {verified_tag}")
            print(f"   Candidate Limit: Accepts up to {seeker.max_commute_minutes:.0f} min commute")
            print(f"   Budget Capacity: {seeker.max_budget:,.0f} NIS (Surplus: {surplus_tag} above room rent)")
            print(f"   Lifestyle:       Cleanliness {seeker.preferences.cleanliness}/5, Pets: {seeker.preferences.allows_pets}, Smoking: {seeker.preferences.is_smoker}, Kashrut: {seeker.preferences.kashrut_level}")
            print(f"   {Color.GRAY}{'-' * 74}{Color.RESET}")
    else:
        print(f"\n{Color.YELLOW}No registered seekers currently match your apartment's room rent, location, and lifestyle rules.{Color.RESET}")

    if rejected_candidates:
        print(f"\n{Color.GRAY}[FILTERED OUT CANDIDATES]{Color.RESET}")
        for rej in rejected_candidates:
            cand = rej["seeker"]
            print(f"  {Color.GRAY}* {cand.name} (Phone: {cand.phone}): Filtered out ->{Color.RESET} {Color.RED}{rej['reason']}{Color.RESET}")

    print(f"\n{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")
    print(f"  {Color.BOLD_CYAN}HOST MATCHING SESSION COMPLETED{Color.RESET}")
    print(f"{Color.BOLD_CYAN}{'=' * 80}{Color.RESET}")


if __name__ == "__main__":
    try:
        run_host_interactive_session()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Host matching session aborted by user. Goodbye!{Color.RESET}")
