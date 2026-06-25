# shadowcrawler/core/checkpoint_manager.py
# ShadowCrawler v4.1.0 — Unified Checkpoint Manager
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Stores and restores the full Engine state for:
#   - run.py
#   - resume.py
#   - download.py
#
# Checkpoints include:
#   - frontier.seen
#   - frontier.queues
#   - frontier.stats
#   - media_items
#   - spider_name
#   - output_folder
#   - browser enabled/disabled
#   - debug / verbose
#   - max_pages
#   - user_agent
#   - delay
#   - save_data
#   - no_media
#   - fetch_mode (NEW in v4.x)

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from shadowcrawler.models.request import Request
from shadowcrawler.core.media import MediaItem
from shadowcrawler.logging import get_logger


class CheckpointManager:
    """Unified checkpoint manager for ShadowCrawler v4.1.0.

    Responsible for:
        - Serializing the full Engine state into a JSON checkpoint.
        - Restoring a lightweight CP object for resume/download.
        - Ensuring compatibility across run/resume/download workflows.

    Args:
        path: Path to the checkpoint file.
    """

    def __init__(self, path: str = "checkpoint.json") -> None:
        self.path = Path(path)
        self.logger = get_logger("engine")

    # ------------------------------------------------------------
    # SAVE (engine → checkpoint.json)
    # ------------------------------------------------------------
    def save(self, engine: Any) -> None:
        """Save the full Engine state to a JSON checkpoint.

        Args:
            engine: The running CrawlerEngine instance.
        """
        data: Dict[str, Any] = {
            "frontier": {
                "seen": list(engine.frontier.seen),
                "queues": {
                    str(priority): [req.url for req in queue]
                    for priority, queue in engine.frontier.queues.items()
                },
                "stats": engine.frontier.status(),
            },

            # Serialized media items
            "media_items": [
                item.__dict__ for item in getattr(engine, "media_items", [])
            ],

            # Engine configuration
            "spider_name": engine.spider_name,
            "output_folder": engine.output_folder,
            "browser": engine.browser_manager is not None,
            "debug": getattr(engine, "debug", False),
            "verbose": getattr(engine, "verbose", False),
            "max_pages": engine.max_pages,
            "user_agent": engine.user_agent,
            "delay": engine.delay,
            "save_data": engine.save_data,
            "no_media": getattr(engine.media_extractor, "disabled", False),

            # NEW: fetch mode (http / browser)
            "fetch_mode": getattr(engine, "fetch_mode", "http"),
        }

        self.path.write_text(json.dumps(data, indent=2))
        self.logger.info(f"Checkpoint saved → {self.path}")

    # ------------------------------------------------------------
    # LOAD (checkpoint.json → CP object)
    # ------------------------------------------------------------
    @staticmethod
    def load(path: str) -> Any:
        """Load a checkpoint and return a lightweight CP object.

        Args:
            path: Path to the checkpoint file.

        Returns:
            A CP object containing all necessary state for resume/download.
        """
        path = Path(path)
        raw = json.loads(path.read_text())

        # Rebuild media items
        media_items: List[MediaItem] = [
            MediaItem(**m) for m in raw.get("media_items", [])
        ]

        # Rebuild frontier data
        frontier_raw = raw.get("frontier", {})
        seen = set(frontier_raw.get("seen", []))
        queues = frontier_raw.get("queues", {})
        stats = frontier_raw.get("stats", {})

        # Simple container object
        class CP:
            pass

        cp = CP()
        cp.media_items = media_items
        cp.seen = seen
        cp.queues = queues
        cp.stats = stats

        # Engine configuration
        cp.spider_name = raw.get("spider_name")
        cp.output_folder = raw.get("output_folder")
        cp.browser = raw.get("browser", False)
        cp.debug = raw.get("debug", False)
        cp.verbose = raw.get("verbose", False)
        cp.max_pages = raw.get("max_pages")
        cp.user_agent = raw.get("user_agent")
        cp.delay = raw.get("delay")
        cp.save_data = raw.get("save_data", True)
        cp.no_media = raw.get("no_media", False)

        # NEW: fetch mode
        cp.fetch_mode = raw.get("fetch_mode", "http")

        return cp
