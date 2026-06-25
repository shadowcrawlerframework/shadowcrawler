# shadowcrawler/auth/authbrowserdemo/AuthBrowserDemoAuth.py
# ShadowCrawler v4.1.1 — Example Browser Auth Handler (Playwright)
#
# This file is provided **as an example only**.
# It demonstrates how to implement a manual login flow using Playwright.
# It is NOT intended for production use.
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Example authentication handler for demoqa.com.

This module demonstrates:
    - Detecting when login is required.
    - Waiting for the user to manually log in.
    - Persisting browser storage_state to disk.
    - Integrating with BrowserManager and PlaywrightFetcher.

Notes:
    - This handler is intentionally simple and provided **as-is**.
    - It is meant for educational and demonstration purposes.
    - Real-world sites require robust, site-specific implementations.
"""

import asyncio
from typing import Any
from playwright.async_api import Page, BrowserContext

from shadowcrawler.logging import get_logger


class AuthBrowserDemoAuthHandler:
    """Example Playwright-based authentication handler for demoqa.com.

    Responsibilities:
        - Detect login requirement on demoqa.com.
        - Allow the user to manually log in.
        - Persist storage_state to disk.
        - Demonstrate the BaseAuthHandler contract.

    This class is intentionally minimal and not production-ready.
    """

    domain: str = "demoqa.com"
    storage_path: str = "auth_demoqa_session.json"

    def __init__(self) -> None:
        """Initialize the demo authentication handler."""
        self.logger = get_logger("auth")

    # ------------------------------------------------------------
    # LOGIN REQUIRED?
    # ------------------------------------------------------------
    async def is_login_required(self, page: Page) -> bool:
        """Determine whether the current page requires login.

        Args:
            page: Playwright Page instance.

        Returns:
            True if login is required, False otherwise.
        """
        url = page.url

        # Special case: demoqa shows a "Go To Profile" button even on /login
        if "/login" in url:
            try:
                goto_btn = page.get_by_role("button", name="Go To Profile")
                if await goto_btn.is_visible():
                    return False
            except Exception:
                pass

            try:
                msg = page.get_by_text("You are already logged in")
                if await msg.is_visible():
                    return False
            except Exception:
                pass

            return True

        # If on /profile, check if username is present
        if "/profile" in url:
            try:
                username = await page.locator("#userName-value").inner_text()
                if username.strip():
                    return False
            except Exception:
                pass
            return True

        # Any other page → keep browser open until login is done
        return True

    # ------------------------------------------------------------
    # PERFORM LOGIN (MANUAL)
    # ------------------------------------------------------------
    async def perform_login(self, page: Page) -> None:
        """Wait for the user to manually complete the login flow.

        Args:
            page: Playwright Page instance.
        """
        print("🔐 Please complete the login manually in the browser window…")
        print("When you are fully logged in, press ENTER here to continue.")

        # ⭐ FIX: Mantener el navegador abierto hasta que el usuario confirme
        input()

        # Pequeña pausa para que Playwright estabilice el DOM
        await page.wait_for_timeout(1500)

        print("✅ Login confirmed, continuing…")

    # ------------------------------------------------------------
    # SAVE SESSION
    # ------------------------------------------------------------
    async def save_session(self, context: BrowserContext) -> None:
        """Persist storage_state to disk.

        Args:
            context: Playwright BrowserContext instance.
        """
        try:
            await context.storage_state(path=self.storage_path)
            self.logger.info("Saved session storage_state to %s", self.storage_path)
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to save session: %s", exc)

    # ------------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------------
    async def load_session(self, context: BrowserContext) -> None:
        """Load session state into the browser context.

        Notes:
            BrowserManager already loads storage_state when creating the context.
        """
        return
