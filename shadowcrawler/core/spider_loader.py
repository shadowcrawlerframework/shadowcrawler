# shadowcrawler/core/spider_loader.py
# ShadowCrawler v4.1.0 — Recursive Spider Loader
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# This module loads all spider modules under shadowcrawler.spiders,
# including nested packages and private spiders. Importing a module
# triggers SpiderMeta, which automatically registers any SpiderBase
# subclasses found inside.

import importlib
import pkgutil

import shadowcrawler.spiders as spiders_pkg


def load_all_spiders() -> None:
    """Recursively import all modules under shadowcrawler.spiders.

    Notes:
        - Includes subpackages.
        - Includes _private spiders.
        - Does NOT rely on __init__.py files.
        - Importing modules triggers SpiderMeta, which automatically
          registers all SpiderBase subclasses into SpiderRegistry.
    """
    prefix = spiders_pkg.__name__ + "."

    for module_info in pkgutil.walk_packages(spiders_pkg.__path__, prefix):
        module_name = module_info.name
        importlib.import_module(module_name)
