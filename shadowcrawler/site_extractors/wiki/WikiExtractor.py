# shadowcrawler/site_extractors/wiki/WikiExtractor.py
# ShadowCrawler v4.1.1 — Wikipedia Extractor (Official Example)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Official ShadowCrawler v4 example extractor for Wikipedia.

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class WikiExtractor(SiteExtractorBase):
    """Example extractor for Wikipedia pages.

    Responsibilities:
        - Extract title (<h1 id="firstHeading">)
        - Extract infobox (table.infobox)
        - Extract main content (div#mw-content-text)
        - Extract internal links (/wiki/…)
        - Return a normalized extraction dict

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
        print("🔥 WikiExtractor ejecutado en:", url)

        html = response.html or response.text or ""
        soup = BeautifulSoup(html, "html.parser")

        data: Dict[str, Any] = {}
        media: List[Any] = []
        links: List[str] = []

        # ------------------------------------------------------------
        # TITLE
        # ------------------------------------------------------------
        title_el = soup.find("h1", id="firstHeading")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        # ------------------------------------------------------------
        # INFOBOX
        # ------------------------------------------------------------
        infobox = soup.find("table", class_="infobox")
        if infobox:
            info: Dict[str, str] = {}
            for row in infobox.find_all("tr"):
                header = row.find("th")
                value = row.find("td")
                if header and value:
                    info[header.get_text(strip=True)] = value.get_text(" ", strip=True)
            data["infobox"] = info

        # ------------------------------------------------------------
        # CONTENT
        # ------------------------------------------------------------
        content_el = soup.find("div", id="mw-content-text")
        if content_el:
            data["content"] = content_el.get_text(" ", strip=True)

        # ------------------------------------------------------------
        # INTERNAL LINKS
        # ------------------------------------------------------------
        for a in soup.select("a[href^='/wiki/']"):
            href = a.get("href")
            if not href:
                continue

            if href.startswith("/wiki/Special:"):
                continue

            full = "https://en.wikipedia.org" + href
            links.append(full)

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        return {
            "data": data,
            "media": media,
            "links": links,
            "next_pages": links[:20],
        }
