# shadowcrawler/spiders/httpgallery/HTTPGallerySpider.py
# ShadowCrawler v4.1.3 — HTTP Gallery Spider (PlaceKitten Demo)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs HTTP-only media extraction without
# Playwright, HTML parsing, or browser context. The extractor treats the URL
# itself as an image source and demonstrates minimalistic HTTP workflows.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world spiders require robust, site-specific logic.
#
# Demonstrates:
# - Pure HTTP fetching (RequestsFetcher)
# - Media extraction without HTML parsing
# - Minimalistic demo spider structure
# - Clean separation between spider and extractor

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.httpgallery.HTTPGalleryExtractor import (
    HTTPGalleryExtractor,
)


class HTTPGallerySpider(SpiderBase):
    """
    HTTPGallerySpider — minimal HTTP-only demo for image extraction.

    This spider demonstrates how ShadowCrawler handles HTTP-only workflows
    without browser context. It classifies URLs into KITTEN / GENERIC and
    delegates all extraction to HTTPGalleryExtractor, which treats the URL
    itself as an image source.

    Responsibilities:
        - Always use HTTP mode (no Playwright).
        - Classify URLs as KITTEN / GENERIC.
        - Delegate extraction to HTTPGalleryExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates:
            - Media extraction without HTML parsing
            - HTTP-only workflows
            - Minimalistic demo spiders
    """

    # ------------------------------------------------------------
    # METADATA (contract-level signals)
    # ------------------------------------------------------------
    name = "HTTPGallery"
    handle = "httpgallery"
    domain = "placekitten.com"

    fetch_mode = "http"      # Force HTTP-only mode
    workers = 2              # Multiple workers OK for HTTP

    extractor_class = HTTPGalleryExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        """
        Classify URLs into logical scopes.

        placekitten.com → KITTEN
        otherwise       → GENERIC
        """
        if "placekitten.com" in url:
            return "KITTEN"
        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        """Only follow KITTEN URLs."""
        return type_ == "KITTEN"

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
        treats the URL itself as an image source.
        """
        response = page

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(response, url, scope=self.classify(url))

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
