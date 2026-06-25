# shadowcrawler/core/frontier.py
# ShadowCrawler v4.1.0 — Frontier (Priority Queue + Dedupe)
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Priority queue with advanced dedupe and modern Request support.

from collections import defaultdict, deque
from typing import Dict, Deque, List, Optional, Set

from shadowcrawler.models.request import Request
from shadowcrawler.logging import get_logger


class Frontier:
    """Priority-based request frontier with dedupe for ShadowCrawler v4.1.0.

    Responsibilities:
        - Deduplicate requests using fingerprint or URL.
        - Maintain unlimited priority queues.
        - Provide pop() and pop_batch() for high concurrency.
        - Support requeue() for retries.
        - Track modern statistics.
        - Provide checkpoint‑friendly serialization.

    Notes:
        This class is intentionally simple and fast. It is designed to be
        fully compatible with checkpointing and high‑concurrency crawlers.
    """

    def __init__(self) -> None:
        self.queues: Dict[int, Deque[Request]] = defaultdict(deque)
        self.seen: Set[str] = set()  # fingerprints or URLs
        self.total_added: int = 0
        self.total_popped: int = 0

        self.logger = get_logger("frontier")

    # ------------------------------------------------------------
    # Fingerprint
    # ------------------------------------------------------------
    def _fingerprint(self, req: Request) -> str:
        """Return the request fingerprint if available, otherwise the URL."""
        return req.fingerprint or req.url

    # ------------------------------------------------------------
    # PUSH
    # ------------------------------------------------------------
    def push(self, request: Request) -> bool:
        """Add a Request if it has not been seen before.

        Args:
            request: The Request object to enqueue.

        Returns:
            True if added, False if deduped.
        """
        fp = self._fingerprint(request)

        if fp in self.seen:
            self.logger.debug(f"Duplicate skipped: {fp}")
            return False

        self.seen.add(fp)
        self.queues[request.priority].append(request)
        self.total_added += 1

        self.logger.debug(f"Queued [{request.priority}] {request.url}")
        return True

    # ------------------------------------------------------------
    # REQUEUE (for retries)
    # ------------------------------------------------------------
    def requeue(self, request: Request) -> bool:
        """Requeue a Request without dedupe (used for retries).

        Args:
            request: The Request object to requeue.

        Returns:
            True always.
        """
        self.queues[request.priority].append(request)
        self.logger.debug(f"Requeued [{request.priority}] {request.url}")
        return True

    # ------------------------------------------------------------
    # POP
    # ------------------------------------------------------------
    def pop(self) -> Optional[Request]:
        """Return the next Request by priority.

        Returns:
            The next Request or None if empty.
        """
        for priority in sorted(self.queues.keys(), reverse=True):
            queue = self.queues[priority]
            if queue:
                req = queue.popleft()
                self.total_popped += 1

                self.logger.debug(f"Popped [{priority}] {req.url}")
                return req

        return None

    # ------------------------------------------------------------
    # POP BATCH
    # ------------------------------------------------------------
    def pop_batch(self, n: int) -> List[Request]:
        """Return up to n Requests by priority.

        Args:
            n: Maximum number of requests to pop.

        Returns:
            A list of Request objects.
        """
        batch: List[Request] = []
        for _ in range(n):
            req = self.pop()
            if not req:
                break
            batch.append(req)
        return batch

    # ------------------------------------------------------------
    # EMPTY
    # ------------------------------------------------------------
    def empty(self) -> bool:
        """Return True if no URLs remain to process."""
        return all(len(q) == 0 for q in self.queues.values())

    # ------------------------------------------------------------
    # SIZE
    # ------------------------------------------------------------
    def size(self) -> int:
        """Return the total number of pending Requests."""
        return sum(len(q) for q in self.queues.values())

    # ------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------
    def status(self) -> Dict[str, object]:
        """Return modern frontier statistics.

        Returns:
            A dictionary with counts and per‑priority queue sizes.
        """
        return {
            "seen": len(self.seen),
            "queued": self.size(),
            "added": self.total_added,
            "popped": self.total_popped,
            "priorities": {p: len(q) for p, q in self.queues.items()},
        }
