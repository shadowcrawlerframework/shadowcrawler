# shadowcrawler/logging.py
# ShadowCrawler v4.1.1 — Centralized Corporate Logging System
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# This software is licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Centralized logging system for ShadowCrawler.

This module provides:
    - Global logging level control.
    - Per‑module debug overrides.
    - Unified corporate log formatting.
    - Integration with CLI flags (debug / verbose).
    - Logger factory used across the entire framework.

All modules should obtain loggers via:

    from shadowcrawler.logging import get_logger
    logger = get_logger(__name__)

This ensures consistent formatting, levels, and behavior across ShadowCrawler.
"""

import logging
import sys
from typing import Dict


# ------------------------------------------------------------
# Global State
# ------------------------------------------------------------
DEFAULT_GLOBAL_LEVEL: int = logging.INFO
MODULE_DEBUG_LEVELS: Dict[str, int] = {}


# ------------------------------------------------------------
# Global Logging Configuration
# ------------------------------------------------------------
def set_global_level(level_name: str) -> None:
    """Set the global logging level for the entire framework.

    Args:
        level_name: Logging level name (e.g., "INFO", "DEBUG").

    Notes:
        If an invalid level is provided, INFO is used as fallback.
    """
    global DEFAULT_GLOBAL_LEVEL

    level_name = level_name.upper().strip()
    if not hasattr(logging, level_name):
        DEFAULT_GLOBAL_LEVEL = logging.INFO
    else:
        DEFAULT_GLOBAL_LEVEL = getattr(logging, level_name)

    logging.basicConfig(
        level=DEFAULT_GLOBAL_LEVEL,
        stream=sys.stdout,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def enable_module_debug(module_name: str) -> None:
    """Enable DEBUG logging for a specific module.

    Args:
        module_name: Name of the module (e.g., "engine", "downloader").
    """
    MODULE_DEBUG_LEVELS[module_name] = logging.DEBUG


# ------------------------------------------------------------
# Logger Factory
# ------------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """Retrieve a logger configured with ShadowCrawler's corporate formatting.

    Args:
        name: Logger name (typically the module's __name__).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Apply per-module override or fall back to global level
    if name in MODULE_DEBUG_LEVELS:
        logger.setLevel(MODULE_DEBUG_LEVELS[name])
    else:
        logger.setLevel(DEFAULT_GLOBAL_LEVEL)

    # Attach handler only once
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# ------------------------------------------------------------
# CLI Integration
# ------------------------------------------------------------
def configure_logging(debug: bool = False, verbose: bool = False) -> None:
    """Configure logging based on CLI flags.

    Args:
        debug: Enable DEBUG logging globally.
        verbose: Enable DEBUG logging globally (same as debug).
    """
    if verbose or debug:
        set_global_level("DEBUG")
    else:
        set_global_level("INFO")
