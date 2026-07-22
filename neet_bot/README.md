# 🤖 NEET Bot Master Engine & Web Server (`neet_bot/`)

This directory contains the core backend server, Telegram multi-bot polling engine, dataset loaders, PDF report generator, AI weak area evaluator, and SQLite database models.

---

## 📄 File-by-File Explanation

| File Name | Purpose & Functionality |
| :--- | :--- |
| **`main.py`** | Server entry point. Spins up multi-port HTTP health servers (listening on `$PORT`, 8080, 7860) and launches 3 concurrent daemon threads for `@gptbiologybot`, `@gptphysicsbot`, and `@gptchemistrybot` using `asyncio.set_event_loop()`. |
| **`bot_handlers.py`** | Master Telegram callback & command handler module. Manages `/start` welcome messages, single/multi-chapter keyboards, full random test mode (`mode_all_random`), live question navigation, user session states, and `post_init` bot description setters. |
| **`questions.py`** | Dataset loading and sampling engine. Loads `questions_dataset.json` (Biology), `physics_questions.json` (Physics), and `chemistry_questions.json` (Chemistry). Implements balanced per-chapter sampling and random interspersing. |
| **`pdf_report.py`** | ReportLab PDF Report Card generator. Renders Title Header, Performance Metric Cards, Full Test Paper & Answer Key (with `<sub>`/`<sup>` HTML formatting), and AI Weak Area Diagnostic Report at the end. Returns raw PDF `bytes`. |
| **`ai_analyzer.py`** | OpenAI GPT-4o-mini diagnostic evaluator. Receives *only* missed/unattempted questions, identifies core NCERT weak subtopics and common misconceptions, and provides a targeted study plan without solving questions line-by-line. |
| **`db.py`** | SQLite database manager (`neet_bot.db`). Manages tables for `users`, `sessions`, `answers`, and `analytics`. Logs session start, question responses, total score, accuracy, and user interaction stats for the Admin Dashboard. |
| **`config.py`** | Central configuration loader. Reads environment variables for `BIOLOGY_BOT_TOKEN`, `PHYSICS_BOT_TOKEN`, `CHEMISTRY_BOT_TOKEN`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and default fallback tokens. |
| **`test_system.py`** | Automated diagnostic test suite (`unittest`). Executes 8 comprehensive verification tests for datasets, sampling logic, Telegram bots, PDF byte builds, and AI evaluator formatting. |
| **`Dockerfile`** | Container deployment blueprint for Railway / Docker hosting. Installs Python 3.11-slim, requirements, copies codebase, exposes port 8080, and runs `python main.py`. |
| **`requirements.txt`** | Dependency list including `python-telegram-bot`, `reportlab`, `openai`, `httpx`, `apscheduler`, `jinja2`. |

---

## 🧪 Running System Tests

To run all automated system tests inside `neet_bot/`:

```bash
python3 test_system.py
```
