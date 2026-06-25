# shadowcrawler/cli/main.py
# ShadowCrawler v4.1.1 — Main CLI Router
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Primary command-line interface for ShadowCrawler.

This module defines the main CLI entry point and routes all subcommands:
    - run
    - resume
    - download
    - stats
    - list-spiders
    - version
    - config
    - auth
    - inspect
    - spiders-create

The CLI is intentionally thin: each subcommand delegates to a handler
function located in shadowcrawler.cli.commands.<name>.
"""

import argparse
import sys

from shadowcrawler.cli.commands.run import cmd_run
from shadowcrawler.cli.commands.resume import cmd_resume
from shadowcrawler.cli.commands.download import cmd_download
from shadowcrawler.cli.commands.list_spiders import cmd_list_spiders
from shadowcrawler.cli.commands.stats import cmd_stats
from shadowcrawler.cli.commands.version import cmd_version
from shadowcrawler.cli.commands.config import cmd_config
from shadowcrawler.cli.commands.auth import cmd_auth
from shadowcrawler.cli.commands.inspect import cmd_inspect
from shadowcrawler.cli.commands.spiders_create import cmd_spiders_create


# ------------------------------------------------------------
# Parser Builder
# ------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """Build and configure the main ShadowCrawler CLI parser.

    Returns:
        A fully configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="shadowcrawler",
        description="ShadowCrawler — High‑performance modular crawling framework",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------
    p_run = sub.add_parser("run", help="Run a new crawl session")

    p_run.add_argument("-u", "--url", help="Target URL")
    p_run.add_argument("-s", "--spider", help="Force a specific spider")
    p_run.add_argument("-o", "--output", help="Output folder")
    p_run.add_argument("-m", "--max-pages", type=int, help="Maximum number of pages")
    p_run.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    p_run.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    p_run.add_argument("-c", "--checkpoint", help="Checkpoint file")
    p_run.add_argument("--no-media", action="store_true", help="Do not download media")
    p_run.add_argument("--no-data", action="store_true", help="Do not save structured data")
    p_run.add_argument("--user-agent", help="Override User-Agent")
    p_run.add_argument("--delay", type=float, help="Delay between requests")
    p_run.add_argument("--no-color", action="store_true", help="Disable colored output")
    p_run.add_argument("--force", action="store_true", help="Create output folder without asking")

    # Auto-download
    p_run.add_argument("--download", action="store_true", help="Download media after crawl")

    # Fetch mode overrides
    p_run.add_argument(
        "--force-browser",
        action="store_true",
        help="Override fetch_mode and force browser mode",
    )
    p_run.add_argument(
        "--force-http",
        action="store_true",
        help="Override fetch_mode and force HTTP mode",
    )

    # Show Playwright browser window
    p_run.add_argument(
        "--show-browser",
        action="store_true",
        help="Show Playwright browser window (disable headless mode)",
    )

    # ------------------------------------------------------------
    # WORKERS FLAG (nuevo)
    # ------------------------------------------------------------
    p_run.add_argument(
        "-w", "--workers",
        type=int,
        help="Override number of concurrent workers (default: spider or 2)",
    )

    p_run.set_defaults(func=cmd_run)

    # ------------------------------------------------------------
    # RESUME
    # ------------------------------------------------------------
    p_resume = sub.add_parser("resume", help="Resume a previous session")
    p_resume.add_argument("checkpoint", help="Checkpoint file to resume from")
    p_resume.set_defaults(func=cmd_resume)

    # ------------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------------
    p_dl = sub.add_parser("download", help="Download media from a checkpoint")
    p_dl.add_argument("checkpoint", help="Checkpoint file to load media from")
    p_dl.add_argument("-o", "--output", help="Output folder for downloads")
    p_dl.add_argument("-w", "--workers", type=int, default=4, help="Number of download threads")

    # Audit mode
    p_dl.add_argument(
        "--audit",
        action="store_true",
        help="Enable download auditing (writes audit_fails.jsonl and summary).",
    )

    # Fetch mode overrides
    p_dl.add_argument(
        "--force-browser",
        action="store_true",
        help="Override fetch_mode and force browser mode",
    )
    p_dl.add_argument(
        "--force-http",
        action="store_true",
        help="Override fetch_mode and force HTTP mode",
    )

    p_dl.set_defaults(func=cmd_download)

    # ------------------------------------------------------------
    # LIST SPIDERS
    # ------------------------------------------------------------
    p_ls = sub.add_parser("list-spiders", help="List available spiders")
    p_ls.set_defaults(func=cmd_list_spiders)

    # ------------------------------------------------------------
    # INSPECT
    # ------------------------------------------------------------
    p_ins = sub.add_parser("inspect", help="Inspect a spider")
    p_ins.add_argument("name", help="Spider class name")
    p_ins.add_argument("--json", action="store_true", help="Output JSON")
    p_ins.add_argument("--methods", action="store_true", help="Show overridden methods")
    p_ins.add_argument("--attrs", action="store_true", help="Show class attributes")
    p_ins.add_argument("--source", action="store_true", help="Show source code")
    p_ins.add_argument("--all", action="store_true", help="Show everything")
    p_ins.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    p_ins.set_defaults(func=cmd_inspect)

    # ------------------------------------------------------------
    # STATS
    # ------------------------------------------------------------
    p_stats = sub.add_parser("stats", help="Show stats of last session")
    p_stats.set_defaults(func=cmd_stats)

    # ------------------------------------------------------------
    # VERSION
    # ------------------------------------------------------------
    p_ver = sub.add_parser("version", help="Show ShadowCrawler version")
    p_ver.set_defaults(func=cmd_version)

    # ------------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------------
    p_cfg = sub.add_parser("config", help="Manage global configuration")
    p_cfg.add_argument("action", choices=["set", "get", "list", "reset"])
    p_cfg.add_argument("key", nargs="?", help="Configuration key")
    p_cfg.add_argument("value", nargs="?", help="Value for 'set'")
    p_cfg.set_defaults(func=cmd_config)

    # ------------------------------------------------------------
    # AUTH
    # ------------------------------------------------------------
    p_auth = sub.add_parser("auth", help="Manage auth credentials and handlers")
    p_auth_sub = p_auth.add_subparsers(dest="action", required=True)

    p_auth_sub.add_parser("list", help="List configured auth entries")

    p_auth_show = p_auth_sub.add_parser("show", help="Show auth config for a site")
    p_auth_show.add_argument("site")

    p_auth_set = p_auth_sub.add_parser("set", help="Set auth config for a site")
    p_auth_set.add_argument("site")
    p_auth_set.add_argument("--username")
    p_auth_set.add_argument("--password")
    p_auth_set.add_argument("--session", help="Session path")
    p_auth_set.add_argument("--auto-login", type=lambda v: v.lower() == "true")

    p_auth_clear = p_auth_sub.add_parser("clear", help="Clear auth config for a site")
    p_auth_clear.add_argument("site")

    p_auth_test = p_auth_sub.add_parser("test", help="Dry-run test for an auth handler")
    p_auth_test.add_argument("site")
    p_auth_test.add_argument("handler", help="Full handler path")

    p_auth.set_defaults(func=cmd_auth)

    # ------------------------------------------------------------
    # SPIDERS CREATE
    # ------------------------------------------------------------
    p_sc = sub.add_parser("spiders-create", help="Generate a new spider skeleton")
    p_sc.add_argument("name", help="Spider base name")
    p_sc.add_argument("--browser", action="store_true", help="Use Playwright fetcher")
    p_sc.add_argument("--http", action="store_true", help="Use HTTP fetcher")
    p_sc.add_argument("--with-auth", action="store_true", help="Generate auth handler")
    p_sc.add_argument("--with-extractor", action="store_true", help="Generate site extractor")
    p_sc.add_argument("--pagination", action="store_true", help="Include pagination helper")
    p_sc.add_argument("--domain", help="Override spider domain")
    p_sc.add_argument("--private", action="store_true", help="Generate spider in _private/")
    p_sc.add_argument("--force", action="store_true", help="Overwrite existing files")
    p_sc.set_defaults(func=cmd_spiders_create)

    return parser


# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------
def main() -> None:
    """Entry point for the ShadowCrawler CLI."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
