# shadowcrawler/core/crawler_engine.py
# ShadowCrawler v4.1.1 — Asynchronous Crawling Engine
#
# ShadowCrawler — Copyright © 2024–2030 Allan Mancera
# This software is licensed under the Business Source License 1.1 (BUSL‑1.1).

"""
Asynchronous crawling engine for ShadowCrawler.

This module provides the core orchestration logic for crawling sessions:
  - Consumes a Frontier until it is empty or a max_pages limit is reached.
  - Selects between HTTP and browser-based fetchers per Request.
  - Integrates with an optional AuthHandler for browser login flows.
  - Normalizes parsed data and media via MediaExtractor.
  - Enqueues new Requests directly from the parser (SpiderAdapter).
  - Supports checkpointing for long-running crawls.
  - Integrates with the centralized logging system and CLI flags.
"""

import asyncio
import inspect
from typing import Optional, List, Any

from shadowcrawler.fetcher.playwright_fetcher import PlaywrightFetcher
from shadowcrawler.fetcher.requests_fetcher import RequestsFetcher
from shadowcrawler.core.browser_manager import BrowserManager
from shadowcrawler.core.frontier import Frontier
from shadowcrawler.core.media_extractor import MediaExtractor
from shadowcrawler.core.checkpoint_manager import CheckpointManager
from shadowcrawler.models.request import Request
from shadowcrawler.logging import (
    get_logger,
    set_global_level,
    enable_module_debug,
)


class CrawlerEngine:
    """Core asynchronous crawling engine for ShadowCrawler.

    Responsibilities:
        - Orchestrate asynchronous crawling across multiple workers.
        - Consume the Frontier until it is empty or max_pages is reached.
        - Use HTTP or Playwright-based browser fetching per Request.
        - Pass responses to the SpiderAdapter parser.
        - Normalize data and media via MediaExtractor.
        - Enqueue links and next_pages directly from the parser.
        - Support optional AuthHandler for browser login flows.
        - Persist state periodically via CheckpointManager.

    Attributes:
        frontier: Frontier instance providing Requests to crawl.
        media_extractor: MediaExtractor used to normalize data/media.
        browser_manager: Optional BrowserManager for browser sessions.
        max_pages: Optional maximum number of pages to crawl.
        user_agent: Optional User-Agent string for HTTP requests.
        delay: Optional delay (in seconds) between page fetches.
        save_data: Whether to store parsed results in memory.
        output_folder: Optional output folder for downstream components.
        checkpoint_file: Optional path to a checkpoint file.
        spider_name: Optional name of the active spider.
        concurrency: Number of concurrent worker tasks.
        debug: Optional debug module name or "all".
        verbose: Whether to enable global DEBUG logging.
        auth_handler: Optional AuthHandler for browser login/session flows.
    """

    def __init__(
        self,
        frontier: Frontier,
        media_extractor: MediaExtractor,
        browser_manager: Optional[BrowserManager] = None,
        max_pages: Optional[int] = None,
        user_agent: Optional[str] = None,
        delay: Optional[float] = None,
        save_data: bool = True,
        output_folder: Optional[str] = None,
        checkpoint_file: Optional[str] = None,
        spider_name: Optional[str] = None,
        concurrency: int = 2,
        debug: Optional[str] = None,
        verbose: bool = False,
        auth_handler: Optional[Any] = None,
    ) -> None:
        """Initialize a new CrawlerEngine instance.

        Args:
            frontier: Frontier instance that provides Requests to crawl.
            media_extractor: MediaExtractor used to normalize data/media.
            browser_manager: Optional BrowserManager for browser sessions.
            max_pages: Optional maximum number of pages to crawl.
            user_agent: Optional User-Agent string for HTTP requests.
            delay: Optional delay (in seconds) between page fetches.
            save_data: Whether to store parsed results in memory.
            output_folder: Optional output folder for downstream components.
            checkpoint_file: Optional path to a checkpoint file.
            spider_name: Optional name of the active spider.
            concurrency: Number of concurrent worker tasks.
            debug: Optional debug module name or "all" for all modules.
            verbose: Whether to enable global DEBUG logging.
            auth_handler: Optional AuthHandler for browser login/session flows.
        """
        # --------------------------------------------------------
        # Global logging configuration
        # --------------------------------------------------------
        if verbose:
            set_global_level("DEBUG")

        if debug:
            if debug == "all":
                for module in [
                    "engine",
                    "frontier",
                    "browser",
                    "extractor",
                    "downloader",
                ]:
                    enable_module_debug(module)
            else:
                enable_module_debug(debug)

        # Store debug/verbose for checkpointing or future use
        self.debug: Optional[str] = debug
        self.verbose: bool = verbose

        self.logger = get_logger("engine")
        self.logger.info("Initializing ShadowCrawler Engine v4.1.1")

        # Base components
        self.frontier: Frontier = frontier
        self.media_extractor: MediaExtractor = media_extractor

        # Fetch mode (assigned externally in run.py)
        self.fetch_mode: str = "http"

        # BrowserManager (may be activated later)
        self.browser_manager: Optional[BrowserManager] = browser_manager

        # Engine configuration
        self.max_pages: Optional[int] = max_pages
        self.user_agent: Optional[str] = user_agent
        self.delay: float = delay or 0.0
        self.save_data: bool = save_data
        self.output_folder: Optional[str] = output_folder
        self.checkpoint_file: Optional[str] = checkpoint_file
        self.spider_name: Optional[str] = spider_name
        self.concurrency: int = concurrency

        # Crawl state
        self.pages: int = 0
        self.results: List[Any] = []
        self.media_items: List[Any] = []

        # Checkpoint manager
        self.checkpoint: Optional[CheckpointManager] = None
        if self.checkpoint_file:
            try:
                self.checkpoint = CheckpointManager(self.checkpoint_file)
                self.logger.info("Checkpoint enabled: %s", self.checkpoint_file)
            except Exception as exc:  # noqa: BLE001
                self.logger.error("Failed to initialize checkpoint: %s", exc)
                self.checkpoint = None

        # Fetchers
        self.http_fetcher: RequestsFetcher = RequestsFetcher(
            user_agent=self.user_agent
        )
        self.browser_fetcher: Optional[PlaywrightFetcher] = None  # Activated lazily

        # Parser (SpiderAdapter) — injected externally
        self.parser: Optional[Any] = None

        # Optional AuthHandler
        self.auth_handler: Optional[Any] = auth_handler

    # ------------------------------------------------------------
    # Browser activation
    # ------------------------------------------------------------
    def activate_browser_if_needed(self) -> None:
        """Activate the browser fetcher if fetch_mode requires it.

        This method:
            - Creates a BrowserManager automatically if fetch_mode is "browser"
              and no BrowserManager was provided.
            - Instantiates a PlaywrightFetcher if a BrowserManager is available
              and no browser_fetcher exists yet.
        """
        if self.fetch_mode == "browser" and self.browser_manager is None:
            self.logger.info(
                "fetch_mode=browser → creating BrowserManager automatically"
            )
            self.browser_manager = BrowserManager()

        if self.browser_manager and self.browser_fetcher is None:
            self.browser_fetcher = PlaywrightFetcher(self.browser_manager)

    # ------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------
    async def worker(self, worker_id: int) -> None:
        """Worker task that processes Requests from the Frontier.

        Each worker:
            - Pops Requests from the Frontier.
            - Respects the max_pages limit if configured.
            - Uses HTTP or browser fetching based on Request metadata.
            - Passes responses to the parser (SpiderAdapter).
            - Normalizes data/media via MediaExtractor.
            - Enqueues new Requests from parsed links and next_pages.
            - Optionally saves checkpoints periodically.

        Args:
            worker_id: Numeric identifier for this worker.
        """
        logger = get_logger("engine")

        while True:
            req: Optional[Request] = self.frontier.pop()
            if req is None:
                logger.debug("Worker %d has no more requests, exiting", worker_id)
                return

            if self.max_pages is not None and self.pages >= self.max_pages:
                logger.debug(
                    "Worker %d reached max_pages=%s, exiting",
                    worker_id,
                    self.max_pages,
                )
                return

            try:
                logger.debug("Worker %d fetching: %s", worker_id, req.url)

                use_browser: bool = bool(req.meta.get("use_browser", False))

                # ---------------------------------------------------
                # Fetchers receive URL + META
                # ---------------------------------------------------
                if use_browser:
                    if not self.browser_fetcher:
                        logger.error(
                            "Browser fetch requested but no browser_manager provided"
                        )
                        continue

                    resp = await self.browser_fetcher.fetch(
                        req.url,
                        req.meta,
                        auth_handler=self.auth_handler,
                    )

                    # ---------------------------------------------------
                    # AUTH: detect login requirement and perform login
                    # ---------------------------------------------------
                    if (
                        self.auth_handler
                        and resp is not None
                        and getattr(resp, "from_browser", False)
                        and getattr(resp, "browser_page", None) is not None
                    ):
                        page = resp.browser_page
                        try:
                            requires_login = await self.auth_handler.is_login_required(
                                page
                            )
                        except Exception as exc:  # noqa: BLE001
                            logger.error(
                                "AuthHandler.is_login_required() failed on %s: %s",
                                req.url,
                                exc,
                            )
                            requires_login = False

                        if requires_login:
                            logger.debug(
                                "Auth required for %s, running perform_login()",
                                req.url,
                            )
                            try:
                                await self.auth_handler.perform_login(page)

                                ctx = page.context
                                try:
                                    await self.auth_handler.save_session(ctx)
                                except Exception as exc:  # noqa: BLE001
                                    logger.error(
                                        "AuthHandler.save_session() failed: %s",
                                        exc,
                                    )

                                try:
                                    html = await page.evaluate(
                                        "document.documentElement.outerHTML"
                                    )
                                    resp.html = html
                                    resp.url = page.url
                                except Exception as exc:  # noqa: BLE001
                                    logger.error(
                                        "Failed to refresh HTML after login on %s: %s",
                                        req.url,
                                        exc,
                                    )

                            except Exception as exc:  # noqa: BLE001
                                logger.error(
                                    "AuthHandler.perform_login() failed on %s: %s",
                                    req.url,
                                    exc,
                                )

                else:
                    resp = self.http_fetcher.fetch(req.url, req.meta)

                if self.parser is None:
                    logger.error("No parser configured in CrawlerEngine")
                    continue

                if resp is None:
                    logger.error(
                        "Worker %d got no response for %s", worker_id, req.url
                    )
                    continue

                # 1) Parse with SpiderAdapter (sync or async)
                parsed = self.parser.parse(resp)
                if inspect.iscoroutine(parsed):
                    parsed = await parsed

                # 2) Normalize ONLY data/media via MediaExtractor
                data_dict = {
                    "data": parsed.data,
                    "media": parsed.media,
                }

                results, _, media_items = self.media_extractor.extract(
                    data=data_dict,
                    source_url=getattr(resp, "url", req.url),
                    spider_name=self.spider_name or "unknown",
                )

                # 3) Register structured data
                if self.save_data:
                    self.results.extend(results)

                # 4) Register media
                self.media_items.extend(media_items)

                # 5) Enqueue new requests directly from SpiderAdapter
                for r in parsed.links:
                    self.frontier.push(r)

                for r in parsed.next_pages:
                    self.frontier.push(r)

                # 6) Page counter
                self.pages += 1

                # 7) Optional delay
                if self.delay > 0:
                    await asyncio.sleep(self.delay)

                # 8) Optional checkpoint (every 25 pages)
                if self.checkpoint and (self.pages % 25 == 0):
                    try:
                        self.checkpoint.save(self)
                        logger.debug("Checkpoint saved")
                    except Exception as exc:  # noqa: BLE001
                        logger.error("Checkpoint save failed: %s", exc)

            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Worker %d failed fetching %s: %s", worker_id, req.url, exc
                )

    # ------------------------------------------------------------
    # Run (async)
    # ------------------------------------------------------------
    async def run(self, start_url: str) -> List[Any]:
        """Run the crawling session asynchronously.

        Note:
            The `start_url` parameter is accepted for future compatibility
            and potential seeding logic, but the current implementation
            assumes that the Frontier is already seeded externally.

        Args:
            start_url: Optional starting URL (currently unused).

        Returns:
            A list of parsed result items collected during the crawl.
        """
        logger = get_logger("engine")
        logger.info("Starting crawl session")

        # Activate browser if fetch_mode requires it
        self.activate_browser_if_needed()

        tasks: List[asyncio.Task[Any]] = [
            asyncio.create_task(self.worker(i))
            for i in range(self.concurrency)
        ]

        await asyncio.gather(*tasks)

        logger.info("Crawl session finished")
        logger.info("Total pages: %d", self.pages)
        logger.info("Total results: %d", len(self.results))
        logger.info("Total media items: %d", len(self.media_items))

        # Final checkpoint
        if self.checkpoint:
            try:
                self.checkpoint.save(self)
                logger.debug("Final checkpoint saved")
            except Exception as exc:  # noqa: BLE001
                logger.error("Final checkpoint save failed: %s", exc)

        return self.results
