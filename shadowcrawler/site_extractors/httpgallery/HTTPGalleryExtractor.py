# shadowcrawler/site_extractors/httpgallery/HTTPGalleryExtractor.py
# ShadowCrawler v4.1.3 — HTTP Gallery Extractor (PlaceKitten Demo)
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs HTTP-only media extraction without
# Playwright, HTML parsing, or browser context. The extractor treats the URL
# itself as an image source and generates additional demo URLs.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world extractors require robust, site-specific parsing logic.
#
# Demonstrates:
# - Pure HTTP media extraction
# - URL-as-image workflows
# - Minimalistic extractor structure
# - Clean separation between spider and extractor

from typing import Any, Dict, List, Optional

from urllib.parse import urlparse
from shadowcrawler.site_extractors.base import SiteExtractorBase


class HTTPGalleryExtractor(SiteExtractorBase):
    """
    HTTPGalleryExtractor — minimal HTTP-only extractor for image galleries.

    This extractor demonstrates how ShadowCrawler handles HTTP-only media
    extraction without HTML parsing or browser context. It treats the URL
    itself as an image source and generates additional demo image URLs.

    Responsibilities:
        - Treat the URL itself as an image.
        - Generate additional image URLs (demo sizes).
        - Return a normalized extraction dict.
        - Contain NO crawling logic.
        - Make NO decisions about what to follow.

    Notes:
        This extractor is intentionally simple to demonstrate that
        ShadowCrawler can extract media without HTML parsing or Playwright.
    """

    def __init__(self, handle: Optional[str] = None) -> None:
        super().__init__(handle)

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    def extract(
        self,
        response: Any,
        url: Optional[str] = None,
        scope: Optional[Any] = None,
    ) -> Dict[str, Any]:
        print("🐱 HTTPGalleryExtractor ejecutado en:", url)

        media: List[Dict[str, Any]] = []
        links: List[str] = []
        next_pages: List[str] = []

        # ------------------------------------------------------------
        # MEDIA ITEM (the URL itself IS the image)
        # ------------------------------------------------------------
        media.append({
            "url": url,
            "page": url,
            "type": "image",
            "meta": {
                "source": "placekitten",
            },
        })

        # ------------------------------------------------------------
        # GENERATE NEXT IMAGES (example sizes)
        # ------------------------------------------------------------
        sizes = [
            (200, 300),
            (300, 300),
            (400, 400),
            (500, 600),
            (800, 600),
        ]

        for w, h in sizes:
            next_pages.append(f"https://placekitten.com/{w}/{h}")

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        return {
            "data": {"media_count": len(media)},
            "media": media,
            "links": links,
            "next_pages": next_pages,
        }
