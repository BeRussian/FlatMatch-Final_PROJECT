"""
Unit tests for CommuteAPIClient, 3x Retries, and 4 Exception Types
"""

import pytest
import requests
from unittest.mock import MagicMock
from flatmatch.api_client import (
    CommuteAPIClient,
    APIConnectionError,
    APIHTTPError,
    APIResponseFormatError,
    APIDataValidationError,
)


def test_api_client_successful_fetch(mock_api_client):
    """Verifies that a 200 OK response with valid JSON returns verified CommuteMetrics."""
    metrics = mock_api_client.fetch_commute_metrics(
        origin_coords=(34.7818, 32.0853),
        dest_coords=(34.8015, 32.1133),
        origin_address="Dizengoff",
        dest_address="TAU",
    )
    assert metrics.is_verified is True
    assert metrics.distance_km == 8.5
    assert metrics.duration_minutes == 18.0


def test_api_client_exhausts_retries_and_raises_connection_error():
    """Verifies that continuous network timeouts trigger 3 retries and raise APIConnectionError."""
    call_count = 0
    sleep_calls = []

    def failing_http_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.Timeout("Simulated socket timeout")

    def mock_sleep(seconds):
        sleep_calls.append(seconds)

    client = CommuteAPIClient(
        http_get=failing_http_get,
        sleep_func=mock_sleep,
        max_retries=3,
        retry_delay=0.1,
    )

    with pytest.raises(APIConnectionError, match="Failed to connect to routing service after 3 attempts"):
        client.fetch_commute_metrics(
            origin_coords=(34.78, 32.08),
            dest_coords=(34.80, 32.11),
        )

    assert call_count == 3
    assert len(sleep_calls) == 2  # Sleeps between attempt 1->2 and 2->3


def test_api_client_retry_success_after_transient_failure():
    """
    Verifies rubric requirement 2.2:
    Retry success after transient network timeout or connection failure:
    - Attempt 1: Raises transient Timeout.
    - Client sleeps for retry_delay.
    - Attempt 2: Succeeds, parses JSON payload, returns verified CommuteMetrics.
    """
    call_count = 0
    sleep_calls = []

    def mock_sleep(seconds):
        sleep_calls.append(seconds)

    def transient_http_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise requests.exceptions.Timeout("Transient socket timeout on attempt 1")

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "code": "Ok",
            "routes": [{"distance": 12500.0, "duration": 1320.0}],
        }
        return resp

    client = CommuteAPIClient(
        http_get=transient_http_get,
        sleep_func=mock_sleep,
        max_retries=3,
        retry_delay=0.1,
    )

    metrics = client.fetch_commute_metrics(
        origin_coords=(34.7818, 32.0853),
        dest_coords=(34.8015, 32.1133),
        origin_address="Tel Aviv",
        dest_address="Ramat Gan",
    )

    assert call_count == 2
    assert len(sleep_calls) == 1
    assert sleep_calls[0] == 0.1
    assert metrics.is_verified is True
    assert metrics.distance_km == 12.5
    assert metrics.duration_minutes == 22.0


@pytest.mark.parametrize("status_code", [400, 403, 404, 500, 503])
def test_api_client_http_error_immediate(status_code):
    """Verifies that non-2xx HTTP responses raise APIHTTPError immediately without retrying."""
    call_count = 0

    def bad_status_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        resp = MagicMock()
        resp.status_code = status_code
        resp.text = f"HTTP {status_code} Error"
        return resp

    client = CommuteAPIClient(http_get=bad_status_get, max_retries=3)

    with pytest.raises(APIHTTPError) as exc_info:
        client.fetch_commute_metrics((34.78, 32.08), (34.80, 32.11))

    assert exc_info.value.status_code == status_code
    assert call_count == 1  # No retries on HTTP client/server errors


def test_api_client_response_format_error():
    """Verifies that malformed JSON raises APIResponseFormatError."""
    def malformed_json_get(*args, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = ValueError("Invalid JSON string")
        resp.text = "<html>502 Bad Gateway</html>"
        return resp

    client = CommuteAPIClient(http_get=malformed_json_get)
    with pytest.raises(APIResponseFormatError, match="Malformed JSON in API response"):
        client.fetch_commute_metrics((34.78, 32.08), (34.80, 32.11))


def test_api_client_data_validation_error():
    """Verifies that JSON missing routes or with non-Ok code raises APIDataValidationError."""
    def missing_routes_get(*args, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"code": "NoRoute", "routes": []}
        return resp

    client = CommuteAPIClient(http_get=missing_routes_get)
    with pytest.raises(APIDataValidationError, match="Response missing valid 'routes' list"):
        client.fetch_commute_metrics((34.78, 32.08), (34.80, 32.11))
