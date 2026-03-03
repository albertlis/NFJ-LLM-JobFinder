"""Scraper configuration — reads variables from .env."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env from project root (2 levels above this file)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def _bool(val: str) -> bool:
    return val.strip().lower() in {"1", "true", "yes"}


# ---- URL ---------------------------------------------------------------
BASE_URL: str = os.getenv(
    "SCRAPER_BASE_URL",
    "https://nofluffjobs.com/pl/artificial-intelligence",
)
CRITERIA: str = os.getenv(
    "SCRAPER_CRITERIA",
    "requirement%3DPython%20salary%3Epln18000m",
)
UTM_PARAMS: str = os.getenv("SCRAPER_UTM_PARAMS", "")

# Build full URL
_query_parts = [f"criteria={CRITERIA}"]
if UTM_PARAMS:
    _query_parts.insert(0, UTM_PARAMS)
SCRAPER_URL: str = f"{BASE_URL}?{'&'.join(_query_parts)}"

# ---- Browser -----------------------------------------------------------
HEADLESS: bool = _bool(os.getenv("SCRAPER_HEADLESS", "true"))

# ---- Delays ------------------------------------------------------------
DELAY_MIN: float = float(os.getenv("SCRAPER_DELAY_MIN", "1.5"))
DELAY_MAX: float = float(os.getenv("SCRAPER_DELAY_MAX", "3.5"))

# ---- Output ------------------------------------------------------------
OUTPUT_PATH: Path = _PROJECT_ROOT / os.getenv(
    "SCRAPER_OUTPUT_PATH", "data/jobs_links.json"
)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
