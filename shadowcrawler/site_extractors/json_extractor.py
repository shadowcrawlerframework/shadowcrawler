# shadowcrawler/site_extractors/json_extractor.py
# ShadowCrawler v4.1.1 — JSON Extractor
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Generic JSON response extractor for ShadowCrawler.

import json
from typing import Any, Dict, Optional

from shadowcrawler.site_extractors.base import SiteExtractorBase


class JSONExtractor(SiteExtractorBase):
    """Generic JSON extractor for ShadowCrawler v4.1.1.

    The spider provides a handler with the signature:

        handler(data: dict | list, response, scope) -> dict

    The handler must return a standard extraction dict:
        {
            "data": {...} | None,
            "media": [...],
            "links": [...],
            "next_pages": [...]
        }

    Notes:
        - Converts response.text → JSON.
        - Calls the spider-defined handler.
        - Does NOT include site logic.
        - Does NOT include crawling logic.
        - Does NOT create Requests.
    """

    def __init__(self, handler: Any) -> None:
        super().__init__(handle="json")
        self.handler = handler

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    def extract(self, response: Any, scope: Optional[Any] = None) -> Dict[str, Any]:
        """Parse JSON from the response and run the spider-defined handler.

        Args:
            response: Full Response object.
            scope: Optional spider-defined context.

        Returns:
            A normalized extraction dict.
        """
        raw = response.text or response.html or ""

        try:
            data = json.loads(raw)
        except Exception as exc:
            self.logger.error(f"JSON parse error: {exc}")
            return self.empty()

        out = self.handler(data, response, scope)

        if not isinstance(out, dict):
            self.logger.error(
                f"{self.__class__.__name__}.handler() must return a dict"
            )
            return self.empty()

        return {
            "data": out.get("data"),
            "media": out.get("media", []),
            "links": out.get("links", []),
            "next_pages": out.get("next_pages", []),
        }
