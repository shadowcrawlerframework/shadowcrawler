# shadowcrawler/spiders/quotes/QuotesSpider.py
# ShadowCrawler v4.1.1 — Quotes to Scrape Spider
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example spider for Quotes to Scrape.

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.quotes.QuotesExtractor import QuotesExtractor


class QuotesSpider(SpiderBase):
    """Spider for Quotes to Scrape (HTTP-only).

    Responsibilities:
        - Always use HTTP mode.
        - Classify URLs into PAGE / TAG / GENERIC.
        - Delegate extraction to QuotesExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates how ShadowCrawler handles:
            - Static HTML pages
            - Pagination via “Next”
            - Tag-based navigation
    """

    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "Quotes"
    handle = "quotes"
    domain = "quotes.toscrape.com"
    fetch_mode = "http"
    workers = 2

    extractor_class = QuotesExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        if not url:
            return "NOFOLLOW"

        u = url.lower()

        if "/page/" in u:
            return "PAGE"

        if "/tag/" in u:
            return "TAG"

        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        return type_ != "NOFOLLOW"

    # ------------------------------------------------------------
    # ALWAYS HTTP
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        return False

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        return {"use_browser": False}

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
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
