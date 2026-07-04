# shadowcrawler/core/spider_registry.py
# ShadowCrawler v4.1.3 — Global Spider Registry
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Centralized registry for all spiders detected by SpiderMeta.
# Does not depend on filesystem scanning and supports both
# public and private spiders.

from typing import Dict, Type, List, Optional


class SpiderRegistry:
    """Global registry for all spiders in ShadowCrawler.

    Notes:
        - Does NOT depend on filesystem scanning.
        - Does NOT rely on __init__.py.
        - Supports both public and private spiders.
        - Registration is handled automatically by SpiderMeta.
    """

    _spiders: Dict[str, Type] = {}

    # ------------------------------------------------------------
    # Register Spider
    # ------------------------------------------------------------
    @classmethod
    def register(cls, spider_cls: Type) -> None:
        """Register a spider class in the global registry.

        Naming priority:
            1. spider_cls.name (if defined)
            2. spider_cls.__name__

        The key is stored in lowercase for case-insensitive lookup.
        """
        name = getattr(spider_cls, "name", spider_cls.__name__)
        key = name.lower()
        cls._spiders[key] = spider_cls

    # ------------------------------------------------------------
    # Retrieve Spider
    # ------------------------------------------------------------
    @classmethod
    def get(cls, name: str) -> Optional[Type]:
        """Retrieve a spider class by name (case-insensitive).

        Args:
            name: The spider name to look up.

        Returns:
            The spider class, or None if not found.
        """
        if not name:
            return None
        return cls._spiders.get(name.lower())

    # ------------------------------------------------------------
    # List All Spiders
    # ------------------------------------------------------------
    @classmethod
    def all(cls, include_private: bool = False) -> List[Type]:
        """Return a list of all registered spiders.

        Args:
            include_private:
                - False → return only public spiders
                - True  → return all spiders (public + private)

        A spider is considered private if it defines:
            private = True
        """
        spiders = list(cls._spiders.values())

        if include_private:
            return spiders

        return [
            s for s in spiders
            if not getattr(s, "private", False)
        ]
