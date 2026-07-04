# shadowcrawler/site_extractors/universalimage/UniversalImageExtractor.py
# ShadowCrawler v4.1.3 — Universal Image Extractor (DOM Mode)
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs DOM-based image extraction using Playwright,
# collecting <img>, <picture><source>, og:image, and rel=image_src references.
#
# Notes:
# - Contains NO crawling logic.
# - Does NOT create Request objects.
# - Does NOT decide what to follow — that is the spider’s job.
# - Designed for public sites without authentication.
# - Respects robots.txt and site policies.

from typing import Any, Dict, Set
from urllib.parse import urljoin


class UniversalImageExtractor:
    """
    UniversalImageExtractor — DOM Mode image extractor.

    This extractor demonstrates how ShadowCrawler collects image URLs from fully
    rendered pages using Playwright. It supports:

        - <img src>
        - <img data-src>
        - <picture><source srcset>
        - <meta property="og:image">
        - <link rel="image_src">

    Responsibilities:
        - Parse DOM elements containing image references.
        - Normalize URLs using urljoin.
        - Return a standardized extraction dict: {"images": [...]}

    Notes:
        - Contains NO crawling logic.
        - Does NOT navigate pages.
        - Does NOT decide what to follow — that is the spider’s job.
    """

    def __init__(self, handle: str) -> None:
        self.handle = handle

    # ------------------------------------------------------------
    # EXTRACT FROM PAGE
    # ------------------------------------------------------------
    async def extract_from_page(self, page: Any, base_url: str) -> Dict[str, Any]:
        print(f"🚀 UniversalImageExtractor ejecutado en: {base_url}")

        urls: Set[str] = set()

        # ------------------------------------------------------------
        # <img src> / <img data-src>
        # ------------------------------------------------------------
        try:
            imgs = await page.query_selector_all("img")
            for img in imgs:
                src = await img.get_attribute("src")
                data_src = await img.get_attribute("data-src")
                for candidate in (src, data_src):
                    if candidate:
                        urls.add(urljoin(base_url, candidate))
        except Exception:
            print("⚠ Error leyendo <img> tags")
            pass

        # ------------------------------------------------------------
        # <picture><source srcset>
        # ------------------------------------------------------------
        try:
            sources = await page.query_selector_all("picture source")
            for s in sources:
                srcset = await s.get_attribute("srcset")
                if srcset:
                    parts = [p.strip().split(" ")[0] for p in srcset.split(",")]
                    for p in parts:
                        if p:
                            urls.add(urljoin(base_url, p))
        except Exception:
            print("⚠ Error leyendo <picture><source>")
            pass

        # ------------------------------------------------------------
        # meta og:image
        # ------------------------------------------------------------
        try:
            og = await page.query_selector("meta[property='og:image']")
            if og:
                content = await og.get_attribute("content")
                if content:
                    urls.add(urljoin(base_url, content))
        except Exception:
            print("⚠ Error leyendo meta og:image")
            pass

        # ------------------------------------------------------------
        # link rel=image_src
        # ------------------------------------------------------------
        try:
            link = await page.query_selector("link[rel='image_src']")
            if link:
                href = await link.get_attribute("href")
                if href:
                    urls.add(urljoin(base_url, href))
        except Exception:
            print("⚠ Error leyendo link rel=image_src")
            pass

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        print(f"🔥 UniversalImageExtractor DONE — images={len(urls)}")

        return {
            "images": list(urls)
        }
