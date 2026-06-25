# shadowcrawler/auth/base.py
# ShadowCrawler v4.1.0 — Base Auth Handler for HTTP (RequestsFetcher)
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# This software is licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Base authentication handler for HTTP-based spiders in ShadowCrawler.

This module provides:
    - A minimal, extensible interface for HTTP authentication.
    - Cookie management for requests.Session.
    - Persistent session storage on disk.
    - Hooks for site-specific login and cookie injection.

This class is used by RequestsFetcher and is intended to be subclassed
by spiders that require login or session persistence.
"""

import os
import json
from typing import Any, Dict, Optional

from shadowcrawler.logging import get_logger


class AuthHandlerBase:
    """Base class for HTTP authentication handlers.

    Responsibilities:
        - Provide a simple interface for HTTP-based authentication.
        - Manage cookies for requests.Session.
        - Persist session cookies to disk.
        - Allow site-specific handlers to implement login() and inject().

    Attributes:
        spider_handle: Unique identifier for the spider instance.
        cookies: Dictionary of session cookies.
        session_file: Path to the JSON file storing cookies.
    """

    SESSION_DIR: str = os.path.expanduser("~/.shadowcrawler/sessions")

    def __init__(self, spider_handle: Optional[str] = None) -> None:
        """Initialize a new AuthHandlerBase instance.

        Args:
            spider_handle: Optional unique identifier for the spider.
                Used to determine the cookie storage file.
        """
        self.logger = get_logger("auth")
        self.spider_handle: str = spider_handle or "default"
        self.cookies: Dict[str, Any] = {}

        os.makedirs(self.SESSION_DIR, exist_ok=True)
        self.session_file: str = os.path.join(
            self.SESSION_DIR, f"{self.spider_handle}.json"
        )

        self.load_session()

    # ------------------------------------------------------------
    # LOGIN (site-specific)
    # ------------------------------------------------------------
    def login(self, session: Any, **kwargs: Any) -> None:
        """Perform login steps for the target site.

        This method must be implemented by subclasses.

        Args:
            session: A requests.Session instance.
            **kwargs: Additional parameters for site-specific login logic.

        Raises:
            NotImplementedError: Always, unless overridden by subclass.
        """
        raise NotImplementedError("login() must be implemented by subclass")

    # ------------------------------------------------------------
    # INJECT COOKIES INTO SESSION
    # ------------------------------------------------------------
    def inject(self, session: Any) -> None:
        """Inject stored cookies into a requests.Session.

        Args:
            session: A requests.Session instance.
        """
        if self.cookies:
            session.cookies.update(self.cookies)

    # ------------------------------------------------------------
    # LOAD SESSION FROM DISK
    # ------------------------------------------------------------
    def load_session(self) -> None:
        """Load session cookies from disk if available."""
        if not os.path.exists(self.session_file):
            return

        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                self.cookies = json.load(f)
            self.logger.info("Loaded session cookies from %s", self.session_file)
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to load session: %s", exc)

    # ------------------------------------------------------------
    # SAVE SESSION TO DISK
    # ------------------------------------------------------------
    def save_session(self) -> None:
        """Persist session cookies to disk."""
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.cookies, f, indent=2)
            self.logger.info("Saved session cookies to %s", self.session_file)
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to save session: %s", exc)
