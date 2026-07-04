# shadowcrawler/core/media.py
# ShadowCrawler v4.1.3 — Media Transport Entity
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Defines MediaItem, the lightweight transport object used throughout
# the extraction and download pipeline.

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class MediaItem:
    """Lightweight media transport entity for ShadowCrawler v4.1.3.

    Represents a downloadable media resource detected by a SiteExtractor.
    This object is passed through the pipeline between:

        - SiteExtractor
        - MediaExtractor
        - Downloader

    Notes:
        - MediaItem does NOT download anything by itself.
        - It simply carries metadata required for the downloader to
          perform the actual request.
    """

    url: str
    page: str
    media_type: str = "unknown"

    # Optional metadata
    referer: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Optional[Any] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # Fluent Helpers
    # ------------------------------------------------------------
    def with_referer(self, referer: str) -> "MediaItem":
        """Attach a referer header and return self (fluent API)."""
        self.referer = referer
        return self

    def with_headers(self, headers: Dict[str, str]) -> "MediaItem":
        """Merge additional headers and return self (fluent API)."""
        if headers:
            self.headers.update(headers)
        return self

    def with_cookies(self, cookies: Any) -> "MediaItem":
        """Attach cookies and return self (fluent API)."""
        self.cookies = cookies
        return self

    def attach(
        self,
        *,
        referer: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Any] = None,
    ) -> "MediaItem":
        """Generic fluent metadata setter."""
        if referer:
            self.referer = referer
        if headers:
            self.headers.update(headers)
        if cookies:
            self.cookies = cookies
        return self

    # ------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"MediaItem(url={self.url}, type={self.media_type}, "
            f"referer={'yes' if self.referer else 'no'}, "
            f"headers={len(self.headers)})"
        )

    # ------------------------------------------------------------
    # Dedupe Support
    # ------------------------------------------------------------
    def __eq__(self, other: Any) -> bool:
        """Two MediaItems are equal if they share the same URL."""
        return isinstance(other, MediaItem) and self.url == other.url

    def __hash__(self) -> int:
        """Hash based solely on URL for dedupe indexing."""
        return hash(self.url)


# ------------------------------------------------------------
# Factory Helper
# ------------------------------------------------------------
def as_media(
    url: str,
    page: str,
    media_type: str = "unknown",
    referer: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Any] = None,
) -> MediaItem:
    """Create a normalized MediaItem instance.

    Used by MediaExtractor and SiteExtractors to convert raw values
    (strings, dicts, etc.) into a consistent MediaItem object.
    """
    return MediaItem(
        url=url,
        page=page,
        media_type=media_type,
        referer=referer,
        headers=headers or {},
        cookies=cookies,
    )
