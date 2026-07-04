# ShadowCrawler v4.1.3 — Spider Overview (Official Examples)

This document provides an overview of all spiders included in the ShadowCrawler
v4.1.3 codebase. Each spider follows the core framework contract:

- URL classification (`classify`)
- Follow rules (`should_follow`)
- Browser vs HTTP mode (`use_browser`)
- Metadata for Playwright (`request_meta`)
- Delegation to extractors (`parse`)

All spiders are educational examples unless otherwise noted.

---

## 🧪 AuthBrowserDemoSpider — Browser Auth Demo

**Path:** `spiders/authbrowserdemo/AuthBrowserDemoSpider.py`  
**Mode:** Browser  
**Purpose:** Demonstrates how ShadowCrawler performs browser-based login flows.

### Features
- Full Playwright browser mode  
- Example login sequence  
- Shows how to maintain session state  
- Educational only — not production-grade  

---

## 🔐 AuthDemoSpider — HTTP Auth Demo

**Path:** `spiders/authdemo/AuthDemoSpider.py`  
**Mode:** HTTP  
**Purpose:** Demonstrates simple HTTP-based authentication.

### Features
- Basic auth flow  
- Simple request/response handling  
- Educational example for HTTP pipelines  

---

## 🖼️ GallerySpider — Static Gallery Collector

**Path:** `spiders/gallery/GallerySpider.py`  
**Mode:** HTTP or Browser  
**Purpose:** Extracts images from simple static galleries.

### Features
- `<img>` extraction  
- Optional browser mode  
- No deep crawling  
- Good for simple HTML galleries  

---

## 🖼️ HTTPGallerySpider — HTTP-only Gallery Collector

**Path:** `spiders/httpgallery/HTTPGallerySpider.py`  
**Mode:** HTTP  
**Purpose:** Lightweight gallery spider without browser rendering.

### Features
- Fast HTTP-only mode  
- Extracts direct image URLs  
- No DOM rendering  

---

## 📰 HTTPNewsSpider — Basic News Spider

**Path:** `spiders/httpnews/HTTPNewsSpider.py`  
**Mode:** HTTP  
**Purpose:** Demonstrates extraction of article text from news-like pages.

### Features
- HTTP-only  
- Extracts titles, paragraphs, links  
- Educational example for text-based sites  

---

## 💬 QuotesSpider — Simple Text Spider

**Path:** `spiders/quotes/QuotesSpider.py`  
**Mode:** HTTP  
**Purpose:** Demonstrates extraction of quotes from simple HTML pages.

### Features
- Very small example  
- Extracts text blocks  
- Ideal for beginners exploring the pipeline  

---

## 🖼️ UniversalImageSpider — DOM Image Collector

**Path:** `spiders/universalimage/UniversalImageSpider.py`  
**Mode:** Browser  
**Purpose:** Collects images from any public site using fully rendered DOM.

### Features
- Persistent Playwright page (`keep_page=True`)  
- Internal navigation (MAX_DEPTH / MAX_PAGES)  
- Extracts `<img>`, `<picture>`, `og:image`, `rel=image_src`  
- Delegates extraction to UniversalImageExtractor  

---

## 📚 WikiSpider — Wikipedia Spider (Official Example)

**Path:** `spiders/wiki/WikiSpider.py`  
**Mode:** Browser  
**Purpose:** Official SC example for large structured sites like Wikipedia.

### Features
- Full browser mode  
- ARTICLE / CATEGORY / FILE / GENERIC classification  
- Deep-mode extraction via WikiExtractor  
- Clean separation between spider and extractor  

---

## 🌀 TumblrSpider — Client-Specific Spider (Not Public)

**Path:** `spiders/tumblr/TumblrSpider.py`  
**Mode:** Browser  
**Purpose:** Custom spider built for a private client.

### Notes
- Not part of public SC examples  
- Tailored to client requirements  
- Uses DOM-based extraction with scroll/lazy-loading  
- Included in the codebase but not documented publicly  

---

# General Notes

- Spiders **do not** extract content themselves — they delegate to extractors.  
- Spiders **do not** decide what data to store — they return normalized dicts.  
- All examples (except TumblrSpider) are **educational** and not production-grade.  
- ShadowCrawler does **not** perform bypasses, exploits, or prohibited scraping.  

