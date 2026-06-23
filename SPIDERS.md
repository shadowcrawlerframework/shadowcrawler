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

- `parse(response)` → yields data or new URLs  
- Optional helpers (login, pagination, browser logic, etc.)

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

Full details are in **AUTH.md**.

---

## 🖼 Media Extraction

Spiders automatically extract:

- Images  
- Videos  
- GIFs  
- Downloadable files  

No extra code is needed unless you want custom behavior.

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

## 🧪 Example Spiders Included

ShadowCrawler ships with several example spiders:

### **QuotesSpider**
Simple HTML extraction.

### **WikiSpider**
Demonstrates structured content parsing.

### **HTTPNewsSpider**
Shows HTTP‑only crawling with article extraction.

### **GallerySpider**
Demonstrates media extraction (images, galleries).

### **AuthBrowserDemoSpider**
Shows login + browser mode + session persistence.

These examples live in:

```
shadowcrawler/spiders/
```

---

## 🧩 Creating a New Spider (CLI)

You can scaffold a new spider using:

```bash
shadowcrawler spiders create myspider
```

This generates:

- Spider class  
- Extractor stub  
- Directory structure  

---

## ❤️ Final Notes

Spiders are the heart of ShadowCrawler.  
They are designed to be:

- simple  
- modular  
- predictable  
- easy to extend  

Whether you're scraping static pages or complex dynamic sites, ShadowCrawler gives you the tools to build clean, maintainable spiders with minimal boilerplate.
