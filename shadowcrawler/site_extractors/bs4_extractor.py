# shadowcrawler/site_extractors/bs4_extractor.py
# ShadowCrawler v4.1.3 — BS4 Extractor
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Generic BeautifulSoup-based extractor for ShadowCrawler.
#
# Notes:
#   - Converts HTML → BeautifulSoup using lxml.
#   - Calls a spider-defined handler(soup, response, scope).
#   - Does NOT include crawling logic — classification, priority,
#     browser usage, and follow rules belong to the spider.
#   - Does NOT create Request objects — SpiderAdapter handles that.
#   - Does NOT filter links or media — spiders decide what to follow.
#   - Fully compatible with DOM‑FULL spiders (response.browser_page available).
#   - Fully serializable and safe for checkpointing.

from typing import Any, Dict, Optional

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class BS4Extractor(SiteExtractorBase):
    """Generic BeautifulSoup-based extractor for ShadowCrawler v4.1.3.

    The spider provides a handler with the signature:

        handler(soup: BeautifulSoup, response, scope) -> dict

    The handler must return a standard extraction dict:
        {
            "data": {...} | None,
            "media": [...],
            "links": [...],
            "next_pages": [...]
        }

    Notes:
        - Converts HTML → BeautifulSoup.
        - Calls the spider-defined handler.
        - Does NOT include site logic.
        - Does NOT include crawling logic.
        - Does NOT create Requests.
        - Media normalization is handled later by MediaExtractor.
        - Link normalization and Request creation are handled by SpiderAdapter.
    """

    def __init__(self, handler: Any) -> None:
        super().__init__(handle="bs4")
        self.handler = handler

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    def extract(self, response: Any, scope: Optional[Any] = None) -> Dict[str, Any]:
        """Run the spider-defined handler on a BeautifulSoup instance.

        Args:
            response: Full Response object.
            scope: Optional spider-defined context.

        Returns:
            A normalized extraction dict.
        """
        html = response.html or response.text or ""
        soup = BeautifulSoup(html, "lxml")

        # Call the spider's handler
        out = self.handler(soup, response, scope)

        # Minimal validation
        if not isinstance(out, dict):
            self.logger.error(
                f"{self.__class__.__name__}.handler() must return a dict"
            )
            return self.empty()

        # Minimal normalization
        return {
            "data": out.get("data"),
            "media": out.get("media", []),
            "links": out.get("links", []),
            "next_pages": out.get("next_pages", []),
        }
