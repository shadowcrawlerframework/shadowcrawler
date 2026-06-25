# shadowcrawler/fetcher/base.py
# ShadowCrawler v4.1.1 — Base Fetcher Interface
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Universal contract for all fetchers:
#   - RequestsFetcher (HTTP)
#   - PlaywrightFetcher (Browser)

from abc import ABC, abstractmethod
from typing import Any

from shadowcrawler.models.request import Request
from shadowcrawler.models.response import Response


class BaseFetcher(ABC):
    """Abstract base class for all ShadowCrawler fetchers.

    Responsibilities:
        - Define the universal async fetch() interface.
        - Ensure the CrawlerEngine can interact with any fetcher
          (HTTP or Browser) in a consistent way.

    Notes:
        - Fetchers must return a normalized Response object.
        - Fetchers must NOT raise exceptions for normal HTTP errors.
        - Fetchers must NOT modify the Request object.
    """

    @abstractmethod
    async def fetch(self, request: Request) -> Response:
        """Perform a request and return a normalized Response.

        Args:
            request: The Request object containing URL, headers, cookies, etc.

        Returns:
            A Response object with:
                - url
                - status
                - headers
                - text / content
                - meta
                - from_browser flag
        """
        ...
