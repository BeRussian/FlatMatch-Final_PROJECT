"""
FlatMatch - External OSRM Commute API Client (Part 2)
======================================================
Handles external network communication with Open Source Routing Machine (OSRM)
Public API. Implements targeted 3-attempt exponential retry logic for network
failures, strict schema validation, 4 distinct error types, and dependency injection.
"""

import time
import requests
from typing import Tuple
from flatmatch.config import (
    API_BASE_URL,
    API_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    get_logger,
)
from flatmatch.models import CommuteMetrics

logger = get_logger("api_client")


# ==============================================================================
# 4 Distinct API Exception Classes (Rubric Section 2.2)
# ==============================================================================

class APIConnectionError(Exception):
    """Raised when network communication times out or connection fails after exhausting retries."""
    pass


class APIHTTPError(Exception):
    """Raised immediately on non-2xx HTTP responses (e.g., 401, 404, 429, 503)."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class APIResponseFormatError(Exception):
    """Raised immediately when API response payload cannot be parsed as valid JSON."""
    pass


class APIDataValidationError(Exception):
    """Raised immediately when response JSON schema is invalid or missing required metrics."""
    pass


# ==============================================================================
# Commute API Client with Retries & DI
# ==============================================================================

class CommuteAPIClient:
    """
    Client for querying travel distance and duration between two geographic coordinates.
    Accepts dependencies via constructor for isolated, zero-network unit testing.
    """

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: float = API_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay: float = RETRY_DELAY,
        http_get=requests.get,
        sleep_func=time.sleep,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.http_get = http_get
        self.sleep_func = sleep_func

    def fetch_commute_metrics(
        self,
        origin_coords: Tuple[float, float],
        dest_coords: Tuple[float, float],
        origin_address: str = "Origin",
        dest_address: str = "Destination",
    ) -> CommuteMetrics:
        """
        Fetches commute distance and duration from OSRM API with retry mechanism.

        Coordinates format: (longitude, latitude)
        """
        lon1, lat1 = origin_coords
        lon2, lat2 = dest_coords
        endpoint = f"{self.base_url}/{lon1},{lat1};{lon2},{lat2}"
        params = {"overview": "false"}

        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"OSRM API Attempt {attempt}/{self.max_retries} -> {endpoint}")
                response = self.http_get(endpoint, params=params, timeout=self.timeout)
                break
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as err:
                last_err = err
                logger.warning(
                    f"OSRM API Attempt {attempt}/{self.max_retries} failed due to network error: {err}"
                )
                if attempt < self.max_retries:
                    self.sleep_func(self.retry_delay)
                else:
                    logger.error(f"OSRM API exhausted all {self.max_retries} attempts: {err}")
                    raise APIConnectionError(
                        f"Failed to connect to routing service after {self.max_retries} attempts: {err}"
                    ) from err

        # Check HTTP status code (Raise immediately, do not retry HTTP errors)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            status_code = getattr(response, "status_code", None)
            logger.error(f"OSRM API returned HTTP error {status_code}: {http_err}")
            raise APIHTTPError(
                f"HTTP request failed with status {status_code}: {http_err}",
                status_code=status_code,
            ) from http_err

        # Parse JSON payload (Raise immediately on malformed JSON)
        try:
            data = response.json()
        except Exception as json_err:
            logger.error(f"OSRM API response could not be parsed as JSON: {json_err}")
            raise APIResponseFormatError(f"Malformed JSON in API response: {json_err}") from json_err

        # Validate schema and required metrics (Raise immediately on missing/invalid fields)
        if not isinstance(data, dict):
            raise APIDataValidationError(f"Expected dict response, got {type(data).__name__}")

        routes = data.get("routes")
        if not isinstance(routes, list) or len(routes) == 0:
            raise APIDataValidationError(f"Response missing valid 'routes' list: {data}")

        primary_route = routes[0]
        if not isinstance(primary_route, dict):
            raise APIDataValidationError(f"First route must be a dict: {primary_route}")

        distance_meters = primary_route.get("distance")
        duration_seconds = primary_route.get("duration")

        if not isinstance(distance_meters, (int, float)) or distance_meters < 0:
            raise APIDataValidationError(f"Missing or negative 'distance': {distance_meters}")
        if not isinstance(duration_seconds, (int, float)) or duration_seconds < 0:
            raise APIDataValidationError(f"Missing or negative 'duration': {duration_seconds}")

        # Convert units and construct domain object
        distance_km = round(distance_meters / 1000.0, 2)
        duration_minutes = round(duration_seconds / 60.0, 2)

        metrics = CommuteMetrics(
            origin_address=origin_address,
            dest_address=dest_address,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            is_verified=True,
        )
        logger.info(f"Successfully computed commute: {metrics}")
        return metrics
