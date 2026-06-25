# Authentication in ShadowCrawler

ShadowCrawler includes a flexible and modular authentication system designed to support login flows, persistent sessions, and browser‑based authentication when required.

This document explains how authentication works, how to implement custom handlers, and how session data is stored and reused.

---

## 🔐 Overview

Authentication in ShadowCrawler is handled by **AuthHandlers**, which are small classes responsible for:

- Logging into a website  
- Detecting whether the user is already authenticated  
- Saving and loading session data  
- Requesting browser mode when needed  

AuthHandlers are optional — spiders that do not require login do not need one.

---

## 🧩 AuthHandler Structure

All authentication handlers inherit from:

```python
from shadowcrawler.auth.base_auth import BaseAuthHandler
```

A typical AuthHandler looks like:

```python
class MySiteAuth(BaseAuthHandler):
    async def login(self, browser):
        # Perform login steps here
        ...

    async def is_logged_in(self, browser):
        # Return True if session is authenticated
        ...
```

Required methods:

- `login(browser)` — performs the login flow  
- `is_logged_in(browser)` — checks if the session is valid  

Optional helpers:

- `prepare_request()`  
- `after_login()`  
- `use_browser_for_auth = True`  

---

## 🗂 Session Storage

ShadowCrawler stores session data locally in a JSON file.

Example:

```
checkpoints/
  mysite/
    session.json
```

Session files may contain:

- Cookies  
- Local storage  
- Tokens  
- Browser state  

### Important Notes

- Session files are **never uploaded**, **never transmitted**, and **never shared** by ShadowCrawler.  
- They remain entirely on the user’s machine.  
- Users are responsible for securing their environment.  

For more details, see **SECURITY.md**.

---

## 🌐 Browser‑Based Authentication

Some sites require:

- JavaScript execution  
- CAPTCHA handling  
- Dynamic login flows  
- Multi‑step authentication  

In these cases, AuthHandlers can request browser mode:

```python
use_browser_for_auth = True
```

ShadowCrawler will:

1. Launch Playwright  
2. Load session state if available  
3. Run `is_logged_in()`  
4. If not logged in, run `login()`  
5. Save updated session state  

---

## 🔄 Automatic Login Flow

When a spider declares an AuthHandler:

```python
auth_handler = MySiteAuth
```

ShadowCrawler will:

1. Load existing session (if any)  
2. Check login state  
3. If not logged in → perform login  
4. Save session  
5. Continue crawling  

This process is automatic and requires no extra code in the spider.

---

## 🕷 Declaring Auth in a Spider

Example:

```python
class MySpider(SpiderBase):
    domain = "example.com"
    auth_handler = MySiteAuth
```

The spider does not need to implement login logic — the AuthHandler handles everything.

---

## 🛠 Creating an Auth Handler (CLI)

ShadowCrawler can scaffold an AuthHandler automatically:

```bash
shadowcrawler spiders create myspider --with-auth
```

This generates:

```
auth/
  myspider/
    MyspiderAuth.py
```

The generated file includes:

- Login method stub  
- Login detection stub  
- Browser mode flag  
- Session handling boilerplate  

---

## 🧪 Example: Simple Login Flow

```python
class DemoAuth(BaseAuthHandler):
    async def login(self, browser):
        page = await browser.new_page()
        await page.goto("https://example.com/login")

        await page.fill("#username", self.username)
        await page.fill("#password", self.password)
        await page.click("button[type=submit]")

        await page.wait_for_load_state("networkidle")

    async def is_logged_in(self, browser):
        page = await browser.new_page()
        await page.goto("https://example.com/profile")
        return "Logout" in await page.content()
```

---

## ⚠ Responsibility Disclaimer

ShadowCrawler provides tools for authentication, but **cannot control how users store or secure their session files**.

Users are responsible for:

- Protecting their local environment  
- Managing file permissions  
- Avoiding sharing session files  
- Ensuring compliance with website terms of service  

ShadowCrawler does not transmit or sync authentication data.

For full details, see **SECURITY.md**.

---

## ❤️ Final Notes

Authentication is one of the most powerful features of ShadowCrawler.  
The system is designed to be:

- modular  
- predictable  
- secure  
- easy to extend  

Whether you're logging into simple sites or complex dynamic platforms, AuthHandlers give you full control with minimal boilerplate.
