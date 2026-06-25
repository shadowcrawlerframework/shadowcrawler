# shadowcrawler/spiders/authbrowserdemo/AuthBrowserDemoSpider.py
# ShadowCrawler v4.1.0 — Auth Browser Demo Spider
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Demonstration spider for manual login flows using Playwright.

from typing import Any, Dict, List

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.authbrowserdemo.AuthBrowserDemoExtractor import (
    AuthBrowserDemoExtractor,
)
from shadowcrawler.auth.authbrowserdemo.AuthBrowserDemoAuth import (
    AuthBrowserDemoAuthHandler,
)


class AuthBrowserDemoSpider(SpiderBase):
    """Spider demonstrating manual login with Playwright.

    Responsibilities:
        - Always use browser mode.
        - Classify pages into LOGIN / PROFILE / GENERIC.
        - Delegate extraction to AuthBrowserDemoExtractor.
        - Delegate authentication to AuthBrowserDemoAuthHandler.
        - Make NO site decisions beyond classification.

    Notes:
        This spider is intentionally minimal. It exists to demonstrate
        how ShadowCrawler handles manual login flows with Playwright.
    """

    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "AuthBrowserDemo"
    handle = "authbrowserdemo"
    domain = "demoqa.com"
    fetch_mode = "browser"
    workers = 2

    extractor_class = AuthBrowserDemoExtractor
    auth_handler_class = AuthBrowserDemoAuthHandler

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        if "/login" in url:
            return "LOGIN"
        if "/profile" in url:
            return "PROFILE"
        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        return True

    # ------------------------------------------------------------
    # ALWAYS USE BROWSER
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        return True

    # ------------------------------------------------------------
    # META
    # ------------------------------------------------------------
    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        return {"use_browser": True}

    # ------------------------------------------------------------
    # PARSE (ASYNC)
    # ------------------------------------------------------------
    async def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
        extractor = self.extractor_class(self.handle)
        result = await extractor.extract(page, url)

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
