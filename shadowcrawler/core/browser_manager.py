# shadowcrawler/core/browser_manager.py
# ShadowCrawler v4.1.3 — Browser Manager (FINAL)
#
# Compatible with:
# - UniversalImageSpider (browser_mode)
# - AuthBrowserDemo (FULL context)
# - show_browser=True without warnings
# - Current Engine/run.py
#
# Notes:
#   - Manages Playwright browser contexts, pages, and sessions.
#   - Provides DOM‑FULL and HTML‑only modes for spiders.
#   - Responsible for lifecycle: create → reuse → close pages/contexts.
#   - Does NOT perform crawling logic; spiders and Engine decide navigation.
#   - Does NOT extract data; extractors handle HTML/JSON/media.
#   - Must preserve browser_page when keep_page=True (DOM‑FULL spiders).
#   - Fully compatible with AuthHandlers (login, session persistence).
#   - Safe for checkpointing; no non‑serializable state is stored here.

import os
from urllib.parse import urlparse
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright
from shadowcrawler.logging import get_logger


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


class BrowserManager:
    """
    Browser Manager for ShadowCrawler v4.1.3.

    This manager provides Playwright contexts for spiders that require DOM access
    or HTML‑only crawling, including FULL contexts for authentication flows.

    Responsibilities:
        - Create and reuse browser contexts per domain.
        - Provide HTML‑only or FULL contexts depending on spider mode.
        - Inject stealth scripts to avoid automation detection.
        - Load sessions and cookies for AuthHandlers.
        - Block heavy resources in HTML‑only mode.
        - Manage page lifecycle and safe browser shutdown.
    """
    
    def __init__(
        self,
        headless: bool = True,
        global_headers: Optional[Dict[str, str]] = None,
        global_cookies: Optional[Dict[str, str]] = None,
        proxy: Optional[Dict[str, Any]] = None,
        show_browser: bool = False,
    ) -> None:

        self.show_browser = show_browser
        self.headless = not show_browser

        self.global_headers = global_headers or {}
        self.global_cookies = global_cookies or {}
        self.proxy = proxy

        self.play = None
        self.browser = None

        # Contexts reused per domain
        self.html_contexts: Dict[str, Any] = {}

        # Service context (used for login flows)
        self.service_context: Optional[Any] = None

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
        domain: Optional[str],
        auth_handler: Optional[Any],
    ) -> Any:
        """Create a new browser context with stealth and optional auth."""

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

        if self.global_headers:
            await ctx.set_extra_http_headers(self.global_headers)

        if self.global_cookies and domain:
            cookies = [
                {"name": k, "value": v, "domain": domain, "path": "/"}
                for k, v in self.global_cookies.items()
            ]
            try:
                await ctx.add_cookies(cookies)
            except Exception:
                pass

        if auth_handler:
            try:
                await auth_handler.load_session(ctx)
            except Exception as exc:
                self.logger.error(f"Auth load failed: {exc}")

        # Block heavy resources in HTML-only mode
        if html_only:
            async def block(route, req):
                if req.resource_type in ["image", "media", "video", "audio", "font", "stylesheet"]:
                    return await route.abort()
                return await route.continue_()
            await ctx.route("**/*", block)

        return ctx

    # ------------------------------------------------------------
    async def get_page(
        self,
        url: str,
        auth_handler: Optional[Any] = None,
        browser_mode: str = "html",
    ) -> Any:
        """Return a new page from a reused context (per domain)."""

        domain = urlparse(url).netloc

        # FULL context if an AuthHandler is present
        if auth_handler is not None:
            html_only = False
        else:
            html_only = (browser_mode == "html")

        # Reuse contexts per domain
        if domain not in self.html_contexts:
            self.html_contexts[domain] = await self._create_context(
                html_only=html_only,
                domain=domain,
                auth_handler=auth_handler,
            )

        return await self.html_contexts[domain].new_page()

    # ------------------------------------------------------------
    async def get_service_context(self, auth_handler: Optional[Any] = None) -> Any:
        """Return a dedicated context for login flows or service operations."""

        if self.service_context:
            return self.service_context

        domain = None

        if auth_handler and hasattr(auth_handler, "domain"):
            domain = auth_handler.domain

        if not domain and self.html_contexts:
            domain = next(iter(self.html_contexts.keys()))

        if not domain:
            domain = "unknown"

        ctx = await self._create_context(
            html_only=False,
            domain=domain,
            auth_handler=auth_handler,
        )

        self.service_context = ctx
        return ctx

    # ------------------------------------------------------------
    async def close(self) -> None:
        """
        Always close Playwright to avoid open pipes.
        Close Chromium only when show_browser=False.
        """

        self.logger.info("Closing Playwright browser")

        # Close all domain contexts
        for ctx in self.html_contexts.values():
            try:
                await ctx.close()
            except Exception:
                pass

        # Close service context
        if self.service_context:
            try:
                await self.service_context.close()
            except Exception:
                pass

        # Close Chromium ONLY if the browser window is not shown
        if not self.show_browser:
            if self.browser:
                try:
                    await self.browser.close()
                except Exception:
                    pass

        # ALWAYS stop Playwright (prevents warnings)
        if self.play:
            try:
                await self.play.stop()
            except Exception:
                pass

        self.logger.debug("Browser closed successfully")
