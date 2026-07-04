# shadowcrawler/auth/base_auth.py
# ShadowCrawler v4.1.3 — Base Authentication Handler (Browser / Playwright)
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# This software is licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Base authentication handler for browser-based spiders in ShadowCrawler.

This module defines BaseAuthHandler, the universal contract for Playwright-based
authentication handlers. Each site-specific handler must implement:

    - Detecting when login is required.
    - Performing the login flow.
    - Loading persistent session state (cookies/storage).
    - Saving persistent session state.
    - Optionally enhancing pages before navigation.

This class does NOT implement login logic.  
Each site must provide its own subclass.
"""

from abc import ABC, abstractmethod
from typing import Any
from playwright.async_api import Page, BrowserContext

from shadowcrawler.logging import get_logger


class BaseAuthHandler(ABC):
    """Abstract base class for browser authentication handlers.

    Responsibilities:
        - Define a consistent interface for authentication handlers.
        - Detect when login is required.
        - Execute login steps.
        - Load and save persistent session state (cookies/storage).
        - Optionally modify pages before navigation.

    Notes:
        - This class does NOT implement login logic.
        - Each site must provide its own handler subclass.
    """

    def __init__(self) -> None:
        """Initialize the base authentication handler."""
        self.logger = get_logger("auth")

    # ------------------------------------------------------------
    # LOGIN REQUIRED?
    # ------------------------------------------------------------
    @abstractmethod
    async def is_login_required(self, page: Page) -> bool:
        """Determine whether the current page requires login.

        Args:
            page: Playwright Page instance.

        Returns:
            True if login is required, False otherwise.

        Examples of login-required signals:
            - Redirect to a login page.
            - Visible login form.
            - "Please sign in" messages.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # PERFORM LOGIN
    # ------------------------------------------------------------
    @abstractmethod
    async def perform_login(self, page: Page) -> bool:
        """Execute the login steps on the given page.

        Args:
            page: Playwright Page instance.

        Returns:
            True if login succeeded, False otherwise.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------------
    @abstractmethod
    async def load_session(self, context: BrowserContext) -> None:
        """Load cookies or storage state into the browser context.

        Args:
            context: Playwright BrowserContext instance.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # SAVE SESSION
    # ------------------------------------------------------------
    @abstractmethod
    async def save_session(self, context: BrowserContext) -> None:
        """Save cookies or storage state from the browser context.

        Args:
            context: Playwright BrowserContext instance.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # ENHANCE PAGE (OPTIONAL)
    # ------------------------------------------------------------
    async def enhance_page(self, page: Page) -> None:
        """Optional hook to modify the page before navigation.

        Args:
            page: Playwright Page instance.

        Examples:
            - Inject headers.
            - Add cookies.
            - Run custom JavaScript.

        Default:
            No operation.
        """
        self.logger.debug("enhance_page(): no-op")
        return
