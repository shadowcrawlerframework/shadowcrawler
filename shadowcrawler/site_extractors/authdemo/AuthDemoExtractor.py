# shadowcrawler/site_extractors/authdemo/AuthDemoExtractor.py
# ShadowCrawler v4.1.0 — Auth Demo Extractor
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Minimal JSON-based extractor for the AuthDemoSpider example.

import json
from typing import Any, Dict, Optional

from shadowcrawler.site_extractors.base import SiteExtractorBase


class AuthDemoExtractor(SiteExtractorBase):
    """Extractor for the AuthDemoSpider (manual login demo).

    Responsibilities:
        - Parse JSON or fallback to raw text.
        - Respect spider-defined scope ("LOGIN", "PROTECTED").
        - Never enqueue navigation automatically.
        - Never make site decisions.
        - Return a normalized extraction dict.

    Notes:
        This extractor is intentionally minimal. It demonstrates how
        authentication flows can be modeled without forcing navigation.
    """

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    def extract(
        self,
        response: Any,
        url: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> Dict[str, Any]:
        print("📄 AuthDemoExtractor ejecutado en:", url)

        # Try to parse JSON
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        links: list = []
        next_pages: list = []
        media: list = []

        # LOGIN → next step is protected page
        if scope == "LOGIN":
            next_pages.append("https://httpbin.org/anything/protected")

        # PROTECTED → mark as authenticated content
        if scope == "PROTECTED":
            data["protected"] = True

        return {
            "data": data,
            "links": links,
            "next_pages": next_pages,
            "media": media,
        }
