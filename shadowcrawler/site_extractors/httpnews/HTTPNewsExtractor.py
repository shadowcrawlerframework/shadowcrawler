# shadowcrawler/site_extractors/httpnews/HTTPNewsExtractor.py
# ShadowCrawler v4.1.3 — HTTP News Extractor (Hacker News Example)
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler parses static HTML news pages such as Hacker News,
# extracting post entries, titles, and pagination links using BeautifulSoup.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world news extractors require robust, site-specific parsing logic.
#
# Demonstrates:
# - Static HTML parsing
# - Extraction of <tr class="athing"> posts
# - Pagination via “More”
# - Clean separation between spider and extractor

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class HTTPNewsExtractor(SiteExtractorBase):
    """
    HTTPNewsExtractor — example extractor for static HTML news pages.

    This extractor demonstrates how ShadowCrawler parses Hacker News using
    BeautifulSoup. It extracts page titles, post entries (<tr class="athing">),
    and pagination links (“More”), returning a normalized extraction dict.

    Responsibilities:
        - Extract page title.
        - Extract post entries (<tr class="athing">).
        - Extract pagination (“More” link).
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
        print("📰 HTTPNewsExtractor ejecutado en:", url)

        html = response.text or ""
        soup = BeautifulSoup(html, "html.parser")

        data: Dict[str, Any] = {}
        links: List[str] = []
        media: List[Any] = []

        # ------------------------------------------------------------
        # TITLE (Hacker News no usa <h1>, usamos <title>)
        # ------------------------------------------------------------
        if soup.title:
            data["title"] = soup.title.get_text(strip=True)

        # ------------------------------------------------------------
        # POSTS (cada noticia es un <tr class='athing'>)
        # ------------------------------------------------------------
        posts: List[Dict[str, Any]] = []

        for row in soup.select("tr.athing"):
            post: Dict[str, Any] = {}

            # ID
            post_id = row.get("id")
            if post_id:
                post["id"] = post_id

            # Title + URL
            title_el = row.select_one("span.titleline > a")
            if title_el:
                post["title"] = title_el.get_text(strip=True)
                post["url"] = title_el.get("href")

            posts.append(post)

        data["posts"] = posts

        # ------------------------------------------------------------
        # PAGINATION
        # ------------------------------------------------------------
        next_pages: List[str] = []
        more = soup.find("a", string="More")

        if more:
            href = more.get("href")
            if href:
                next_pages.append("https://news.ycombinator.com/" + href)

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        return {
            "data": data,
            "media": media,
            "links": next_pages,
            "next_pages": next_pages,
        }
