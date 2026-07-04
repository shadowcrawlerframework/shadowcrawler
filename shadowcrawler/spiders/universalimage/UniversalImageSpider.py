# shadowcrawler/spiders/universalimage/UniversalImageSpider.py
# ShadowCrawler v4.1.3 — Universal Image Spider (Official Example)
#
# DISCLAIMER:
# This spider is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs DOM-based image extraction on arbitrary
# public sites using Playwright, maintaining a persistent browser page and
# performing controlled internal navigation.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world spiders require robust, site-specific logic.
#
# Demonstrates:
# - Browser-based DOM extraction
# - <img>, <picture>, og:image, rel=image_src discovery
# - Controlled internal navigation (MAX_DEPTH / MAX_PAGES)
# - Clean separation between spider and extractor

from typing import Any, Dict, List, Set
from urllib.parse import urljoin, urlparse

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.models.response import Response
from shadowcrawler.site_extractors.universalimage.UniversalImageExtractor import UniversalImageExtractor


class UniversalImageSpider(SpiderBase):
    """
    UniversalImageSpider — DOM-based demo spider for image collection.

    This spider demonstrates how ShadowCrawler uses Playwright to extract images
    from fully rendered pages. It maintains a persistent browser page, navigates
    internal links up to a controlled depth, and delegates extraction to
    UniversalImageExtractor.

    Responsibilities:
        - Always use browser mode (Playwright).
        - Maintain a persistent page (keep_page=True).
        - Extract images using UniversalImageExtractor.
        - Perform controlled internal navigation (MAX_DEPTH / MAX_PAGES).
        - Make NO crawling decisions beyond internal-link traversal.

    Notes:
        This spider demonstrates:
            - DOM-based image extraction
            - Internal link discovery
            - Persistent browser-page usage
    """

    # ------------------------------------------------------------
    # METADATA (contract-level signals)
    # ------------------------------------------------------------
    name = "UniversalImage"
    handle = "universalimage"
    domain = None

    fetch_mode = "browser"   # Force Playwright mode
    workers = 1              # Single worker recommended for persistent-page mode

    extractor_class = UniversalImageExtractor
    auth_handler_class = None

    MAX_PAGES: int = 50
    MAX_DEPTH: int = 3

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        """UniversalImageSpider treats all URLs as GENERIC."""
        return "GENERIC"

    # ------------------------------------------------------------
    # FOLLOW RULES
    # ------------------------------------------------------------
    def should_follow(self, type_: str) -> bool:
        """UniversalImageSpider does not follow based on type; only internal links."""
        return False

    # ------------------------------------------------------------
    # ALWAYS USE BROWSER
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        """Force Playwright browser mode."""
        return True

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        """Browser metadata for PlaywrightFetcher."""
        return {
            "use_browser": True,
            "browser_mode": "full",
            "keep_page": True,   # 🔥 CRÍTICO — UniversalImage necesita mantener la página abierta
            "wait_time": 20000,
        }

    # ------------------------------------------------------------
    # INTERNAL LINK CHECK
    # ------------------------------------------------------------
    def _is_internal(self, base: str, link: str) -> bool:
        """Check if a link belongs to the same domain."""
        if not link:
            return False
        b = urlparse(base)
        l = urlparse(link)
        return b.netloc == l.netloc

    # ------------------------------------------------------------
    # INTERNAL LINK EXTRACTION
    # ------------------------------------------------------------
    async def _extract_internal_links(self, page: Any, base_url: str) -> Set[str]:
        """Extract internal links from the DOM."""
        links: Set[str] = set()
        try:
            anchors = await page.query_selector_all("a[href]")
            for a in anchors:
                href = await a.get_attribute("href")
                if not href:
                    continue
                full = urljoin(base_url, href)
                if self._is_internal(base_url, full):
                    links.add(full)
        except Exception:
            print("⚠ Error extrayendo enlaces internos")
            pass
        return links

    # ------------------------------------------------------------
    # PARSE (browser-based)
    # ------------------------------------------------------------
    async def parse(self, response: Response, **kwargs) -> Dict[str, Any]:
        print("🚀 UniversalImageSpider ejecutado en:", response.url)

        page = getattr(response, "browser_page", None)
        if page is None:
            print("⚠ Page es None, abortando.")
            return {"links": [], "next_pages": [], "media": [], "data": {}}

        visited: Set[str] = set()
        queue: List[Dict[str, Any]] = [{"url": response.url, "depth": 0}]
        all_images: Set[str] = set()

        extractor = self.extractor_class(self.handle)

        while queue and len(visited) < self.MAX_PAGES:
            item = queue.pop(0)
            current_url = item["url"]
            depth = item["depth"]

            if current_url in visited:
                continue
            visited.add(current_url)

            print(f"🔥 VISITING: {current_url} (depth={depth})")

            try:
                await page.goto(current_url, wait_until="load")
                await page.wait_for_timeout(2000)
            except Exception as exc:
                print("⚠ Error navegando:", exc)
                continue

            extracted = await extractor.extract_from_page(page, current_url)
            imgs = extracted.get("images", [])
            print(f"🖼️ FOUND {len(imgs)} IMAGES IN {current_url}")
            all_images.update(imgs)

            if depth < self.MAX_DEPTH:
                links = await self._extract_internal_links(page, current_url)
                print(f"🌐 FOUND {len(links)} INTERNAL LINKS IN {current_url}")
                for link in links:
                    if link not in visited:
                        queue.append({"url": link, "depth": depth + 1})

        print(f"🔥 UNIVERSAL IMAGE DONE — pages={len(visited)}, images={len(all_images)}")

        media_items = [{"url": u, "type": "image"} for u in all_images]

        data = {
            "pages_visited": len(visited),
            "images_collected": len(all_images),
        }

        return {
            "links": [],
            "next_pages": [],
            "media": media_items,
            "data": data,
        }
