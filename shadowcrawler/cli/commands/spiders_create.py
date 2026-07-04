# shadowcrawler/cli/commands/spiders_create.py
# ShadowCrawler v4.1.3 — Spider Generator (Full‑Browser Default Edition)
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for generating new spider skeletons (SC v4.1.3).

Features:
    - Full‑browser spiders by default (Playwright visible + persistent page).
    - Supports --full-browser / --browser / --http.
    - Creates spider, extractor, and optional auth handler.
    - SC v4.1.3‑standard templates (async parse, extractor persistente).
    - Supports public and private spiders.
"""

import os
import sys
import re
from typing import Any


# ------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREY = "\033[90m"
    RESET = "\033[0m"


def color(text: str, c: str, enabled: bool = True) -> str:
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def ensure_init(path: str) -> None:
    init_path = os.path.join(path, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("")


def write_file(path: str, content: str, force: bool = False) -> None:
    if os.path.exists(path) and not force:
        raise FileExistsError(f"File exists: {path}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


# ------------------------------------------------------------
# Templates (SC v4.1.3 Full‑Browser Default)
# ------------------------------------------------------------
SPIDER_TEMPLATE = """\
\"\"\"Auto-generated SC v4.1.3 spider for {domain}.\"\"\"

import asyncio
from typing import Any, Dict

from shadowcrawler.core.spider_base import SpiderBase
from shadowcrawler.models.response import Response
from shadowcrawler.site_extractors{extractor_prefix}.{extractor_module} import {extractor_class}
{auth_import}


class {class_name}(SpiderBase):
    # ------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------
    name = "{spider_name}"
    handle = "{handle}"
    domain = "{domain}"

    # Full-browser default (Playwright visible + persistent page)
    fetch_mode = "{fetch_mode}"
    workers = {workers}

    extractor_class = {extractor_class}
    auth_handler_class = {auth_class}

    # ------------------------------------------------------------
    # INIT (extractor persistente)
    # ------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.extractor = self.extractor_class(self.handle)

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------
    def classify(self, url: str) -> str:
        return "GENERIC"

    def should_follow(self, type_: str) -> bool:
        return False

    # ------------------------------------------------------------
    # FETCH MODE DECISION
    # ------------------------------------------------------------
    def use_browser(self, url: str, type_: str) -> bool:
        return {use_browser}

    def request_meta(self, url: str, type_: str) -> Dict[str, Any]:
        return {request_meta}

    # ------------------------------------------------------------
    # PARSER (async, full-browser compatible)
    # ------------------------------------------------------------
    async def parse(self, response: Response, **kwargs) -> Dict[str, Any]:
        page = getattr(response, "browser_page", None)

        if page is None:
            return {"links": [], "next_pages": [], "media": [], "data": {}}

        result = await self.extractor.extract_from_page(page, response.url)

        return {
            "links": result.get("links", []),
            "next_pages": result.get("next_pages", []),
            "media": result.get("media", []),
            "data": result.get("data", {}),
        }
"""


EXTRACTOR_TEMPLATE = """\
\"\"\"Auto-generated SC v4.1.3 extractor for {domain}.\"\"\"

from shadowcrawler.site_extractors.base import SiteExtractorBase


class {class_name}(SiteExtractorBase):
    async def extract_from_page(self, page, url: str):
        # TODO: Implement DOM extraction
        return {"links": [], "next_pages": [], "media": [], "data": {}}
"""


AUTH_TEMPLATE = """\
\"\"\"Auto-generated SC v4.1.3 Auth Handler for {domain}.\"\"\"

from shadowcrawler.auth.base import AuthHandlerBase


class {class_name}(AuthHandlerBase):
    async def login(self, browser):
        # TODO: Implement login logic
        return browser
"""


# ------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------
def cmd_spiders_create(args: Any) -> None:
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
    # 3. Determine fetch_mode (full-browser default)
    # --------------------------------------------------------
    if args.full_browser:
        fetch_mode = "full-browser"
        use_browser = True
        workers = 1
        request_meta = {
            "use_browser": True,
            "browser_mode": "full",
            "keep_page": True,
            "wait_time": 20000,
            "stealth": True,
            "javaScriptEnabled": True,
            "bypassCSP": True,
            "imagesEnabled": True,
            "webgl": True,
            "serviceWorkers": "allow",
        }

    elif args.browser:
        fetch_mode = "browser"
        use_browser = True
        workers = 1
        request_meta = {"use_browser": True, "browser_mode": "simple"}

    elif args.http:
        fetch_mode = "http"
        use_browser = False
        workers = 2
        request_meta = {"use_browser": False}

    else:
        # DEFAULT → FULL-BROWSER
        fetch_mode = "full-browser"
        use_browser = True
        workers = 1
        request_meta = {
            "use_browser": True,
            "browser_mode": "full",
            "keep_page": True,
            "wait_time": 20000,
            "stealth": True,
            "javaScriptEnabled": True,
            "bypassCSP": True,
            "imagesEnabled": True,
            "webgl": True,
            "serviceWorkers": "allow",
        }

    # --------------------------------------------------------
    # 4. Prepare template values
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
        fetch_mode=fetch_mode,
        workers=workers,
        extractor_prefix=extractor_prefix,
        extractor_module=extractor_folder + "." + extractor_class,
        extractor_class=extractor_class,
        use_browser="True" if use_browser else "False",
        request_meta=request_meta,
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
    # 5. Write files
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
        sys.exit(1)

    # --------------------------------------------------------
    # 6. Final UX messages
    # --------------------------------------------------------
    print(color("\nYour spider template is ready!", Colors.GREEN, use_color))
    print(color("\nNext steps:", Colors.YELLOW, use_color))
    print(f"  - Edit your spider: {spider_path}")
    print(f"  - Edit your extractor: {extractor_path}")
    if args.with_auth:
        print(f"  - Edit your auth handler: {auth_path}")

    print(color("\nRun your spider with:", Colors.YELLOW, use_color))
    print(color(f"  shadowcrawler run --spider {spider_class} --url https://example.com\n", Colors.GREEN, use_color))
