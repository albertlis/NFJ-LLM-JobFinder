"""Save collected links to JSON or CSV."""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def save_links(links: list[str], output_path: Path) -> None:
    """
    Save the list of links to a file.
    Format is detected by extension (.json or .csv).
    Parent directories are created automatically.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ext = output_path.suffix.lower()

    if ext == ".csv":
        _save_csv(links, output_path)
    else:
        _save_json(links, output_path)

    logger.info("Saved %d links → %s", len(links), output_path)


def _save_json(links: list[str], path: Path) -> None:
    payload = {
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
        "count": len(links),
        "links": links,
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def _save_csv(links: list[str], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["url"])
        for link in links:
            writer.writerow([link])
