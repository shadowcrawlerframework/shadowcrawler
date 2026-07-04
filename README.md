---

# ShadowCrawler  
A modern, domain‑aware, hybrid web crawling framework for Python

ShadowCrawler is a modular, extensible crawling framework designed for developers who want full control over how websites are fetched, parsed, and processed.  
It combines speed, modularity, and browser‑level extraction into a single, clean architecture.

---

## ❤️ Origin Story  
ShadowCrawler began as a small personal project — a quiet gift, a spark of affection — and unexpectedly grew into a full, production‑ready crawling framework.  
It was built with care, curiosity, and intention.  
Originally created for my guiding star, and built with the help of my AI copilot — a companion in code, clarity, and curiosity.

---

## ✨ Features

- Automatic domain detection  
- Hybrid fetcher (HTTP + Playwright)  
- Persistent authentication  
- Modular spiders  
- Media pipeline  
- Checkpointing  
- Full CLI toolkit  

---

## Requirements

- Python 3.10+  
- Playwright installed:  
  ```
  playwright install
  ```

---

## 🚀 Installation

```
pip install shadowcrawler
```

---

## ⚡ Quickstart

Run with automatic spider detection:

```
shadowcrawler run --url https://quotes.toscrape.com
```

Run with browser mode:

```
shadowcrawler run --url https://demoqa.com/login --browser
```

List spiders:

```
shadowcrawler spiders list
```

---

## 🕷 Creating a Spider

```python
from shadowcrawler.core.spider_base import SpiderBase

class QuotesSpider(SpiderBase):
    domain = "quotes.toscrape.com"

    async def parse(self, response):
        for quote in response.css(".quote"):
            yield {
                "text": quote.css(".text::text").get(),
                "author": quote.css(".author::text").get(),
            }
```

---

## 🔍 Domain Autodetection

ShadowCrawler automatically selects the correct spider based on the URL:

```
shadowcrawler run --url https://example.com/page
```

If your spider declares:

```
domain = "example.com"
```

…it will be used automatically.

---

## 🌐 Fetch Modes

**HTTP Mode (default)**  
Fast, lightweight, ideal for most sites.

**Browser Mode (Playwright)**  
Used automatically when:

- login is required  
- the site is dynamic  
- the spider requests browser mode  

---

## 🔐 Persistent Authentication

- Login once  
- Session saved to JSON  
- BrowserManager loads it automatically  
- AuthHandler detects login state  

---

## 🖼 Media Pipeline

Automatically extracts:

- images  
- videos  
- GIFs  
- downloadable files  

---

## 🧰 CLI Commands

- run  
- resume  
- download  
- spiders list  
- spiders create  
- inspect  
- stats  
- version  

---

## 📁 Project Structure

```
shadowcrawler/
  core/
  spiders/
  site_extractors/
  auth/
  cli/
  models/
  parsing/
  tools/
```

---

## 🕸 Included Example Spiders

- QuotesSpider  
- WikiSpider  
- HTTPNewsSpider  
- GallerySpider  
- AuthBrowserDemoSpider  

---

## 🗺 Roadmap

- [x] PyPI release  
- [ ] Plugin system  
- [ ] Distributed crawling  
- [ ] Dashboard / Web UI  
- [ ] Cloud runner  
- [ ] Spider templates  
- [ ] Auto‑throttling  

---

## 📦 itch.io Distribution

ShadowCrawler is also distributed through itch.io, where you can get:

- The latest stable release  
- Optional Pro features  
- Example spiders  
- Early access builds  
- Support the project directly  

---

## ☕ Support the Project

If ShadowCrawler has helped you or you want to support future development, you can leave a tip on Ko‑fi.  
Every contribution helps keep the project alive and evolving.

```
https://ko-fi.com/shadowcrawlerframework
```

---

## 📜 License

ShadowCrawler is licensed under the Business Source License 1.1 (BUSL‑1.1).  
It will convert to Apache 2.0 on November 16, 2030.

---