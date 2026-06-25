# shadowcrawler/cli/commands/download.py
# ShadowCrawler v4.1.1 — Download Media from Checkpoint
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for downloading media items from a previously generated checkpoint.

This module provides:
    - Automatic fetch_mode detection (http / browser)
    - Manual fetch_mode overrides (--force-browser / --force-http)
    - Automatic BrowserManager creation when required
    - Optional auditing via PrivateDownloader (metadata-rich JSONL logging)

The downloader supports both HTTP and Playwright-based media fetching.
"""

import os
import sys
import asyncio
from typing import Any, Optional

from shadowcrawler.core.downloader import Downloader
from shadowcrawler.core.downloader_private import PrivateDownloader
from shadowcrawler.core.checkpoint_manager import CheckpointManager
from shadowcrawler.core.browser_manager import BrowserManager
from shadowcrawler.logging import get_logger

logger = get_logger("download")


# ------------------------------------------------------------
# Async Download Runner
# ------------------------------------------------------------
async def _run_download_async(args: Any) -> None:
    """Execute the asynchronous download workflow.

    Steps:
        1. Validate checkpoint file.
        2. Load media items.
        3. Determine fetch_mode (auto or manual override).
        4. Create BrowserManager if needed.
        5. Instantiate Downloader or PrivateDownloader.
        6. Download all media items.
        7. Clean up browser resources.

    Args:
        args: Parsed argparse arguments.
    """
    checkpoint_path = args.checkpoint
    output_dir = args.output or "downloads"

    # ------------------------------------------------------------
    # Validate checkpoint
    # ------------------------------------------------------------
    if not os.path.exists(checkpoint_path):
        logger.error(f"Checkpoint not found: {checkpoint_path}")
        sys.exit(1)

    logger.info(f"Loading checkpoint: {checkpoint_path}")
    cp = CheckpointManager.load(checkpoint_path)

    media_items = getattr(cp, "media_items", None)
    if not media_items:
        logger.error(
            "No media_items found in checkpoint. "
            "Did you run the crawl with media extraction enabled?"
        )
        sys.exit(1)

    logger.info(f"Loaded {len(media_items)} media items")

    # ------------------------------------------------------------
    # Prepare output directory
    # ------------------------------------------------------------
    if not os.path.exists(output_dir):
        logger.info(f"Creating output folder: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------
    # 1. Detect fetch_mode from checkpoint
    # ------------------------------------------------------------
    fetch_mode: str = getattr(cp, "fetch_mode", "http")

    # ------------------------------------------------------------
    # 2. Manual override
    # ------------------------------------------------------------
    if getattr(args, "force_browser", False):
        fetch_mode = "browser"
    elif getattr(args, "force_http", False):
        fetch_mode = "http"

    logger.info(f"Download fetch_mode = {fetch_mode}")

    # ------------------------------------------------------------
    # 3. Create BrowserManager if needed
    # ------------------------------------------------------------
    browser_context = getattr(args, "browser_context", None)
    browser_manager: Optional[BrowserManager] = None

    if fetch_mode == "browser" and browser_context is None:
        logger.info("fetch_mode=browser → creating BrowserManager for downloader")
        browser_manager = BrowserManager()
        await browser_manager.start()

        # Downloader does not use auth handlers
        browser_context = await browser_manager.get_service_context(auth_handler=None)

    # ------------------------------------------------------------
    # 4. Choose downloader (normal vs private)
    # ------------------------------------------------------------
    use_private = getattr(args, "audit", False)
    logger.info("Starting download session...")

    # ------------------------------------------------------------
    # 5. Create downloader (PrivateDownloader includes metadata)
    # ------------------------------------------------------------
    if use_private:
        dl = PrivateDownloader(
            output_dir=output_dir,
            workers=getattr(args, "workers", 4),
            browser_context=browser_context,
            spider_name=getattr(cp, "spider_name", None),
            fetch_mode=fetch_mode,
        )
    else:
        dl = Downloader(
            output_dir=output_dir,
            workers=getattr(args, "workers", 4),
            browser_context=browser_context,
        )

    await dl.download_all(media_items)

    logger.info("Download session finished.")

    # ------------------------------------------------------------
    # Cleanup browser if created here
    # ------------------------------------------------------------
    if browser_manager:
        await browser_manager.close()


# ------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------
def cmd_download(args: Any) -> None:
    """Entry point for the `shadowcrawler download` command.

    Args:
        args: Parsed argparse arguments.
    """
    asyncio.run(_run_download_async(args))
