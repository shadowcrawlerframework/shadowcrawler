# shadowcrawler/auth/authdemo/AuthDemoAuth.py
# ShadowCrawler v4.1.0 — Example HTTP Auth Handler (RequestsFetcher)
#
# This file is provided **as an example only**.
# It demonstrates how to implement a simple HTTP-based login flow.
# It is NOT intended for production use.
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Example HTTP authentication handler for httpbin.org.

This module demonstrates:
    - Sending a POST login request.
    - Storing a fake session cookie.
    - Persisting cookies using AuthHandlerBase.
    - Integrating with RequestsFetcher.

Notes:
    - This handler is intentionally simple and provided **as-is**.
    - It is meant for educational and demonstration purposes.
    - Real-world sites require robust, site-specific implementations.
"""

import json
from typing import Any

from shadowcrawler.auth.base import AuthHandlerBase


class AuthDemoAuth(AuthHandlerBase):
    """Example HTTP authentication handler for httpbin.org.

    Responsibilities:
        - Send a POST request to simulate login.
        - Store a fake session cookie.
        - Persist cookies using AuthHandlerBase.

    This class is intentionally minimal and not production-ready.
    """

    LOGIN_URL: str = "https://httpbin.org/post"

    # ------------------------------------------------------------
    # PERFORM LOGIN
    # ------------------------------------------------------------
    def login(self, session: Any, **kwargs: Any) -> bool:
        """Perform a simple POST login to httpbin.org.

        Args:
            session: A requests.Session instance.
            **kwargs: Optional username/password overrides.

        Returns:
            True if login succeeded, False otherwise.
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

        self.cookies = {"session": session_cookie}
        self.save_session()

        return True

    # ------------------------------------------------------------
    # INJECT COOKIES
    # ------------------------------------------------------------
    def inject(self, session: Any) -> None:
        """Inject stored cookies into the requests.Session.

        Args:
            session: A requests.Session instance.
        """
        if self.cookies:
            session.cookies.update(self.cookies)
