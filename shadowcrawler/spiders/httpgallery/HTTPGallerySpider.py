# shadowcrawler/spiders/httpgallery/HTTPGallerySpider.py
# ShadowCrawler v4.1.0 — HTTP Gallery Spider (PlaceKitten Demo)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example spider for HTTP-only media sources.

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.httpgallery.HTTPGalleryExtractor import (
    HTTPGalleryExtractor,
)


class HTTPGallerySpider(SpiderBase):
    """Spider for HTTP-only image galleries (PlaceKitten demo).

    Responsibilities:
        - Always use HTTP mode.
        - Classify URLs as KITTEN / GENERIC.
        - Delegate extraction to HTTPGalleryExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates how ShadowCrawler handles:
            - Media extraction without HTML parsing
            - HTTP-only workflows
            - Minimalistic demo spiders
    """

    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "HTTPGallery"
    handle = "httpgallery"
    domain = "placekitten.com"
    fetch_mode = "http"
    workers = 2

    extractor_class = HTTPGalleryExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        if "placekitten.com" in url:
            return "KITTEN"
        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        return type_ == "KITTEN"

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

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(response, url, scope=self.classify(url))

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
