# tools/manual_login.py
# ShadowCrawler v4.1.3 — Manual Login Utility
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# This tool allows users to manually authenticate into any website using
# a real Playwright browser session. After login, the authenticated
# storage state (cookies + local/session storage) is saved to disk so
# spiders can reuse it for authenticated crawling.
#
# Notes:
#   - Standalone utility; not part of the crawling engine.
#   - Used to generate authenticated Playwright sessions manually.
#   - Does NOT automate login; user performs all actions.
#   - Produces a storage_state JSON file reusable by spiders and AuthHandlers.
#   - Safe for debugging; does not modify engine or spider behavior.
#   - Fully compatible with DOM‑FULL spiders and browser-based AuthHandlers.


"""
ShadowCrawler Manual Login Tool (SC v4)

This tool opens a real browser window (via Playwright) so the user can
log in manually. Once authenticated, the session is saved to a JSON file
that spiders can reuse for authenticated crawling.

Usage:
    python manual_login.py --url https://example.com/login --output session.json

Notes:
    - This tool does NOT automate login.
    - The user performs the login manually.
    - After login, press ENTER in the console to save the session.
"""

import os
import argparse
from typing import Optional
from playwright.sync_api import sync_playwright


DEFAULT_SESSION_DIR = os.path.expanduser("~/.shadowcrawler/sessions")


def manual_login(login_url: str, output_file: str) -> None:
    """Open a browser window, allow manual login, then save session state.

    Parameters:
        login_url (str): URL of the login page.
        output_file (str): Path where the session JSON will be saved.
    """

    # Ensure session directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print("\n[Manual Login] Starting Playwright browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()

        print(f"\nOpening login page:\n  {login_url}")
        page.goto(login_url, wait_until="networkidle")

        print("\nPlease log in manually in the browser window.")
        print("Once you are fully logged in (e.g., dashboard/profile visible),")
        print("return to this console and press ENTER to save the session.")
        input()

        # Give the page a moment to settle
        page.wait_for_timeout(2000)

        # Save session state
        context.storage_state(path=output_file)

        print("\n[Manual Login] Session saved to:")
        print(f"  {output_file}")

        browser.close()
        print("\nBrowser closed. Manual login complete.\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ShadowCrawler Manual Login Tool (SC v4)"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Login page URL (e.g., https://example.com/login)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(DEFAULT_SESSION_DIR, "session.json"),
        help=f"Output session file (default: {DEFAULT_SESSION_DIR}/session.json)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    manual_login(args.url, args.output)
