# shadowcrawler/core/dedupe_index.py
# ShadowCrawler v4.1.1 — Dedupe Index
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Global hash index to prevent duplicate media downloads.
# Features:
#   - JSON persistence
#   - Atomic writes
#   - Thread‑safe operations
#   - Orphan cleanup
#   - Modular logging

import os
import json
import hashlib
import threading
from pathlib import Path
from typing import Dict, Optional

from shadowcrawler.logging import get_logger


class DedupeIndex:
    """Thread‑safe global deduplication index for media downloads.

    Responsibilities:
        - Track SHA‑256 hashes of downloaded media.
        - Prevent duplicate downloads across sessions.
        - Persist index to disk using atomic writes.
        - Clean orphaned entries when files are deleted.
        - Provide safe concurrent access via threading.Lock.

    Args:
        index_path: Path to the JSON dedupe index file.
    """

    def __init__(self, index_path: str = "dedupe_index.json") -> None:
        self.index_path = Path(index_path)
        self.lock = threading.Lock()
        self.index: Dict[str, str] = {}

        self.logger = get_logger("downloader")

        self._load()

    # ------------------------------------------------------------
    # LOAD
    # ------------------------------------------------------------
    def _load(self) -> None:
        """Load the dedupe index from disk."""
        if self.index_path.exists():
            try:
                self.index = json.loads(self.index_path.read_text())
                self.logger.debug(
                    f"Dedupe index loaded ({len(self.index)} entries)"
                )
            except Exception as exc:
                self.logger.error(f"Failed to load dedupe index: {exc}")
                self.index = {}
        else:
            self.logger.debug("No dedupe index found, starting fresh")

    # ------------------------------------------------------------
    # SAVE (ATOMIC)
    # ------------------------------------------------------------
    def _save(self) -> None:
        """Persist the index using atomic write."""
        try:
            tmp = self.index_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.index, indent=2))
            tmp.replace(self.index_path)
            self.logger.debug("Dedupe index saved")
        except Exception as exc:
            self.logger.error(f"Failed to save dedupe index: {exc}")

    # ------------------------------------------------------------
    # HASH
    # ------------------------------------------------------------
    def compute_hash(self, data: bytes) -> str:
        """Compute SHA‑256 hash of raw bytes.

        Args:
            data: Raw binary data.

        Returns:
            Hexadecimal SHA‑256 hash string.
        """
        return hashlib.sha256(data).hexdigest()

    # ------------------------------------------------------------
    # HAS
    # ------------------------------------------------------------
    def has(self, hash_value: str) -> bool:
        """Return True if the hash already exists in the index.

        Args:
            hash_value: SHA‑256 hash string.

        Returns:
            True if present, False otherwise.
        """
        with self.lock:
            return hash_value in self.index

    # ------------------------------------------------------------
    # ADD
    # ------------------------------------------------------------
    def add(self, hash_value: str, file_path: str) -> None:
        """Add a hash → file_path entry and persist the change.

        Args:
            hash_value: SHA‑256 hash string.
            file_path: Path to the downloaded file.
        """
        with self.lock:
            self.index[hash_value] = file_path
            self._save()

    # ------------------------------------------------------------
    # CLEAN ORPHANS
    # ------------------------------------------------------------
    def clean_orphans(self) -> None:
        """Remove hashes pointing to files that no longer exist."""
        with self.lock:
            to_delete = [
                h for h, path in self.index.items()
                if not os.path.exists(path)
            ]

            for h in to_delete:
                del self.index[h]

            if to_delete:
                self.logger.info(
                    f"Cleaned {len(to_delete)} orphaned dedupe entries"
                )
                self._save()
            else:
                self.logger.debug("No orphaned dedupe entries found")
