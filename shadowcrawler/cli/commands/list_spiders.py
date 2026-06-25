# shadowcrawler/cli/commands/list_spiders.py
# ShadowCrawler v4.1.1 — List Available Spiders
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for listing all public spiders registered in ShadowCrawler.

This module displays:
    - Spider name and module path
    - Domain
    - Extractor class
    - Fetcher type (browser/http/default)
    - Auth handler
    - Pagination support
    - Rate limits
    - Custom headers/cookies
    - Playwright hook usage

Private spiders (inside _private/) are automatically excluded.
"""

from typing import Any

from shadowcrawler.core.spider_registry import SpiderRegistry
from shadowcrawler.core.spider_loader import load_all_spiders
from shadowcrawler.fetcher.playwright_fetcher import PlaywrightFetcher
from shadowcrawler.fetcher.requests_fetcher import RequestsFetcher


# ------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------
class Colors:
    """ANSI color escape codes for CLI output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    GREY = "\033[90m"
    RESET = "\033[0m"


def color(text: str, c: str, enabled: bool = True) -> str:
    """Apply ANSI color to text if enabled."""
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def get_extractor_name(spider_cls: type) -> str:
    """Return the extractor class name for a spider."""
    extractor = getattr(spider_cls, "extractor", None)
    if extractor:
        return extractor.__class__.__name__

    extractor_class = getattr(spider_cls, "extractor_class", None)
    return extractor_class.__name__ if extractor_class else "(no extractor)"


def get_fetcher_name(spider_cls: type) -> str:
    """Return the fetcher type (browser/http/default)."""
    fetcher = getattr(spider_cls, "fetcher", None)
    if fetcher:
        if isinstance(fetcher, PlaywrightFetcher):
            return "browser"
        if isinstance(fetcher, RequestsFetcher):
            return "http"
        return fetcher.__class__.__name__

    fetcher_class = getattr(spider_cls, "fetcher_class", None)
    if fetcher_class:
        if fetcher_class is PlaywrightFetcher:
            return "browser"
        if fetcher_class is RequestsFetcher:
            return "http"
        return fetcher_class.__name__

    return "(default)"


def get_auth_name(spider_cls: type) -> str:
    """Return the auth handler class name."""
    auth = getattr(spider_cls, "auth_handler", None)
    if auth:
        return auth.__class__.__name__

    auth_class = getattr(spider_cls, "auth_handler_class", None)
    return auth_class.__name__ if auth_class else "(no auth)"


def get_pagination(spider_cls: type) -> str:
    """Return yes/no depending on pagination support."""
    if hasattr(spider_cls, "paginate") or hasattr(spider_cls, "next_page"):
        return "yes"
    if getattr(spider_cls, "pagination", False):
        return "yes"
    return "no"


def get_rate_limit(spider_cls: type) -> Any:
    """Return rate‑limit or delay configuration."""
    if hasattr(spider_cls, "rate_limit"):
        return getattr(spider_cls, "rate_limit")
    if hasattr(spider_cls, "delay"):
        return getattr(spider_cls, "delay")
    if hasattr(spider_cls, "min_delay") or hasattr(spider_cls, "max_delay"):
        return "variable"
    return "(none)"


def get_headers(spider_cls: type) -> str:
    """Return yes/no for custom headers."""
    if hasattr(spider_cls, "headers") or hasattr(spider_cls, "default_headers"):
        return "custom"
    return "(none)"


def get_cookies(spider_cls: type) -> str:
    """Return yes/no for custom cookies."""
    if hasattr(spider_cls, "cookies") or hasattr(spider_cls, "default_cookies"):
        return "custom"
    return "(none)"


def get_pw_hooks(spider_cls: type) -> str:
    """Return yes/no for Playwright hook usage."""
    if hasattr(spider_cls, "enhance_page"):
        return "yes"
    if hasattr(spider_cls, "before_navigation"):
        return "yes"
    if hasattr(spider_cls, "after_navigation"):
        return "yes"
    if getattr(spider_cls, "playwright_hooks", False):
        return "yes"
    return "no"


# ------------------------------------------------------------
# Main Command
# ------------------------------------------------------------
def cmd_list_spiders(args: Any = None) -> None:
    """Entry point for the `shadowcrawler list-spiders` command."""
    use_color = True

    # Load all spiders (public + private)
    load_all_spiders()

    print(color("Available spiders:", Colors.BLUE, use_color))

    # Only list public spiders
    for spider_cls in SpiderRegistry.all(include_private=False):
        spider_name = getattr(spider_cls, "name", spider_cls.__name__)
        domain = getattr(spider_cls, "domain", None)
        domain_str = domain if domain else "(no domain)"

        print(color(f"\n{spider_name}", Colors.BLUE, use_color))
        print(color(f"  class:      {spider_cls.__module__}.{spider_cls.__name__}", Colors.GREY, use_color))

        # Private module warning
        if "/_private/" in spider_cls.__module__.replace(".", "/"):
            print(color("[WARN] You are loading a private module (_private).", Colors.YELLOW, use_color))
            print(color("       Private modules are not part of the public ShadowCrawler distribution.", Colors.YELLOW, use_color))
            print(color("       You are fully responsible for their usage.", Colors.YELLOW, use_color))

        print(f"  domain:     {color(domain_str, Colors.GREEN, use_color)}")
        print(f"  extractor:  {color(get_extractor_name(spider_cls), Colors.YELLOW, use_color)}")
        print(f"  fetcher:    {color(get_fetcher_name(spider_cls), Colors.YELLOW, use_color)}")
        print(f"  auth:       {color(get_auth_name(spider_cls), Colors.YELLOW, use_color)}")
        print(f"  pagination: {color(get_pagination(spider_cls), Colors.GREEN, use_color)}")
        print(f"  rate-limit: {color(get_rate_limit(spider_cls), Colors.GREEN, use_color)}")
        print(f"  headers:    {color(get_headers(spider_cls), Colors.GREEN, use_color)}")
        print(f"  cookies:    {color(get_cookies(spider_cls), Colors.GREEN, use_color)}")
        print(f"  pw-hooks:   {color(get_pw_hooks(spider_cls), Colors.GREEN, use_color)}")
