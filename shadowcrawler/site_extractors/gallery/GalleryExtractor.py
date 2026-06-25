# shadowcrawler/site_extractors/gallery/GalleryExtractor.py
# ShadowCrawler v4.1.0 — Gallery Extractor (Unsplash Example)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example extractor for image galleries (Unsplash).

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class GalleryExtractor(SiteExtractorBase):
    """Example extractor for image galleries (Unsplash).

    Responsibilities:
        - Extract images from <img srcset>.
        - Extract category links (/t/...).
        - Extract photo links (/photos/...).
        - Simulate pagination for infinite-scroll pages.
        - Return a normalized extraction dict.

    Notes:
        - Contains NO crawling logic.
        - Does NOT create Request objects.
        - Does NOT decide what to follow — that is the spider’s job.
    """

    def __init__(self, handle: Optional[str] = None) -> None:
        super().__init__(handle)

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    def extract(
        self,
        response: Any,
        url: Optional[str] = None,
        scope: Optional[Any] = None,
    ) -> Dict[str, Any]:
        print("🖼️ GalleryExtractor ejecutado en:", url)

        html = response.html or ""
        soup = BeautifulSoup(html, "html.parser")

        data: Dict[str, Any] = {}
        links: List[str] = []
        media: List[Dict[str, Any]] = []

        # ------------------------------------------------------------
        # IMAGE EXTRACTION
        # ------------------------------------------------------------
        for img in soup.select("img[srcset]"):
            src = img.get("src")
            if not src:
                continue

            media.append({
                "url": src,
                "page": url,
                "type": "image",
            })

        # ------------------------------------------------------------
        # CATEGORY LINKS
        # ------------------------------------------------------------
        for a in soup.select("a[href^='/t/']"):
            href = a.get("href")
            if href:
                links.append("https://unsplash.com" + href)

        # ------------------------------------------------------------
        # PHOTO LINKS
        # ------------------------------------------------------------
        for a in soup.select("a[href^='/photos/']"):
            href = a.get("href")
            if href:
                links.append("https://unsplash.com" + href)

        # ------------------------------------------------------------
        # PAGINATION (Unsplash usa scroll infinito → simulamos next_pages)
        # ------------------------------------------------------------
        next_pages = links[:10]

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        return {
            "data": {"image_count": len(media)},
            "media": media,
            "links": links,
            "next_pages": next_pages,
        }
