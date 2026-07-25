# ⚡ `physics_bot` — Specialized GPT Physics Telegram Bot

`physics_bot` is a standalone, dedicated Telegram bot service focused exclusively on NEET and JEE Mains **Physics** preparation.

---

## 📄 File-by-File Breakdown & Responsibilities

### Core Application Files

#### 1. [`main.py`](file:///home/arun/projects/neet_pp/physics_bot/main.py)
* **Function**: Single-subject runner and health server.
* **What it does**:
  * Initializes the Physics database (`db.py`).
  * Runs Telegram polling for the Physics Telegram Bot Token (`PHYSICS_BOT_TOKEN`).
  * Serves local web test interfaces and health check endpoints.

#### 2. [`bot_handlers.py`](file:///home/arun/projects/neet_pp/physics_bot/bot_handlers.py)
* **Function**: Telegram bot command handlers tailored for Physics.
* **What it does**:
  * Handles `/start`, `/test`, `/mock`, `/analytics` commands.
  * Manages Physics chapter selection menus (*Mechanics, Electrodynamics, Optics, Thermodynamics, Modern Physics*).
  * Evaluates responses and triggers AI performance analysis and PDF report card generation.

#### 3. [`questions.py`](file:///home/arun/projects/neet_pp/physics_bot/questions.py)
* **Function**: Physics question dataset loader.
* **What it does**:
  * Loads `physics_bot/data/questions_dataset.json` containing **4,524 Physics PYQs & NCERT questions** across 20 active NTA chapters.
  * Provides randomized question selection per chapter or full subject mock test.

#### 4. [`pdf_report.py`](file:///home/arun/projects/neet_pp/physics_bot/pdf_report.py)
* **Function**: Physics PDF test report generator.
* **What it does**:
  * Builds downloadable PDF report cards featuring score summaries, question-by-question analysis, and **💡 Detailed Solutions** with step-by-step derivations for every question.

#### 5. [`ai_analyzer.py`](file:///home/arun/projects/neet_pp/physics_bot/ai_analyzer.py)
* **Function**: AI Physics Diagnostic Mentor.
* **What it does**:
  * Communicates with OpenAI `gpt-4o-mini` to evaluate student errors in Physics (*e.g. unit conversion traps, sign convention errors, vector resolution*).

#### 6. [`db.py`](file:///home/arun/projects/neet_pp/physics_bot/db.py)
* **Function**: SQLite database driver for Physics bot analytics.

#### 7. [`config.py`](file:///home/arun/projects/neet_pp/physics_bot/config.py)
* **Function**: Configuration file for Physics bot tokens and credentials.

---

### Data Directory (`physics_bot/data/`)

| File | Question Count | Active NTA Chapters |
| :--- | :-: | :-: |
| **`questions_dataset.json`** | 4,524 Questions | 20 Active NTA Physics Chapters |
