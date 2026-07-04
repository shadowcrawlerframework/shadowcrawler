# shadowcrawler/spiders/httpnews/HTTPNewsSpider.py
# ShadowCrawler v4.1.3 — HTTP News Spider (Hacker News Example)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs HTTP-only extraction on static HTML
# news sites such as Hacker News, using RequestsFetcher and a simple
# classification model for ARTICLE / CATEGORY / GENERIC pages.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world news spiders require robust, site-specific logic.
#
# Demonstrates:
# - Static HTML parsing
# - Pagination via “More”
# - HTTP-only workflows
# - Clean separation between spider and extractor

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.httpnews.HTTPNewsExtractor import (
    HTTPNewsExtractor,
)


class HTTPNewsSpider(SpiderBase):
    """
    HTTPNewsSpider — static HTML demo for Hacker News.

    This spider demonstrates how ShadowCrawler handles HTTP-only news sites
    without browser context. It classifies URLs into ARTICLE, CATEGORY, and
    GENERIC, delegates extraction to HTTPNewsExtractor, and avoids making
    crawling decisions beyond simple classification.

    Responsibilities:
        - Always use HTTP mode.
        - Classify URLs into ARTICLE / CATEGORY / GENERIC.
        - Delegate extraction to HTTPNewsExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates:
            - Static HTML pages
            - Pagination via “More”
            - HTTP-only workflows
    """

    # ------------------------------------------------------------
    # METADATA (contract-level signals)
    # ------------------------------------------------------------
    name = "HTTPNews"
    handle = "httpnews"
    domain = "news.ycombinator.com"

    fetch_mode = "http"      # Force HTTP-only mode
    workers = 2              # Multiple workers OK for HTTP

    extractor_class = HTTPNewsExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        """
        Classify URLs into logical scopes.

        /news/     → ARTICLE
        /category/ → CATEGORY
        otherwise  → GENERIC
        """
        if not url:
            return "NOFOLLOW"

        u = url.lower()

        if "/news/" in u:
            return "ARTICLE"

        if "/category/" in u:
            return "CATEGORY"

        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        """Follow everything except NOFOLLOW."""
        return type_ != "NOFOLLOW"

    # ------------------------------------------------------------
    # ALWAYS HTTP (no browser)
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        """Force HTTP-only mode."""
        return False

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        """Meta is minimal for HTTP spiders."""
        return {"use_browser": False}

    # ------------------------------------------------------------
    # PARSE (HTTP-only)
    # ------------------------------------------------------------
    def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
        """
        Parse HTTP responses.

        The extractor receives the raw HTTP response object and
        parses static HTML using BeautifulSoup.
        """
        response = page

        # If HTTP fetcher failed or returned no text
        if response is None or not getattr(response, "text", None):
            return {"links": [], "next_pages": [], "media": [], "data": {}}

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(response, url, scope=self.classify(url))

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
