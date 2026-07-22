# 🛠️ Scratch Scripts & Generator Pipelines (`scratch/`)

This directory contains standalone Python pipeline scripts used to generate 5,000 Physics MCQs, 5,000 Chemistry MCQs, order chapters according to official NTA syllabus sequence, clean MathML tags, and strip Q-number prefixes.

---

## 📄 Script Breakdown

| Script Name | Functionality & Utility |
| :--- | :--- |
| **`generate_unique_5000_phys_chem.py`** | Generates 5,000 unique Physics MCQs (250 questions per chapter) with chapter-specific formulas for all 20 Physics chapters. |
| **`generate_unique_chemistry.py`** | Generates 5,000 unique Chemistry MCQs (250 questions per chapter) with chemical equations for all 20 Chemistry chapters. |
| **`order_nta_syllabus.py`** | Reorders chapter keys in `questions_dataset.json`, `physics_questions.json`, and `chemistry_questions.json` to match the exact official NTA / NCERT syllabus sequence. |
| **`clean_mathml_and_unicode.py`** | Strips raw MathML HTML tags (`<math ...>`), resolves unescaped HTML entities, and cleans non-breaking space characters (`\u00a0`). |
| **`strip_q_numbers_and_degrees.py`** | Permanently strips `Q121:` question number prefixes and converts `^circ` LaTeX angle notation into clean degree symbols (`°`). |

---

## ⚡ Execution Command

Scripts in `scratch/` can be run independently using the project virtual environment:

```bash
python3 scratch/order_nta_syllabus.py
python3 scratch/strip_q_numbers_and_degrees.py
```
