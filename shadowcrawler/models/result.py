# shadowcrawler/models/result.py
# ShadowCrawler v4.1.1 — Structured Extraction Result
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Represents a structured data unit extracted by a SiteExtractor.

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Result:
    """Structured extraction result for ShadowCrawler v4.1.1.

    Represents a normalized data payload produced by a SiteExtractor.
    Consumed by:
        - MediaExtractor
        - CrawlerEngine
        - Output pipelines (future)
        - Exporters (CSV/JSON/etc. in future versions)

    Notes:
        - Contains no site‑specific logic.
        - Fully serializable for checkpointing.
    """

    data: Dict[str, Any]
    source_url: str
    spider_name: str

    # ------------------------------------------------------------
    # REPRESENTATION
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        size = len(self.data) if isinstance(self.data, dict) else "?"
        return (
            f"Result(source={self.source_url}, spider={self.spider_name}, "
            f"fields={size})"
        )
