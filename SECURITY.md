---

# Security Policy

## Supported Versions
Security updates will be provided for the latest major release of ShadowCrawler.

---

## Reporting a Vulnerability
If you discover a security vulnerability, please report it responsibly.

**Do not open a public GitHub issue.**

Instead, contact the maintainers privately at:

**shadowcrawler.framework@gmail.com**

Please include:
- A clear description of the vulnerability.
- Steps to reproduce (if applicable).
- Potential impact.
- Any suggested fixes or patches.

We will:
- Acknowledge your report within 72 hours.
- Investigate the issue promptly.
- Provide a timeline for the fix when possible.
- Credit you in the release notes unless you prefer to remain anonymous.

---

## Session Files and Authentication Data

ShadowCrawler supports **persistent authentication**, which stores session data (cookies, tokens, or login state) locally on the user's machine.

To ensure security:

- Session files are **never uploaded**, **never transmitted**, and **never shared** by ShadowCrawler.  
- These files remain entirely under the user’s control and are stored in the local filesystem.  
- Users are responsible for protecting their own environment, including:
  - File permissions  
  - Operating system security  
  - Disk encryption  
  - Avoiding sharing session files with others  

ShadowCrawler **cannot** prevent misuse of session files if a user’s machine is compromised or if the files are shared intentionally or accidentally.

**The security of local session data is the responsibility of the user.**

---

## Responsible Use

ShadowCrawler must not be used for:

- Illegal activities  
- Unauthorized access to systems  
- Harassment, abuse, or targeted harm  
- Violations of terms of service of any website  
- Bypassing access controls or protections  

Users are responsible for:

- Ensuring compliance with local laws and regulations  
- Respecting website policies, including robots.txt and rate limits  
- Managing the impact of their crawls, especially when using multiple workers  

ShadowCrawler does not transmit data to third parties and does not perform any network activity beyond what the user explicitly requests.

---

## Disclosure Policy
We follow a responsible disclosure model:

- Vulnerabilities are fixed privately  
- A patch is released  
- A public advisory is published afterward  

---

## Disclaimer
ShadowCrawler provides tools for automation and crawling, but **cannot control how users store, secure, or manage their own authentication data**.

By using this software, users agree that:

- They are responsible for securing their environment  
- They understand the risks of storing session data locally  
- They will not hold the maintainers liable for misuse, leaks, or compromise of data stored on their own systems

---
