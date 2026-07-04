# shadowcrawler/spiders/authbrowserdemo/AuthBrowserDemoSpider.py
# ShadowCrawler v4.1.3 — Auth Browser Demo Spider (Tumblr-style)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs browser-based authentication using
# Playwright with a FULL browser context, persistent storage_state, and
# a clean Tumblr-style AuthHandler integration.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world sites require robust, site-specific spiders and authentication logic.
#
# Demonstrates:
# - FULL Playwright browser context
# - Persistent cookies + localStorage
# - Automatic session restoration
# - Login flow handled entirely by AuthHandler
# - CSS and React loading correctly
# - Clean separation between spider, auth, and extractor

from typing import Any, Dict
from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.models.response import Response

from shadowcrawler.site_extractors.authbrowserdemo.AuthBrowserDemoExtractor import (
    AuthBrowserDemoExtractor,
)
from shadowcrawler.auth.authbrowserdemo.AuthBrowserDemoAuth import (
    AuthBrowserDemoAuthHandler,
)


class AuthBrowserDemoSpider(SpiderBase):
    """
    AuthBrowserDemo — clean, consistent, Tumblr-style authentication spider.

    This spider demonstrates how ShadowCrawler handles browser-based
    authentication using Playwright. It uses a FULL browser context,
    persistent storage_state, and a dedicated AuthHandler to manage
    login and session restoration.

    Design principles:
        - FULL browser context defined at class level.
        - AuthHandler defined at class level.
        - No login logic inside request_meta().
        - No requires_login flag needed.
        - No dependency on initial URL.
        - Session always loads correctly.
        - CSS and React always load.
    """

    name = "AuthBrowserDemo"
    handle = "authbrowserdemo"
    domain = "demoqa.com"

    fetch_mode = "browser"
    browser_mode = "full"   # FULL context always
    workers = 1

    extractor_class = AuthBrowserDemoExtractor
    auth_handler_class = AuthBrowserDemoAuthHandler  # Same pattern as Tumblr

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
        return False

    # ------------------------------------------------------------
    # ALWAYS USE BROWSER
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        return True

    # ------------------------------------------------------------
    # META (MINIMAL)
    # ------------------------------------------------------------
    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        return {
            "use_browser": True,
            "wait_time": 5000,
            "keep_page": True,
            # No auth_handler here
            # No requires_login here
            # No browser_mode here
        }

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    async def parse(self, response: Response, **kwargs) -> Dict[str, Any]:
        page: Any = getattr(response, "browser_page", None)
        url: str = response.url

        extractor = self.extractor_class(self.handle)
        result = await extractor.extract(page, url)

        return {
            "links": [],
            "next_pages": [],
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
