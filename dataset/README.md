# 📚 NEET & JEE Mains Test Dataset (Biology, Chemistry & Physics)

A comprehensive, curated test dataset of authentic **NEET** and **JEE Mains** Previous Year Questions (PYQs) from the last 14 years (2012–2025) along with high-yield popular NCERT question banks.

Every question includes complete multiple-choice options, correct answer keys, detailed step-by-step solutions/explanations, examination year tags, and standard NCERT chapter categorizations.

---

## 📊 Master Dataset Overview & Statistics

| Subject | Total Questions | NEET PYQs | JEE Mains PYQs / Popular NCERT Qs | NCERT Chapters | Formats |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Biology** | **10,427** | 1,836 | 8,591 | 38 | JSON, JSONL |
| **Chemistry** | **5,243** | 3,270 | 1,973 | 20 | JSON, JSONL |
| **Physics** | **3,841** | 1,571 | 2,270 | 20 | JSON, JSONL |
| **GRAND TOTAL** | **19,511** | **6,677** | **12,834** | **78** | **JSON, JSONL** |

---

## 📁 Directory Structure

```
dataset/
├── README.md                           # Master dataset documentation & statistics
├── biology/
│   ├── biology_pyqs_dataset.json       # Master JSON grouped by NCERT Biology Chapters
│   ├── biology_pyqs.jsonl              # JSONL stream (1 line per question)
│   └── neet_pyqs_14yr.json             # 14-Year NEET Biology PYQs (2012-2025)
├── chemistry/
│   ├── chemistry_pyqs_dataset.json     # Master JSON grouped by NCERT Chemistry Chapters
│   ├── chemistry_pyqs.jsonl            # JSONL stream (1 line per question)
│   ├── neet_pyqs_10yr.json             # 10-Year NEET Chemistry PYQs
│   └── jee_mains_pyqs_10yr.json        # 10-Year JEE Mains Chemistry PYQs (2015-2025)
└── physics/
    ├── physics_pyqs_dataset.json       # Master JSON grouped by NCERT Physics Chapters
    ├── physics_pyqs.jsonl              # JSONL stream (1 line per question)
    ├── neet_pyqs_10yr.json             # 10-Year NEET Physics PYQs
    └── jee_mains_pyqs_10yr.json        # 10-Year JEE Mains Physics PYQs (2015-2025)
```

---

## 📝 Item Schema

Each question object in the JSON/JSONL dataset follows this standard schema:

```json
{
  "question": "What is the estimated number of known and described species on Earth?",
  "options": {
    "A": "1.7-1.8 million",
    "B": "7-8 million",
    "C": "2 million",
    "D": "500,000"
  },
  "answer": "A",
  "solution": "**Correct Answer: (A)**\n\n**Explanation:**\nThe number of known and described species on Earth ranges between 1.7-1.8 million.",
  "exam": "NEET 2020",
  "year": 2020,
  "subject": "Biology",
  "chapter": "The Living World"
}
```

---

## 💻 Usage Code Examples

### Python (JSON Loading)
```python
import json

# Load Biology Master Dataset
with open('dataset/biology/biology_pyqs_dataset.json') as f:
    bio_data = json.load(f)

print(f"Total Biology Questions: {bio_data['total_questions']}")
first_chapter = list(bio_data['chapters'].keys())[0]
sample_q = bio_data['chapters'][first_chapter][0]

print("Question:", sample_q['question'])
print("Options:", sample_q['options'])
print("Correct Answer:", sample_q['answer'])
print("Solution:", sample_q['solution'])
```

### Python (JSONL Streaming)
```python
import json

# Stream 14-Year Biology PYQs
with open('dataset/biology/biology_pyqs.jsonl') as f:
    for line in f:
        q = json.loads(line)
        if q['exam'].startswith('NEET') and q['year'] >= 2020:
            print(f"[{q['exam']}] {q['chapter']}: {q['question'][:80]}...")
```
