# shadowcrawler/spiders/wiki/WikiSpider.py
# ShadowCrawler v4.1.3 — Wikipedia Spider (Official Example)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs browser-based extraction on large,
# structured sites such as Wikipedia, using Playwright to render dynamic
# content and a classification model for ARTICLE / CATEGORY / FILE / GENERIC.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world Wikipedia spiders require robust, site-specific logic.
#
# Demonstrates:
# - Browser-based DOM extraction
# - Infobox parsing
# - Internal link discovery
# - Clean separation between spider and extractor

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.wiki.WikiExtractor import WikiExtractor


class WikiSpider(SpiderBase):
    """
    WikiSpider — browser-based demo for Wikipedia.

    This spider demonstrates how ShadowCrawler handles large structured sites
    using Playwright. It classifies URLs into ARTICLE, CATEGORY, FILE, and
    GENERIC, excludes Special: pages, and delegates extraction to WikiExtractor.

    Responsibilities:
        - Always use browser mode (Playwright).
        - Classify URLs into ARTICLE / CATEGORY / FILE / GENERIC.
        - Exclude Special: pages.
        - Delegate extraction to WikiExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates:
            - Large structured sites
            - Infobox extraction
            - Internal link discovery
    """

    # ------------------------------------------------------------
    # METADATA (contract-level signals)
    # ------------------------------------------------------------
    name = "Wiki"
    handle = "wiki"
    domain = "wikipedia.org"

    fetch_mode = "browser"   # Force Playwright mode
    workers = 2              # Multiple workers OK for browser mode

    extractor_class = WikiExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        """
        Classify URLs into logical scopes.

        /wiki/Special: → NOFOLLOW
        /wiki/Category: → CATEGORY
        /wiki/File:     → FILE
        /wiki/...       → ARTICLE
        otherwise        → GENERIC
        """
        if not url:
            return "NOFOLLOW"

        u = url.lower()

        if "/wiki/special:" in u:
            return "NOFOLLOW"

        if "/wiki/category:" in u:
            return "CATEGORY"

        if "/wiki/file:" in u:
            return "FILE"

        if "/wiki/" in u:
            return "ARTICLE"

        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        """Follow everything except NOFOLLOW."""
        return type_ != "NOFOLLOW"

    # ------------------------------------------------------------
    # ALWAYS USE BROWSER
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        """Force Playwright browser mode."""
        return True

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        """Browser metadata for PlaywrightFetcher."""
        return {"use_browser": True}

    # ------------------------------------------------------------
    # PARSE (browser-based)
    # ------------------------------------------------------------
    def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
        response = getattr(page, "response_obj", page)
    
        # Accept .html or .text (PlaywrightFetcher uses .html)
        html = getattr(response, "html", None) or getattr(response, "text", None)
        if response is None or not html:
            return {"links": [], "next_pages": [], "media": [], "data": {}}
    
        extractor = self.extractor_class(self.handle)
        result = extractor.extract(response, url, scope=self.classify(url))
    
        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
    