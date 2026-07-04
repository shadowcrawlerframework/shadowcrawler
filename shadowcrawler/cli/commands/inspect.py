# shadowcrawler/cli/commands/inspect.py
# ShadowCrawler v4.1.3 — Spider Inspection Tool
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Spider inspection command for the ShadowCrawler CLI.

This module provides:
    - Human‑readable and JSON inspection output.
    - Metadata extraction (domain, extractor, fetcher, auth).
    - Pagination and rate‑limit detection.
    - Custom headers/cookies detection.
    - Playwright hook detection.
    - Overridden method listing.
    - Class attribute listing.
    - Optional source code display.

It supports both public and private spiders.
"""

import os
import inspect as pyinspect
import json
import sys
from typing import Any, Dict, List

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.core.spider_registry import SpiderRegistry
from shadowcrawler.core.spider_loader import load_all_spiders
from shadowcrawler.fetcher.playwright_fetcher import PlaywrightFetcher
from shadowcrawler.fetcher.requests_fetcher import RequestsFetcher
from shadowcrawler.cli.commands.config import load_config


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
    """Apply ANSI color to text if enabled."""
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def get_extractor_name(cls: type) -> str:
    """Return the extractor class name for a spider."""
    inst = getattr(cls, "extractor", None)
    if inst:
        return inst.__class__.__name__
    c = getattr(cls, "extractor_class", None)
    return c.__name__ if c else "(no extractor)"


def get_fetcher_name(cls: type) -> str:
    """Return the fetcher type (browser/http/default)."""
    inst = getattr(cls, "fetcher", None)
    if inst:
        if isinstance(inst, PlaywrightFetcher):
            return "browser"
        if isinstance(inst, RequestsFetcher):
            return "http"
        return inst.__class__.__name__

    c = getattr(cls, "fetcher_class", None)
    if c:
        if c is PlaywrightFetcher:
            return "browser"
        if c is RequestsFetcher:
            return "http"
        return c.__name__

    return "(default)"


def get_auth_name(cls: type) -> str:
    """Return the auth handler class name."""
    inst = getattr(cls, "auth_handler", None)
    if inst:
        return inst.__class__.__name__
    c = getattr(cls, "auth_handler_class", None)
    return c.__name__ if c else "(no auth)"


def get_pagination(cls: type) -> str:
    """Return yes/no depending on pagination support."""
    if hasattr(cls, "paginate") or hasattr(cls, "next_page"):
        return "yes"
    if getattr(cls, "pagination", False):
        return "yes"
    return "no"


def get_rate_limit(cls: type) -> Any:
    """Return rate‑limit or delay configuration."""
    if hasattr(cls, "rate_limit"):
        return getattr(cls, "rate_limit")
    if hasattr(cls, "delay"):
        return getattr(cls, "delay")
    if hasattr(cls, "min_delay") or hasattr(cls, "max_delay"):
        return "variable"
    return "(none)"


def get_headers(cls: type) -> str:
    """Return yes/no for custom headers."""
    if hasattr(cls, "headers") or hasattr(cls, "default_headers"):
        return "custom"
    return "(none)"


def get_cookies(cls: type) -> str:
    """Return yes/no for custom cookies."""
    if hasattr(cls, "cookies") or hasattr(cls, "default_cookies"):
        return "custom"
    return "(none)"


def get_pw_hooks(cls: type) -> str:
    """Return yes/no for Playwright hook usage."""
    if hasattr(cls, "enhance_page"):
        return "yes"
    if hasattr(cls, "before_navigation"):
        return "yes"
    if hasattr(cls, "after_navigation"):
        return "yes"
    if getattr(cls, "playwright_hooks", False):
        return "yes"
    return "no"


def get_methods(cls: type) -> List[str]:
    """Return a list of overridden methods."""
    base_methods = set(dir(SpiderBase))
    cls_methods = set(dir(cls))
    overrides = sorted(list(cls_methods - base_methods))
    return overrides


def get_attrs(cls: type) -> Dict[str, str]:
    """Return class attributes (non‑dunder, non‑methods)."""
    attrs = {}
    for k, v in cls.__dict__.items():
        if not k.startswith("__") and not pyinspect.isroutine(v):
            attrs[k] = repr(v)
    return attrs


def get_source(cls: type) -> str:
    """Return source code for the spider class."""
    try:
        return pyinspect.getsource(cls)
    except Exception:
        return "(source unavailable)"


# ------------------------------------------------------------
# Main Command
# ------------------------------------------------------------
def cmd_inspect(args: Any) -> None:
    """Entry point for the `shadowcrawler inspect` command."""
    use_color = not args.no_color and sys.stdout.isatty()

    # Load all spiders (public + private)
    load_all_spiders()

    spider_cls = SpiderRegistry.get(args.name)
    if not spider_cls:
        print(color(f"Spider '{args.name}' not found.", Colors.RED, use_color))
        print("Use 'shadowcrawler list-spiders' to see available spiders.")
        return

    module = spider_cls.__module__

    # ------------------------------------------------------------
    # JSON MODE
    # ------------------------------------------------------------
    if args.json:
        data = {
            "name": getattr(spider_cls, "name", spider_cls.__name__),
            "module": module,
            "domain": getattr(spider_cls, "domain", None),
            "extractor": get_extractor_name(spider_cls),
            "fetcher": get_fetcher_name(spider_cls),
            "auth": get_auth_name(spider_cls),
            "pagination": get_pagination(spider_cls),
            "rate_limit": get_rate_limit(spider_cls),
            "headers": get_headers(spider_cls),
            "cookies": get_cookies(spider_cls),
            "pw_hooks": get_pw_hooks(spider_cls),
            "methods": get_methods(spider_cls),
            "attributes": get_attrs(spider_cls),
        }
        print(json.dumps(data, indent=2))
        return

    # ------------------------------------------------------------
    # HUMAN OUTPUT
    # ------------------------------------------------------------
    print(color(f"\nSpider: {getattr(spider_cls, 'name', spider_cls.__name__)}", Colors.BLUE, use_color))
    print(color(f"  module: {module}", Colors.GREY, use_color))

    # Private module warning
    if "/_private/" in module.replace(".", "/"):
        print(color("[WARN] You are loading a private module (_private).", Colors.YELLOW, use_color))
        print(color("       Private modules are not part of the public ShadowCrawler distribution.", Colors.YELLOW, use_color))
        print(color("       You are fully responsible for their usage.", Colors.YELLOW, use_color))

    print(f"  domain:     {color(getattr(spider_cls, 'domain', '(no domain)'), Colors.GREEN, use_color)}")
    print(f"  extractor:  {color(get_extractor_name(spider_cls), Colors.YELLOW, use_color)}")
    print(f"  fetcher:    {color(get_fetcher_name(spider_cls), Colors.YELLOW, use_color)}")
    print(f"  auth:       {color(get_auth_name(spider_cls), Colors.YELLOW, use_color)}")
    print(f"  pagination: {color(get_pagination(spider_cls), Colors.GREEN, use_color)}")
    print(f"  rate-limit: {color(get_rate_limit(spider_cls), Colors.GREEN, use_color)}")
    print(f"  headers:    {color(get_headers(spider_cls), Colors.GREEN, use_color)}")
    print(f"  cookies:    {color(get_cookies(spider_cls), Colors.GREEN, use_color)}")
    print(f"  pw-hooks:   {color(get_pw_hooks(spider_cls), Colors.GREEN, use_color)}")

    # ------------------------------------------------------------
    # AUTH DETAILS
    # ------------------------------------------------------------
    cfg = load_config()
    auth_cfg = cfg.get("auth", {})

    site_key = spider_cls.__name__.replace("Spider", "").lower()
    auth_data = auth_cfg.get(site_key, {})

    print(color("\nAuth Details", Colors.BLUE, use_color))

    handler_name = get_auth_name(spider_cls)
    print(f"  handler:    {color(handler_name, Colors.YELLOW, use_color)}")

    username = auth_data.get("username")
    print(f"  username:   {color(username if username else '(missing)', Colors.GREEN if username else Colors.RED, use_color)}")

    password = auth_data.get("password")
    print(f"  password:   {color('******' if password else '(missing)', Colors.GREEN if password else Colors.RED, use_color)}")

    session = auth_data.get("session_path")
    if session:
        exists = os.path.exists(os.path.expanduser(session))
        print(f"  session:    {color(session, Colors.GREEN if exists else Colors.YELLOW, use_color)}")
    else:
        print(f"  session:    {color('(none)', Colors.RED, use_color)}")

    auto_login = auth_data.get("auto_login", False)
    print(f"  auto_login: {color(str(auto_login).lower(), Colors.GREEN if auto_login else Colors.YELLOW, use_color)}")

    if username and password:
        print(f"  status:     {color('OK ✓', Colors.GREEN, use_color)}")
    else:
        print(f"  status:     {color('INCOMPLETE ⚠', Colors.YELLOW, use_color)}")

    # ------------------------------------------------------------
    # METHODS
    # ------------------------------------------------------------
    if args.methods or args.all:
        print(color("\nMethods:", Colors.BLUE, use_color))
        for m in get_methods(spider_cls):
            print(f"  - {m}")

    # ------------------------------------------------------------
    # ATTRIBUTES
    # ------------------------------------------------------------
    if args.attrs or args.all:
        print(color("\nAttributes:", Colors.BLUE, use_color))
        for k, v in get_attrs(spider_cls).items():
            print(f"  {k}: {v}")

    # ------------------------------------------------------------
    # SOURCE CODE
    # ------------------------------------------------------------
    if args.source:
        print(color("\nSource code:", Colors.BLUE, use_color))
        print(get_source(spider_cls))
