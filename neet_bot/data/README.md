# 📊 Bundled NEET Datasets (`neet_bot/data/`)

This directory contains the production JSON question banks bundled directly inside the repository to ensure offline availability and instant execution on Docker / Railway hosting containers.

---

## 📂 File-by-File Breakdown

| Dataset File | Subject | Chapter Count | Total MCQs | Description |
| :--- | :--- | :-: | :-: | :--- |
| **`questions_dataset.json`** | NEET Biology | **32 Chapters** | **7,735 MCQs** | Complete NCERT Biology line-by-line question bank covering Class 11 and Class 12 topics in official NTA order. |
| **`physics_questions.json`** | NEET Physics | **20 Chapters** | **5,000 MCQs** | Complete Physics question bank (250 questions per chapter) covering Mechanics, Thermodynamics, Electrodynamics, Optics, and Modern Physics. |
| **`chemistry_questions.json`** | NEET Chemistry | **20 Chapters** | **5,000 MCQs** | Complete Chemistry question bank (250 questions per chapter) covering Organic Reactions, Bonding, Thermodynamics, Equilibrium, and Kinetics. |

---

## 📐 Data Schema

Each JSON dataset follows a standardized schema:

```json
{
  "subject": "NEET Subject Name",
  "total_chapters": 20,
  "total_questions": 5000,
  "chapter_order": [
    "Chapter Name 1",
    "Chapter Name 2"
  ],
  "chapters": {
    "Chapter Name 1": [
      {
        "question": "Question text without Q-number prefix...",
        "options": {
          "A": "Option A text",
          "B": "Option B text",
          "C": "Option C text",
          "D": "Option D text"
        },
        "answer": "A"
      }
    ]
  }
}
```

---

## 🧹 Quality Assurance Standards

- **Zero Q-Prefixes**: All `Q121:` or `Q1:` prefixes have been stripped.
- **Clean Unicode Formatting**: Chemical formulas (`H₂SO₄`, `CH₃-CH=CH₂`, `sp³d²`), physics variables (`vₑ`, `Kₛₚ`), and degree symbols (`45°`) are pre-formatted.
- **25% Balanced Answer Key**: Correct answers (`A`, `B`, `C`, `D`) are evenly distributed.
