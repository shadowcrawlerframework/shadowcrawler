# shadowcrawler/auth/authdemo/AuthDemoAuth.py
# ShadowCrawler v4.1.3 — HTTP Auth Handler (RequestsFetcher)
#
# DISCLAIMER:
# This authentication handler is provided **for demonstration and educational purposes only**.
# It simulates a login flow using a simple POST request and a fake session cookie.
#
# This example is intentionally minimal and NOT intended for production use.
# Real-world authentication flows require robust, site-specific implementations.
#
# Demonstrates:
# - Simple POST-based login
# - Cookie persistence
# - Session restoration
# - Authentication without Playwright

import json
from typing import Any
from shadowcrawler.auth.base import AuthHandlerBase


class AuthDemoAuth(AuthHandlerBase):
    """
    HTTP authentication handler for httpbin.org.

    This handler simulates a login by sending a POST request
    and storing a fake session cookie. It demonstrates how
    ShadowCrawler handles authentication without browser context.
    """

    LOGIN_URL: str = "https://httpbin.org/post"

    # ------------------------------------------------------------
    # CHECK IF LOGIN IS REQUIRED
    # ------------------------------------------------------------
    def is_login_required(self, session: Any) -> bool:
        """
        Determines whether the user is already logged in.

        For this demo:
            - If the session contains our fake cookie, we consider it logged in.
        """
        return "session" not in session.cookies

    # ------------------------------------------------------------
    # PERFORM LOGIN
    # ------------------------------------------------------------
    def login(self, session: Any, **kwargs: Any) -> bool:
        """
        Perform a simple POST login to httpbin.org.

        This is a minimal example:
            - Send POST with username/password
            - Save a fake cookie
            - Persist cookie to disk
        """
        username = kwargs.get("username", "allan")
        password = kwargs.get("password", "1234")

        payload = {"username": username, "password": password}

        print("🔐 Sending login POST to:", self.LOGIN_URL)
        resp = session.post(self.LOGIN_URL, json=payload)

        if resp.status_code != 200:
            print("❌ Login failed:", resp.status_code)
            return False

        # Fake session cookie for demonstration
        session_cookie = f"{username}_{password}"
        print("✅ Login OK, saving cookie:", session_cookie)

        # Save cookies in memory
        self.cookies = {"session": session_cookie}

        # Persist cookies to disk
        self.save_session()

        # Inject into session immediately
        session.cookies.update(self.cookies)

        return True

    # ------------------------------------------------------------
    # LOAD SESSION (NO ARGUMENTS)
    # ------------------------------------------------------------
    def load_session(self) -> None:
        """
        Load cookies from disk into memory.

        AuthHandlerBase handles reading the JSON file.
        """
        super().load_session()

    # ------------------------------------------------------------
    # INJECT COOKIES INTO SESSION
    # ------------------------------------------------------------
    def inject(self, session: Any) -> None:
        """
        Inject stored cookies into the requests.Session.

        This is called automatically by the engine when needed.
        """
        if self.cookies:
            session.cookies.update(self.cookies)
