"""Scraper package — collect job links from NoFluffJobs."""

from nofluffjobs_llm_matcher.scraper.browser import create_browser
from nofluffjobs_llm_matcher.scraper.links import collect_job_links
from nofluffjobs_llm_matcher.scraper.pagination import load_all_offers

__all__ = ["create_browser", "collect_job_links", "load_all_offers"]
