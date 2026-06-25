# shadowcrawler/parsing/spider_adapter.py
# ShadowCrawler v4.1.0 — Spider Adapter
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Role:
#   - Bridge between Spider and Extractor
#   - Does NOT make site decisions
#   - Calls spider.parse(...)
#   - Converts raw links into clean Request objects for the Engine

import inspect
from urllib.parse import urljoin
from typing import Any, List, Dict

from shadowcrawler.logging import get_logger
from shadowcrawler.models.request import Request


class ParsedResult:
    """Container for parsed spider output."""

    def __init__(
        self,
        links: List[Request],
        next_pages: List[Request],
        media: List[Any],
        data: Dict[str, Any],
    ) -> None:
        self.links = links
        self.next_pages = next_pages
        self.media = media
        self.data = data


class SpiderAdapter:
    """Adapter between SpiderBase and the extraction pipeline.

    Responsibilities:

    SPIDER:
        - Determines page types
        - Decides what to follow
        - Decides what to ignore
        - Performs normalization
        - Handles pagination
        - Determines valid media

    EXTRACTOR:
        - Extracts HTML → links / media / data

    ADAPTER:
        - Calls spider.parse(...)
        - Makes NO site decisions
        - Converts links → clean Request objects
    """

    def __init__(self, spider: Any, extractor: Any = None) -> None:
        # Extractor kept for CLI compatibility; site logic lives in the spider.
        self.spider = spider
        self.extractor = extractor
        self.logger = get_logger("adapter")

    # ------------------------------------------------------------
    # PARSE (ASYNC‑AWARE)
    # ------------------------------------------------------------
    async def parse(self, response: Any) -> ParsedResult:
        """Call spider.parse() and convert its output into structured objects.

        Args:
            response: Normalized Response object from a fetcher.

        Returns:
            ParsedResult with:
                - links: List[Request]
                - next_pages: List[Request]
                - media: List[Any]
                - data: Dict[str, Any]
        """
        url = getattr(response, "url", None)

        try:
            # Call spider.parse(...) — may be sync or async
            result = self.spider.parse(
                page=response,
                url=url,
                requests=None,
                request=None,
                response=response,
            )

            # If parse() returned a coroutine → await it
            if inspect.iscoroutine(result):
                result = await result

        except Exception as exc:
            self.logger.error(f"Spider.parse() error on {url}: {exc}")
            return ParsedResult([], [], [], {})

        # Safety: if spider returned None
        if not result:
            return ParsedResult([], [], [], {})

        raw_links = result.get("links", [])
        raw_next = result.get("next_pages", [])

        links: List[Request] = []
        next_pages: List[Request] = []

        base_url = url or ""

        # --------------------------------------------------------
        # LINKS
        # --------------------------------------------------------
        for href in raw_links:
            if not href:
                continue

            abs_url = urljoin(base_url, href)
            norm_url = self.spider.normalize(abs_url)

            type_ = self.spider.classify(norm_url)
            if not self.spider.should_follow(type_):
                continue

            meta = self.spider.request_meta(norm_url, type_)
            req = self.spider.make_request(norm_url, meta=meta)
            links.append(req)

        # --------------------------------------------------------
        # NEXT PAGES
        # --------------------------------------------------------
        for href in raw_next:
            if not href:
                continue

            abs_url = urljoin(base_url, href)
            norm_url = self.spider.normalize(abs_url)

            type_ = self.spider.classify(norm_url)
            if not self.spider.should_follow(type_):
                continue

            meta = self.spider.request_meta(norm_url, type_)
            req = self.spider.make_request(norm_url, meta=meta)
            next_pages.append(req)

        # --------------------------------------------------------
        # RETURN PARSED RESULT
        # --------------------------------------------------------
        return ParsedResult(
            links=links,
            next_pages=next_pages,
            media=result.get("media", []),
            data=result.get("data", {}),
        )
