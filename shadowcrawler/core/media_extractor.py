# shadowcrawler/core/media_extractor.py
# ShadowCrawler v4.1.3 — Media Extractor
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Normalizes media and data. Does NOT modify Requests.
#
# Notes:
#   - Normalizes media dictionaries produced by extractors.
#   - Does NOT fetch media; Downloader handles actual downloads.
#   - Does NOT classify URLs; spiders decide what is media.
#   - Does NOT create Requests; SpiderAdapter handles link normalization.
#   - Supports DOM‑FULL spiders (may inspect browser_page if provided).
#   - Fully serializable; contains no crawling or browser state.
#   - Media extraction is purely structural (URL, type, metadata).


from typing import Dict, Any, List, Tuple

from shadowcrawler.models.result import Result
from shadowcrawler.core.media import MediaItem, as_media
from shadowcrawler.logging import get_logger


class MediaExtractor:
    """Normalize media and structured data for ShadowCrawler v4.1.3.

    Responsibilities:
        - Convert raw media entries into MediaItem objects.
        - Convert structured data into Result objects.
        - Do NOT modify links.
        - Do NOT modify next_pages.
        - Do NOT create Requests.
        - Do NOT assign priorities.
        - Do NOT filter media.

    Notes:
        This extractor is intentionally minimal. All crawling logic,
        link extraction, pagination, and request generation happens
        in the SpiderAdapter and SiteExtractors.
    """

    def __init__(self, disabled: bool = False) -> None:
        self.logger = get_logger("media")
        self.disabled = disabled

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    def extract(
        self,
        data: Dict[str, Any],
        source_url: str,
        spider_name: str,
    ) -> Tuple[List[Result], List[Any], List[MediaItem]]:
        """Extract structured data and media items from a spider output.

        Args:
            data: The dictionary returned by a SiteExtractor.
            source_url: URL of the page being processed.
            spider_name: Name of the spider producing the data.

        Returns:
            A tuple of:
                - results: List[Result]
                - new_requests: always empty (Requests come from SpiderAdapter)
                - media_items: List[MediaItem]
        """
        results: List[Result] = []
        media_items: List[MediaItem] = []

        self.logger.debug(f"MediaExtractor.extract() → {source_url}")

        # --------------------------------------------------------
        # 1. DATA PAYLOAD
        # --------------------------------------------------------
        payload = data.get("data")
        if payload:
            results.append(
                Result(
                    data=payload,
                    source_url=source_url,
                    spider_name=spider_name,
                )
            )

        # If media is disabled, stop here
        if self.disabled:
            return results, [], []

        # --------------------------------------------------------
        # 2. MEDIA
        # --------------------------------------------------------
        raw_media = data.get("media", [])
        for m in raw_media:

            # Already a MediaItem
            if isinstance(m, MediaItem):
                media_items.append(m)
                continue

            # Dict format
            if isinstance(m, dict):
                url = m.get("url")
                page = m.get("page", source_url)
                media_type = m.get("type", "unknown")
                referer = m.get("referer")
                headers = m.get("headers")
                cookies = m.get("cookies")

                if url:
                    media_items.append(
                        as_media(
                            url=url,
                            page=page,
                            media_type=media_type,
                            referer=referer,
                            headers=headers,
                            cookies=cookies,
                        )
                    )
                continue

            # String format (URL only)
            if isinstance(m, str):
                media_items.append(as_media(url=m, page=source_url))
                continue

        # --------------------------------------------------------
        # 3. DO NOT TOUCH LINKS OR NEXT_PAGES
        # --------------------------------------------------------
        return results, [], media_items
