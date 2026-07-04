# shadowcrawler/site_extractors/authdemo/AuthDemoExtractor.py
# ShadowCrawler v4.1.3 — HTTP-only extractor for AuthDemoSpider
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how to parse plain HTTP responses using RequestsFetcher, without Playwright.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world extractors require robust, site-specific parsing logic.
#
# Demonstrates:
# - Parsing plain HTTP responses
# - JSON fallback
# - Text fallback
# - No browser or JavaScript context

from typing import Any, Dict
from shadowcrawler.logging import get_logger


class AuthDemoExtractor:
    """
    HTTP-only extractor for AuthDemoSpider.

    This extractor receives a requests.Response object and
    extracts basic information such as status code, JSON data,
    and raw text. It demonstrates how extraction works without
    browser context.
    """

    def __init__(self, spider_handle: str) -> None:
        self.handle = spider_handle
        self.logger = get_logger("extractor")

    def extract(self, response: Any, url: str, scope: str) -> Dict[str, Any]:
        self.logger.info(f"Running AuthDemoExtractor on: {url}")

        # ------------------------------------------------------------
        # 1) Basic response info
        # ------------------------------------------------------------
        status = getattr(response, "status_code", None)
        text = getattr(response, "text", None)

        # ------------------------------------------------------------
        # 2) Try JSON if available
        # ------------------------------------------------------------
        json_data = None
        try:
            json_data = response.json()
        except Exception:
            pass

        # ------------------------------------------------------------
        # 3) Build result
        # ------------------------------------------------------------
        data = {
            "url": url,
            "status": status,
            "scope": scope,
            "json": json_data,
            "text": text if json_data is None else None,
        }

        return {
            "data": data,
            "links": [],
            "next_pages": [],
            "media": [],
        }
