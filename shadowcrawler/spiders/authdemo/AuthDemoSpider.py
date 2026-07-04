# shadowcrawler/spiders/authdemo/AuthDemoSpider.py
# ShadowCrawler v4.1.3 — Auth Demo Spider (HTTP Login)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler handles authentication without Playwright,
# using pure HTTP requests and a persistent requests.Session.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world sites require robust, site-specific spiders and authentication logic.
#
# Demonstrates:
# - Pure HTTP requests
# - Persistent requests.Session
# - Automatic login flow
# - Cookie-based session persistence

import requests
from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.authdemo.AuthDemoExtractor import AuthDemoExtractor
from shadowcrawler.auth.authdemo.AuthDemoAuth import AuthDemoAuth


class AuthDemoSpider(SpiderBase):
    """
    AuthDemo — HTTP-only authentication demo.

    This spider shows how ShadowCrawler handles authentication
    without browser context. It uses requests.Session to maintain
    cookies and demonstrates a minimal login flow.
    """

    # ------------------------------------------------------------
    # SPIDER METADATA (contract-level signals)
    # ------------------------------------------------------------
    name = "AuthDemo"
    handle = "authdemo"
    domain = "httpbin.org"

    fetch_mode = "http"          # Force HTTP-only crawling
    workers = 1                  # Single worker for clarity

    extractor_class = AuthDemoExtractor
    auth_handler_class = AuthDemoAuth   # HTTP AuthHandler

    def __init__(self) -> None:
        super().__init__()

        # Persistent HTTP session (cookies, headers, tokens)
        self.session = requests.Session()

        # Auth handler instance (loads cookies from disk)
        self.auth = AuthDemoAuth(self.handle)

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        """
        Classify URLs into logical scopes.

        /post      → LOGIN
        /anything  → PROTECTED
        otherwise  → GENERIC
        """
        if "/post" in url:
            return "LOGIN"
        if "/anything" in url:
            return "PROTECTED"
        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        """Only follow LOGIN and PROTECTED pages."""
        return type_ in ("LOGIN", "PROTECTED")

    # ------------------------------------------------------------
    # ALWAYS HTTP (no browser)
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        """Force HTTP-only mode."""
        return False

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        """Meta is minimal for HTTP spiders."""
        return {"use_browser": False}

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
        """
        Parse HTTP responses.

        LOGIN:
            - Trigger HTTP login via AuthHandler.
        PROTECTED:
            - Session should already contain cookies/tokens.
        GENERIC:
            - No authentication required.
        """
        scope = self.classify(url)

        # Automatic HTTP login
        if scope == "LOGIN":
            print("🔐 Performing HTTP login…")
            self.auth.login(self.session)

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(page, url, scope=scope)

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
