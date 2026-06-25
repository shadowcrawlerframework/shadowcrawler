# shadowcrawler/models/response.py
# ShadowCrawler v4.1.0 — Response Model
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Normalized response object used by:
#   - RequestsFetcher
#   - PlaywrightFetcher
#   - CrawlerEngine
#   - SpiderAdapter
#   - MediaExtractor
#   - CheckpointManager

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import json


@dataclass
class Response:
    """Normalized fetch result for ShadowCrawler v4.1.0.

    Represents a unified response object consumed by:
        - RequestsFetcher
        - PlaywrightFetcher
        - CrawlerEngine
        - SpiderAdapter
        - MediaExtractor
        - CheckpointManager

    Notes:
        - Contains no site‑specific logic.
        - Fully serializable for checkpointing.
        - Supports both HTTP and browser-based fetchers.
    """

    # ------------------------------------------------------------
    # CORE FIELDS
    # ------------------------------------------------------------
    url: str
    html: str = ""
    text: str = ""
    status: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)
    from_browser: bool = False

    # ------------------------------------------------------------
    # OPTIONAL RAW DATA
    # ------------------------------------------------------------
    raw_bytes: Optional[bytes] = None
    encoding: Optional[str] = None

    # ------------------------------------------------------------
    # REDIRECTS
    # ------------------------------------------------------------
    final_url: Optional[str] = None
    redirect_chain: List[str] = field(default_factory=list)

    # ------------------------------------------------------------
    # TIMING
    # ------------------------------------------------------------
    elapsed: Optional[float] = None

    # ------------------------------------------------------------
    # ORIGINAL REQUEST
    # ------------------------------------------------------------
    request: Any = None

    # ------------------------------------------------------------
    # BROWSER‑SPECIFIC FIELDS
    # ------------------------------------------------------------
    browser_page: Any = None
    sniffed_media: Any = None

    # ------------------------------------------------------------
    # POST‑INIT NORMALIZATION
    # ------------------------------------------------------------
    def __post_init__(self) -> None:
        """Normalize html/text and default final_url."""
        if self.html:
            self.text = self.html
        else:
            self.html = self.text or ""
            self.text = self.html

        if not self.final_url:
            self.final_url = self.url

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def is_ok(self) -> bool:
        """Return True if status is 2xx."""
        return 200 <= self.status < 300

    def is_error(self) -> bool:
        """Return True if status is 4xx or 5xx."""
        return self.status >= 400

    def browser(self) -> bool:
        """Return True if the response came from Playwright."""
        return self.from_browser

    def json(self) -> Optional[Any]:
        """Attempt to parse the response text as JSON."""
        try:
            return json.loads(self.text)
        except Exception:
            return None

    def __repr__(self) -> str:
        src = "browser" if self.from_browser else "http"
        return (
            f"Response(url={self.url}, status={self.status}, "
            f"src={src}, html_len={len(self.html)})"
        )
