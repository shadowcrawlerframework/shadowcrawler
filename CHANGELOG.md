---

# Changelog

All notable changes to **ShadowCrawler** will be documented in this file.

This project follows semantic versioning for public releases.  
Internal development builds prior to **4.1.0** are not listed here.

---

## [4.1.0] — Initial Public Release

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

---
