# shadowcrawler/spiders/authdemo/AuthDemoSpider.py
# ShadowCrawler v4.1.0 — Auth Demo Spider (HTTP Login)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Demonstration spider for HTTP-based login flows using requests.Session().

import requests
from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors.authdemo.AuthDemoExtractor import AuthDemoExtractor
from shadowcrawler.auth.authdemo.AuthDemoAuth import AuthDemoAuth


class AuthDemoSpider(SpiderBase):
    """Spider demonstrating HTTP login using requests.Session().

    Responsibilities:
        - Maintain a persistent HTTP session.
        - Classify pages into LOGIN / PROTECTED / GENERIC.
        - Trigger automatic login when entering LOGIN scope.
        - Delegate extraction to AuthDemoExtractor.
        - Delegate authentication to AuthDemoAuth.
    """

    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "AuthDemo"
    handle = "authdemo"
    domain = "httpbin.org"
    fetch_mode = "http"
    workers = 2

    extractor_class = AuthDemoExtractor
    auth_handler_class = AuthDemoAuth  # optional

    def __init__(self) -> None:
        super().__init__()

        # Persistent HTTP session
        self.session = requests.Session()

        # Auth handler instance
        self.auth = AuthDemoAuth(self.handle)

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        if "/post" in url:
            return "LOGIN"
        if "/anything" in url:
            return "PROTECTED"
        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        return type_ in ("LOGIN", "PROTECTED")

    # ------------------------------------------------------------
    # ALWAYS HTTP
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        return False

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        return {"use_browser": False}

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------
    def parse(self, page: Any, url: str, **kwargs) -> Dict[str, Any]:
        scope = self.classify(url)

        # Automatic HTTP login
        if scope == "LOGIN":
            print("🔐 Ejecutando login HTTP…")
            self.auth.login(self.session)

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(page, url, scope=scope)

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
