# shadowcrawler/core/browser_manager.py
# ShadowCrawler v4.1.0 — Browser Manager
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
BrowserManager for ShadowCrawler v4.1.0.

Responsibilities:
    - Provide HTML‑only Playwright contexts for crawling (resource‑blocked).
    - Provide FULL Playwright contexts for downloading (media-enabled).
    - Inject stealth JS to reduce bot detection.
    - Load global headers/cookies.
    - Load auth handler sessions when available.
    - Reuse contexts per domain for efficiency.
    - Support storage_state‑based session restoration.
"""

import os
from urllib.parse import urlparse
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright
from shadowcrawler.logging import get_logger


# ------------------------------------------------------------
# Stealth Script (anti‑bot fingerprint smoothing)
# ------------------------------------------------------------
STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
Object.defineProperty(navigator, 'languages', { get: () => ['es-MX','es','en-US'] });

const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(p) {
  if (p === 37445) return 'Intel Inc.';
  if (p === 37446) return 'Intel Iris OpenGL';
  return getParameter.call(this, p);
};

HTMLCanvasElement.prototype.toDataURL = () =>
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB";

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = p =>
  p.name === 'notifications'
    ? Promise.resolve({ state: Notification.permission })
    : originalQuery(p);

Object.defineProperty(window.screen, 'width', { get: () => 1920 });
Object.defineProperty(window.screen, 'height', { get: () => 1080 });
Object.defineProperty(window.screen, 'availWidth', { get: () => 1920 });
Object.defineProperty(window.screen, 'availHeight', { get: () => 1080 });

Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
"""


# ------------------------------------------------------------
# BrowserManager
# ------------------------------------------------------------
class BrowserManager:
    """Playwright browser lifecycle and context manager for ShadowCrawler.

    Args:
        headless: Whether to run Chromium in headless mode.
        global_headers: Optional global HTTP headers.
        global_cookies: Optional global cookies.
        proxy: Optional proxy configuration.
        show_browser: If True, forces visible browser window.
    """

    def __init__(
        self,
        headless: bool = True,
        global_headers: Optional[Dict[str, str]] = None,
        global_cookies: Optional[Dict[str, str]] = None,
        proxy: Optional[Dict[str, Any]] = None,
        show_browser: bool = False,
    ) -> None:
        # show_browser overrides headless
        self.headless = not show_browser

        self.global_headers = global_headers or {}
        self.global_cookies = global_cookies or {}
        self.proxy = proxy

        self.play = None
        self.browser = None

        self.html_contexts: Dict[str, Any] = {}      # Per-domain HTML-only contexts
        self.service_context: Optional[Any] = None   # FULL context for downloader

        self.logger = get_logger("browser")

    # ------------------------------------------------------------
    async def start(self) -> None:
        """Start Playwright and launch Chromium."""
        self.logger.info("Starting Playwright browser")

        self.play = await async_playwright().start()

        args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        }

        if self.proxy:
            args["proxy"] = self.proxy

        self.browser = await self.play.chromium.launch(**args)
        self.logger.debug("Browser initialized")

    # ------------------------------------------------------------
    async def _create_context(
        self,
        html_only: bool,
        domain: Optional[str] = None,
        auth_handler: Optional[Any] = None,
    ) -> Any:
        """Create a new Playwright context.

        Args:
            html_only: If True, block images/media/fonts/etc.
            domain: Domain for cookie scoping.
            auth_handler: Optional auth handler with load_session(ctx) or storage_path.

        Returns:
            A Playwright BrowserContext instance.
        """
        storage_state = None
        if auth_handler and hasattr(auth_handler, "storage_path"):
            if os.path.exists(auth_handler.storage_path):
                storage_state = auth_handler.storage_path

        ctx = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="es-MX",
            color_scheme="dark",
            storage_state=storage_state,
        )

        await ctx.add_init_script(STEALTH_JS)

        # Global headers
        if self.global_headers:
            await ctx.set_extra_http_headers(self.global_headers)

        # Global cookies
        if self.global_cookies and domain:
            cookies = [
                {"name": k, "value": v, "domain": domain, "path": "/"}
                for k, v in self.global_cookies.items()
            ]
            try:
                await ctx.add_cookies(cookies)
            except Exception:
                pass

        # Auth handler session loading
        if auth_handler:
            try:
                await auth_handler.load_session(ctx)
            except Exception as exc:
                self.logger.error(f"Auth load failed: {exc}")

        # Resource blocking for HTML‑only mode
        if html_only:
            async def block(route, req):
                if req.resource_type in ["image", "media", "video", "audio", "font", "stylesheet"]:
                    return await route.abort()
                return await route.continue_()
            await ctx.route("**/*", block)

        return ctx

    # ------------------------------------------------------------
    async def get_page(self, url: str, auth_handler: Optional[Any] = None) -> Any:
        """Return a new page from a per-domain HTML‑only context."""
        domain = urlparse(url).netloc
        if domain not in self.html_contexts:
            self.html_contexts[domain] = await self._create_context(
                html_only=(auth_handler is None),  # FULL if auth handler exists
                domain=domain,
                auth_handler=auth_handler,
            )
        return await self.html_contexts[domain].new_page()

    # ------------------------------------------------------------
    async def get_service_context(self, auth_handler: Optional[Any] = None) -> Any:
        """Return a FULL context for downloading (media-enabled)."""
        if self.service_context:
            return self.service_context

        domain = None
        if auth_handler and hasattr(auth_handler, "domain"):
            domain = auth_handler.domain

        if not domain:
            domain = "poringa.net"

        self.logger.info(f"Creating FULL service context for domain: {domain}")

        ctx = await self._create_context(
            html_only=False,
            domain=domain,
            auth_handler=auth_handler,
        )

        self.service_context = ctx
        return ctx

    # ------------------------------------------------------------
    async def close(self) -> None:
        """Close all contexts and the browser cleanly."""
        self.logger.info("Closing Playwright browser")

        for ctx in self.html_contexts.values():
            try:
                await ctx.close()
            except Exception:
                pass

        if self.service_context:
            try:
                await self.service_context.close()
            except Exception:
                pass

        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass

        if self.play:
            try:
                await self.play.stop()
            except Exception:
                pass

        self.logger.debug("Browser closed successfully")
