# shadowcrawler/fetcher/playwright_fetcher.py
# ShadowCrawler v4.1.3 — Playwright Fetcher (DOM‑FULL compatible)

from typing import Any, Optional

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from shadowcrawler.logging import get_logger
from shadowcrawler.models.response import Response


class PlaywrightFetcher:
    """Playwright fetcher for ShadowCrawler v4.1.3.

    This fetcher is used for spiders that require DOM access or HTML‑only crawling.

    Responsibilities:
        - Fetch HTML using Playwright contexts.
        - Respect spider-defined browser_mode ("html" or "full").
        - KEEP browser_page alive for DOM‑FULL spiders (UniversalImage).
        - Close pages only when explicitly requested.
    """

    def __init__(self, browser_manager: Any) -> None:
        self.browser_manager = browser_manager
        self.logger = get_logger("browser")
        
    # ------------------------------------------------------------
    # FETCH (DOM-FULL + JS-DYNAMIC compatible)
    # ------------------------------------------------------------
    async def fetch(
        self,
        url: str,
        meta: Optional[dict] = None,
        auth_handler: Optional[Any] = None,
    ) -> Response:
        meta = meta or {}

        use_browser = meta.get("use_browser", True)
        wait_for = meta.get("wait_for")
        wait_time = meta.get("wait_time", 10000)

        browser_mode = meta.get("browser_mode", "html")
        keep_page = meta.get("keep_page", True)

        if not use_browser:
            return Response(url, "", 0, {}, None, False, None)

        # Acquire page
        page = await self.browser_manager.get_page(
            url,
            auth_handler=auth_handler,
            browser_mode=browser_mode,
        )

        try:
            self.logger.debug(f"Playwright GET: {url}")

            # ⭐ Espera real para JS dinámico
            response = await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(500)

            if not response:
                if not keep_page:
                    await page.close()

                return Response(
                    url=url,
                    html="",
                    status=0,
                    headers={},
                    request=None,
                    from_browser=True,
                    browser_page=page if keep_page else None,
                )

            # ⭐ Recaptura del DOM después del JS
            try:
                html = await page.content()
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

            if not keep_page:
                await page.close()

            # ⭐ Construimos el Response y lo guardamos en la página
            page.response_obj = Response(
                url=response.url if response else url,
                html=body.decode("utf-8", errors="ignore"),
                status=response.status if response else 0,
                headers=response.headers if response else {},
                request=None,
                from_browser=True,
                browser_page=page if keep_page else None,
            )
            
            # ⭐ Devolvemos el Response real
            return page.response_obj

        except Exception as exc:
            self.logger.error(f"Playwright error on {url}: {exc}")

            try:
                if not keep_page:
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
                browser_page=page if keep_page else None,
            )
