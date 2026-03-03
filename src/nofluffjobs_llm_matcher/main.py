"""CLI entry point: nfj-matcher scrape"""

import argparse
import logging
import sys
from pathlib import Path

from nofluffjobs_llm_matcher.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def _run_scrape(output: Path, headless: bool) -> None:
    from nofluffjobs_llm_matcher import config
    from nofluffjobs_llm_matcher.scraper import (
        collect_job_links,
        create_browser,
        load_all_offers,
    )
    from nofluffjobs_llm_matcher.storage import save_links

    url = config.SCRAPER_URL
    logger.info("Scraping: %s", url)
    logger.info("Headless: %s", headless)

    with create_browser(headless=headless) as (_, __, page):
        logger.info("Navigating to URL...")
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)

        # Accept cookie banner if present (NFJ / OneTrust)
        for label in ("Accept all", "Akceptuję wszystkie"):
            try:
                btn = page.get_by_role("button", name=label).first
                btn.wait_for(state="visible", timeout=4_000)
                btn.click()
                logger.debug("Cookie banner accepted (%s).", label)
                break
            except Exception:
                pass

        load_all_offers(page)
        links = collect_job_links(page)
        logger.info("Collected %d unique links.", len(links))

    save_links(links, output)


def cli_entry() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="nfj-matcher",
        description="NoFluffJobs scraper — collects job offer links.",
    )
    subparsers = parser.add_subparsers(dest="command")

    scrape_parser = subparsers.add_parser("scrape", help="Scrape job offers.")
    scrape_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output file path (.json or .csv). Defaults to SCRAPER_OUTPUT_PATH from .env.",
    )
    scrape_parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Run browser in headless mode (default: from .env).",
    )
    scrape_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO).",
    )

    args = parser.parse_args()

    if args.command != "scrape":
        parser.print_help()
        sys.exit(0)

    setup_logging(args.log_level)

    from nofluffjobs_llm_matcher import config

    output = args.output or config.OUTPUT_PATH
    headless = args.headless if args.headless is not None else config.HEADLESS

    _run_scrape(output=output, headless=headless)


if __name__ == "__main__":
    cli_entry()
