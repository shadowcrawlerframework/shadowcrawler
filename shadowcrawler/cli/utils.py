# shadowcrawler/cli/utils.py
# ShadowCrawler v4.1.1 — CLI Utilities
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Utility helpers for the ShadowCrawler CLI.

This module provides:
    - Dynamic discovery of site extractors.
    - Automatic extractor resolution based on URL domain.
    - Optional forced extractor selection.

These utilities are used by CLI commands such as:
    - run
    - inspect
    - spiders-create
"""

import importlib
import pkgutil
from typing import Dict, Optional, Type
from urllib.parse import urlparse

from shadowcrawler.site_extractors.base import SiteExtractorBase


# ------------------------------------------------------------
# Dynamic Extractor Loader
# ------------------------------------------------------------
def _load_all_extractors() -> Dict[str, Type[SiteExtractorBase]]:
    """Dynamically load all extractors from shadowcrawler.site_extractors.

    Private modules (folders starting with "_") are ignored.

    Returns:
        dict[str, type]: Mapping of extractor name → extractor class.
    """
    import shadowcrawler.site_extractors as pkg

    extractors: Dict[str, Type[SiteExtractorBase]] = {}

    for module_info in pkgutil.iter_modules(pkg.__path__):
        name = module_info.name

        # Skip private extractors
        if name.startswith("_"):
            continue

        module = importlib.import_module(f"shadowcrawler.site_extractors.{name}")

        # Find classes that inherit from SiteExtractorBase
        for attr in dir(module):
            obj = getattr(module, attr)
            try:
                if (
                    isinstance(obj, type)
                    and issubclass(obj, SiteExtractorBase)
                    and obj is not SiteExtractorBase
                ):
                    extractors[attr.lower()] = obj
            except Exception:
                # Ignore any attribute that cannot be inspected
                pass

    return extractors


# ------------------------------------------------------------
# Extractor Resolver
# ------------------------------------------------------------
def resolve_extractor(url: str, forced: Optional[str] = None) -> Optional[Type[SiteExtractorBase]]:
    """Resolve an extractor class based on URL or forced name.

    Resolution order:
        1. Forced extractor name (if provided).
        2. Automatic domain matching via ALLOWED_NETLOCS.
        3. None if no match is found.

    Args:
        url: Target URL.
        forced: Optional forced extractor name.

    Returns:
        Extractor class or None if not found.
    """
    extractors = _load_all_extractors()

    # ------------------------------------------------------------
    # 1) Forced extractor by name
    # ------------------------------------------------------------
    if forced:
        forced_lower = forced.lower()
        extractor = extractors.get(forced_lower)

        # Warn if forced extractor comes from a private module
        if extractor:
            module_name = extractor.__module__
            if "_private" in module_name.lower():
                print(
                    "[WARN] You are loading a private module (_private).\n"
                    "       Private modules are not supported and may behave differently."
                )

        return extractor

    # ------------------------------------------------------------
    # 2) Automatic detection by domain
    # ------------------------------------------------------------
    domain = urlparse(url).netloc.lower()

    for extractor in extractors.values():
        allowed = getattr(extractor, "ALLOWED_NETLOCS", None)
        if allowed and any(domain.endswith(net) for net in allowed):
            return extractor

    # ------------------------------------------------------------
    # 3) No extractor found
    # ------------------------------------------------------------
    return None
