# shadowcrawler/cli/commands/resume.py
# ShadowCrawler v4.1.1 — Resume a Previous Crawl Session
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for resuming a previous crawl session from a checkpoint.

This module:
    - Loads a checkpoint file.
    - Reconstructs the crawler state (Frontier, MediaExtractor, BrowserManager).
    - Restores engine configuration (max_pages, delay, user_agent, etc.).
    - Restores logging configuration from the checkpoint (NOT CLI flags).
    - Resumes the crawl exactly where it left off.

This is the counterpart to `shadowcrawler run` and is essential for
long-running or interrupted crawls.
"""

import os
import sys
from typing import Any

from shadowcrawler.core.crawler_engine import CrawlerEngine
from shadowcrawler.core.frontier import Frontier
from shadowcrawler.core.media_extractor import MediaExtractor
from shadowcrawler.core.browser_manager import BrowserManager
from shadowcrawler.core.checkpoint_manager import CheckpointManager
from shadowcrawler.logging import configure_logging


# ------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------
class Colors:
    """ANSI color escape codes for CLI output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"


def color(text: str, c: str, enabled: bool = True) -> str:
    """Apply ANSI color to text if enabled."""
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Main Command
# ------------------------------------------------------------
def cmd_resume(args: Any) -> None:
    """Entry point for the `shadowcrawler resume` command.

    Args:
        args: Parsed argparse arguments.
    """
    use_color = not getattr(args, "no_color", False) and sys.stdout.isatty()
    checkpoint_file = args.checkpoint

    # ------------------------------------------------------------
    # Validate checkpoint
    # ------------------------------------------------------------
    if not os.path.exists(checkpoint_file):
        print(color(f"Checkpoint not found: {checkpoint_file}", Colors.RED, use_color))
        sys.exit(1)

    print(color("Loading checkpoint...", Colors.BLUE, use_color))

    # ------------------------------------------------------------
    # Load checkpoint
    # ------------------------------------------------------------
    data = CheckpointManager.load(checkpoint_file)

    # ------------------------------------------------------------
    # Restore logging from checkpoint (NOT from CLI flags)
    # ------------------------------------------------------------
    configure_logging(
        debug=data.get("debug", False),
        verbose=data.get("verbose", False),
    )

    # ------------------------------------------------------------
    # Rebuild Frontier
    # ------------------------------------------------------------
    frontier = Frontier()
    frontier.seen = data["seen"]
    frontier.queues = data["queues"]
    frontier.stats = data["stats"]

    # ------------------------------------------------------------
    # Rebuild components
    # ------------------------------------------------------------
    media_extractor = MediaExtractor(disabled=data.get("no_media", False))

    browser_manager = None
    if data.get("browser", False):
        browser_manager = BrowserManager()

    # ------------------------------------------------------------
    # Rebuild Engine
    # ------------------------------------------------------------
    engine = CrawlerEngine(
        frontier=frontier,
        media_extractor=media_extractor,
        browser_manager=browser_manager,
        max_pages=data.get("max_pages"),
        user_agent=data.get("user_agent"),
        delay=data.get("delay"),
        save_data=data.get("save_data", True),
        output_folder=data.get("output_folder"),
        checkpoint_file=checkpoint_file,
        spider_name=data.get("spider_name"),
    )

    print(color("Resuming crawl...", Colors.GREEN, use_color))

    # ------------------------------------------------------------
    # Resume crawl
    # ------------------------------------------------------------
    engine.resume()

    print(color("Crawl resumed and completed.", Colors.GREEN, use_color))
