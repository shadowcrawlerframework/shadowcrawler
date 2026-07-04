# **ShadowCrawler**  
A modern, domain‑aware, hybrid web crawling framework for Python.

[![PyPI](https://img.shields.io/pypi/v/shadowcrawler)](https://pypi.org/project/shadowcrawler/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-BUSL--1.1-blue)](LICENSE)
[![GitHub Releases](https://img.shields.io/github/v/release/shadowcrawlerframework/shadowcrawler)](https://github.com/shadowcrawlerframework/shadowcrawler/releases)

ShadowCrawler is a modular, extensible crawling framework designed for developers who want full control over how websites are fetched, parsed, and processed.  
It combines speed, modularity, and browser‑level extraction into a single, clean architecture.

---

## ❤️ Origin Story  
ShadowCrawler began as a small personal project — a quiet spark that grew into a full, production‑ready crawling framework.  
It was built with care, curiosity, and intention, shaped by countless iterations and the help of an AI copilot that assisted with clarity, structure, and design.

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

PyPI: `https://pypi.org/project/shadowcrawler/`

---

## ⚡ Quickstart

Run with automatic spider detection:

```
shadowcrawler run --url [https://quotes.toscrape.com](https://quotes.toscrape.com)
```

Run with browser mode:

```
shadowcrawler run --url [https://demoqa.com/login](https://demoqa.com/login) --browser
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

### HTTP Mode (default)  
Fast, lightweight, ideal for most sites.

### Browser Mode (Playwright)  
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
- UniversalImageSpider

---

## 🔖 Versioning

ShadowCrawler follows semantic versioning:

- **MAJOR** — architecture changes  
- **MINOR** — new features  
- **PATCH** — fixes and stability updates  

Latest release: **4.1.3**

---

## 🗺 Roadmap

- [x] PyPI release  
- [x] itch.io release  
- [x] GitHub release  
- [ ] Plugin system  
- [ ] Distributed crawling  
- [ ] Dashboard / Web UI  
- [ ] Cloud runner  
- [ ] Spider templates  
- [ ] Auto‑throttling  

---

## 📦 itch.io Distribution

ShadowCrawler is also distributed through itch.io:

`https://shadowcrawlerframework.itch.io/shadowcrawler`

---

## 🔗 GitHub Releases

All versions, changelogs, and downloadable builds:

`https://github.com/shadowcrawlerframework/shadowcrawler/releases`

---

## 🤝 Contributing

See the full guide:  
`CONTRIBUTING.md`

---

## ☕ Support the Project

If ShadowCrawler has helped you or you want to support future development, you can leave a tip on Ko‑fi:

`https://ko-fi.com/shadowcrawlerframework`

---

## 📜 License

ShadowCrawler is licensed under the Business Source License 1.1 (BUSL‑1.1).  
It will convert to Apache 2.0 on November 16, 2030.

---
