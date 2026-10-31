"""
FlatMatch Configuration & Logging Module
========================================
Encapsulates environment variables, OSRM API settings, coordinates,
and secure logging without exposing sensitive data or secrets.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Tuple


def _load_dotenv(dotenv_path: Path | None = None) -> None:
    """Safely load key-value pairs from .env file into os.environ if not already set."""
    if dotenv_path is None:
        dotenv_path = Path.cwd() / ".env"
    if not dotenv_path.is_file():
        return
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # Silently ignore parsing errors to prevent startup crash
        pass


_load_dotenv()

# API Configuration
API_BASE_URL: str = os.getenv(
    "FLATMATCH_API_BASE_URL",
    "https://router.project-osrm.org/route/v1/driving",
)
API_TIMEOUT: float = float(os.getenv("FLATMATCH_API_TIMEOUT", "5"))
MAX_RETRIES: int = int(os.getenv("FLATMATCH_API_MAX_RETRIES", "3"))
RETRY_DELAY: float = float(os.getenv("FLATMATCH_API_RETRY_DELAY", "0.5"))
API_KEY: str = os.getenv("FLATMATCH_API_KEY", "")

# City coordinates in (longitude, latitude) format for OSRM routing
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    "Tel Aviv": (34.7818, 32.0853),
    "Jerusalem": (35.2137, 31.7683),
    "Haifa": (34.9896, 32.7940),
    "Ramat Gan": (34.8242, 32.0823),
    "Beer Sheva": (34.7915, 31.2530),
    "Herzliya": (34.8436, 32.1663),
    # Additional supported cities for full compatibility
    "Givatayim": (34.8105, 32.0722),
    "Rishon LeZion": (34.8016, 31.9730),
    "Petah Tikva": (34.8878, 32.0840),
    "Holon": (34.7818, 32.0158),
    "Bat Yam": (34.7505, 32.0171),
    "Netanya": (34.8555, 32.3215),
    "Kfar Saba": (34.9076, 32.1750),
    "Ra'anana": (34.8732, 32.1848),
    "Ashdod": (34.6553, 31.8044),
    "Ashkelon": (34.5715, 31.6688),
    "Modi'in": (35.0089, 31.8903),
}


class SecretRedactingFormatter(logging.Formatter):
    """
    Formatter that ensures secrets (such as API_KEY) and sensitive credentials
    are never leaked into log outputs.
    """

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        current_api_key = os.getenv("FLATMATCH_API_KEY", API_KEY)
        if current_api_key and len(current_api_key) > 3 and current_api_key in formatted:
            formatted = formatted.replace(current_api_key, "***REDACTED***")
        return formatted


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured Logger instance with uniform formatting and secret redaction.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = SecretRedactingFormatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
