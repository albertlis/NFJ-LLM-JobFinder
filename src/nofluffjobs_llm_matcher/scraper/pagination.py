"""Pagination handler: click 'Load more offers' until all results are visible."""

import logging
import random
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from nofluffjobs_llm_matcher.config import DELAY_MAX, DELAY_MIN

logger = logging.getLogger(__name__)

_POSTINGS_SELECTOR = "nfj-postings-list"
_LOAD_MORE_SELECTOR = "button[nfjloadmore]"
_LOAD_MORE_TEXT = "Load more offers"
_LOAD_MORE_TEXT_PL = "Pokaż kolejne oferty"
_MAX_CLICKS = 200


def _random_delay() -> None:
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def _count_postings(page: Page) -> int:
    """Return the current number of loaded job cards."""
    return page.locator("nfj-postings-list a[href*='/job/']").count()


def _simulate_scroll(page: Page) -> None:
    """Scroll the page down in several steps to simulate human behaviour.

    Stops 9 viewport-heights before the bottom to avoid triggering
    scroll-based overlays or sticky banners near the page footer.
    """
    scroll_height: int = page.evaluate("() => document.body.scrollHeight")
    viewport_height: int = page.evaluate("() => window.innerHeight")
    # Stay at least 9 viewport heights away from the very bottom
    max_scroll = max(0, scroll_height - 9 * viewport_height)
    steps = random.randint(3, 6)
    for i in range(1, steps + 1):
        target = int(max_scroll * i / steps)
        page.evaluate(f"window.scrollTo({{top: {target}, behavior: 'smooth'}})")
        time.sleep(random.uniform(0.2, 0.6))


def _find_load_more_button(page: Page):
    """Return the first visible 'load more' button or None."""
    btn = page.locator(_LOAD_MORE_SELECTOR).first
    try:
        btn.wait_for(state="visible", timeout=2_000)
        return btn
    except PlaywrightTimeoutError:
        pass

    # Fallback: search by text (EN then PL)
    for text in (_LOAD_MORE_TEXT, _LOAD_MORE_TEXT_PL):
        btn_text = page.get_by_role("button", name=text).first
        try:
            btn_text.wait_for(state="visible", timeout=2_000)
            return btn_text
        except PlaywrightTimeoutError:
            continue

    return None


def _simulate_mouse_move_to(page: Page, x: float, y: float) -> None:
    """Move the mouse through several intermediate points (human simulation)."""
    current_x = random.randint(100, 800)
    current_y = random.randint(100, 400)
    steps = random.randint(4, 8)
    for i in range(1, steps + 1):
        ix = current_x + (x - current_x) * i / steps + random.uniform(-5, 5)
        iy = current_y + (y - current_y) * i / steps + random.uniform(-5, 5)
        page.mouse.move(ix, iy)
        time.sleep(random.uniform(0.02, 0.08))


def _dismiss_overlays(page: Page) -> None:
    """
    Hide Angular CDK overlay containers that may intercept pointer events.
    Tries keyboard Escape first (closes tooltips/dropdowns), then hides via JS.
    """
    try:
        page.keyboard.press("Escape")
        time.sleep(0.15)
    except Exception:
        pass

    # If the overlay is still present, hide it via JS so it no longer intercepts clicks.
    overlays_hidden: int = page.evaluate(
        """() => {
            const overlays = document.querySelectorAll(
                '.cdk-overlay-container, .cdk-overlay-backdrop, .cdk-overlay-pane'
            );
            let count = 0;
            overlays.forEach(el => {
                if (el.style.display !== 'none') {
                    el.style.display = 'none';
                    count++;
                }
            });
            return count;
        }"""
    )
    if overlays_hidden:
        logger.debug("Dismissed %d CDK overlay element(s).", overlays_hidden)
        time.sleep(0.1)


def load_all_offers(page: Page) -> None:
    """
    Main pagination loop.
    Clicks 'Load more offers' until the button disappears
    or the offer count stops growing.
    """
    page.wait_for_selector(_POSTINGS_SELECTOR, timeout=30_000)
    logger.info("Page loaded. Starting pagination...")

    clicks = 0
    stale_rounds = 0
    max_stale = 3

    while clicks < _MAX_CLICKS:
        count_before = _count_postings(page)

        _simulate_scroll(page)
        _random_delay()

        btn = _find_load_more_button(page)
        if btn is None:
            logger.info("No more offers to load.")
            break

        box = btn.bounding_box()
        if box:
            cx = box["x"] + box["width"] / 2 + random.uniform(-10, 10)
            cy = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
            _simulate_mouse_move_to(page, cx, cy)
            time.sleep(random.uniform(0.1, 0.3))

        # Dismiss any Angular CDK overlay that might intercept pointer events.
        _dismiss_overlays(page)

        # Prefer JS click — bypasses overlay interception; fall back to Playwright click.
        try:
            btn.evaluate("el => el.click()")
        except Exception:
            try:
                btn.click(timeout=15_000)
            except PlaywrightTimeoutError:
                logger.warning("Click timed out even after overlay dismissal — forcing JS click.")
                btn.evaluate("el => el.click()")

        clicks += 1
        logger.info("Click #%d — waiting for new offers...", clicks)

        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except PlaywrightTimeoutError:
            pass

        _random_delay()

        count_after = _count_postings(page)
        new_items = count_after - count_before
        logger.info("Offers after click: %d (+%d)", count_after, new_items)

        if new_items == 0:
            stale_rounds += 1
            if stale_rounds >= max_stale:
                logger.info(
                    "No new offers for %d rounds. Stopping pagination.", max_stale
                )
                break
        else:
            stale_rounds = 0

    if clicks >= _MAX_CLICKS:
        logger.warning("Reached click limit of %d.", _MAX_CLICKS)

    logger.info("Total offers loaded: %d", _count_postings(page))
