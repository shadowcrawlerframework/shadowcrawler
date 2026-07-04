# shadowcrawler/site_extractors/gallery/GalleryExtractor.py
# ShadowCrawler v4.1.3 — Gallery Extractor (Unsplash Example)
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler parses image-heavy gallery pages using BeautifulSoup,
# extracting multiple image formats (src, srcset, lazy-loaded, <picture>/<source>,
# CSS background-image) and discovering category/photo links.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world gallery extractors require robust, site-specific parsing logic.
#
# Demonstrates:
# - Static HTML parsing (no Playwright dependency)
# - Extraction of multiple image formats
# - Category and photo link discovery
# - Infinite-scroll pagination simulation

from typing import Any, Dict, List, Optional
import re

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class GalleryExtractor(SiteExtractorBase):
    """
    GalleryExtractor — enhanced extractor for Unsplash-style image galleries.

    This extractor demonstrates how ShadowCrawler handles image-heavy sites
    using static HTML parsing. It supports multiple image formats, including
    <img srcset>, lazy-loaded attributes, <picture>/<source> tags, and CSS
    background-image URLs. It also discovers category/photo links and simulates
    pagination for infinite-scroll layouts.

    Improvements:
        - Extract <img srcset>, <img src>, lazy-loaded images.
        - Extract <picture> and <source> images.
        - Extract CSS background-image URLs.
        - Extract category and photo links.
        - Simulate pagination.

    Notes:
        - Fully synchronous (compatible with ShadowCrawler).
        - Does NOT depend on Playwright DOM.
        - Works with static HTML or page.content() DOM.
    """

    def __init__(self, handle: Optional[str] = None) -> None:
        super().__init__(handle)

    def extract(
        self,
        response: Any,
        url: Optional[str] = None,
        scope: Optional[Any] = None,
        browser_page: Optional[Any] = None,
    ) -> Dict[str, Any]:

        print("🖼️ GalleryExtractor running on:", url)

        html = response.html or ""
        soup = BeautifulSoup(html, "html.parser")

        links: List[str] = []
        media: List[Dict[str, Any]] = []

        # ------------------------------------------------------------
        # 1. IMG: srcset + src + lazy-loaded
        # ------------------------------------------------------------
        for img in soup.find_all("img"):
            candidates = [
                img.get("src"),
                img.get("srcset"),
                img.get("data-src"),
                img.get("data-lazy"),
                img.get("data-lazy-src"),
                img.get("data-original"),
            ]

            for c in candidates:
                if not c:
                    continue

                # srcset → tomar la primera URL
                if " " in c:
                    c = c.split(" ")[0]

                if c.startswith("http"):
                    media.append({
                        "url": c,
                        "page": url,
                        "type": "image",
                    })

        # ------------------------------------------------------------
        # 2. <picture> / <source>
        # ------------------------------------------------------------
        for picture in soup.find_all("picture"):
            for source in picture.find_all("source"):
                srcset = source.get("srcset")
                src = source.get("src")

                candidates = [srcset, src]

                for c in candidates:
                    if not c:
                        continue

                    if " " in c:
                        c = c.split(" ")[0]

                    if c.startswith("http"):
                        media.append({
                            "url": c,
                            "page": url,
                            "type": "image",
                        })

        # ------------------------------------------------------------
        # 3. CSS background-image
        # ------------------------------------------------------------
        bg_regex = re.compile(r'background-image:\s*url\(["\']?(.*?)["\']?\)', re.IGNORECASE)

        for tag in soup.find_all(style=True):
            style = tag.get("style", "")
            match = bg_regex.search(style)
            if match:
                bg_url = match.group(1)
                if bg_url.startswith("http"):
                    media.append({
                        "url": bg_url,
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
        # PAGINATION (simulate infinite scroll)
        # ------------------------------------------------------------
        next_pages = links[:10]

        return {
            "data": {"image_count": len(media)},
            "media": media,
            "links": links,
            "next_pages": next_pages,
        }
