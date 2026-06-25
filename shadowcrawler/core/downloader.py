# shadowcrawler/core/downloader.py
# ShadowCrawler v4.1.1 — Universal Downloader
#
# ShadowCrawler © 2024–2030 Allan Mancera
# Licensed under the Business Source License 1.1 (BUSL‑1.1).
#
# Features:
#   - HTTPX streaming (in a worker thread)
#   - Playwright fallbacks:
#       * context.request.get()
#       * page.goto()
#       * in‑page fetch() (bypass some 403/Referer issues)
#   - Persistent dedupe (disk scan)
#   - In‑memory dedupe
#   - Hybrid hash (start + end + size)
#   - “Vendible” naming style:
#       00001_belle_delphine_a2afd0b666.jpg
#   - Global incremental prefix per folder
#   - Fix: Playwright .body() instead of .read()
#   - Fix: rename() with retry for WinError 32
#   - No site‑specific logic (spiders provide everything)

import os
import hashlib
import httpx
import asyncio
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set, Tuple

from shadowcrawler.logging import get_logger


class Downloader:
    """Universal media downloader for ShadowCrawler.

    Responsibilities:
        - Download media via HTTPX (primary).
        - Fallback to Playwright when needed.
        - Deduplicate downloads (in‑memory + on‑disk).
        - Generate consistent, “vendible” filenames.
        - Handle platform quirks (e.g., Windows rename issues).

    Args:
        output_dir: Target directory for downloaded files.
        workers: Maximum concurrent downloads.
        browser_context: Optional Playwright BrowserContext for fallbacks.
    """

    def __init__(self, output_dir: str, workers: int = 4, browser_context: Optional[Any] = None) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.workers = workers
        self.browser_context = browser_context
        self.logger = get_logger("downloader")

        # In‑memory dedupe
        self._seen_hashes: Set[str] = set()

        # Global incremental prefix
        self._counter: int = self._detect_next_counter()

        # Persistent dedupe (scan existing files)
        self._load_existing_hashes()

    # ------------------------------------------------------------
    # Global incremental prefix
    # ------------------------------------------------------------
    def _detect_next_counter(self) -> int:
        """Detect the next numeric prefix based on existing files."""
        nums = []
        for f in self.output_dir.glob("*.*"):
            name = f.name
            if "_" in name:
                prefix = name.split("_")[0]
                if prefix.isdigit():
                    nums.append(int(prefix))
        return max(nums) + 1 if nums else 1

    # ------------------------------------------------------------
    # Persistent dedupe
    # ------------------------------------------------------------
    def _load_existing_hashes(self) -> None:
        """Scan existing files and populate the in‑memory dedupe set."""
        self.logger.info("Scanning existing files for dedupe...")

        for file in self.output_dir.iterdir():
            if not file.is_file():
                continue

            try:
                h = self._compute_hybrid_hash_sync(file)
                self._seen_hashes.add(h)
                self.logger.debug(f"[dedupe] Existing file OK → {file.name}")
            except Exception as exc:
                self.logger.error(f"[dedupe] Failed hashing {file}: {exc}")

        self.logger.info(f"Dedupe loaded: {len(self._seen_hashes)} existing files")

    # ------------------------------------------------------------
    # Helpers: file type detection
    # ------------------------------------------------------------
    def _detect_extension(self, head: bytes, content_type: Optional[str]) -> str:
        """Detect file extension from content-type and magic bytes."""
        ct = (content_type or "").lower()

        if "image/jpeg" in ct:
            return ".jpg"
        if "image/png" in ct:
            return ".png"
        if "image/gif" in ct:
            return ".gif"
        if "image/webp" in ct:
            return ".webp"
        if "video/mp4" in ct:
            return ".mp4"

        if head.startswith(b"\xFF\xD8\xFF"):
            return ".jpg"
        if head.startswith(b"\x89PNG"):
            return ".png"
        if head.startswith(b"GIF8"):
            return ".gif"
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            return ".webp"
        if len(head) >= 12 and head[4:8] == b"ftyp":
            return ".mp4"

        if "image" in ct:
            return ".img"
        if "video" in ct:
            return ".vid"

        return ".bin"

    def _extract_filename_from_cd(self, cd: Optional[str]) -> Optional[str]:
        """Extract filename from Content-Disposition header, if present."""
        if not cd:
            return None
        parts = cd.split("filename=")
        if len(parts) < 2:
            return None
        name = parts[1].strip().strip('"').strip("'")
        return name or None

    # ------------------------------------------------------------
    # Helpers: names and paths (v4.7)
    # ------------------------------------------------------------
    def _normalize_base(self, name: str) -> str:
        """Normalize a base filename into a safe, vendible form."""
        name = name.replace("-", "_").replace(" ", "_").replace("%20", "_")
        name = "".join(c for c in name if c.isalnum() or c in "_")
        return name.lower().strip("_") or "file"

    def _make_vendible_filename(self, url: str, ext: str) -> str:
        """Generate a vendible filename with prefix + base + short hash."""
        clean = url.split("?")[0].split("#")[0]
        base = os.path.basename(clean) or "file"
        base = os.path.splitext(base)[0]
        base = self._normalize_base(base)

        # Short hash based on URL
        url_hash = hashlib.md5(clean.encode()).hexdigest()[:10]

        # Global incremental prefix
        prefix = f"{self._counter:05d}"
        self._counter += 1

        return f"{prefix}_{base}_{url_hash}{ext}"

    # ------------------------------------------------------------
    # Helpers: hybrid hash
    # ------------------------------------------------------------
    def _compute_hybrid_hash_sync(self, path: Path) -> str:
        """Compute a hybrid SHA‑256 hash based on file start, end, and size."""
        size = path.stat().st_size
        h = hashlib.sha256()

        with path.open("rb") as f:
            if size <= 50 * 1024 * 1024:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            else:
                first = f.read(32 * 1024 * 1024)
                h.update(first)

                if size > 4 * 1024 * 1024:
                    f.seek(-4 * 1024 * 1024, os.SEEK_END)
                else:
                    f.seek(0, os.SEEK_SET)

                last = f.read(4 * 1024 * 1024)
                h.update(last)
                h.update(str(size).encode("utf-8"))

        return h.hexdigest()

    async def _compute_hybrid_hash(self, path: Path) -> str:
        """Async wrapper for hybrid hash computation in a worker thread."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._compute_hybrid_hash_sync, path)

    # ------------------------------------------------------------
    # Core download via HTTPX (sync in a thread)
    # ------------------------------------------------------------
    def _download_httpx_sync(self, media: Any) -> Tuple[Optional[Path], Optional[str]]:
        """Synchronous HTTPX streaming download, executed in a worker thread."""
        url = getattr(media, "url", None)
        if not url:
            return None, "no-url"

        headers: Dict[str, str] = getattr(media, "headers", {}) or {}
        cookies_raw = getattr(media, "cookies", None) or []
        cookies = {c["name"]: c["value"] for c in cookies_raw}

        try:
            with httpx.stream(
                "GET",
                url,
                headers=headers,
                cookies=cookies,
                timeout=30.0,
                follow_redirects=True,
            ) as resp:
                if resp.status_code != 200:
                    return None, f"status-{resp.status_code}"

                iter_chunks = resp.iter_bytes()
                try:
                    first_chunk = next(iter_chunks)
                except StopIteration:
                    first_chunk = b""

                head = first_chunk
                content_type = resp.headers.get("Content-Type")
                cd = resp.headers.get("Content-Disposition")

                ext = self._detect_extension(head, content_type)
                cd_name = self._extract_filename_from_cd(cd)

                filename = self._make_vendible_filename(url, ext)
                target = self.output_dir / filename
                tmp = target.with_suffix(target.suffix + ".tmp")

                with tmp.open("wb") as f:
                    if first_chunk:
                        f.write(first_chunk)
                    for chunk in iter_chunks:
                        f.write(chunk)

            return tmp, None

        except httpx.HTTPStatusError as exc:
            return None, f"status-{exc.response.status_code}"
        except Exception as exc:
            return None, f"error-{exc}"

    async def _download_httpx(self, media: Any) -> Tuple[Optional[Path], Optional[str]]:
        """Async wrapper for HTTPX download in a worker thread."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._download_httpx_sync, media)

    # ------------------------------------------------------------
    # Fallback 1: Playwright context.request.get()
    # ------------------------------------------------------------
    async def _download_playwright_request(self, media: Any) -> Tuple[Optional[Path], Optional[str]]:
        """Download using Playwright's context.request.get()."""
        if not self.browser_context:
            return None, "no-browser"

        url = getattr(media, "url", None)
        if not url:
            return None, "no-url"

        headers: Dict[str, str] = getattr(media, "headers", {}) or {}
        cookies_raw = getattr(media, "cookies", None) or []
        cookies = {c["name"]: c["value"] for c in cookies_raw}

        referer = headers.get("Referer") or headers.get("referer")

        try:
            if cookies:
                cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                headers = headers.copy()
                headers["Cookie"] = cookie_header

            kwargs: Dict[str, Any] = {"headers": headers}
            if referer:
                kwargs["referrer"] = referer
                kwargs["referrer_policy"] = "strict-origin-when-cross-origin"

            resp = await self.browser_context.request.get(url, **kwargs)
            if resp.status != 200:
                return None, f"status-{resp.status}"

            body = await resp.body()

            head = body[:4096]
            content_type = resp.headers.get("content-type")
            cd = resp.headers.get("content-disposition")

            ext = self._detect_extension(head, content_type)
            cd_name = self._extract_filename_from_cd(cd)

            filename = self._make_vendible_filename(url, ext)
            target = self.output_dir / filename
            tmp = target.with_suffix(target.suffix + ".tmp")

            with tmp.open("wb") as f:
                f.write(body)

            return tmp, None

        except Exception as exc:
            return None, f"error-{exc}"

    # ------------------------------------------------------------
    # Fallback 2: Playwright page.goto()
    # ------------------------------------------------------------
    async def _download_playwright_page_goto(self, media: Any) -> Tuple[Optional[Path], Optional[str]]:
        """Download using Playwright's page.goto()."""
        if not self.browser_context:
            return None, "no-browser"

        url = getattr(media, "url", None)
        if not url:
            return None, "no-url"

        headers: Dict[str, str] = getattr(media, "headers", {}) or {}
        referer = headers.get("Referer") or headers.get("referer")

        try:
            page = await self.browser_context.new_page()

            kwargs: Dict[str, Any] = {}
            if referer:
                kwargs["referer"] = referer
                kwargs["referrer_policy"] = "strict-origin-when-cross-origin"

            resp = await page.goto(url, **kwargs)

            if not resp or resp.status != 200:
                status = resp.status if resp else "no-response"
                await page.close()
                return None, f"status-{status}"

            body = await resp.body()

            head = body[:4096]
            content_type = resp.headers.get("content-type")
            cd = resp.headers.get("content-disposition")

            ext = self._detect_extension(head, content_type)
            cd_name = self._extract_filename_from_cd(cd)

            filename = self._make_vendible_filename(url, ext)
            target = self.output_dir / filename
            tmp = target.with_suffix(target.suffix + ".tmp")

            with tmp.open("wb") as f:
                f.write(body)

            await page.close()
            return tmp, None

        except Exception as exc:
            return None, f"error-{exc}"

    # ------------------------------------------------------------
    # Fallback 3: in‑page fetch() from the HTML context
    # ------------------------------------------------------------
    async def _download_playwright_fetch(self, media: Any) -> Tuple[Optional[Path], Optional[str]]:
        """Download using in‑page fetch() executed inside a Playwright page."""
        if not self.browser_context:
            return None, "no-browser"

        url = getattr(media, "url", None)
        if not url:
            return None, "no-url"

        page_url = getattr(media, "page_url", None)

        try:
            page = await self.browser_context.new_page()

            if page_url:
                await page.goto(page_url)
            else:
                await page.goto(url)

            js = """
            async (resourceUrl) => {
                try {
                    const resp = await fetch(resourceUrl, {
                        method: "GET",
                        credentials: "include",
                    });
                    if (!resp.ok) {
                        return { ok: false, status: resp.status, body: null, contentType: null };
                    }
                    const contentType = resp.headers.get("content-type") || "";
                    const buf = await resp.arrayBuffer();
                    const bytes = Array.from(new Uint8Array(buf));
                    return { ok: true, status: resp.status, body: bytes, contentType };
                } catch (e) {
                    return { ok: false, status: 0, body: null, contentType: null };
                }
            }
            """

            result = await page.evaluate(js, url)

            if not result or not result.get("ok"):
                status = result.get("status") if result else "no-result"
                await page.close()
                return None, f"status-{status}"

            body_bytes = bytes(result["body"])
            head = body_bytes[:4096]
            content_type = result.get("contentType") or ""

            ext = self._detect_extension(head, content_type)

            filename = self._make_vendible_filename(url, ext)
            target = self.output_dir / filename
            tmp = target.with_suffix(target.suffix + ".tmp")

            with tmp.open("wb") as f:
                f.write(body_bytes)

            await page.close()
            return tmp, None

        except Exception as exc:
            return None, f"error-{exc}"

    # ------------------------------------------------------------
    # Finalization: dedupe + rename
    # ------------------------------------------------------------
    async def _finalize(self, tmp: Path, media: Any) -> Tuple[Any, bool]:
        """Finalize a download: dedupe check + rename from .tmp to final."""
        file_hash = await self._compute_hybrid_hash(tmp)

        if file_hash in self._seen_hashes:
            self.logger.info(f"[dedupe] Duplicate detected, skipping: {tmp}")
            try:
                tmp.unlink()
            except Exception:
                pass
            return media, True

        self._seen_hashes.add(file_hash)

        final = tmp.with_suffix("")  # remove .tmp

        for _ in range(10):
            try:
                tmp.rename(final)
                break
            except PermissionError:
                time.sleep(0.05)

        self.logger.info(f"Downloaded: {final}")
        return media, True

    # ------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------
    async def _download_one(self, media: Any) -> Tuple[Any, bool]:
        """Download a single media item with HTTPX + Playwright fallbacks."""
        url = getattr(media, "url", None)
        self.logger.debug(f"Downloading {url}")

        tmp, err = await self._download_httpx(media)

        if tmp and err is None:
            return await self._finalize(tmp, media)

        if err and not err.startswith("status-"):
            self.logger.error(f"Failed to download {url}: {err}")
            return media, False

        if err and any(code in err for code in ["status-403", "status-401", "status-429"]):
            self.logger.debug(f"HTTPX blocked ({err}), trying Playwright request.get(): {url}")
            tmp2, err2 = await self._download_playwright_request(media)
            if tmp2 and not err2:
                return await self._finalize(tmp2, media)

            self.logger.debug(f"Playwright request.get failed ({err2}), trying page.goto(): {url}")
            tmp3, err3 = await self._download_playwright_page_goto(media)
            if tmp3 and not err3:
                return await self._finalize(tmp3, media)

            self.logger.debug(f"Playwright page.goto failed ({err3}), trying fetch() inside page: {url}")
            tmp4, err4 = await self._download_playwright_fetch(media)
            if tmp4 and not err4:
                return await self._finalize(tmp4, media)

            self.logger.error(f"Failed to download {url}: {err4}")
            return media, False

        self.logger.error(f"Failed to download {url}: {err}")
        return media, False

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    async def download_all(self, media_items: Iterable[Any]) -> None:
        """Download all media items concurrently.

        Args:
            media_items: Iterable of media objects with at least `url` attribute.
        """
        media_items = list(media_items)
        total = len(media_items)
        self.logger.info(f"Starting downloads: {total} items")

        ok = 0
        fail = 0

        sem = asyncio.Semaphore(self.workers)

        async def worker(m: Any) -> None:
            nonlocal ok, fail
            async with sem:
                media, success = await self._download_one(m)
                if success:
                    ok += 1
                else:
                    fail += 1

        await asyncio.gather(*(worker(m) for m in media_items))

        self.logger.info(f"Download session finished. OK={ok}, FAIL={fail}")
