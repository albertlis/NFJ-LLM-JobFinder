"""Collect job listing href links from nfj-postings-list components."""

import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)

_NFJ_BASE = "https://nofluffjobs.com"

# Selector: links inside both nfj-postings-list components
_LINK_SELECTOR = "nfj-postings-list a[href*='/job/']"


def collect_job_links(page: Page) -> list[str]:
    """
    Collect and return a sorted, deduplicated list of absolute job offer URLs
    from the current page state.
    """
    elements = page.query_selector_all(_LINK_SELECTOR)

    hrefs: set[str] = set()
    for el in elements:
        href = el.get_attribute("href")
        if href:
            if href.startswith("/"):
                href = f"{_NFJ_BASE}{href}"
            hrefs.add(href)

    links = sorted(hrefs)
    logger.info("Collected %d unique job links.", len(links))
    return links
