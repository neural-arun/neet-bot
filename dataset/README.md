# 📚 NEET & JEE Mains 10-Year Test Dataset (Chemistry & Physics)

A comprehensive, curated test dataset of authentic **NEET** and **JEE Mains** Previous Year Questions (PYQs) from the last 10 years (2015–2025).

Every question includes complete multiple-choice options, correct answer keys, detailed step-by-step solutions/explanations, examination year tags, and standard NCERT chapter categorizations.

---

## 📊 Dataset Overview & Statistics

| Subject | Total PYQs | NEET PYQs | JEE Mains PYQs (2015-2025) | Chapters | Formats |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Chemistry** | **5,243** | 3,270 | 1,973 | 20 | JSON, JSONL |
| **Physics** | **3,841** | 1,571 | 2,270 | 20 | JSON, JSONL |
| **TOTAL** | **9,084** | **4,841** | **4,243** | **40** | **JSON, JSONL** |

---

## 📁 Directory Structure

```
dataset/
├── README.md                           # Dataset documentation & statistics
├── chemistry/
│   ├── chemistry_pyqs_dataset.json     # Master JSON grouped by NCERT Chapters
│   ├── chemistry_pyqs.jsonl            # JSONL stream (1 line per question)
│   ├── neet_pyqs_10yr.json             # 10-Year NEET Chemistry PYQs
│   └── jee_mains_pyqs_10yr.json        # 10-Year JEE Mains Chemistry PYQs (2015-2025)
└── physics/
    ├── physics_pyqs_dataset.json       # Master JSON grouped by NCERT Chapters
    ├── physics_pyqs.jsonl              # JSONL stream (1 line per question)
    ├── neet_pyqs_10yr.json             # 10-Year NEET Physics PYQs
    └── jee_mains_pyqs_10yr.json        # 10-Year JEE Mains Physics PYQs (2015-2025)
```

---

## 📝 Item Schema

Each question object in the JSON/JSONL dataset follows this standard schema:

```json
{
  "question": "What is the density of N₂ at 227 °C and 5.00 atm pressure? (R = 0.082 L atm K⁻¹ mol⁻¹)",
  "options": {
    "A": "3.41 g/mL",
    "B": "40 g/mL",
    "C": "81 g/mL",
    "D": "41 g/mL"
  },
  "answer": "A",
  "solution": "**Correct Answer: (A)**\n\n**Explanation:**\n$$\\begin{aligned} pV &= nRT \\\\ P &= \\frac{m}{M} \\times \\frac{RT}{V} \\\\ &= \\frac{5 \\times 28}{0.0821 \\times 500} = 3.41 \\text{ g/mL} \\end{aligned}$$",
  "exam": "NEET 2020",
  "year": 2020,
  "subject": "Chemistry",
  "chapter": "Some Basic Concepts of Chemistry"
}
```

---

## 📖 Chapter Breakdown

### 🧪 Chemistry Chapters (20 NCERT Chapters)
1. Some Basic Concepts of Chemistry
2. Structure of Atom
3. Classification of Elements and Periodicity
4. Chemical Bonding and Molecular Structure
5. States of Matter and Thermodynamics
6. Equilibrium
7. Redox Reactions and Electrochemistry
8. Chemical Kinetics
9. Surface Chemistry and Extraction
10. p-Block Elements
11. d- and f-Block Elements
12. Coordination Compounds
13. Organic Chemistry: Basic Principles
14. Hydrocarbons
15. Haloalkanes and Haloarenes
16. Alcohols, Phenols and Ethers
17. Aldehydes, Ketones and Carboxylic Acids
18. Amines
19. Biomolecules
20. Polymers and Everyday Chemistry

### ⚡ Physics Chapters (20 NCERT Chapters)
1. Units and Measurements
2. Motion in a Straight Line
3. Motion in a Plane
4. Laws of Motion
5. Work, Energy, and Power
6. System of Particles and Rotational Motion
7. Gravitation
8. Mechanical Properties of Solids and Fluids
9. Thermal Properties and Thermodynamics
10. Kinetic Theory of Gases
11. Oscillations and Waves
12. Electrostatics and Capacitance
13. Current Electricity
14. Moving Charges and Magnetism
15. Electromagnetic Induction and AC
16. Electromagnetic Waves
17. Ray Optics and Wave Optics
18. Dual Nature of Radiation and Matter
19. Atoms and Nuclei
20. Semiconductor Electronics

---

## 💻 Usage Code Examples

### Python (JSON Loading)
```python
import json

# Load Chemistry Master Dataset
with open('dataset/chemistry/chemistry_pyqs_dataset.json') as f:
    chem_data = json.load(f)

print(f"Total Chemistry Questions: {chem_data['total_questions']}")
first_chapter = list(chem_data['chapters'].keys())[0]
sample_q = chem_data['chapters'][first_chapter][0]

print("Question:", sample_q['question'])
print("Options:", sample_q['options'])
print("Correct Answer:", sample_q['answer'])
print("Solution:", sample_q['solution'])
```

### Python (JSONL Streaming)
```python
import json

# Stream Physics PYQs
with open('dataset/physics/physics_pyqs.jsonl') as f:
    for line in f:
        q = json.loads(line)
        if q['exam'].startswith('JEE Main') and q['year'] >= 2022:
            print(f"[{q['exam']}] {q['chapter']}: {q['question'][:80]}...")
```
