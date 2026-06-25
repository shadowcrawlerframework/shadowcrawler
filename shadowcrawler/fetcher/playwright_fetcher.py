# shadowcrawler/fetcher/playwright_fetcher.py
# ShadowCrawler v4.1.0 — Playwright Fetcher (HTML‑ONLY SAFE)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# - Uses ONLY HTML‑only contexts
# - Never touches the FULL downloader context
# - Always closes pages safely
# - Returns normalized Response objects

from typing import Any, Optional

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from shadowcrawler.logging import get_logger
from shadowcrawler.models.response import Response


class PlaywrightFetcher:
    """HTML‑only Playwright fetcher for ShadowCrawler v4.1.0.

    Responsibilities:
        - Fetch HTML using lightweight HTML‑only contexts.
        - Never interact with the FULL download context.
        - Always close pages safely unless an AuthHandler needs them.
        - Return normalized Response objects compatible with the Engine.

    Notes:
        This fetcher is intentionally minimal and safe. It avoids
        heavy browser contexts and ensures memory stability.
    """

    def __init__(self, browser_manager: Any) -> None:
        self.browser_manager = browser_manager
        self.logger = get_logger("browser")

    # ------------------------------------------------------------
    # FETCH
    # ------------------------------------------------------------
    async def fetch(
        self,
        url: str,
        meta: Optional[dict] = None,
        auth_handler: Optional[Any] = None,
    ) -> Response:
        """Fetch a URL using Playwright in HTML‑only mode.

        Args:
            url: Target URL.
            meta: Optional metadata dict (use_browser, wait_for, wait_time).
            auth_handler: Optional authentication handler.

        Returns:
            A normalized Response object.
        """
        meta = meta or {}

        use_browser = meta.get("use_browser", True)
        wait_for = meta.get("wait_for")
        wait_time = meta.get("wait_time", 10000)

        # If browser usage is disabled, return an empty Response
        if not use_browser:
            return Response(url, "", 0, {}, None, False, None)

        # Acquire an HTML‑only page
        page = await self.browser_manager.get_page(url, auth_handler=auth_handler)

        try:
            self.logger.debug(f"Playwright GET: {url}")
            response = await page.goto(url, wait_until="domcontentloaded")

            # No response → still return a Response object
            if not response:
                if auth_handler is None:
                    await page.close()

                return Response(
                    url=url,
                    html="",
                    status=0,
                    headers={},
                    request=None,
                    from_browser=True,
                    browser_page=page if auth_handler else None,
                )

            # Extract HTML
            try:
                html = await page.evaluate("document.documentElement.outerHTML")
                body = html.encode("utf-8")
            except Exception:
                try:
                    body = await response.body()
                except Exception:
                    try:
                        text = await response.text()
                        body = text.encode("utf-8")
                    except Exception:
                        body = b""

            # Optional wait_for selector
            if wait_for:
                try:
                    await page.wait_for_selector(wait_for, timeout=wait_time)
                except PlaywrightTimeoutError:
                    self.logger.debug(f"wait_for failed: {wait_for}")

            # Close page only if no AuthHandler needs it
            if auth_handler is None:
                await page.close()

            return Response(
                url=response.url,
                html=body.decode("utf-8", errors="ignore"),
                status=response.status,
                headers=response.headers,
                request=None,
                from_browser=True,
                browser_page=page if auth_handler else None,
            )

        except Exception as exc:
            self.logger.error(f"Playwright error on {url}: {exc}")

            try:
                if auth_handler is None:
                    await page.close()
            except Exception:
                pass

            return Response(
                url=url,
                html="",
                status=0,
                headers={},
                request=None,
                from_browser=True,
                browser_page=page if auth_handler else None,
            )
