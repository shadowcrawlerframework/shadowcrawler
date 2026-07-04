# shadowcrawler/spiders/gallery/GallerySpider.py
# ShadowCrawler v4.1.3 — Gallery Spider (Unsplash Example)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs browser-based extraction on
# image-heavy gallery sites such as Unsplash, using Playwright to
# render dynamic content, simulate infinite scroll, and discover
# category/photo pages.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world gallery spiders require robust, site-specific logic.
#
# Demonstrates:
# - Browser-based DOM extraction
# - Infinite-scroll simulation
# - Category and photo discovery
# - Clean separation between spider and extractor

from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.gallery.GalleryExtractor import GalleryExtractor


class GallerySpider(SpiderBase):
    """
    GallerySpider — browser-based demo for Unsplash-style image galleries.

    This spider demonstrates how ShadowCrawler handles image-heavy sites
    using Playwright. It classifies pages into PHOTO, CATEGORY, and GENERIC,
    delegates all extraction to GalleryExtractor, and avoids making crawling
    decisions beyond simple classification.

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
    # METADATA (contract-level signals)
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
        # REQUIRED for DOM extraction in 4.1.3
        return {
            "use_browser": True,
            "browser_mode": "html",
            "keep_page": True,
        }

    # ------------------------------------------------------------
    # PARSE (MODERN SIGNATURE)
    # ------------------------------------------------------------
    def parse(self, response: Any) -> Dict[str, Any]:
        # Modern Response object from PlaywrightFetcher
        if response is None or not getattr(response, "html", None):
            return {"links": [], "next_pages": [], "media": [], "data": {}}

        url = response.url
        browser_page = getattr(response, "browser_page", None)

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(
            response,
            url,
            scope=self.classify(url),
            browser_page=browser_page,
        )

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
