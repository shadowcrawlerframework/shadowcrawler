# shadowcrawler/cli/commands/auth.py
# ShadowCrawler v4.1.1 — Auth Management Commands
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI interface for managing authentication configuration and testing
authentication handlers.

This module provides:
    - Listing configured auth entries.
    - Showing auth configuration for a site.
    - Setting username/password/session for a site.
    - Clearing auth configuration.
    - Dry-run testing of authentication handler classes.

These commands operate on the global ShadowCrawler configuration file.
"""

import os
import sys
import importlib
import inspect
import json
from typing import Any, Dict

from shadowcrawler.auth.base_auth import BaseAuthHandler
from shadowcrawler.cli.commands.config import load_config, save_config


# ------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------
class Colors:
    """ANSI color escape codes for CLI output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREY = "\033[90m"
    RESET = "\033[0m"


def color(text: str, c: str, enabled: bool = True) -> str:
    """Apply ANSI color to text if enabled.

    Args:
        text: The text to colorize.
        c: ANSI color code.
        enabled: Whether to apply color.

    Returns:
        Colored text or original text.
    """
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Config Loader
# ------------------------------------------------------------
def _get_auth_cfg() -> Dict[str, Any]:
    """Load global configuration and ensure the 'auth' section exists.

    Returns:
        The configuration dictionary with an ensured 'auth' section.
    """
    cfg = load_config()
    if "auth" not in cfg:
        cfg["auth"] = {}
    return cfg


# ------------------------------------------------------------
# Main Command Router
# ------------------------------------------------------------
def cmd_auth(args: Any) -> None:
    """Main router for the `shadowcrawler auth` command.

    Args:
        args: Parsed argparse arguments.
    """
    use_color = sys.stdout.isatty()
    cfg = _get_auth_cfg()

    # ------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------
    if args.action == "list":
        print(color("\nConfigured auth entries:\n", Colors.BLUE, use_color))

        if not cfg["auth"]:
            print(color("  (none)", Colors.GREY, use_color))
            return

        for site, data in cfg["auth"].items():
            has_user = bool(data.get("username"))
            has_session = bool(data.get("session_path"))
            print(
                f"  {color(site, Colors.GREEN, use_color)}"
                f"  — user: {color('yes' if has_user else 'no', Colors.YELLOW, use_color)}"
                f"  — session: {color('yes' if has_session else 'no', Colors.YELLOW, use_color)}"
            )
        return

    # ------------------------------------------------------------
    # SHOW
    # ------------------------------------------------------------
    if args.action == "show":
        site = args.site
        data = cfg["auth"].get(site)

        if not data:
            print(color(f"No auth config for site: {site}", Colors.RED, use_color))
            return

        print(color(f"\nAuth config for '{site}':", Colors.BLUE, use_color))
        print(json.dumps(data, indent=2))
        return

    # ------------------------------------------------------------
    # SET
    # ------------------------------------------------------------
    if args.action == "set":
        site = args.site
        entry = cfg["auth"].get(site, {})

        if args.username:
            entry["username"] = args.username
        if args.password:
            entry["password"] = args.password
        if args.session:
            entry["session_path"] = args.session
        if args.auto_login is not None:
            entry["auto_login"] = args.auto_login

        cfg["auth"][site] = entry
        save_config(cfg)

        print(color(f"Updated auth config for '{site}'.", Colors.GREEN, use_color))
        return

    # ------------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------------
    if args.action == "clear":
        site = args.site

        if site in cfg["auth"]:
            del cfg["auth"][site]
            save_config(cfg)
            print(color(f"Cleared auth config for '{site}'.", Colors.GREEN, use_color))
        else:
            print(color(f"No auth config for site: {site}", Colors.RED, use_color))
        return

    # ------------------------------------------------------------
    # TEST
    # ------------------------------------------------------------
    if args.action == "test":
        site = args.site
        handler_path = args.handler  # e.g. shadowcrawler.auth.my_auth.MyAuthHandler

        # Import handler
        try:
            module_name, class_name = handler_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            handler_cls = getattr(module, class_name)
        except Exception as exc:  # noqa: BLE001
            print(color(f"Cannot import handler: {handler_path}", Colors.RED, use_color))
            print(color(str(exc), Colors.GREY, use_color))
            return

        # Warn if handler is private
        if "_private" in module_name.lower():
            print(
                color(
                    "[WARN] You are loading a private module (_private).\n"
                    "       Private modules are not supported and may behave differently.",
                    Colors.YELLOW,
                    use_color,
                )
            )

        # Validate handler class
        if not inspect.isclass(handler_cls) or not issubclass(handler_cls, BaseAuthHandler):
            print(color("Handler is not a valid BaseAuthHandler subclass.", Colors.RED, use_color))
            return

        # Display test info
        data = cfg["auth"].get(site, {})
        print(color(f"\nTesting auth handler '{class_name}' for site '{site}'", Colors.BLUE, use_color))
        print(color(f"  username: {'set' if data.get('username') else 'missing'}", Colors.YELLOW, use_color))
        print(color(f"  password: {'set' if data.get('password') else 'missing'}", Colors.YELLOW, use_color))
        print(color(f"  session:  {data.get('session_path', '(none)')}", Colors.YELLOW, use_color))
        print(color("\nNOTE: This is a dry test (no real login performed).", Colors.GREY, use_color))
        return
