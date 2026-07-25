# 🧪 `chemistry_bot` — Specialized GPT Chemistry Telegram Bot

`chemistry_bot` is a standalone, dedicated Telegram bot service focused exclusively on NEET and JEE Mains **Chemistry** preparation.

---

## 📄 File-by-File Breakdown & Responsibilities

### Core Application Files

#### 1. [`main.py`](file:///home/arun/projects/neet_pp/chemistry_bot/main.py)
* **Function**: Single-subject runner and health server.
* **What it does**:
  * Initializes the Chemistry database (`db.py`).
  * Runs Telegram polling for the Chemistry Telegram Bot Token (`CHEMISTRY_BOT_TOKEN`).
  * Serves local web test interfaces and health check endpoints.

#### 2. [`bot_handlers.py`](file:///home/arun/projects/neet_pp/chemistry_bot/bot_handlers.py)
* **Function**: Telegram bot command handlers tailored for Chemistry.
* **What it does**:
  * Handles `/start`, `/test`, `/mock`, `/analytics` commands.
  * Manages Chemistry chapter selection menus (*Physical, Inorganic, Organic Chemistry*).
  * Evaluates responses and triggers AI performance analysis and PDF report card generation.

#### 3. [`questions.py`](file:///home/arun/projects/neet_pp/chemistry_bot/questions.py)
* **Function**: Chemistry question dataset loader.
* **What it does**:
  * Loads `chemistry_bot/data/questions_dataset.json` containing **4,392 Chemistry PYQs & NCERT questions** across 18 active NTA chapters.
  * Provides randomized question selection per chapter or full subject mock test.

#### 4. [`pdf_report.py`](file:///home/arun/projects/neet_pp/chemistry_bot/pdf_report.py)
* **Function**: Chemistry PDF test report generator.
* **What it does**:
  * Builds downloadable PDF report cards featuring score summaries, question-by-question analysis, and **💡 Detailed Solutions** for every question.

#### 5. [`ai_analyzer.py`](file:///home/arun/projects/neet_pp/chemistry_bot/ai_analyzer.py)
* **Function**: AI Chemistry Diagnostic Mentor.
* **What it does**:
  * Communicates with OpenAI `gpt-4o-mini` to evaluate student errors in Chemistry (*e.g. stoichiometry traps, formula confusion, reaction mechanisms*).

#### 6. [`db.py`](file:///home/arun/projects/neet_pp/chemistry_bot/db.py)
* **Function**: SQLite database driver for Chemistry bot analytics.

#### 7. [`config.py`](file:///home/arun/projects/neet_pp/chemistry_bot/config.py)
* **Function**: Configuration file for Chemistry bot tokens and credentials.

---

### Data Directory (`chemistry_bot/data/`)

| File | Question Count | Active NTA Chapters |
| :--- | :-: | :-: |
| **`questions_dataset.json`** | 4,392 Questions | 18 Active NTA Chemistry Chapters |
