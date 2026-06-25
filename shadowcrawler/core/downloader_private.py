# shadowcrawler/core/downloader_private.py
# ShadowCrawler v4.1.0 — Private Downloader Extension
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# This module provides a safe extension point for users who want to
# customize download behavior without modifying the core Downloader.
#
# Features:
#   - Failure interception
#   - Structured audit logging
#   - Full compatibility with the core downloader
#   - Zero changes to core logic

from typing import Any, Iterable, Tuple

from shadowcrawler.core.downloader import Downloader
from shadowcrawler.audit.audit_logger import AuditLogger


class PrivateDownloader(Downloader):
    """Optional extension of the core Downloader with auditing.

    Responsibilities:
        - Intercept download failures.
        - Record detailed audit logs.
        - Preserve all core download behavior.
        - Provide a stable customization layer for end‑users.

    Args:
        spider_name: Name of the spider performing the download.
        fetch_mode: Fetch mode used during the crawl (http/browser).
        *args, **kwargs: Passed directly to the core Downloader.
    """

    def __init__(self, *args, spider_name: str = None, fetch_mode: str = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Create auditor with metadata
        self.audit = AuditLogger(
            path="audit_fails.jsonl",
            spider_name=spider_name,
            fetch_mode=fetch_mode,
        )

    # ------------------------------------------------------------
    # Override: download one item with auditing
    # ------------------------------------------------------------
    async def _download_one(self, media: Any) -> Tuple[Any, bool]:
        """Download a single media item with auditing on failure."""
        url = getattr(media, "url", None)
        self.logger.debug(f"Downloading {url}")

        # 1) Primary: HTTPX
        tmp, err = await self._download_httpx(media)

        if tmp and err is None:
            return await self._finalize(tmp, media)

        # Non‑status errors → definitive failure
        if err and not err.startswith("status-"):
            self.logger.error(f"Failed to download {url}: {err}")
            self.audit.fail(media, err)
            return media, False

        # 2) Status‑based fallbacks
        if err and any(code in err for code in ["status-403", "status-401", "status-429"]):
            self.logger.debug(f"HTTPX blocked ({err}), trying Playwright request.get(): {url}")
            tmp2, err2 = await self._download_playwright_request(media)
            if tmp2 and not err2:
                return await self._finalize(tmp2, media)

            self.logger.debug(f"Playwright request.get failed ({err2}), trying page.goto(): {url}")
            tmp3, err3 = await self._download_playwright_page_goto(media)
            if tmp3 and not err3:
                return await self._finalize(tmp3, media)

            self.logger.debug(f"Playwright page.goto failed ({err3}), trying fetch() inside page: {url}")
            tmp4, err4 = await self._download_playwright_fetch(media)
            if tmp4 and not err4:
                return await self._finalize(tmp4, media)

            # All fallbacks failed
            final_err = err4 or err3 or err2 or err
            self.logger.error(f"Failed to download {url}: {final_err}")
            self.audit.fail(media, final_err)
            return media, False

        # 3) Any other status error
        self.logger.error(f"Failed to download {url}: {err}")
        self.audit.fail(media, err)
        return media, False

    # ------------------------------------------------------------
    # Override: print audit summary after all downloads
    # ------------------------------------------------------------
    async def download_all(self, media_items: Iterable[Any]) -> None:
        """Download all media items and print audit summary."""
        await super().download_all(media_items)
        self.audit.print_summary()
