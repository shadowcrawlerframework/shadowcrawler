# AuthBrowserDemoExtractor.py
# ShadowCrawler v4.1.1 — Manual Login Demo Extractor
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Example extractor for sites requiring manual login.
# Does NOT enqueue next_pages.
# Does NOT force navigation.
# Only extracts minimal data and lets the AuthHandler control the flow.

from typing import Any, Dict, List

from shadowcrawler.logging import get_logger


class AuthBrowserDemoExtractor:
    """Minimal extractor for manual-login demonstration spiders.

    Responsibilities:
        - Receive a Playwright Page object.
        - Extract minimal data without making navigation decisions.
        - Never enqueue next_pages.
        - Never modify crawling flow.
        - Allow AuthHandler to fully control login/session logic.

    Notes:
        This extractor is intentionally simple. It demonstrates how
        ShadowCrawler handles authenticated browser sessions without
        forcing navigation or interfering with the AuthHandler.
    """

    def __init__(self, handle: str) -> None:
        self.handle = handle
        self.logger = get_logger("extractor")

    # ------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------
    async def extract(self, page: Any, url: str) -> Dict[str, Any]:
        """Extract minimal information from the page.

        Args:
            page: Playwright Page instance.
            url: Current page URL.

        Returns:
            A dict with:
                - links: []
                - next_pages: []
                - media: []
                - data: extracted fields
        """
        print(f"📄 AuthBrowserDemoExtractor ejecutado en: {url}")

        data: Dict[str, Any] = {}
        media: List[Any] = []
        links: List[str] = []
        next_pages: List[str] = []

        # If we're on /profile, attempt to read the username
        if "/profile" in url:
            try:
                username = await page.locator("#userName-value").inner_text()
                data["username"] = username
            except Exception:
                pass

        return {
            "links": links,
            "next_pages": next_pages,
            "media": media,
            "data": data,
        }
