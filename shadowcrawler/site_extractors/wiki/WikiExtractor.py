# shadowcrawler/site_extractors/wiki/WikiExtractor.py
# ShadowCrawler v4.1.3 — Wikipedia Extractor (Ultra Deep Mode v2)
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs browser-based extraction on large,
# structured sites such as Wikipedia, using Playwright to render dynamic
# content and a classification model for ARTICLE / CATEGORY / FILE / GENERIC.
#
# Ultra Deep Mode v2:
# - Espera activa para lazy-loading en categorías
# - Recaptura del DOM después de que Wikipedia cargue artículos
# - Extracción profunda de enlaces en categorías y artículos
# - Soporte para /wiki/, /w/index.php, Category:, File:, Portal:, List_of_
# - Crawling profundo real sin modificar el spider

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from shadowcrawler.site_extractors.base import SiteExtractorBase


class WikiExtractor(SiteExtractorBase):
    """
    WikiExtractor — Ultra Deep Mode v2 extractor for Wikipedia.

    This extractor demonstrates how ShadowCrawler parses fully rendered
    Wikipedia pages using Playwright. It extracts titles, infoboxes, main
    content, and internal links — including deep-mode support for /wiki/,
    /w/index.php, Category:, File:, Portal:, and List_of_ pages, with
    explicit handling of lazy-loaded category content.

    Responsibilities:
        - Extract title (<h1 id="firstHeading">)
        - Extract infobox (table.infobox)
        - Extract main content (div#mw-content-text)
        - Extract internal links (Ultra Deep Mode v2)
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
        print("🚀 WikiExtractor (Ultra Deep Mode v2) ejecutado en:", url)

        page = getattr(response, "page", None)

        # ------------------------------------------------------------
        # ESPERA ACTIVA PARA CATEGORÍAS (lazy-loading)
        # ------------------------------------------------------------
        if page is not None and scope == "CATEGORY":
            try:
                page.evaluate(
                    """
                    return new Promise(resolve => {
                        const done = () => {
                            const el = document.querySelector('#mw-pages');
                            if (el && el.querySelectorAll('a').length > 10) {
                                resolve(true);
                            } else {
                                setTimeout(done, 300);
                            }
                        };
                        done();
                    });
                    """
                )
            except Exception:
                pass

        # ------------------------------------------------------------
        # RECAPTURA DEL DOM DESPUÉS DEL LAZY-LOADING
        # ------------------------------------------------------------
        html = ""
        try:
            if page is not None:
                html = page.content()
        except Exception:
            html = response.html or response.text or ""

        if not html:
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
        # INTERNAL LINKS (ULTRA DEEP MODE v2)
        # ------------------------------------------------------------
        for a in soup.find_all("a"):
            href = a.get("href")
            if not href:
                continue

            # Skip Special:
            if href.startswith("/wiki/Special:"):
                continue

            # Accept /wiki/...
            if href.startswith("/wiki/"):
                links.append("https://en.wikipedia.org" + href)
                continue

            # Accept /w/index.php?title=...
            if href.startswith("/w/index.php"):
                links.append("https://en.wikipedia.org" + href)
                continue

        # ------------------------------------------------------------
        # RESULT
        # ------------------------------------------------------------
        return {
            "data": data,
            "media": media,
            "links": links,
            "next_pages": links[:100],
        }
