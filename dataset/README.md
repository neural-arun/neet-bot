# 📚 Official NTA NEET Test Dataset (Biology, Chemistry & Physics)

A comprehensive, curated test dataset of authentic **NEET** and **JEE Mains** Previous Year Questions (PYQs) and high-yield NCERT question banks filtered strictly according to the **Latest Official NTA NEET Syllabus**.

All deleted/out-of-syllabus chapters (e.g. *Transport in Plants*, *Digestion and Absorption*, *Mineral Nutrition*, *Reproduction in Organisms*, *Environmental Issues*, *Surface Chemistry & Extraction*, *Polymers & Everyday Chemistry*) have been completely removed.

Every question includes complete multiple-choice options, correct answer keys, detailed step-by-step solutions/explanations, examination year tags, and standard active NCERT chapter categorizations.

---

## 📊 Master Dataset Overview & Statistics (Active NTA Syllabus)

| Subject | Total Questions | NEET PYQs | Practice / NCERT Question Banks | NTA Chapters | Formats |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Biology** | **11,279** | 1,836 | 9,443 | **32** | JSON, JSONL |
| **Chemistry** | **4,392** | 2,419 | 1,973 | **18** | JSON, JSONL |
| **Physics** | **4,524** | 2,254 | 2,270 | **20** | JSON, JSONL |
| **GRAND TOTAL** | **20,195** | **6,509** | **13,686** | **70** | **JSON, JSONL** |

---

## 📁 Directory Structure

```
dataset/
├── README.md                           # Master NTA dataset documentation & statistics
├── biology/
│   ├── biology_pyqs_dataset.json       # Master JSON (32 Active NTA Biology Chapters)
│   ├── biology_pyqs.jsonl              # JSONL stream (1 line per question)
│   └── neet_pyqs_14yr.json             # 14-Year NEET Biology PYQs (2012-2025)
├── chemistry/
│   ├── chemistry_pyqs_dataset.json     # Master JSON (18 Active NTA Chemistry Chapters)
│   ├── chemistry_pyqs.jsonl            # JSONL stream (1 line per question)
│   ├── neet_pyqs_10yr.json             # 10-Year NEET Chemistry PYQs
│   └── jee_mains_pyqs_10yr.json        # 10-Year JEE Mains Chemistry PYQs (2015-2025)
└── physics/
    ├── physics_pyqs_dataset.json       # Master JSON (20 Active NTA Physics Chapters)
    ├── physics_pyqs.jsonl              # JSONL stream (1 line per question)
    ├── neet_pyqs_10yr.json             # 10-Year NEET Physics PYQs
    └── jee_mains_pyqs_10yr.json        # 10-Year JEE Mains Physics PYQs (2015-2025)
```
