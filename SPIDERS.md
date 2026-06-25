---

# Spiders in ShadowCrawler

ShadowCrawler uses a **domain‑aware, modular spider architecture**.  
Each spider is responsible for crawling a specific domain and extracting structured data from it.

This document explains how spiders work, how to create them, and how ShadowCrawler selects the correct spider automatically.

---

## 🕸 What Is a Spider?

A **Spider** is a Python class that:

- Declares the domain it handles  
- Defines how to fetch pages (HTTP or browser)  
- Parses responses and yields data  
- Optionally handles login or browser logic  
- Coordinates with extractors and auth handlers  

All spiders inherit from:

```python
from shadowcrawler.core.spider_base import SpiderBase
```

---

## 🌐 Domain Declaration

Every spider must declare the domain it is responsible for:

```python
domain = "quotes.toscrape.com"
```

ShadowCrawler uses this to automatically select the correct spider based on the URL.

Example:

```bash
shadowcrawler run --url https://quotes.toscrape.com
```

This will automatically load `QuotesSpider`.

---

## 🧱 Basic Spider Structure

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

A spider must implement:

- `parse(response)` → yields data, media, or new URLs  
- Optional helpers (pagination, login logic, browser overrides, etc.)

---

## 🔍 Automatic Spider Selection

ShadowCrawler chooses the spider using:

1. The URL’s domain  
2. Spider’s declared `domain`  
3. Subdomain matching  
4. Fallback heuristics  

If no spider matches, the CLI will show an error.

---

## 🌐 Fetch Modes in Spiders

Spiders can request specific fetch modes:

```python
fetch_mode = "browser"
```

Supported values:

- `"http"`
- `"browser"`
- `"auto"` (default)
- `"browser-first"` (future)
- `"http-first"` (future)

Spiders can also override dynamically:

```python
def use_browser(self, url, type_):
    return "/login" in url
```

CLI flags such as:

- `--force-browser`  
- `--force-http`  
- `--show-browser`  

…override spider preferences.  
For full details, see **FETCH_MODES.md**.

---

## 🔐 Authentication (Optional)

If a spider requires login, it can declare:

```python
auth_handler = MyAuthHandler
```

ShadowCrawler will:

- Load session data  
- Attempt login if needed  
- Switch to browser mode when required  
- Share the authenticated session with all workers  

Authentication always runs **before** the crawl begins.

Full details are in **AUTH.md**.

---

## 🖼 Media Extraction

Spiders automatically extract:

- Images  
- Videos  
- GIFs  
- Downloadable files  

This is handled by the **media pipeline**, which:

- Normalizes filenames  
- Organizes directories  
- Avoids duplicates  
- Works with multi‑worker crawls  

Spiders can disable automatic extraction:

```python
auto_extract_media = False
```

Or yield media manually:

```python
yield response.as_media(url)
```

Full details in **MEDIA_PIPELINE.md**.

---

## 🧭 Pagination

Spiders can implement pagination manually:

```python
next_page = response.css("a.next::attr(href)").get()
if next_page:
    yield response.follow(next_page)
```

Or use custom logic depending on the site.

---

## ⚙ Multi‑Worker Behavior (`--workers N`)

Spiders do **not** need to change anything to support multi‑worker crawling.

The engine handles:

- Queue distribution  
- Deduplication  
- Shared checkpointing  
- Shared session state  

Spiders remain simple and deterministic.

---

## 🛠 Spider Scaffolding (CLI)

ShadowCrawler includes a scaffolding tool that generates all required components for a new spider.

### Basic spider creation

```bash
shadowcrawler spiders create myspider
```

This generates:

```
shadowcrawler/
  spiders/
    myspider/
      MyspiderSpider.py
  site_extractors/
    myspider/
      MyspiderExtractor.py
```

You get:

- A **Spider** class  
- A **SiteExtractor** class  
- A clean folder structure  

### Creating a spider with authentication support

```bash
shadowcrawler spiders create myspider --with-auth
```

This generates:

```
auth/
  myspider/
    MyspiderAuth.py
```

### Creating a spider with extractor + auth (full template)

```bash
shadowcrawler spiders create myspider --with-extractor --with-auth
```

This is recommended for complex sites.

---

## 📁 Generated File Responsibilities

### **Spider (`MyspiderSpider.py`)**
- Declares the domain  
- Defines parsing logic  
- Controls fetch mode  
- Coordinates with extractor and auth  
- Yields data, media, and new URLs  

### **SiteExtractor (`MyspiderExtractor.py`)**
- Handles CSS/XPath extraction  
- Normalizes data  
- Provides helper methods for parsing  
- Can customize media extraction  

### **AuthHandler (`MyspiderAuth.py`)**
- Manages login flows  
- Saves and loads session data  
- Detects login state  
- Can request browser mode when needed  

---

## 🧪 Example Spiders Included

ShadowCrawler ships with several example spiders:

### **QuotesSpider**
Simple HTML extraction.

### **WikiSpider**
Structured content parsing.

### **HTTPNewsSpider**
HTTP‑only crawling with article extraction.

### **GallerySpider**
Media extraction (images, galleries).

### **AuthBrowserDemoSpider**
Login + browser mode + session persistence.

These examples live in:

```
shadowcrawler/spiders/
```

---

## ❤️ Final Notes

Spiders are the heart of ShadowCrawler.  
They are designed to be:

- simple  
- modular  
- predictable  
- easy to extend  

Whether you're scraping static pages or complex dynamic sites, ShadowCrawler gives you the tools to build clean, maintainable spiders with minimal boilerplate.

---
