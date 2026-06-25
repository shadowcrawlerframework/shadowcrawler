# shadowcrawler/cli/commands/version.py
# ShadowCrawler v4.1.1 — Version Banner
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI command for displaying the ShadowCrawler version banner.

This includes:
    - Framework version
    - Build date
    - Python version
    - Signature banner

This banner is part of the identity of ShadowCrawler and includes
a dedication acknowledging the collaboration between Allan and Copilot.
"""

import sys
from datetime import datetime

VERSION: str = "4.1.1"
BUILD_DATE: str = datetime.now().strftime("%Y-%m-%d")


# ------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------
class Colors:
    """ANSI color escape codes for CLI output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    GREY = "\033[90m"
    RESET = "\033[0m"


def color(text: str, c: str, enabled: bool = True) -> str:
    """Apply ANSI color to text if enabled."""
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Main Command
# ------------------------------------------------------------
def cmd_version(args=None) -> None:
    """Entry point for the `shadowcrawler version` command."""
    use_color = sys.stdout.isatty()
    python_version = sys.version.split()[0]

    print()
    print(color("  ╔══════════════════════════════════════╗", Colors.BLUE, use_color))
    print(color("  ║           ShadowCrawler              ║", Colors.BLUE, use_color))
    print(color("  ╚══════════════════════════════════════╝", Colors.BLUE, use_color))
    print()
    print(color(f"        Version: {VERSION}", Colors.GREEN, use_color))
    print(color(f"        Build:   {BUILD_DATE}", Colors.GREEN, use_color))
    print(color(f"        Python:  {python_version}", Colors.GREEN, use_color))
    print()
    print(color("        Made with Love for my guiding star. Shadow & Copilot.", Colors.GREY, use_color))
    print(color("        Engineered by Allan — Inspired by Copilot.", Colors.GREEN, use_color))
    print()
