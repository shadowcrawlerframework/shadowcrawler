# shadowcrawler/site_extractors/base.py
# ShadowCrawler v4.1.3 — Site Extractor Base Class
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Universal extractor contract for ShadowCrawler spiders.
#
# Notes:
#   - Extractors operate ONLY on Response objects; they do NOT fetch pages.
#   - Extractors contain NO crawling logic — classification, priority,
#     browser usage, and follow rules belong to the spider.
#   - Extractors MUST return a dict with keys: data, media, links, next_pages.
#   - Extractors MUST NOT create Request objects — SpiderAdapter handles that.
#   - Extractors MUST NOT filter links or media — spiders decide what to follow.
#   - Fully compatible with DOM‑FULL spiders (response.browser_page available).
#   - Fully serializable and safe for checkpointing.

from urllib.parse import urljoin
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup
from shadowcrawler.logging import get_logger


class SiteExtractorBase:
    """Base class for all ShadowCrawler site extractors (v4.1.3).

    Responsibilities:
        - Receive a full Response object.
        - Provide helpers for HTML parsing, JSON extraction, media creation,
          and URL normalization.
        - Return a standard extraction dict:

            {
                "data": {...} | None,
                "media": [...],
                "links": [...],
                "next_pages": [...]
            }

    Notes:
        - Concrete extractors MUST implement extract().
        - Extractors contain NO crawling logic — that belongs to the spider.
        - Media normalization is handled later by MediaExtractor.
        - Link normalization and Request creation are handled by SpiderAdapter.
    """

    def __init__(self, handle: Optional[str] = None) -> None:
        self.handle = handle
        self.logger = get_logger(f"extractor:{handle}")

    # ------------------------------------------------------------
    # EXTRACT (ABSTRACT)
    # ------------------------------------------------------------
    def extract(
        self,
        response: Any,
        url: Optional[str] = None,
        scope: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Extract links, media, and data from a Response.

        Args:
            response: Full Response object.
            url: Current URL (optional override).
            scope: Optional spider-defined context.

        Returns:
            A dict with keys:
                - data
                - media
                - links
                - next_pages
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.extract() must be implemented"
        )

    # ------------------------------------------------------------
    # HTML HELPER
    # ------------------------------------------------------------
    def soup(self, html: str) -> BeautifulSoup:
        """Return a BeautifulSoup object using the lxml parser."""
        return BeautifulSoup(html or "", "lxml")

    # ------------------------------------------------------------
    # NORMALIZE
    # ------------------------------------------------------------
    def normalize(self, url: Optional[str], base_url: str) -> Optional[str]:
        """Normalize relative URLs using urljoin."""
        if not url:
            return None

        url = url.strip()
        if not url:
            return None

        normalized = urljoin(base_url, url)
        self.logger.debug(f"Normalized URL: {url} → {normalized}")
        return normalized

    # ------------------------------------------------------------
    # MEDIA HELPER
    # ------------------------------------------------------------
    def media(
        self,
        url: str,
        page: Optional[str] = None,
        media_type: str = "unknown",
        **kwargs
    ) -> Dict[str, Any]:
        """Helper to create media dictionaries."""
        return {
            "url": url,
            "page": page,
            "type": media_type,
            **kwargs,
        }

    # ------------------------------------------------------------
    # RESULT TEMPLATE
    # ------------------------------------------------------------
    def empty(self) -> Dict[str, Any]:
        """Return a standard empty extraction dict."""
        return {
            "data": None,
            "media": [],
            "links": [],
            "next_pages": [],
        }
