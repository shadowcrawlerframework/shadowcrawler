---

# Contributing to ShadowCrawler

Thank you for your interest in contributing to **ShadowCrawler**!  
This project aims to be a modern, modular, and developer‑friendly crawling framework.  
All contributions are welcome — code, documentation, ideas, examples, and bug reports.

---

## 🧭 Project Philosophy

- **Clarity over cleverness** — code should be readable and maintainable.  
- **Modularity** — each component should have a clear responsibility.  
- **Developer experience first** — CLI, logs, and errors should help, not hinder.  
- **Respect for users** — breaking changes must be discussed and documented.  

---

## 🐛 Reporting Bugs

Before opening an issue:

1. Confirm the **ShadowCrawler version** you’re using.  
2. Check **existing issues** to avoid duplicates.  
3. Provide a **minimal reproducible example** if possible.  

A good bug report includes:

- ShadowCrawler version  
- Python version  
- Operating system  
- Command executed  
- Relevant logs or traceback  
- Expected behavior  
- Actual behavior  

---

## 💡 Requesting Features

To propose a new feature:

1. Open an issue labeled `Feature request`.  
2. Describe:  
   - The **problem** you want to solve  
   - The **expected usage** (CLI or code example)  
   - The **impact** or motivation  
3. Optional: share implementation ideas  

---

## 🔧 Contributing Code

1. **Fork** the repository.  
2. Create a descriptive branch:

```bash
git checkout -b feature/clear-name
# or
git checkout -b fix/describe-the-bug
```

3. Install dependencies in development mode:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

4. Run tests before committing:

```bash
pytest
```

5. Make small, focused commits with clear messages:

```bash
git commit -m "Add browser checkpoint support to AuthHandler"
```

6. Push your branch and open a **Pull Request**.

---

## 🔄 Pull Request Guidelines

A good PR:

- Is focused on a single change.  
- Includes tests when applicable.  
- Updates documentation if needed.  
- **Keeps CLI flags, docs, and examples consistent**  
  (e.g., `--workers`, `--force-browser`).  
- Passes all existing tests.  
- Explains the motivation behind the change.  

Maintainers may request adjustments — this is normal and part of collaboration.

---

## 🧪 Tests

ShadowCrawler uses **pytest**.

- Add tests for new features.  
- Add regression tests for bug fixes.  
- Keep tests small, clear, and isolated.  

Run all tests:

```bash
pytest
```

---

## 📚 Documentation Contributions

Documentation improvements are always welcome:

- README enhancements  
- Examples  
- Spider templates  
- Architecture explanations  
- Diagrams  
- Tutorials  
- **Updates to CLI docs when adding or modifying flags**  

Even small fixes (typos, formatting, clarity) are valuable.

---

## ❤️ Final Note

ShadowCrawler started as a personal project and grew thanks to curiosity, intention, and community.  
Your contribution — big or small — helps shape its future.

Thank you for being part of it.

---
