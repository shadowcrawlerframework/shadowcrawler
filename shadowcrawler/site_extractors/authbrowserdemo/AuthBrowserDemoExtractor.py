# shadowcrawler/site_extractors/authbrowserdemo/AuthBrowserDemoExtractor.py
# ShadowCrawler v4.1.3 — Robust Auth Browser Demo Extractor
#
# DISCLAIMER:
# This extractor is provided **for demonstration and educational purposes only**.
# It shows how ShadowCrawler performs browser-based extraction using Playwright
# after a manual authentication flow, waiting for React to mount and reading
# UI elements directly from the rendered DOM.
#
# This example is intentionally simple and NOT intended for production use.
# Real-world extractors require robust, site-specific parsing logic.
#
# Demonstrates:
# - Waiting for React to mount
# - Extracting username, email, avatar, and UI elements
# - Graceful fallback when elements are missing
# - Clean Playwright-based DOM extraction

from typing import Any, Dict
from shadowcrawler.logging import get_logger


class AuthBrowserDemoExtractor:
    """
    Robust extractor for the AuthBrowserDemo spider.

    This extractor demonstrates how ShadowCrawler uses Playwright to
    extract data from a fully rendered React page. It waits for the
    profile UI to mount, reads username/email/avatar elements, and
    provides clear debug logs with graceful fallback behavior.

    Responsibilities:
        - Wait for React to fully mount the profile page.
        - Extract username, email, avatar, and UI elements.
        - Provide clear debug logs.
        - Fail gracefully with fallback data.
    """

    def __init__(self, spider_handle: str) -> None:
        self.handle = spider_handle
        self.logger = get_logger("extractor")

    # ------------------------------------------------------------
    # MAIN EXTRACT METHOD
    # ------------------------------------------------------------
    async def extract(self, page: Any, url: str) -> Dict[str, Any]:
        self.logger.info(f"Running AuthBrowserDemoExtractor on: {url}")

        # ------------------------------------------------------------
        # 1) Wait for React to mount the profile page
        # ------------------------------------------------------------
        try:
            await page.wait_for_selector("#userName-value", timeout=8000)
            await page.wait_for_selector("#userEmail-value", timeout=8000)
            self.logger.debug("Profile elements detected.")
        except Exception:
            self.logger.warning(
                "React did not mount profile elements within timeout."
            )

        # ------------------------------------------------------------
        # 2) Extract username
        # ------------------------------------------------------------
        try:
            username_el = await page.query_selector("#userName-value")
            username = await username_el.inner_text() if username_el else None
            if username:
                self.logger.debug(f"Username extracted: {username}")
            else:
                self.logger.debug("Username not found on profile page.")
        except Exception:
            username = None
            self.logger.debug("Error extracting username.")

        # ------------------------------------------------------------
        # 3) Extract email
        # ------------------------------------------------------------
        try:
            email_el = await page.query_selector("#userEmail-value")
            email = await email_el.inner_text() if email_el else None
            if email:
                self.logger.debug(f"Email extracted: {email}")
            else:
                self.logger.debug("Email not found on profile page.")
        except Exception:
            email = None
            self.logger.debug("Error extracting email.")

        # ------------------------------------------------------------
        # 4) Extract avatar (if present)
        # ------------------------------------------------------------
        try:
            avatar_el = await page.query_selector("img[src*='profile']")
            avatar_url = await avatar_el.get_attribute("src") if avatar_el else None
            if avatar_url:
                self.logger.debug(f"Avatar extracted: {avatar_url}")
            else:
                self.logger.debug("Avatar not found.")
        except Exception:
            avatar_url = None
            self.logger.debug("Error extracting avatar.")

        # ------------------------------------------------------------
        # 5) Extract logout button (optional)
        # ------------------------------------------------------------
        try:
            logout_el = await page.query_selector("#submit")
            logout_text = await logout_el.inner_text() if logout_el else None
            if logout_text:
                self.logger.debug(f"Logout button detected: {logout_text}")
            else:
                self.logger.debug("Logout button not found.")
        except Exception:
            logout_text = None
            self.logger.debug("Error extracting logout button.")

        # ------------------------------------------------------------
        # 6) Final data structure
        # ------------------------------------------------------------
        data = {
            "url": url,
            "username": username,
            "email": email,
            "avatar_url": avatar_url,
            "logout_button": logout_text,
            "react_loaded": username is not None or email is not None,
        }

        return {
            "data": data,
            "media": [],      # No media extraction in this demo
            "links": [],
            "next_pages": [],
        }
