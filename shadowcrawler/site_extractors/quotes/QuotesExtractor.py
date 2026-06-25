# shadowcrawler/site_extractors/quotes/QuotesExtractor.py
# ShadowCrawler v4.1.0 — Quotes to Scrape Extractor
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example extractor for Quotes to Scrape.

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class QuotesExtractor(SiteExtractorBase):
    """Example extractor for Quotes to Scrape.

    Responsibilities:
        - Extract quotes, authors, and tags.
        - Extract pagination (next page).
        - Extract tag links.
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
        print("💬 QuotesExtractor ejecutado en:", url)

        html = response.text or ""
        soup = BeautifulSoup(html, "html.parser")

        data: Dict[str, Any] = {}
        links: List[str] = []
        media: List[Any] = []

        # ------------------------------------------------------------
        # QUOTES
        # ------------------------------------------------------------
        quotes: List[Dict[str, Any]] = []

        for q in soup.select("div.quote"):
            text_el = q.select_one("span.text")
            author_el = q.select_one("small.author")
            tags = [t.get_text(strip=True) for t in q.select("div.tags a.tag")]

            quotes.append({
                "text": text_el.get_text(strip=True) if text_el else None,
                "author": author_el.get_text(strip=True) if author_el else None,
                "tags": tags,
            })

        data["quotes"] = quotes

        # ------------------------------------------------------------
        # PAGINATION
        # ------------------------------------------------------------
        next_pages: List[str] = []
        next_btn = soup.select_one("li.next > a")

        if next_btn:
            href = next_btn.get("href")
            if href:
                next_pages.append("https://quotes.toscrape.com" + href)

        # ------------------------------------------------------------
        # TAG LINKS
        # ------------------------------------------------------------
        for a in soup.select("a.tag"):
            href = a.get("href")
            if href:
                links.append("https://quotes.toscrape.com" + href)

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        return {
            "data": data,
            "media": media,
            "links": links,
            "next_pages": next_pages,
        }
