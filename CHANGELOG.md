# Changelog

All notable changes to **ShadowCrawler** will be documented in this file.

This project follows semantic versioning for public releases.  
Internal development builds prior to **4.1.1** are not listed here.

---

## [4.1.3] — Authentication & Browser Context Fixes

### Fixed
- Resolved an issue where `requires_login` did not activate the AuthHandler on the first URL.
- Fixed a bug where Playwright context initialization ignored `browser_mode="full"` for certain spiders.
- Corrected behavior where React‑based pages were parsed before fully mounting.
- Improved session restoration (cookies + localStorage) for authentication spiders.
- Fixed inconsistent handling of `keep_page=True` across workers.
- Ensured that `show-browser` mode always loads full CSS and JS resources.
- Improved extractor reliability for dynamic pages (e.g., DemoQA Profile).

### Added
- Robust authentication handler pattern (Tumblr‑style) for demo spiders.
- Full React‑aware extractor for AuthBrowserDemo.
- Better logging around authentication flow and session restoration.

### Notes
This version stabilizes the authentication pipeline and ensures consistent FULL browser context behavior across spiders.

---

## [4.1.2] — BrowserManager & Resource Blocking Improvements

### Fixed
- Corrected an issue where HTML‑only mode blocked essential scripts on sites requiring minimal JS.
- Fixed domain context mixing inside BrowserManager.
- Ensured Playwright closes cleanly in all modes to avoid pipe warnings.
- Fixed `browser_mode="full"` not being respected by UniversalImageSpider.
- Corrected context recycling issues across domains.

### Improved
- Resource blocking logic now behaves consistently across spiders.
- Better handling of forced browser mode (`--force-browser`).
- More reliable session loading for spiders using AuthHandler.

### Notes
This version focused on stabilizing BrowserManager and improving JS‑dependent crawling.

---

## [4.1.1] — Initial Public Release

### Added
- Full modular crawling engine with domain‑aware spider selection.  
- Hybrid fetcher (HTTP + Playwright) with automatic mode switching.  
- Persistent authentication system with session storage.  
- Media extraction pipeline (images, videos, GIFs, files).  
- Checkpointing system for safe crawl resuming.  
- **Multi‑worker crawling support (`--workers N`).**  
- **Forced browser mode flag (`--force-browser`).**  
- CLI toolkit:
  - `run`
  - `resume`
  - `download`
  - `spiders list`
  - `spiders create`
  - `inspect`
  - `stats`
  - `version`
- Example spiders:
  - QuotesSpider  
  - WikiSpider  
  - HTTPNewsSpider  
  - GallerySpider  
  - AuthBrowserDemoSpider
- Logging improvements and structured output.  
- Initial documentation and project assets.

### Notes
This is the first **public** release of ShadowCrawler.  
The internal engine has undergone many iterations and refinements prior to this version.

---

## Future Versions
Future releases will include:

- Plugin system  
- Distributed crawling  
- Dashboard / Web UI  
- Cloud runner  
- Spider templates  
- Auto‑throttling  
