# shadowcrawler/cli/commands/spiders_create.py
# ShadowCrawler v4.1.0 — Spider Generator (SC v4 Standard Edition)
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for generating new spider skeletons.

Features:
    - Creates spider, extractor, and optional auth handler.
    - Supports public and private spiders.
    - Ensures directory structure and __init__.py files.
    - Provides SC v4‑standard templates.
    - Supports --browser / --http / --with-auth / --with-extractor / --pagination.

This generator is intentionally simple and produces editable templates.
"""

import os
import sys
import re
from typing import Any


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
# Helpers
# ------------------------------------------------------------
def ensure_dir(path: str) -> None:
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def ensure_init(path: str) -> None:
    """Ensure __init__.py exists inside a folder."""
    init_path = os.path.join(path, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("")


def write_file(path: str, content: str, force: bool = False) -> None:
    """Write a file to disk, respecting overwrite rules."""
    if os.path.exists(path) and not force:
        raise FileExistsError(f"File exists: {path}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def sanitize_name(name: str) -> str:
    """Convert a human-readable name into a safe class/module identifier."""
    return re.sub(r"[^A-Za-z0-9]", "", name)


# ------------------------------------------------------------
# Templates
# ------------------------------------------------------------
SPIDER_TEMPLATE = """\
\"\"\"Auto-generated SC v4 spider for {domain}.\"\"\"

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.site_extractors{extractor_prefix}.{extractor_module} import {extractor_class}
{auth_import}


class {class_name}(SpiderBase):
    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "{spider_name}"
    handle = "{handle}"
    domain = "{domain}"
    fetch_mode = "{fetch_mode}"

    # Default worker count for this spider.
    # Users can override via CLI: --workers N
    workers = 2

    extractor_class = {extractor_class}
    auth_handler_class = {auth_class}

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str):
        if not url:
            return "NOFOLLOW"
        u = url.lower()
        return "GENERIC"

    def should_follow(self, type_: str):
        return type_ != "NOFOLLOW"

    # ------------------------------------------------------------
    # FETCH MODE DECISION
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str):
        return {use_browser}

    def request_meta(self, url: str, type_: str):
        return {{"use_browser": {use_browser}}}

    # ------------------------------------------------------------
    # PARSER
    # ------------------------------------------------------------
    def parse(self, page, url, **kwargs):
        response = page
        if response is None or not getattr(response, "html", None):
            return {{"links": [], "next_pages": [], "media": [], "data": {{}}}}

        extractor = self.extractor_class(self.handle)
        result = extractor.extract(response, url, scope=self.classify(url))

        return {{
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {{}}),
        }}
"""


EXTRACTOR_TEMPLATE = """\
\"\"\"Auto-generated SC v4 extractor for {domain}.\"\"\"

from shadowcrawler.site_extractors.base import SiteExtractorBase
from bs4 import BeautifulSoup


class {class_name}(SiteExtractorBase):
    pass
"""


AUTH_TEMPLATE = """\
\"\"\"Auto-generated SC v4 Auth Handler for {domain}.\"\"\"

from shadowcrawler.auth.base import AuthHandlerBase


class {class_name}(AuthHandlerBase):
    def login(self, browser):
        return browser
"""


# ------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------
def cmd_spiders_create(args: Any) -> None:
    """Entry point for the `shadowcrawler spiders-create` command."""
    use_color = sys.stdout.isatty()

    # --------------------------------------------------------
    # 1. Sanitize name
    # --------------------------------------------------------
    raw_name = args.name
    safe_name = sanitize_name(raw_name)

    spider_class = f"{safe_name}Spider"
    extractor_class = f"{safe_name}Extractor"
    auth_class = f"{safe_name}Auth"

    spider_folder = safe_name.lower()
    extractor_folder = safe_name.lower()
    auth_folder = safe_name.lower()

    # --------------------------------------------------------
    # 2. Determine paths
    # --------------------------------------------------------
    base_spider_dir = "shadowcrawler/spiders"
    base_extractor_dir = "shadowcrawler/site_extractors"
    base_auth_dir = "shadowcrawler/auth"

    if args.private:
        base_spider_dir = os.path.join(base_spider_dir, "_private")
        base_extractor_dir = os.path.join(base_extractor_dir, "_private")
        base_auth_dir = os.path.join(base_auth_dir, "_private")

    spider_dir = os.path.join(base_spider_dir, spider_folder)
    extractor_dir = os.path.join(base_extractor_dir, extractor_folder)
    auth_dir = os.path.join(base_auth_dir, auth_folder)

    ensure_dir(spider_dir)
    ensure_dir(extractor_dir)
    if args.with_auth:
        ensure_dir(auth_dir)

    ensure_init(spider_dir)
    ensure_init(extractor_dir)
    if args.with_auth:
        ensure_init(auth_dir)

    spider_path = os.path.join(spider_dir, f"{spider_class}.py")
    extractor_path = os.path.join(extractor_dir, f"{extractor_class}.py")
    auth_path = os.path.join(auth_dir, f"{auth_class}.py")

    # --------------------------------------------------------
    # 3. Prepare template values
    # --------------------------------------------------------
    extractor_prefix = "" if not args.private else "._private"
    auth_import = (
        f"from shadowcrawler.auth{extractor_prefix}.{auth_folder}.{auth_class} import {auth_class}"
        if args.with_auth else ""
    )
    auth_class_value = auth_class if args.with_auth else "None"

    spider_code = SPIDER_TEMPLATE.format(
        domain=args.domain or raw_name.lower(),
        spider_name=raw_name,
        class_name=spider_class,
        handle=safe_name.lower(),
        fetch_mode="browser" if args.browser else "http",
        extractor_prefix=extractor_prefix,
        extractor_module=extractor_folder + "." + extractor_class,
        extractor_class=extractor_class,
        use_browser="True" if args.browser else "False",
        auth_import=auth_import,
        auth_class=auth_class_value,
    )

    extractor_code = EXTRACTOR_TEMPLATE.format(
        domain=args.domain or raw_name.lower(),
        class_name=extractor_class,
    )

    auth_code = AUTH_TEMPLATE.format(
        domain=args.domain or raw_name.lower(),
        class_name=auth_class,
    )

    # --------------------------------------------------------
    # 4. Write files
    # --------------------------------------------------------
    try:
        write_file(spider_path, spider_code, force=args.force)
        print(color(f"Created spider: {spider_path}", Colors.GREEN, use_color))

        if args.with_extractor:
            write_file(extractor_path, extractor_code, force=args.force)
            print(color(f"Created extractor: {extractor_path}", Colors.GREEN, use_color))

        if args.with_auth:
            write_file(auth_path, auth_code, force=args.force)
            print(color(f"Created auth handler: {auth_path}", Colors.GREEN, use_color))

    except FileExistsError as exc:
        print(color(str(exc), Colors.RED, use_color))
        print(color("\nA spider with this name already exists.", Colors.YELLOW, use_color))
        print("Options:")
        print(f"  • Use a different name, for example:")
        print(f"       shadowcrawler spiders-create {raw_name}V2 --with-extractor")
        print("  • Or overwrite the existing files with --force:")
        print(f"       shadowcrawler spiders-create {raw_name} --with-extractor --force")
        sys.exit(1)

    # --------------------------------------------------------
    # 5. Final UX messages
    # --------------------------------------------------------
    print(color("\nYour spider template is ready!", Colors.GREEN, use_color))

    print(color("\nNext steps:", Colors.YELLOW, use_color))
    print("  1. Edit your spider:")
    print(f"       - {spider_path}")
    print("       - Implement classify() and parse()")

    if args.with_extractor:
        print("  2. Edit your extractor:")
        print(f"       - {extractor_path}")

    if args.with_auth:
        print("  3. Edit your auth handler:")
        print(f"       - {auth_path}")

    print(color("\nRun your spider with:", Colors.YELLOW, use_color))
    print(color(f"  shadowcrawler run --spider {spider_class} --url https://example.com\n", Colors.GREEN, use_color))
