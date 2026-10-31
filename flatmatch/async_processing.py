"""
FlatMatch - Asynchronous Operations & Rate Limiting (Part 4)
=============================================================
Demonstrates Python asyncio concurrency for non-blocking I/O operations
(such as querying municipal property registries or geocoding APIs) with
semaphore-controlled concurrency to prevent server flooding.
"""

import asyncio
from typing import List, Dict, Any, Optional
from flatmatch.config import get_logger

logger = get_logger("async")

# Default simulated registry data for offline tests and predictable execution
DEFAULT_REGISTRY_DB: Dict[str, Dict[str, Any]] = {
    "APT-TLV-01": {"is_verified": True, "details": "Municipality verified residential property"},
    "APT-TLV-02": {"is_verified": True, "details": "Approved rental unit with safety inspection"},
    "APT-TLV-03": {"is_verified": True, "details": "Registered standard apartment"},
    "APT-TLV-04": {"is_verified": False, "details": "Pending building permits inspection"},
    "APT-RG-01": {"is_verified": True, "details": "Ramat Gan municipality verified unit"},
    "APT-GIV-01": {"is_verified": True, "details": "Givatayim certified shared flat"},
    "APT-JER-01": {"is_verified": True, "details": "Jerusalem historical district registered"},
    "APT-HFA-01": {"is_verified": True, "details": "Haifa municipal registry verified"},
    "APT-BS-01": {"is_verified": True, "details": "Beer Sheva university area verified"},
}


async def fetch_apartment_verification_async(
    apt_id: str,
    simulated_db: Optional[Dict[str, Dict[str, Any]]] = None,
    delay_seconds: float = 0.05,
) -> Dict[str, Any]:
    """
    Simulates an asynchronous external API or database call to verify
    an apartment's municipal registration.
    """
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)

    db = simulated_db if simulated_db is not None else DEFAULT_REGISTRY_DB
    record = db.get(apt_id)

    if record:
        return {
            "apt_id": apt_id,
            "is_verified": record.get("is_verified", False),
            "details": record.get("details", ""),
        }
    else:
        return {
            "apt_id": apt_id,
            "is_verified": False,
            "details": "Apartment ID not found in municipal registry",
        }


async def collect_verifications_sequential(
    apt_ids: List[str],
    simulated_db: Optional[Dict[str, Dict[str, Any]]] = None,
    delay_seconds: float = 0.05,
) -> List[Dict[str, Any]]:
    """
    Collects verifications sequentially, awaiting each one before initiating the next.
    Used as a baseline for performance comparisons against concurrent execution.
    """
    results: List[Dict[str, Any]] = []
    for apt_id in apt_ids:
        res = await fetch_apartment_verification_async(
            apt_id, simulated_db=simulated_db, delay_seconds=delay_seconds
        )
        results.append(res)
    return results


async def collect_verifications_concurrent(
    apt_ids: List[str],
    simulated_db: Optional[Dict[str, Dict[str, Any]]] = None,
    max_concurrency: int = 4,
    delay_seconds: float = 0.05,
) -> List[Dict[str, Any]]:
    """
    Collects apartment verifications concurrently using asyncio.gather.
    Rate-limits parallel tasks with asyncio.Semaphore to prevent API throttling
    or server flooding.
    
    Preserves the exact original ordering corresponding to the input apt_ids list.
    """
    semaphore = asyncio.Semaphore(max(1, max_concurrency))

    async def _bounded_fetch(apt_id: str) -> Dict[str, Any]:
        async with semaphore:
            return await fetch_apartment_verification_async(
                apt_id, simulated_db=simulated_db, delay_seconds=delay_seconds
            )

    tasks = [_bounded_fetch(apt_id) for apt_id in apt_ids]
    results = await asyncio.gather(*tasks)
    return list(results)
