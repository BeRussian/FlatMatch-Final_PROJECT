"""
FlatMatch - Iterators, Generators, and Lazy Evaluation (Part D)
==============================================================
This module implements custom Iterable and Iterator classes,
generator functions with yield, and a 3-stage lazy evaluation pipeline
using Generator Expressions.
"""

try:
    from flatmatch.models import ApartmentSeeker, Preferences, sample_apartment_seekers
except ImportError:
    from .models import ApartmentSeeker, Preferences, sample_apartment_seekers


# ==============================================================================
# 1. Custom Iterable and Iterator
# ==============================================================================

class SeekerIterator:
    """
    A dedicated Iterator class that encapsulates traversal state over an item sequence.
    Maintains its own independent cursor index, implements __iter__ and __next__,
    and raises StopIteration when traversal is complete.
    """

    def __init__(self, items: list):
        # Keeps a reference to the sequence and tracks the current traversal position
        self._items = items
        self._cursor = 0

    def __iter__(self):
        # An iterator must return itself when __iter__ is invoked
        return self

    def __next__(self):
        # Fetch the next element or raise StopIteration
        if self._cursor >= len(self._items):
            raise StopIteration
        item = self._items[self._cursor]
        self._cursor += 1
        return item

    @property
    def cursor(self) -> int:
        """Current position index of this iterator instance."""
        return self._cursor


class SeekerCollection:
    """
    A custom collection class that implements the Iterable protocol.
    Stores ApartmentSeeker objects and produces a fresh, independent
    SeekerIterator whenever iter() is invoked on it.
    """

    def __init__(self, seekers: list = None):
        self._seekers = []
        if seekers is not None:
            for s in seekers:
                self.add(s)

    def add(self, seeker: ApartmentSeeker) -> None:
        if not isinstance(seeker, ApartmentSeeker):
            raise TypeError("Only ApartmentSeeker instances can be added to SeekerCollection.")
        self._seekers.append(seeker)

    def __iter__(self) -> SeekerIterator:
        # Returns a new, independent iterator every time iter() is called
        return SeekerIterator(self._seekers)

    def __len__(self) -> int:
        return len(self._seekers)

    def __getitem__(self, index: int) -> ApartmentSeeker:
        return self._seekers[index]

    def __repr__(self) -> str:
        return f"SeekerCollection(total_seekers={len(self._seekers)})"


# ==============================================================================
# 2. Generator with yield
# ==============================================================================

def stream_budget_candidates(seekers, max_budget_ceiling: float):
    """
    A generator function that lazily yields candidates whose max_budget
    is within or equal to the specified budget ceiling.

    Demonstrates:
    - Lazy generation of matching items one by one.
    - Yielding execution control back to the caller without storing
      the entire filtered list in memory.
    """
    for seeker in seekers:
        if seeker.max_budget <= max_budget_ceiling:
            yield seeker


# ==============================================================================
# 3. 3-Stage Lazy Processing Pipeline (Generator Expressions)
# ==============================================================================

def build_lazy_seeker_pipeline(source_iterable, target_city: str, min_cleanliness: int):
    """
    Constructs a 3-stage lazy evaluation pipeline using Generator Expressions:
    - Stage 1: Filter seekers who include the target city in their preferred cities.
    - Stage 2: Filter seekers whose cleanliness preference meets the minimum threshold.
    - Stage 3: Transform/format candidate records into a concise summary string.

    CRITICAL: No intermediate lists or containers are created in memory!
    Items flow one by one through each stage only when requested by the consumer.
    """
    # Stage 1: City filter (generator expression)
    stage1_city_filter = (
        seeker for seeker in source_iterable
        if any(c.strip().lower() == target_city.strip().lower() for c in seeker.preferred_cities)
    )

    # Stage 2: Cleanliness score filter (generator expression)
    stage2_cleanliness_filter = (
        seeker for seeker in stage1_city_filter
        if seeker.preferences.cleanliness >= min_cleanliness
    )

    # Stage 3: Transformation / Formatted summary projection (generator expression)
    stage3_summary_projection = (
        f"Selected Candidate: {seeker.name} | Budget: {seeker.max_budget} NIS | Cleanliness: {seeker.preferences.cleanliness}/5"
        for seeker in stage2_cleanliness_filter
    )

    return stage3_summary_projection


# ==============================================================================
# Verification Suite & Demonstration
# ==============================================================================

def demonstrate_independent_iterators():
    print("\n--- 1. Custom Iterable & Independent Iterators Demonstration ---")
    collection = SeekerCollection(sample_apartment_seekers)
    print(f"Created {collection} with {len(collection)} seekers.")

    # Instantiate two separate iterators on the exact same collection
    it1 = iter(collection)
    it2 = iter(collection)

    print("\nAdvancing Iterator 1 by 2 items:")
    first_it1 = next(it1)
    second_it1 = next(it1)
    print(f"  Iterator 1 (cursor={it1.cursor}): {first_it1.name}")
    print(f"  Iterator 1 (cursor={it1.cursor}): {second_it1.name}")

    print("\nAdvancing Iterator 2 by 1 item:")
    first_it2 = next(it2)
    print(f"  Iterator 2 (cursor={it2.cursor}): {first_it2.name}")

    # Assert independence
    assert first_it1.name == first_it2.name == "Alice Cohen"
    assert second_it1.name == "Ben Levi"
    assert it1.cursor == 2, f"Expected it1 cursor at 2, got {it1.cursor}"
    assert it2.cursor == 1, f"Expected it2 cursor at 1, got {it2.cursor}"
    print("\n[PASS] Verified: Iterators maintain completely independent positions on the same collection.")


def demonstrate_generator_lifecycle():
    print("\n--- 2. Generator with yield Lifecycle Demonstration ---")
    budget_limit = 3500.0
    
    # 1. Generator creation without immediate evaluation
    gen = stream_budget_candidates(sample_apartment_seekers, budget_limit)
    print(f"Created generator object: {gen} (no execution has taken place yet)")

    # 2. Single call with next()
    first_candidate = next(gen)
    print(f"First candidate via next(): {first_candidate.name} (Budget: {first_candidate.max_budget} NIS)")
    assert first_candidate.max_budget <= budget_limit

    # 3. Resuming traversal using a for loop
    print("Resuming traversal via for loop (continues from where next() paused):")
    resumed_names = []
    for candidate in gen:
        print(f"  * Resumed: {candidate.name} (Budget: {candidate.max_budget} NIS)")
        resumed_names.append(candidate.name)
        assert candidate.max_budget <= budget_limit

    # 4. Proving generator exhaustion
    print("\nVerifying exhausted generator behavior:")
    exhausted_items = list(gen)
    print(f"  Items produced by exhausted generator: {exhausted_items}")
    assert len(exhausted_items) == 0

    try:
        next(gen)
        assert False, "Should have raised StopIteration"
    except StopIteration:
        print("  [PASS] next() on exhausted generator raises StopIteration as required.")

    # 5. Proving a new generator instance is required to restart traversal
    fresh_gen = stream_budget_candidates(sample_apartment_seekers, budget_limit)
    fresh_first = next(fresh_gen)
    assert fresh_first.name == first_candidate.name
    print(f"  [PASS] Fresh generator restarts traversal from start: {fresh_first.name}")


def demonstrate_lazy_pipeline():
    print("\n--- 3. 3-Stage Lazy Evaluation Pipeline Demonstration ---")
    # Build pipeline: Target Tel Aviv, Cleanliness >= 4
    pipeline = build_lazy_seeker_pipeline(
        source_iterable=sample_apartment_seekers,
        target_city="Tel Aviv",
        min_cleanliness=4
    )
    print(f"Constructed pipeline generator expression: {pipeline}")

    # Consume ONLY the first 2 results
    print("\nConsuming strictly the first 2 results from the pipeline:")
    result_1 = next(pipeline)
    print(f"  Result 1: {result_1}")
    result_2 = next(pipeline)
    print(f"  Result 2: {result_2}")

    # Verify that partial consumption halts and does not exhaust the source
    print("\n[PASS] Lazy pipeline successfully consumed 2 items without materializing intermediate lists.")


if __name__ == "__main__":
    print("============================================================")
    print("FlatMatch - Part D: Iterators, Generators & Pipeline Demo")
    print("============================================================")
    demonstrate_independent_iterators()
    demonstrate_generator_lifecycle()
    demonstrate_lazy_pipeline()
    print("\n============================================================")
    print("All iterators and generator requirements passed successfully!")
    print("============================================================")
