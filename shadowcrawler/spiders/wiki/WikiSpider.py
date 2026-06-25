# shadowcrawler/spiders/wiki/WikiSpider.py
# ShadowCrawler v4.1.0 — Wikipedia Spider (Official Example)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example spider for Wikipedia.

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.wiki.WikiExtractor import WikiExtractor


class WikiSpider(SpiderBase):
    """Spider for Wikipedia pages.

    Responsibilities:
        - Always use browser mode (Playwright).
        - Classify URLs into ARTICLE / CATEGORY / FILE / GENERIC.
        - Exclude Special: pages.
        - Delegate extraction to WikiExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates how ShadowCrawler handles:
            - Large structured sites
            - Infobox extraction
            - Internal link discovery
    """

    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "Wiki"
    handle = "wiki"
    domain = "wikipedia.org"
    fetch_mode = "browser"
    workers = 2

    extractor_class = WikiExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
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
        return type_ != "NOFOLLOW"

    # ------------------------------------------------------------
    # ALWAYS USE BROWSER
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        return True

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        return {"use_browser": True}

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
        response = page

        # If Playwright failed or returned no HTML
        if response is None or not getattr(response, "html", None):
            return {"links": [], "next_pages": [], "media": [], "data": {}}

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(response, url, scope=self.classify(url))

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
