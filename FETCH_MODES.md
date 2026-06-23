# Fetch Modes in ShadowCrawler

ShadowCrawler uses a **hybrid fetching system** that automatically chooses between fast HTTP requests and full browser automation via Playwright.

This document explains how fetch modes work, how spiders can request them, and how the engine decides which mode to use.

---

## 🌐 Overview

ShadowCrawler supports two primary fetch modes:

### **1. HTTP Mode (default)**
- Fast  
- Lightweight  
- Ideal for static or semi‑static sites  
- Uses `requests` under the hood  
- No JavaScript execution  

### **2. Browser Mode**
- Powered by Playwright  
- Executes JavaScript  
- Supports login flows  
- Handles dynamic content  
- Required for sites that block HTTP crawlers  

ShadowCrawler automatically selects the correct mode unless overridden.

---

## 🔍 Automatic Mode Selection

The engine determines the fetch mode using:

1. **Spider’s declared `fetch_mode`**
2. **Spider’s `use_browser()` method**
3. **CLI flags (`--browser` / `--no-browser`)**
4. **Auth requirements**
5. **Site behavior (dynamic content, JS rendering)**

### Priority Order

From highest to lowest:

1. **CLI override**  
2. **Spider’s explicit `fetch_mode`**  
3. **Spider’s `use_browser(url, type_)`**  
4. **Engine heuristics**  
5. **Default: HTTP**

---

## 🕷 Declaring Fetch Mode in a Spider

A spider can explicitly declare its preferred mode:

```python
fetch_mode = "browser"
```

Supported values:

- `"http"`
- `"browser"`
- `"auto"` (engine decides)
- `"hybrid"` (future use)
- `"browser-first"` (future use)
- `"http-first"` (future use)

If omitted, ShadowCrawler defaults to **auto**.

---

## 🧠 `use_browser()` Method

Spiders can override mode selection dynamically:

```python
def use_browser(self, url: str, type_: str):
    return True  # always use browser
```

Common patterns:

### Use browser only for login pages

```python
def use_browser(self, url, type_):
    return "/login" in url
```

### Use browser only for POST pages

```python
def use_browser(self, url, type_):
    return type_ == self.POST
```

---

## 🛠 CLI Overrides

Users can force a mode:

### Force browser mode

```bash
shadowcrawler run --url https://example.com --browser
```

### Force HTTP mode

```bash
shadowcrawler run --url https://example.com --no-browser
```

CLI overrides always take priority.

---

## 🔐 Authentication and Fetch Modes

If a spider uses an `AuthHandler`, ShadowCrawler may automatically switch to browser mode when:

- Login is required  
- Cookies must be refreshed  
- The site uses dynamic login flows  
- The spider explicitly requests browser mode  

Session data is stored locally and never transmitted.

---

## ⚙ Engine Behavior Summary

| Scenario | Mode Used |
|---------|-----------|
| Spider declares `fetch_mode = "browser"` | Browser |
| Spider declares `fetch_mode = "http"` | HTTP |
| CLI `--browser` | Browser |
| CLI `--no-browser` | HTTP |
| Spider’s `use_browser()` returns True | Browser |
| Dynamic site detected | Browser |
| Everything else | HTTP |

---

## 🧪 Debugging Fetch Modes

Use `--debug` to see mode decisions:

```bash
shadowcrawler run --url https://example.com --debug
```

The engine will print:

- Selected mode  
- Reason for selection  
- Overrides applied  

---

## 📝 Notes

- Browser mode is slower but more powerful.  
- HTTP mode is faster but limited.  
- Spiders should declare their needs clearly.  
- Users can override behavior at any time.  

---

## ❤️ Final Thoughts

ShadowCrawler’s hybrid fetcher is designed to be flexible, predictable, and developer‑friendly.  
Whether you’re crawling static sites or complex dynamic platforms, the engine adapts to your needs with minimal configuration.
