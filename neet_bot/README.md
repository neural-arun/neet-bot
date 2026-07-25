# 🤖 `neet_bot` — Master NEET Telegram Bot & Web Engine

`neet_bot` is the core execution package powering the master multi-bot engine, Telegram handlers, Web App API server, performance analytics database, PDF report generator, and AI diagnostic mentor.

---

## 📄 File-by-File Breakdown & Responsibilities

### Core Application Files

#### 1. [`main.py`](file:///home/arun/projects/neet_pp/neet_bot/main.py)
* **Function**: Master application launcher and HTTP health server.
* **What it does**:
  * Initializes the SQLite database (`db.py`).
  * Spawns multi-threaded Telegram polling workers for Biology, Chemistry, and Physics bots simultaneously.
  * Runs a non-blocking `HTTPServer` on port `8080` (or `$PORT`) to serve the Web App (`/`), Chapter API (`/api/chapters`), Question API (`/api/questions`), AI Analysis API (`/api/analyze`), and Admin Analytics (`/api/analytics`).

#### 2. [`bot_handlers.py`](file:///home/arun/projects/neet_pp/neet_bot/bot_handlers.py)
* **Function**: Telegram bot command and callback query handlers.
* **What it does**:
  * Implements `/start`, `/help`, `/test`, `/mock`, `/analytics`, and `/reset` commands.
  * Handles multi-choice inline buttons (`A`, `B`, `C`, `D`), navigation, chapter picker menus, and test submission.
  * Manages active quiz state per user in memory.
  * Triggers PDF report generation and AI performance evaluation upon test completion.

#### 3. [`questions.py`](file:///home/arun/projects/neet_pp/neet_bot/questions.py)
* **Function**: Question database loader and selection engine.
* **What it does**:
  * Loads active dataset JSON files from `neet_bot/data/` for Biology, Chemistry, and Physics.
  * Provides `get_chapter_list(subject)`, `get_random_questions(chapter, count, subject)`, and `get_full_neet_mock()` functions.

#### 4. [`pdf_report.py`](file:///home/arun/projects/neet_pp/neet_bot/pdf_report.py)
* **Function**: ReportLab PDF test report card generator.
* **What it does**:
  * Generates styled, multi-page PDF report cards summarizing test performance.
  * Appends a dedicated **`💡 Detailed Solution`** box for every single question showing step-by-step mathematical derivations, NCERT explanations, and correct options.

#### 5. [`ai_analyzer.py`](file:///home/arun/projects/neet_pp/neet_bot/ai_analyzer.py)
* **Function**: AI Master Diagnostic Mentor.
* **What it does**:
  * Communicates with OpenAI's API (`gpt-4o-mini`).
  * Analyzes student missed questions and generates structured feedback covering **Core Weak Topics**, **Key Misconceptions**, and **Actionable NCERT Focus Plans**.

#### 6. [`db.py`](file:///home/arun/projects/neet_pp/neet_bot/db.py)
* **Function**: SQLite database layer (`neet_bot.db`).
* **What it does**:
  * Stores user profiles, test history, question attempts, scores, and web analytics.
  * Computes aggregate platform analytics (total tests taken, average percentage, top weak chapters).

#### 7. [`config.py`](file:///home/arun/projects/neet_pp/neet_bot/config.py)
* **Function**: Central environment configuration file.
* **What it does**:
  * Loads environment variables from `.env` (Telegram Bot Tokens, OpenAI API Key, Admin Password, Port).

---

### Web App Directory (`neet_bot/web/`)

| File | Purpose |
| :--- | :--- |
| **`index.html`** | Student-facing interactive web application for taking chapterwise tests directly in the browser. |
| **`admin.html`** | Password-protected admin dashboard displaying live student performance metrics and analytics. |
| **`app.js`** | Client-side JavaScript handling test state, timer countdown, API requests, and dynamic UI rendering. |
| **`style.css`** | Modern, responsive dark-mode styling with glassmorphism aesthetics. |
| **`logo.png`** | Platform branding badge. |

---

### Data Directory (`neet_bot/data/`)

| File | Question Count | Active NTA Chapters |
| :--- | :-: | :-: |
| **`questions_dataset.json`** | 11,279 Biology Questions | 32 NTA Biology Chapters |
| **`chemistry_questions.json`** | 4,392 Chemistry Questions | 18 NTA Chemistry Chapters |
| **`physics_questions.json`** | 4,524 Physics Questions | 20 NTA Physics Chapters |
