# shadowcrawler/fetcher/requests_fetcher.py
# ShadowCrawler v4.1.3 — Requests Fetcher (HTTP)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Compatible with CrawlerEngine v4.x (url + meta signature).
# Provides a stable, lightweight HTTP GET fetcher using requests.

import requests
from typing import Any, Dict, Optional

from shadowcrawler.logging import get_logger


class RequestsFetcher:
    """Lightweight HTTP fetcher for ShadowCrawler v4.1.3.

    Responsibilities:
        - Perform basic HTTP GET requests.
        - Provide a stable fallback when browser fetch is not required.
        - Return raw `requests.Response` objects (Engine normalizes later).

    Notes:
        This fetcher is intentionally simple and synchronous. It is used
        when Playwright is unnecessary or disabled.
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: float = 20.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.logger = get_logger("downloader")

        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        # Default headers
        self.headers: Dict[str, str] = {
            "User-Agent": self.user_agent,
            "Accept":
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        if headers:
            self.headers.update(headers)

        self.timeout = timeout

    # ------------------------------------------------------------
    # FETCH (url + meta)
    # ------------------------------------------------------------
    def fetch(self, url: str, meta: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """Perform a GET request and return a raw `requests.Response`.

        Args:
            url: Target URL.
            meta: Optional metadata (ignored by this fetcher).

        Returns:
            A raw `requests.Response` object, or None on error.
        """
        meta = meta or {}
        try:
            self.logger.debug(f"RequestsFetcher GET: {url}")
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            return resp
        except Exception as exc:
            self.logger.error(f"RequestsFetcher error on {url}: {exc}")
            return None
