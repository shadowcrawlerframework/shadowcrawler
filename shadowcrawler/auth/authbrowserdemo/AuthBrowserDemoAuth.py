# shadowcrawler/auth/authbrowserdemo/AuthBrowserDemoAuth.py
# ShadowCrawler v4.1.3 — Auth Browser Demo Handler (Tumblr-style)
#
# DISCLAIMER:
# This authentication handler is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs browser-based authentication using Playwright
# with a FULL browser context, persistent storage_state, and manual login flow.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world authentication flows require robust, site-specific implementations.
#
# Demonstrates:
# - FULL Playwright browser context
# - Persistent cookies + localStorage
# - Session restoration via storage_state
# - Manual login flow handled entirely by the user
# - Clean separation between spider, auth handler, and extractor

import os
import json
from typing import Any
from shadowcrawler.logging import get_logger


class AuthBrowserDemoAuthHandler:
    """
    Authentication handler for the AuthBrowserDemo spider.

    This handler demonstrates how ShadowCrawler manages browser-based
    authentication using Playwright. It restores full storage_state,
    loads localStorage, and saves the session after manual login.

    Responsibilities:
        - Load and restore full storage_state (cookies + localStorage).
        - Save full session after manual login.
        - Provide consistent FULL browser context behavior.
        - Avoid relying on request_meta() or requires_login.
    """

    def __init__(self) -> None:
        self.logger = get_logger("auth")
        self.domain = "demoqa.com"

        self.storage_path = os.path.expanduser(
            "~/.shadowcrawler/sessions/authbrowserdemo.json"
        )

    # ------------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------------
    async def is_login_required(self, page: Any) -> bool:
        """
        Determines whether the user is already logged in.
        For DemoQA, the profile page contains #userName-value when logged in.
        """
        try:
            el = await page.query_selector("#userName-value")
            return el is None
        except Exception:
            return True

    # ------------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------------
    async def load_session(self, context: Any) -> None:
        if not os.path.exists(self.storage_path):
            self.logger.debug("No previous session found for AuthBrowserDemo.")
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                state = json.load(f)

            await context.set_storage_state(state)

            if "localStorage" in state:
                await context.add_init_script(
                    f"""
                    const data = {json.dumps(state["localStorage"])};
                    for (const key in data) {{
                        localStorage.setItem(key, data[key]);
                    }}
                    """
                )

            self.logger.info("AuthBrowserDemo session restored successfully.")

        except Exception as exc:
            self.logger.error(f"Error loading AuthBrowserDemo session: {exc}")

    # ------------------------------------------------------------
    # SAVE SESSION
    # ------------------------------------------------------------
    async def save_session(self, context: Any, page: Any) -> None:
        try:
            state = await context.storage_state()
            local = await page.evaluate("() => ({...localStorage})")
            state["localStorage"] = local

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)

            self.logger.info(
                f"AuthBrowserDemo session saved to {self.storage_path}"
            )

        except Exception as exc:
            self.logger.error(f"Error saving AuthBrowserDemo session: {exc}")

    # ------------------------------------------------------------
    # MANUAL LOGIN
    # ------------------------------------------------------------
    async def perform_login(self, page: Any) -> None:
        print("🔐 Please log in manually in the browser window…")
        print("Press ENTER here when you are done.")
        input("")

        print("✅ Login confirmed.")
        await self.save_session(page.context, page)
