"""
FlatMatch - Geocoding Client
=============================
Translates address strings into (longitude, latitude) coordinates.
Supports:
1. Fast local pre-indexed coordinates (from flatmatch.config) for 100% offline tests.
2. Live public OpenStreetMap Nominatim API for real-time address search.
3. In-memory cache to prevent duplicate HTTP queries.
"""

from typing import Dict, Tuple, Optional
import requests
from flatmatch.config import CITY_COORDINATES, get_logger

logger = get_logger("geocoding")


class AddressNotFoundError(Exception):
    """Raised when an address string cannot be resolved to geographic coordinates."""
    pass


# Specific pre-indexed coordinates for key academic and urban landmarks (lon, lat)
LANDMARK_COORDINATES: Dict[str, Tuple[float, float]] = {
    "אוניברסיטת תל אביב": (34.8015, 32.1133),
    "הקריה האקדמית אונו, קרית אונו": (34.8624, 32.0617),
    "הטכניון, חיפה": (35.0228, 32.7770),
    "האוניברסיטה העברית, ירושלים": (35.1978, 31.7744),
    "אוניברסיטת בן-גוריון, באר שבע": (34.8009, 31.2622),
    "מרכז עזריאלי, תל אביב": (34.7919, 32.0747),
    "מתחם הבורסה, רמת גן": (34.8033, 32.0837),
    "חוף תל ברוך": (34.7865, 32.1285),
    "דיזנגוף סנטר, תל אביב": (34.7743, 32.0754),
}


class NominatimGeocodingClient:
    """
    Geocoding client translating textual addresses into (lon, lat) coordinates.
    """

    def __init__(self, use_live_network: bool = False, http_get=requests.get):
        self.use_live_network = use_live_network
        self.http_get = http_get
        self._cache: Dict[str, Tuple[float, float]] = {}

    def geocode(self, address: str) -> Tuple[float, float]:
        """
        Resolves an address string into (longitude, latitude).
        
        Checks in order:
        1. In-memory cache.
        2. Known landmark coordinates.
        3. Known city coordinates.
        4. Live Nominatim network API (if enabled).
        5. Default fallback to Tel Aviv center.
        """
        if not isinstance(address, str) or not address.strip():
            raise ValueError("address must be a non-empty string")

        clean_addr = address.strip()

        # 1. Check in-memory cache
        if clean_addr in self._cache:
            return self._cache[clean_addr]

        # 2. Check local landmark coordinates
        for landmark, coords in LANDMARK_COORDINATES.items():
            if landmark.lower() in clean_addr.lower() or clean_addr.lower() in landmark.lower():
                self._cache[clean_addr] = coords
                return coords

        # 3. Check local city coordinates
        for city, coords in CITY_COORDINATES.items():
            if city.lower() in clean_addr.lower():
                self._cache[clean_addr] = coords
                return coords

        # 4. Live network lookup if requested
        if self.use_live_network:
            try:
                url = "https://nominatim.openstreetmap.org/search"
                headers = {"User-Agent": "FlatMatch-Academic-Project/1.0"}
                params = {"q": clean_addr, "format": "json", "limit": 1}
                response = self.http_get(url, params=params, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                        coords = (round(lon, 4), round(lat, 4))
                        self._cache[clean_addr] = coords
                        logger.info(f"Resolved live coordinates for '{clean_addr}': {coords}")
                        return coords
            except Exception as err:
                logger.warning(f"Live geocoding failed for '{clean_addr}': {err}")

        # 5. Safe default fallback (Center Tel Aviv)
        default_coords = CITY_COORDINATES.get("Tel Aviv", (34.7818, 32.0853))
        self._cache[clean_addr] = default_coords
        return default_coords
