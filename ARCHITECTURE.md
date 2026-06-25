---

# ShadowCrawler Architecture

ShadowCrawler is built around a **modular, domain‑aware crawling engine** designed for clarity, extensibility, and real‑world scraping workflows.  
This document provides a high‑level overview of the internal architecture and how the major components interact.

---

## 🧩 Core Components

ShadowCrawler is composed of the following major subsystems:

- **Spider Engine** — orchestrates crawling, scheduling, and spider selection  
- **Fetchers** — HTTP and Browser (Playwright) fetch modes  
- **Spiders** — domain‑specific crawling logic  
- **Site Extractors** — structured data extraction  
- **Auth Handlers** — login and session persistence  
- **Media Pipeline** — downloading and processing media  
- **Checkpointing System** — resume crawls safely  
- **CLI Toolkit** — user‑facing interface for running spiders  
- **Worker Pool** — multi‑worker concurrent crawling (`--workers N`)  

Each subsystem is independent and replaceable.

---

## 🕷 Spider Engine

The engine is responsible for:

- Selecting the correct spider based on the URL  
- Managing the crawl queue  
- Handling fetch mode decisions  
- Passing responses to spiders  
- Coordinating extractors, auth, and media pipeline  
- Saving checkpoints and session data  
- Distributing work across multiple workers when `--workers` is enabled  

The engine is intentionally minimal and predictable.

---

## ⚙️ Worker Pool (Multi‑Worker Crawling)

ShadowCrawler supports concurrent crawling through a **worker pool**, activated via:

```bash
shadowcrawler run --url https://example.com --workers 4
```

The worker system:

- Spawns **N asynchronous workers**  
- Each worker fetches, parses, and schedules new URLs  
- Shares a centralized frontier (queue)  
- Ensures deduplication across all workers  
- Works with both HTTP and Browser fetchers  
- Automatically integrates with checkpointing  

Workers dramatically improve throughput on:

- media‑heavy sites  
- paginated content  
- large collections of static pages  

---

## 🌐 Fetchers: HTTP + Browser

ShadowCrawler uses a **hybrid fetching system**:

### **HTTP Fetcher**
- Fast  
- Lightweight  
- Ideal for static pages  
- Uses `requests`  

### **Browser Fetcher (Playwright)**
- Executes JavaScript  
- Supports login flows  
- Handles dynamic content  
- Required for modern sites  

The engine decides which fetcher to use based on:

- Spider’s `fetch_mode`  
- `use_browser()` overrides  
- CLI flags (`--force-browser`)  
- Auth requirements  

Full details in **FETCH_MODES.md**.

---

## 🕸 Spiders

Spiders define:

- The domain they handle  
- How to parse responses  
- Whether they need browser mode  
- Whether they require authentication  
- How to follow links or paginate  

Spiders are intentionally small and focused.

Full details in **SPIDERS.md**.

---

## 🧪 Site Extractors

Extractors are responsible for:

- CSS/XPath extraction  
- Normalizing data  
- Providing helper methods for spiders  
- Keeping parsing logic clean and reusable  

Each spider has its own extractor directory:

```
site_extractors/
  domain/
    DomainExtractor.py
```

---

## 🔐 Auth Handlers

AuthHandlers manage:

- Login flows  
- Session persistence  
- Detecting login state  
- Browser‑based authentication when needed  

They integrate seamlessly with the engine and fetchers.

Full details in **AUTH.md**.

---

## 🖼 Media Pipeline

The media pipeline handles:

- Image downloads  
- Video downloads  
- GIFs  
- File attachments  
- Directory organization  
- Filename normalization  

It runs automatically when spiders yield media URLs.

---

## 💾 Checkpointing System

ShadowCrawler includes a robust checkpointing system that stores:

- Crawl progress  
- Session data  
- Pending URLs  
- Spider state  

This allows:

- Crash recovery  
- Long‑running crawls  
- Incremental crawling  
- Multi‑worker safe resume  

Checkpoints are stored locally and never transmitted.

---

## 🧰 CLI Toolkit

The CLI provides commands for:

- Running spiders  
- Resuming crawls  
- Downloading media  
- Inspecting pages  
- Listing spiders  
- Creating new spiders  
- Viewing stats  
- Checking version  

Example:

```bash
shadowcrawler run --url https://example.com --workers 4
```

---

## 🛠 Project Structure

A typical ShadowCrawler project looks like:

```
shadowcrawler/
  core/
  spiders/
  site_extractors/
  auth/
  media/
  checkpoints/
  cli/
```

Each directory has a single responsibility.

---

## 🧭 Design Philosophy

ShadowCrawler is built on:

- **Clarity over cleverness**  
- **Modularity over monoliths**  
- **Predictability over magic**  
- **Explicit behavior over hidden logic**  
- **Real‑world practicality over academic purity**  

The architecture is intentionally simple, stable, and easy to extend.

---

## ❤️ Final Notes

ShadowCrawler’s architecture is designed to support:

- Real‑world scraping  
- Dynamic sites  
- Authenticated workflows  
- Media‑heavy crawls  
- Long‑running jobs  
- Multi‑worker concurrency  
- Custom spiders and extensions  

Whether you're building simple scrapers or complex authenticated crawlers, the architecture gives you a clean, predictable foundation to work with.

---
