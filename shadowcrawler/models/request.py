# shadowcrawler/models/request.py
# ShadowCrawler v4.1.0 — Request Model
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Universal work unit for Engine, Frontier, and Fetchers.

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class Request:
    """Crawling request entity for ShadowCrawler v4.1.0.

    Represents a normalized crawling request consumed by:
        - Frontier
        - RequestsFetcher
        - PlaywrightFetcher
        - CrawlerEngine
        - CheckpointManager

    Notes:
        - Contains no site‑specific logic.
        - Fully serializable for checkpointing.
        - Designed for both HTTP and browser fetchers.
    """

    # ------------------------------------------------------------
    # CORE
    # ------------------------------------------------------------
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None

    # ------------------------------------------------------------
    # CRAWLING METADATA
    # ------------------------------------------------------------
    meta: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    use_browser: bool = False
    allow_redirects: bool = True

    # ------------------------------------------------------------
    # INTERNAL (no site logic)
    # ------------------------------------------------------------
    depth: int = 0
    retries: int = 0
    timeout: Optional[float] = None
    fingerprint: Optional[str] = None
    source_url: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    # ------------------------------------------------------------
    # FLUENT HELPERS
    # ------------------------------------------------------------
    def with_meta(self, **kwargs) -> "Request":
        """Add or update metadata (fluent API)."""
        self.meta.update(kwargs)
        return self

    def with_headers(self, headers: Dict[str, str]) -> "Request":
        """Add or update HTTP headers (fluent API)."""
        self.headers.update(headers)
        return self

    def with_cookies(self, cookies: Dict[str, str]) -> "Request":
        """Add or update cookies (fluent API)."""
        self.cookies.update(cookies)
        return self

    def browser(self, enabled: bool = True) -> "Request":
        """Enable or disable browser mode (fluent API)."""
        self.use_browser = enabled
        return self

    def with_priority(self, value: int) -> "Request":
        """Set request priority (fluent API)."""
        self.priority = value
        return self

    def with_timeout(self, seconds: float) -> "Request":
        """Set request timeout (fluent API)."""
        self.timeout = seconds
        return self

    def clone(self, **overrides) -> "Request":
        """Create a copy of this Request with optional overrides.

        Useful for advanced spiders that need to duplicate a request
        while modifying only a few fields.
        """
        data = self.__dict__.copy()
        data.update(overrides)
        return Request(**data)
