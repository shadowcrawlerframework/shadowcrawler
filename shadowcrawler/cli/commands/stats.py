# shadowcrawler/cli/commands/stats.py
# ShadowCrawler v4.1.3 — Show Crawl Statistics
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for displaying crawl statistics from a checkpoint file.

This module provides:
    - Spider metadata
    - Frontier statistics
    - Media statistics
    - Engine statistics
    - Output folder summary
    - JSON mode
    - Selective sections (--frontier, --media, --engine, --details)

It is useful for inspecting crawl results without resuming the crawl.
"""

import os
import json
import sys
from typing import Any, Dict

from shadowcrawler.core.checkpoint_manager import CheckpointManager


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
# Main Command
# ------------------------------------------------------------
def cmd_stats(args: Any) -> None:
    """Entry point for the `shadowcrawler stats` command.

    Args:
        args: Parsed argparse arguments.
    """
    use_color = not getattr(args, "no_color", False) and sys.stdout.isatty()

    checkpoint_file = getattr(args, "checkpoint", None)

    # ------------------------------------------------------------
    # Auto-detect latest checkpoint if none provided
    # ------------------------------------------------------------
    if not checkpoint_file:
        if not os.path.exists("./checkpoints"):
            print(color("No checkpoints found.", Colors.RED, use_color))
            return

        files = sorted(
            [f for f in os.listdir("./checkpoints") if f.endswith(".chk")],
            reverse=True,
        )
        if not files:
            print(color("No checkpoint files found.", Colors.RED, use_color))
            return

        checkpoint_file = os.path.join("./checkpoints", files[0])

    if not os.path.exists(checkpoint_file):
        print(color(f"Checkpoint not found: {checkpoint_file}", Colors.RED, use_color))
        return

    print(color(f"Loading stats from: {checkpoint_file}", Colors.BLUE, use_color))

    data = CheckpointManager.load(checkpoint_file)

    # ------------------------------------------------------------
    # JSON MODE
    # ------------------------------------------------------------
    if args.json:
        print(json.dumps(data, indent=2))
        return

    # ------------------------------------------------------------
    # SPIDER INFO
    # ------------------------------------------------------------
    print(color("\nSpider Info", Colors.BLUE, use_color))
    print(f"  name:      {color(data.get('spider_name', '(unknown)'), Colors.GREEN, use_color)}")
    print(f"  domain:    {color(data.get('domain', '(unknown)'), Colors.GREEN, use_color)}")
    print(f"  extractor: {color(data.get('extractor', '(unknown)'), Colors.YELLOW, use_color)}")
    print(f"  fetcher:   {color(data.get('fetcher', '(unknown)'), Colors.YELLOW, use_color)}")
    print(f"  auth:      {color(data.get('auth', '(unknown)'), Colors.YELLOW, use_color)}")

    # ------------------------------------------------------------
    # FRONTIER STATS
    # ------------------------------------------------------------
    if args.frontier or args.details or not (args.media or args.engine):
        stats = data.get("stats", {})
        print(color("\nFrontier Stats", Colors.BLUE, use_color))
        print(f"  processed: {color(stats.get('processed', 0), Colors.GREEN, use_color)}")
        print(f"  pending:   {color(stats.get('pending', 0), Colors.YELLOW, use_color)}")
        print(f"  unique:    {color(stats.get('unique', 0), Colors.GREEN, use_color)}")
        print(f"  failed:    {color(stats.get('failed', 0), Colors.RED, use_color)}")
        print(f"  max-depth: {color(stats.get('max_depth', 0), Colors.GREEN, use_color)}")

    # ------------------------------------------------------------
    # MEDIA STATS
    # ------------------------------------------------------------
    if args.media or args.details or not (args.frontier or args.engine):
        media = data.get("media_stats", {})
        print(color("\nMedia Stats", Colors.BLUE, use_color))
        print(f"  images:    {color(media.get('images', 0), Colors.GREEN, use_color)}")
        print(f"  videos:    {color(media.get('videos', 0), Colors.GREEN, use_color)}")
        print(f"  saved:     {color(media.get('saved', 0), Colors.GREEN, use_color)}")
        print(f"  ignored:   {color(media.get('ignored', 0), Colors.YELLOW, use_color)}")
        print(f"  failed:    {color(media.get('failed', 0), Colors.RED, use_color)}")

    # ------------------------------------------------------------
    # ENGINE STATS
    # ------------------------------------------------------------
    if args.engine or args.details or not (args.frontier or args.media):
        eng = data.get("engine_stats", {})
        print(color("\nEngine Stats", Colors.BLUE, use_color))
        print(f"  requests:  {color(eng.get('requests', 0), Colors.GREEN, use_color)}")
        print(f"  retries:   {color(eng.get('retries', 0), Colors.YELLOW, use_color)}")
        print(f"  errors:    {color(eng.get('errors', 0), Colors.RED, use_color)}")
        print(f"  avg-time:  {color(eng.get('avg_time', 0), Colors.GREEN, use_color)}")

    # ------------------------------------------------------------
    # OUTPUT INFO
    # ------------------------------------------------------------
    print(color("\nOutput", Colors.BLUE, use_color))
    out = data.get("output_folder", "(none)")
    print(f"  folder: {color(out, Colors.GREY, use_color)}")

    if os.path.exists(out):
        files = os.listdir(out)
        total = sum(os.path.getsize(os.path.join(out, f)) for f in files)
        print(f"  files:  {color(len(files), Colors.GREEN, use_color)}")
        print(f"  size:   {color(f'{total/1024:.2f} KB', Colors.GREEN, use_color)}")

    print()
