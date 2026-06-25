# shadowcrawler/spiders/gallery/GallerySpider.py
# ShadowCrawler v4.1.1 — Gallery Spider (Unsplash Example)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example spider for image galleries (Unsplash).

from typing import Any, Dict, List, Optional

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.gallery.GalleryExtractor import GalleryExtractor


class GallerySpider(SpiderBase):
    """Spider for Unsplash-style image galleries.

    Responsibilities:
        - Always use browser mode (Playwright).
        - Classify URLs into PHOTO / CATEGORY / GENERIC.
        - Delegate extraction to GalleryExtractor.
        - Make NO crawling decisions beyond classification.

    Notes:
        This spider demonstrates how ShadowCrawler handles:
            - Image-heavy sites
            - Infinite-scroll simulation
            - Category and photo discovery
    """

    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "Gallery"
    handle = "gallery"
    domain = "unsplash.com"
    fetch_mode = "browser"
    workers = 2

    extractor_class = GalleryExtractor
    auth_handler_class = None

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        if not url:
            return "NOFOLLOW"

        u = url.lower()

        if "/photos/" in u:
            return "PHOTO"

        if "/t/" in u:
            return "CATEGORY"

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
