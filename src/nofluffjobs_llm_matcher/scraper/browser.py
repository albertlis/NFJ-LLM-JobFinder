"""Browser setup with anti-bot measures: stealth, random UA, fingerprints, headers."""

import logging
import random
from contextlib import contextmanager
from collections.abc import Generator

from fake_useragent import UserAgent
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

# Spójne nagłówki Sec-CH-UA dla najnowszego Chrome na Windows
_SEC_CH_UA = '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"'
_SEC_CH_UA_PLATFORM = '"Windows"'

# Realistic PC screen resolutions
_VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 2560, "height": 1440},
    {"width": 1600, "height": 900},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
]


def _get_chrome_ua() -> str:
    """Return a random Chrome/Windows User-Agent string."""
    ua = UserAgent(browsers=["chrome"], os=["windows"])
    return ua.random


@contextmanager
def create_browser(headless: bool = True) -> Generator[tuple[Browser, BrowserContext, Page], None, None]:
    """
    Context manager returning (browser, context, page) with anti-bot settings.
    Automatically closes all resources on exit.
    """
    with Stealth().use_sync(sync_playwright()) as pw:
        user_agent = _get_chrome_ua()
        viewport = random.choice(_VIEWPORTS)
        logger.debug("Using UA: %s  viewport: %s", user_agent, viewport)

        browser = _launch_browser(pw, headless=headless)
        context = _create_context(browser, user_agent, viewport)
        page = context.new_page()


        # Extra HTTP headers consistent with the chosen UA
        context.set_extra_http_headers(
            {
                "Accept-Language": "en-US,en;q=0.9,pl;q=0.8",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
                ),
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
                "Sec-CH-UA": _SEC_CH_UA,
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": _SEC_CH_UA_PLATFORM,
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
            }
        )

        try:
            yield browser, context, page
        finally:
            context.close()
            browser.close()


def _launch_browser(pw: Playwright, headless: bool) -> Browser:
    return pw.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--lang=en-US",
        ],
    )


def _create_context(
    browser: Browser,
    user_agent: str,
    viewport: dict[str, int],
) -> BrowserContext:
    return browser.new_context(
        user_agent=user_agent,
        viewport=viewport,  # type: ignore[arg-type]
        locale="en-US",
        timezone_id="Europe/Warsaw",
        java_script_enabled=True,
        bypass_csp=False,
        device_scale_factor=random.choice([1.0, 1.25, 1.5]),
        has_touch=False,
        color_scheme="light",
        permissions=[],
    )

