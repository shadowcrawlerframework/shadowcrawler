# shadowcrawler/core/spider_base.py
# ShadowCrawler v4.1.0 — Base Spider Class
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Defines SpiderBase, the foundational class for all spiders in the
# ShadowCrawler framework. Provides:
#   - Automatic registration via SpiderMeta
#   - Standard page-type constants
#   - Default crawling rules
#   - Request creation helpers
#   - A consistent parse() interface for the adapter and engine

from typing import Any, Dict, Optional

from shadowcrawler.logging import get_logger
from shadowcrawler.core.spider_registry import SpiderRegistry
from shadowcrawler.models.request import Request


# ------------------------------------------------------------
# Spider MetaClass (Auto-Registration)
# ------------------------------------------------------------
class SpiderMeta(type):
    """Metaclass that automatically registers subclasses of SpiderBase.

    Notes:
        - The base class itself is NOT registered.
        - Registration is silent and safe for optional contexts.
    """

    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)

        # Late import to avoid circular dependency
        try:
            from shadowcrawler.core.spider_base import SpiderBase

            if cls is not SpiderBase and issubclass(cls, SpiderBase):
                SpiderRegistry.register(cls)

        except Exception:
            # Fail silently — registration is optional
            pass

        return cls


# ------------------------------------------------------------
# Spider Base Class
# ------------------------------------------------------------
class SpiderBase(metaclass=SpiderMeta):
    """Universal contract for all spiders in ShadowCrawler v4.1.0.

    Spiders define:
        - classify(url): determine page type
        - should_follow(type): decide if a page should be crawled
        - use_browser(url, type): browser vs HTTP fetch mode
        - request_meta(url, type): metadata for the request
        - parse(page, url, **kwargs): extract links, media, and data

    Subclasses may override any method to implement site‑specific logic.
    """

    # ------------------------------------------------------------
    # Standard Page Types
    # ------------------------------------------------------------
    PAGE = "PAGE"
    MEDIA = "MEDIA"
    GALLERY = "GALLERY"
    POST = "POST"
    SEARCH = "SEARCH"
    PROFILE = "PROFILE"
    TAG = "TAG"
    CATEGORY = "CATEGORY"
    NOFOLLOW = "NOFOLLOW"

    def __init__(self) -> None:
        self.logger = get_logger("spider")

    # ------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        """Determine the type of page based on its URL.

        Default:
            Everything is NOFOLLOW unless overridden.
        """
        return self.NOFOLLOW

    # ------------------------------------------------------------
    # Crawl Rules
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        """Return True if this page type should be crawled.

        Default:
            Only PAGE types are followed.
        """
        return type_ == self.PAGE

    # ------------------------------------------------------------
    # URL Normalization
    # ------------------------------------------------------------
    def normalize(self, url: str) -> str:
        """Normalize or clean a URL before enqueueing it.

        Default:
            Return the URL unchanged.
        """
        return url

    # ------------------------------------------------------------
    # Media Filtering
    # ------------------------------------------------------------
    def bad_media(self, url: str) -> bool:
        """Return True if this media URL should be ignored.

        Default:
            No media is considered bad.
        """
        return False

    # ------------------------------------------------------------
    # Browser Usage
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        """Return True if this page requires browser rendering.

        Default:
            Always False (HTTP-only).
        """
        return False

    # ------------------------------------------------------------
    # Priority
    # ------------------------------------------------------------
    def priority(self, url: str, type_: str) -> int:
        """Assign a priority to the request.

        Default:
            All requests have equal priority (0).
        """
        return 0

    # ------------------------------------------------------------
    # Scope
    # ------------------------------------------------------------
    def scope(self, url: str, type_: str) -> Optional[str]:
        """Optional scoping mechanism for extractors.

        Default:
            None (no scope).
        """
        return None

    # ------------------------------------------------------------
    # Request Metadata
    # ------------------------------------------------------------
    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        """Return metadata to attach to the Request object.

        Default:
            Empty dict.
        """
        return {}

    # ------------------------------------------------------------
    # Request Factory
    # ------------------------------------------------------------
    def make_request(self, url: str, meta: Optional[Dict[str, Any]] = None) -> Request:
        """Create a normalized Request object for the engine.

        Required by:
            - SpiderAdapter
            - Frontier
            - CrawlerEngine
        """
        meta = meta or {}
        return Request(url=url, meta=meta)

    # ------------------------------------------------------------
    # Parse Method
    # ------------------------------------------------------------
    def parse(
        self,
        page: Any,
        url: str,
        requests: Any = None,
        request: Any = None,
        response: Any = None,
    ) -> Dict[str, Any]:
        """Default parse implementation.

        Args:
            page: Response object (Requests or Playwright).
            url: Current URL.
            requests: Deprecated compatibility placeholder.
            request: Deprecated compatibility placeholder.
            response: Deprecated compatibility placeholder.

        Returns:
            dict with:
                - links: list of URLs
                - media: list of MediaItem objects
                - data: extracted metadata
        """
        self.logger.debug(f"SpiderBase.parse() called on {url} (default no-op)")
        return {
            "links": [],
            "media": [],
            "data": {},
        }
