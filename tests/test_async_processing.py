"""
Unit tests for Asynchronous Operations and Concurrency Rate Limiting
"""

import pytest
import asyncio
from flatmatch.async_processing import (
    fetch_apartment_verification_async,
    collect_verifications_sequential,
    collect_verifications_concurrent,
)


def test_fetch_apartment_verification_known_and_unknown():
    """Verifies async verification fetch against simulated registry."""
    sim_db = {
        "APT-01": {"is_verified": True, "details": "Legitimate unit"},
        "APT-02": {"is_verified": False, "details": "Code violation"},
    }

    async def _run():
        res1 = await fetch_apartment_verification_async("APT-01", simulated_db=sim_db, delay_seconds=0.0)
        assert res1["is_verified"] is True
        assert res1["apt_id"] == "APT-01"

        res2 = await fetch_apartment_verification_async("APT-02", simulated_db=sim_db, delay_seconds=0.0)
        assert res2["is_verified"] is False

        res_unknown = await fetch_apartment_verification_async("APT-NONE", simulated_db=sim_db, delay_seconds=0.0)
        assert res_unknown["is_verified"] is False
        assert "not found" in res_unknown["details"]

    asyncio.run(_run())


def test_sequential_vs_concurrent_result_equivalence():
    """Verifies that concurrent collection preserves exact input ordering and contents."""
    sim_db = {
        f"APT-{i}": {"is_verified": i % 2 == 0, "details": f"Unit {i}"}
        for i in range(1, 10)
    }
    apt_ids = [f"APT-{i}" for i in range(1, 10)]

    async def _run():
        seq_results = await collect_verifications_sequential(
            apt_ids, simulated_db=sim_db, delay_seconds=0.001
        )
        con_results = await collect_verifications_concurrent(
            apt_ids, simulated_db=sim_db, max_concurrency=3, delay_seconds=0.001
        )

        assert len(seq_results) == len(apt_ids)
        assert len(con_results) == len(apt_ids)
        assert seq_results == con_results

    asyncio.run(_run())


def test_concurrency_semaphore_limits_active_workers():
    """Verifies that asyncio.Semaphore limits the maximum concurrent active tasks."""
    active_workers = 0
    max_observed_active = 0
    lock = asyncio.Lock()

    async def tracking_fetch(apt_id: str):
        nonlocal active_workers, max_observed_active
        async with lock:
            active_workers += 1
            if active_workers > max_observed_active:
                max_observed_active = active_workers
        await asyncio.sleep(0.01)
        async with lock:
            active_workers -= 1
        return {"apt_id": apt_id, "is_verified": True}

    async def _run():
        sem = asyncio.Semaphore(2)

        async def bounded(apt_id):
            async with sem:
                return await tracking_fetch(apt_id)

        tasks = [bounded(f"APT-{i}") for i in range(6)]
        await asyncio.gather(*tasks)

    asyncio.run(_run())
    assert max_observed_active <= 2

