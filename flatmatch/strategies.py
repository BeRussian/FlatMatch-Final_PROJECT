"""
FlatMatch - Matching Strategies (Strategy Pattern - Part 3)
============================================================
Defines the Strategy pattern for computing candidate match scores
polymorphically with interchangeable algorithms.
"""

from abc import ABC, abstractmethod
from typing import Optional
from flatmatch.models import ApartmentSeeker, RoommateSeeker, CommuteMetrics


class MatchingStrategy(ABC):
    """
    Abstract Strategy defining the algorithm interface for match scoring.
    """

    @abstractmethod
    def calculate_score(
        self,
        seeker: ApartmentSeeker,
        owner: RoommateSeeker,
        commute: Optional[CommuteMetrics] = None,
    ) -> float:
        """
        Calculates and returns a normalized compatibility score between 0.0 and 100.0.
        """
        pass


class BudgetFocusedStrategy(MatchingStrategy):
    """
    Strategy 1: Emphasizes financial savings and cleanliness compatibility,
    with lower sensitivity to commute times.
    """

    def calculate_score(
        self,
        seeker: ApartmentSeeker,
        owner: RoommateSeeker,
        commute: Optional[CommuteMetrics] = None,
    ) -> float:
        # Base score
        score = 50.0

        # Budget savings: reward when rent is below seeker's ceiling
        rent_to_pay = owner.apartment.rent_per_room
        savings = seeker.max_budget - rent_to_pay
        if savings > 0:
            score += min(30.0, (savings / 50.0) * 1.5)
        else:
            score -= abs(savings) * 0.05

        # Cleanliness compatibility (difference of 0 to 4 points)
        cleanliness_diff = abs(seeker.preferences.cleanliness - owner.preferences.cleanliness)
        score -= cleanliness_diff * 6.0

        # Minor commute penalty
        if commute and commute.is_verified:
            score -= min(15.0, commute.duration_minutes * 0.3)
        else:
            score -= 5.0

        return round(max(0.0, min(100.0, score)), 2)


class CommuteAndLifestyleStrategy(MatchingStrategy):
    """
    Strategy 2: Prioritizes verified short commute duration and apartment amenities
    over pure budget margins.
    """

    def calculate_score(
        self,
        seeker: ApartmentSeeker,
        owner: RoommateSeeker,
        commute: Optional[CommuteMetrics] = None,
    ) -> float:
        score = 60.0

        # Commute duration bonus/penalty
        if commute and commute.is_verified:
            if commute.duration_minutes <= 20.0:
                # Strong bonus for short commutes
                score += (20.0 - commute.duration_minutes) * 1.5
            else:
                # Gradual penalty for longer commutes
                score -= (commute.duration_minutes - 20.0) * 1.2
        else:
            score -= 10.0  # Unverified commute penalty

        # Amenities overlap: reward apartment perks (balcony, elevator, AC, etc.)
        amenities_count = len(owner.apartment.amenities)
        score += min(20.0, amenities_count * 4.0)

        # Lifestyle & Sleep compatibility
        if seeker.preferences.sleep_schedule == owner.preferences.sleep_schedule:
            score += 5.0

        cleanliness_diff = abs(seeker.preferences.cleanliness - owner.preferences.cleanliness)
        score -= cleanliness_diff * 4.0

        return round(max(0.0, min(100.0, score)), 2)
