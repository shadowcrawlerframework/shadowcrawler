# shadowcrawler/audit/audit_logger.py
# ShadowCrawler v4.1.0 — Audit Logger
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# This software is licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Industrial-grade audit logger for ShadowCrawler.

This module provides:
    - JSONL-based failure logging for media download errors.
    - Counters grouped by media type and error type.
    - Execution metadata (run_id, spider_name, fetch_mode).
    - Optional human-readable summary output.

Audit logs are designed for:
    - Debugging download failures.
    - Post-run analysis.
    - Automated QA pipelines.
    - Large-scale crawling diagnostics.
"""

import json
from datetime import datetime
from collections import Counter
from typing import Any, Optional


class AuditLogger:
    """Audit logger for tracking media download failures.

    Responsibilities:
        - Write one JSONL entry per failure.
        - Maintain counters by media type and error type.
        - Attach execution metadata (run_id, spider_name, fetch_mode).
        - Provide an optional summary at the end of the crawl.

    Attributes:
        path: Path to the JSONL audit file.
        total: Total number of failures recorded.
        by_type: Counter of failures grouped by media type.
        by_error: Counter of failures grouped by error string.
        run_id: Unique identifier for this crawl session.
        spider_name: Optional name of the active spider.
        fetch_mode: Optional fetch mode ("http" or "browser").
    """

    def __init__(
        self,
        path: str = "audit_fails.jsonl",
        spider_name: Optional[str] = None,
        fetch_mode: Optional[str] = None,
    ) -> None:
        """Initialize a new AuditLogger instance.

        Args:
            path: Path to the JSONL audit file.
            spider_name: Optional name of the active spider.
            fetch_mode: Optional fetch mode ("http" or "browser").
        """
        self.path: str = path
        self.total: int = 0
        self.by_type: Counter = Counter()
        self.by_error: Counter = Counter()

        # Execution metadata
        self.run_id: str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.spider_name: Optional[str] = spider_name
        self.fetch_mode: Optional[str] = fetch_mode

    # ------------------------------------------------------------
    # Record Failure
    # ------------------------------------------------------------
    def fail(self, media: Any, error: Exception) -> None:
        """Record a failure event and append it to the JSONL audit file.

        Args:
            media: MediaItem instance (or similar object).
            error: Exception or error message.

        Notes:
            This method never raises; failures in audit logging
            should not interrupt the crawl.
        """
        media_type = getattr(media, "media_type", None)
        error_str = str(error)

        # Update counters
        self.total += 1
        self.by_type[media_type] += 1
        self.by_error[error_str] += 1

        # Build JSONL entry
        entry = {
            "run_id": self.run_id,
            "timestamp": datetime.utcnow().isoformat(),

            # Context metadata
            "spider": self.spider_name,
            "fetch_mode": self.fetch_mode,

            # Media details
            "url": getattr(media, "url", None),
            "page": getattr(media, "page", None),
            "type": media_type,
            "error": error_str,
        }

        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            # Audit logging must never break the crawl
            pass

    # ------------------------------------------------------------
    # Summary Output
    # ------------------------------------------------------------
    def print_summary(self) -> None:
        """Print a human-readable summary of all failures recorded."""
        print("\n====================")
        print(" AUDIT SUMMARY")
        print("====================")
        print(f"Run ID: {self.run_id}")
        print(f"Total failures: {self.total}")

        if self.by_type:
            print("\nBy media type:")
            for t, c in self.by_type.items():
                print(f"  {t}: {c}")

        if self.by_error:
            print("\nBy error type:")
            for e, c in self.by_error.items():
                print(f"  {e}: {c}")

        print("====================\n")
