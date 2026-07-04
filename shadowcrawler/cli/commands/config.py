# shadowcrawler/cli/commands/config.py
# ShadowCrawler v4.1.3 — Global Configuration Manager
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
CLI commands for managing the global ShadowCrawler configuration file.

This module provides:
    - Loading and saving the global config (YAML).
    - Setting and retrieving nested configuration keys.
    - Resetting configuration to defaults.
    - Pretty-printing configuration for inspection.

The configuration file is stored at:
    ~/.shadowcrawler/config.yaml
"""

import os
import sys
import yaml
from typing import Any, Dict, Tuple, Optional

CONFIG_DIR = os.path.expanduser("~/.shadowcrawler")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

# ------------------------------------------------------------
# Default Configuration
# ------------------------------------------------------------
DEFAULT_CONFIG: Dict[str, Any] = {
    "engine": {
        "concurrency": 4,
        "delay": 0.0,
        "max_pages": None,
        "max_depth": None,
        "retry_policy": "exponential",
        "timeout": 30,
        "checkpoint_interval": 60,
        "output_dir": "./output",
    },
    "browser": {
        "headless": True,
        "block_resources": True,
        "viewport": [1280, 720],
        "user_agent": "ShadowCrawler/1.0",
        "session_path": "~/.shadowcrawler/sessions",
        "persist_session": True,
    },
    "http": {
        "timeout": 15,
        "follow_redirects": True,
        "default_headers": {"User-Agent": "ShadowCrawler/1.0"},
        "proxy": None,
        "http2": True,
    },
    "media": {
        "download": True,
        "output_dir": "./media",
        "dedupe_index": "~/.shadowcrawler/dedupe.json",
        "max_size": "50MB",
        "allowed_types": ["jpg", "png", "mp4"],
    },
    "logging": {
        "level": "INFO",
        "modules": ["engine", "frontier"],
        "format": "simple",
        "file": None,
    },
    "spiders": {},
    "auth": {},
    "cli": {
        "color": True,
        "banner": "full",
        "default_output_dir": "./output",
        "default_spider": None,
    },
}


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
    """Apply ANSI color to text if enabled.

    Args:
        text: Text to colorize.
        c: ANSI color code.
        enabled: Whether to apply color.

    Returns:
        Colored or plain text.
    """
    return f"{c}{text}{Colors.RESET}" if enabled else text


# ------------------------------------------------------------
# Helpers (NO recursion)
# ------------------------------------------------------------
def ensure_config() -> None:
    """Ensure the configuration directory and file exist.

    Notes:
        Does NOT call save_config() to avoid recursion.
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, sort_keys=False)


def load_config() -> Dict[str, Any]:
    """Load the global configuration file.

    Returns:
        Parsed configuration dictionary.
    """
    ensure_config()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(data: Dict[str, Any]) -> None:
    """Save configuration to disk.

    Notes:
        Does NOT call ensure_config() to avoid recursion.
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)


def resolve_key_path(cfg: Dict[str, Any], key: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Resolve a dotted key path (e.g., 'engine.timeout').

    Args:
        cfg: Configuration dictionary.
        key: Dotted key path.

    Returns:
        (parent_dict, final_key) or (None, None) if invalid.
    """
    parts = key.split(".")
    ref = cfg

    for p in parts[:-1]:
        if p not in ref:
            return None, None
        ref = ref[p]

    return ref, parts[-1]


# ------------------------------------------------------------
# CLI Command
# ------------------------------------------------------------
def cmd_config(args: Any) -> None:
    """Main router for the `shadowcrawler config` command.

    Args:
        args: Parsed argparse arguments.
    """
    use_color = sys.stdout.isatty()

    # LIST
    if args.action == "list":
        cfg = load_config()
        print(color("\nCurrent ShadowCrawler Configuration:\n", Colors.BLUE, use_color))
        print(yaml.dump(cfg, sort_keys=False))
        return

    # RESET
    if args.action == "reset":
        save_config(DEFAULT_CONFIG)
        print(color("Configuration reset to defaults.", Colors.GREEN, use_color))
        return

    # GET
    if args.action == "get":
        cfg = load_config()
        parent, key = resolve_key_path(cfg, args.key)

        if parent is None or key not in parent:
            print(color(f"Key not found: {args.key}", Colors.RED, use_color))
            return

        print(color(f"{args.key} = {parent[key]}", Colors.GREEN, use_color))
        return

    # SET
    if args.action == "set":
        cfg = load_config()
        parent, key = resolve_key_path(cfg, args.key)

        if parent is None:
            print(color(f"Invalid key path: {args.key}", Colors.RED, use_color))
            return

        # Convert value type
        val = args.value
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        elif val.isdigit():
            val = int(val)

        parent[key] = val
        save_config(cfg)

        print(color(f"Updated {args.key} = {val}", Colors.GREEN, use_color))
        return
