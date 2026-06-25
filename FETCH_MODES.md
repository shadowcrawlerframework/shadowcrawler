---

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

1. **CLI flags (`--force-browser`, `--force-http`)**
2. **Auth requirements (`use_browser_for_auth`)**
3. **Spider’s declared `fetch_mode`**
4. **Spider’s `use_browser()` method**
5. **Engine heuristics (dynamic content detection)**

### Priority Order (highest → lowest)

1. **CLI override (`--force-browser` / `--force-http`)**  
2. **AuthHandler requesting browser mode**  
3. **Spider’s explicit `fetch_mode`**  
4. **Spider’s `use_browser(url, type_)`**  
5. **Engine heuristics**  
6. **Default: HTTP**

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

Users can override fetch mode behavior:

### Force browser mode (Playwright for all requests)

```bash
shadowcrawler run --url https://example.com --force-browser
```

### Force HTTP mode (disable browser entirely)

```bash
shadowcrawler run --url https://example.com --force-http
```

### Show the browser window (disable headless mode)

```bash
shadowcrawler run --url https://example.com --show-browser
```

### Debug fetch mode decisions

```bash
shadowcrawler run --url https://example.com --debug
```

> **Note:**  
> The old flags `--browser` and `--no-browser` have been replaced by  
> **`--force-browser`** and **`--force-http`** for clarity and consistency.

---

## 🔐 Authentication and Fetch Modes

If a spider uses an `AuthHandler`, ShadowCrawler may automatically switch to browser mode when:

- Login is required  
- Cookies must be refreshed  
- The site uses dynamic login flows  
- The AuthHandler sets `use_browser_for_auth = True`  

Authentication always runs **before** the crawl begins, ensuring:

- Workers share the same authenticated session  
- Browser mode is activated if required  
- Session state is saved once and reused  

Session data is stored locally and never transmitted.

---

## ⚙ Worker Interaction (`--workers N`)

Multi‑worker crawling does **not** change fetch mode selection.

Workers:

- Use the fetch mode already chosen by the engine  
- Never run authentication  
- Never override fetch mode  
- Share the same session and cookies  

Example:

```bash
shadowcrawler run --url https://example.com --workers 4
```

If browser mode is active (via spider, auth, or `--force-browser`),  
**all workers use browser mode**.

If HTTP mode is active,  
**all workers use HTTP mode**.

---

## ⚙ Engine Behavior Summary

| Scenario | Mode Used |
|---------|-----------|
| CLI `--force-browser` | Browser |
| CLI `--force-http` | HTTP |
| AuthHandler requests browser | Browser |
| Spider declares `fetch_mode = "browser"` | Browser |
| Spider declares `fetch_mode = "http"` | HTTP |
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
- Whether browser mode was forced by auth or CLI  

---

## 📝 Notes

- Browser mode is slower but more powerful.  
- HTTP mode is faster but limited.  
- Spiders should declare their needs clearly.  
- AuthHandlers may force browser mode.  
- Users can override behavior at any time with `--force-browser` or `--force-http`.  
- Workers inherit the selected fetch mode.  
- `--show-browser` is useful for debugging login flows.  

---

## ❤️ Final Thoughts

ShadowCrawler’s hybrid fetcher is designed to be flexible, predictable, and developer‑friendly.  
Whether you’re crawling static sites or complex dynamic platforms, the engine adapts to your needs with minimal configuration.

---
