# NEET Practice Paper Bot — Understanding Document

## What We're Building

A **Telegram bot** that helps NEET aspirants practice Biology daily with interactive quizzes and AI-powered evaluation PDF reports.

---

## Core Workflow

### 1. Daily Test Delivery (50 Questions)

- Every day, the bot sends **exactly 50 questions** to students.
- Questions are selected **chapter-by-chapter** (e.g., start with Chapter 1 of Class 11, finish all its questions, then move to Chapter 2, and so on).
- The questions are generated from:
  - **NCERT textbooks** (Class 11 & 12 Biology chapter PDFs we downloaded)
  - **NEET PYQs** (last 10 years of question papers we downloaded)
- Questions are delivered as **Telegram quiz messages** (MCQ with 4 options) — one by one.
- **No PDF is used for delivering questions.**

### 2. Answering & Instant Feedback on Telegram

- Each question appears as a **Telegram quiz poll** with a single correct answer.
- Student taps their chosen option → bot instantly reveals if it was correct or wrong and shows the right answer.
- Instant feedback per question — no waiting for all 50.

### 3. AI-Powered Post-Test Analysis (PDF Report)

- Once all 50 questions are attempted, the student can trigger **"Analyze My Performance"** .
- The AI looks at:
  - Which questions were right vs wrong
  - Which **chapters/topics** the student is weak in
  - **Patterns** in mistakes (e.g., consistently wrong on Plant Kingdom or Genetics)
- It generates a **personalized PDF report** with:
  - Score summary
  - Topic-wise strength/weakness breakdown
  - Suggestions on what to revise next
- This PDF is for **evaluation/reference only** — questions themselves are never in a PDF.

---

## Key Components (What the Bot Needs)

| Component | Purpose |
|-----------|---------|
| **Question Generator** | Creates MCQs from NCERT content + PYQs, chapter-by-chapter |
| **Telegram Bot** | Sends quiz questions one-by-one, collects answers, shows instant right/wrong |
| **PDF Report Generator** | Builds a post-test analysis PDF (evaluation report only) |
| **AI Analyzer** | Takes student's performance data → generates weakness analysis + PDF report content |
| **Progress Tracker** | Knows which chapter each student is on, how many questions they've done |

---

## Student's Experience (Step by Step)

1. Student opens the Telegram bot.
2. Bot says: *"Today's test: Class 11 — Chapter 4: Animal Kingdom (50 questions)"*
3. Bot sends **Question 1** as a Telegram quiz: *"Which of the following is not a characteristic of phylum Annelida?"* with 4 option buttons.
4. Student taps an option.
5. Bot instantly shows: *"Correct ✓"* or *"Wrong ✗ — Correct answer: C"*.
6. Bot moves to **Question 2**, and so on through all 50.
7. After all 50 done, student taps **"Analyze My Performance"** .
8. AI generates a **PDF report** and the bot sends it: *"You scored 38/50. Weak areas: Animal Kingdom (60%), Biomolecules (40%). Revise Chapter 4 & 9."*

---

## Data We Already Have

| Data | Location |
|------|----------|
| NCERT Class 11 Biology (20 chapters) | `data/bio_ncert/class11/` |
| NCERT Class 12 Biology (13 chapters) | `data/bio_ncert/class12/` |
| NEET PYQs 2016–2025 (11 papers) | `data/pyqs/` |

---

## What's NOT Decided Yet (For Later Planning)

- Technology stack (Python? Node.js?)
- How exactly questions are generated (LLM-based? Template-based? Both?)
- How the PDF report is built (Latex? ReportLab? WeasyPrint?)
- Database for storing student progress
- Hosting/deployment
