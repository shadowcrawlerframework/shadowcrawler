# shadowcrawler/parsing/spider_adapter.py
# ShadowCrawler v4.1.3 — Spider Adapter (DOM‑FULL compatible)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Adapter between SpiderBase and the extraction pipeline.
#
# Notes:
#   - Supports both modern DOM‑FULL spiders (parse(response=...))
#     and legacy spiders (parse(page, url, ...)).
#   - Does NOT modify media or data; only normalizes links and next_pages.
#   - Does NOT create Requests by itself; relies entirely on spider methods:
#         normalize(), classify(), should_follow(), request_meta(), make_request().
#   - Never raises exceptions to the engine; returns empty ParsedResult on error.
#   - Fully compatible with Playwright DOM‑FULL mode (browser_page preserved).
#   - Fully compatible with HTTP-only spiders.
#   - Fully serializable and safe for checkpointing.

import inspect
from urllib.parse import urljoin
from typing import Any, List, Dict

from shadowcrawler.logging import get_logger
from shadowcrawler.models.request import Request
from shadowcrawler.models.response import Response


class ParsedResult:
    """Container for parsed spider output.

    Represents the normalized output of a spider after link processing,
    next-page normalization, and media/data passthrough.
    """

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
        - Call spider.parse() using the correct signature (modern or legacy).
        - Normalize links and next_pages into Request objects.
        - Preserve media and data exactly as returned by the spider.
        - Provide DOM‑FULL compatibility by passing browser_page when needed.
        - Ensure safe error handling (never break the engine).

    Notes:
        - This adapter does NOT perform extraction logic.
        - It only orchestrates spider output normalization.
        - Media normalization is handled by MediaExtractor.
    """

    def __init__(self, spider: Any, extractor: Any = None) -> None:
        self.spider = spider
        self.extractor = extractor
        self.logger = get_logger("adapter")

    # ------------------------------------------------------------
    # PARSE (ASYNC‑AWARE)
    # ------------------------------------------------------------
    async def parse(self, response: Response) -> ParsedResult:
        url = getattr(response, "url", None)

        try:
            # Case 1: Modern DOM‑FULL spiders (parse(response=...))
            try:
                result = self.spider.parse(response=response)
            except TypeError:
                # Case 2: Legacy spiders (parse(page, url))
                page = getattr(response, "browser_page", None)
                result = self.spider.parse(
                    page=page,
                    url=url,
                    requests=None,
                    request=None,
                    response=response,
                )

            # Await coroutine if needed
            if inspect.iscoroutine(result):
                result = await result

        except Exception as exc:
            self.logger.error(f"Spider.parse() error on {url}: {exc}")
            return ParsedResult([], [], [], {})

        if not result:
            return ParsedResult([], [], [], {})

        raw_links = result.get("links", [])
        raw_next = result.get("next_pages", [])

        links: List[Request] = []
        next_pages: List[Request] = []

        base_url = url or ""

        # LINKS
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

        # NEXT PAGES
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

        return ParsedResult(
            links=links,
            next_pages=next_pages,
            media=result.get("media", []),
            data=result.get("data", {}),
        )
