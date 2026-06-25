# shadowcrawler/cli/commands/run.py
# ShadowCrawler v4.1.0 — Run a New Crawl Session
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for starting a new crawl session.

Features:
    - Automatic fetch_mode detection (http / browser)
    - Manual fetch_mode override
    - Automatic BrowserManager lifecycle
    - Service BrowserContext for auto-download
    - Checkpoint v3.1 support
    - Spider autodetection by domain
    - Optional auto-download after crawl

This is the primary entry point for running new crawls.
"""

import sys
import os
import asyncio
from urllib.parse import urlparse
from typing import Any, Optional

from shadowcrawler.core.browser_manager import BrowserManager
from shadowcrawler.core.crawler_engine import CrawlerEngine
from shadowcrawler.core.frontier import Frontier
from shadowcrawler.core.media_extractor import MediaExtractor
from shadowcrawler.core.checkpoint_manager import CheckpointManager
from shadowcrawler.logging import configure_logging
from shadowcrawler.parsing.spider_adapter import SpiderAdapter
from shadowcrawler.models.request import Request

from shadowcrawler.core.spider_loader import load_all_spiders
from shadowcrawler.core.spider_registry import SpiderRegistry

from shadowcrawler.cli.commands.download import _run_download_async


# ------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------
class Colors:
    """ANSI color escape codes for CLI output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


def colorize(text: str, color: str, enabled: bool = True) -> str:
    """Apply ANSI color to text if enabled."""
    return f"{color}{text}{Colors.RESET}" if enabled else text


def confirm(prompt: str, default: bool = True) -> bool:
    """Ask the user for confirmation (Y/n or y/N)."""
    if not sys.stdin.isatty():
        return False

    suffix = "Y/n" if default else "y/N"
    ans = input(f"{prompt} [{suffix}]: ").strip().lower()
    return (ans == "" and default) or ans == "y"


# ------------------------------------------------------------
# Spider Autodetection
# ------------------------------------------------------------
def autodetect_spider(url: str) -> Optional[type]:
    """Detect a spider class based on the URL's domain."""
    domain = urlparse(url).netloc.lower()

    for spider_cls in SpiderRegistry.all(include_private=True):
        spider_domain = getattr(spider_cls, "domain", None)
        if not spider_domain:
            continue

        domains = (
            [spider_domain.lower()]
            if isinstance(spider_domain, str)
            else [d.lower() for d in spider_domain]
        )

        if any(domain.endswith(d) for d in domains):
            return spider_cls

    return None


# ------------------------------------------------------------
# Async Runner
# ------------------------------------------------------------
async def _run_async(args: Any, use_color: bool) -> None:
    """Execute the asynchronous crawl workflow."""
    configure_logging(debug=args.debug, verbose=args.verbose)

    # Output folder
    if args.output and not os.path.exists(args.output):
        if args.force or confirm(
            colorize(
                f"Output folder '{args.output}' does not exist. Create it?",
                Colors.BLUE,
                use_color,
            )
        ):
            os.makedirs(args.output, exist_ok=True)
        else:
            print(colorize("Aborted: output folder missing.", Colors.RED, use_color))
            sys.exit(1)

    # Load spiders
    load_all_spiders()

    spider_cls = None

    # Explicit spider
    if args.spider:
        spider_cls = SpiderRegistry.get(args.spider)
        if not spider_cls:
            print(colorize(f"Spider '{args.spider}' not found.", Colors.RED, use_color))
            sys.exit(1)

    # Autodetect spider
    if not spider_cls:
        spider_cls = autodetect_spider(args.url)

    if not spider_cls:
        print(
            colorize(
                f"No spider found for domain: {urlparse(args.url).netloc}",
                Colors.RED,
                use_color,
            )
        )
        sys.exit(1)

    print(colorize(f"Using spider: {spider_cls.__name__}", Colors.BLUE, use_color))

    spider = spider_cls()

    # Auth handler
    auth_handler = None
    if hasattr(spider, "auth_handler_class") and spider.auth_handler_class:
        auth_handler = spider.auth_handler_class()

    # Extractor
    extractor_cls = getattr(spider_cls, "extractor_class", None)
    if not extractor_cls:
        print(
            colorize(
                f"Spider '{spider_cls.__name__}' has no extractor_class defined.",
                Colors.RED,
                use_color,
            )
        )
        sys.exit(1)

    extractor = extractor_cls(spider.handle)
    parser_adapter = SpiderAdapter(spider, extractor)

    # Base components
    frontier = Frontier()
    media_extractor = MediaExtractor(disabled=args.no_media)

    # Fetch mode
    fetch_mode = getattr(spider, "fetch_mode", "http")

    if args.force_browser:
        fetch_mode = "browser"
    elif args.force_http:
        fetch_mode = "http"

    print(colorize(f"Fetch mode: {fetch_mode}", Colors.YELLOW, use_color))

    # BrowserManager
    browser_manager = None
    if fetch_mode == "browser":
        browser_manager = BrowserManager(show_browser=args.show_browser)
        await browser_manager.start()

    # ------------------------------------------------------------
    # WORKERS: CLI override > spider attribute > default (2)
    # ------------------------------------------------------------
    workers = args.workers or getattr(spider, "workers", 2)

    print(colorize(f"Workers: {workers}", Colors.YELLOW, use_color))

    # Create Engine
    engine = CrawlerEngine(
        frontier=frontier,
        media_extractor=media_extractor,
        browser_manager=browser_manager,
        max_pages=args.max_pages,
        user_agent=args.user_agent,
        delay=args.delay,
        save_data=not args.no_data,
        output_folder=args.output,
        checkpoint_file=args.checkpoint,
        spider_name=spider_cls.__name__,
        auth_handler=auth_handler,
        debug=args.debug,
        verbose=args.verbose,
        concurrency=workers,  # ← AQUÍ SE APLICA
    )

    engine.parser = parser_adapter
    engine.fetch_mode = fetch_mode

    # Initial push
    frontier.push(
        Request(
            url=args.url,
            priority=0,
            meta={"use_browser": fetch_mode == "browser"},
        )
    )

    print(colorize("Starting crawl...", Colors.GREEN, use_color))
    await engine.run(args.url)
    print(colorize("Crawl finished.", Colors.GREEN, use_color))

    # Save checkpoint
    if args.checkpoint:
        cp = CheckpointManager(args.checkpoint)
        cp.save(engine)
        print(colorize(f"Checkpoint saved → {args.checkpoint}", Colors.GREEN, use_color))

    # Auto-download
    if args.download:
        if not args.checkpoint:
            print(
                colorize(
                    "ERROR: --download requires --checkpoint to be set.",
                    Colors.RED,
                    use_color,
                )
            )
            sys.exit(1)

        print(colorize("Starting auto-download...", Colors.BLUE, use_color))

        service_ctx = None
        if browser_manager:
            service_ctx = await browser_manager.get_service_context(
                auth_handler=auth_handler
            )

        class DLArgs:
            checkpoint = args.checkpoint
            output = args.output
            workers = 4
            browser_context = service_ctx
            audit = False

        await _run_download_async(DLArgs())

        print(colorize("Auto-download finished.", Colors.GREEN, use_color))

    if browser_manager:
        await browser_manager.close()


# ------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------
def cmd_run(args: Any) -> None:
    """Entry point for the `shadowcrawler run` command."""
    use_color = not args.no_color and sys.stdout.isatty()
    asyncio.run(_run_async(args, use_color))
