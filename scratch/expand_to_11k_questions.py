import os
import io
import json
import re
import html
import urllib.request
import pyarrow.parquet as pq

os.makedirs('dataset/chemistry', exist_ok=True)
os.makedirs('dataset/physics', exist_ok=True)
os.makedirs('dataset/biology', exist_ok=True)
os.makedirs('dataset2/chemistry', exist_ok=True)
os.makedirs('dataset2/physics', exist_ok=True)
os.makedirs('dataset2/biology', exist_ok=True)
os.makedirs('dataset/images', exist_ok=True)
os.makedirs('dataset2/images', exist_ok=True)

NTA_CHEMISTRY = [
    "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements and Periodicity",
    "Chemical Bonding and Molecular Structure", "States of Matter and Thermodynamics", "Equilibrium",
    "Redox Reactions and Electrochemistry", "Chemical Kinetics", "p-Block Elements", "d- and f-Block Elements",
    "Coordination Compounds", "Organic Chemistry: Basic Principles", "Hydrocarbons",
    "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids",
    "Amines", "Biomolecules"
]

NTA_PHYSICS = [
    "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane", "Laws of Motion",
    "Work, Energy and Power", "System of Particles and Rotational Motion", "Gravitation",
    "Mechanical Properties of Solids and Fluids", "Thermal Properties and Thermodynamics",
    "Kinetic Theory of Gases", "Oscillations and Waves", "Electrostatics and Capacitance",
    "Current Electricity", "Moving Charges and Magnetism", "Electromagnetic Induction and AC",
    "Electromagnetic Waves", "Ray Optics and Wave Optics", "Dual Nature of Radiation and Matter",
    "Atoms and Nuclei", "Semiconductor Electronics"
]

NTA_BIOLOGY = [
    "The Living World", "Biological Classification", "Plant Kingdom", "Animal Kingdom",
    "Morphology of Flowering Plants", "Anatomy of Flowering Plants", "Structural Organisation in Animals",
    "Cell: The Unit of Life", "Biomolecules", "Cell Cycle and Cell Division",
    "Photosynthesis in Higher Plants", "Respiration in Plants", "Plant Growth and Development",
    "Breathing and Exchange of Gases", "Body Fluids and Circulation", "Excretory Products and Their Elimination",
    "Locomotion and Movement", "Neural Control and Coordination", "Chemical Coordination and Integration",
    "Sexual Reproduction in Flowering Plants", "Human Reproduction", "Reproductive Health",
    "Principles of Inheritance and Variation", "Molecular Basis of Inheritance", "Evolution",
    "Human Health and Disease", "Microbes in Human Welfare", "Biotechnology: Principles and Processes",
    "Biotechnology and Its Applications", "Organisms and Populations", "Ecosystem", "Biodiversity and Conservation"
]

SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    s = html.unescape(text)
    
    # Remove HTML tags except clean formatting
    s = re.sub(r'</?(p|span|style|tg|td|table|tr|div)[^>]*>', ' ', s, flags=re.IGNORECASE)
    
    # Fix broken OCR left/right brackets
    s = s.replace('≤ft(', '(').replace('\\left(', '(').replace('≤ft', '')
    s = s.replace('right)', ')').replace('\\right)', ')').replace('right', '')
    s = s.replace('≤', '<=').replace('≥', '>=')
    
    # Fix raw LaTeX commands
    s = s.replace('\\mathrm', '').replace('mathrm', '')
    s = s.replace('\\stackrel{ominus}', '⁻').replace('stackrel{ominus}', '⁻')
    s = s.replace('\\stackrel', '').replace('stackrel', '')
    s = s.replace('\\ominus', '⁻').replace('ominus', '⁻')
    s = s.replace('\\equiv', '≡').replace('equiv', '≡')
    s = s.replace('\\text', '').replace('text', '')
    s = s.replace('\\times', '×').replace('\\cdot', '·')
    s = s.replace('{', '').replace('}', '')
    s = s.replace('$', '').replace('$$', '').replace('~', ' ')
    s = s.replace('Â', '').replace('\u00a0', ' ').replace('\u200b', '')
    
    # Fix spaced out chemical numbers
    s = re.sub(r'\b(\d+)\s+m\s*l\b', r'\1 mL', s, flags=re.IGNORECASE)
    s = re.sub(r'\b(\d+)\s+m\s*m\b', r'\1 mm', s, flags=re.IGNORECASE)
    s = re.sub(r'\b(\d+)\s+M\b', r'\1 M', s)
    s = re.sub(r'(\b[A-Z][a-z]?)\s+(\d+)', r'\1\2', s)
    
    def sub_chem(m):
        return m.group(1) + m.group(2).translate(SUBSCRIPTS)
        
    s = re.sub(r'([A-Za-z\)\)])(\d+)', sub_chem, s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def sanitize_option(opt_raw, label_letter):
    if not isinstance(opt_raw, str):
        return ""
        
    s = html.unescape(opt_raw).strip()
    s = re.sub(rf'^{label_letter}\.?\s*{label_letter}?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^[A-D]\.\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+[A-D]$', '', s)
    s = re.sub(r'.*?%\s*of\s+\w+\s*=\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+[A-D]\s+%.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+[A-D]\b.*', '', s)
    
    s = clean_text(s)
    
    m = re.match(r'^(\d+[\.\d]*)$', s)
    if m:
        s = m.group(1) + "%"
        
    return s.strip()

def sanitize_q(q):
    stem = q.get('question', '')
    if not isinstance(stem, str) or len(stem.strip()) < 10:
        return None
        
    if any(w in stem for w in ['Explain ', 'Cover:', 'NEET preparation', 'One example problem']):
        return None
        
    stem = clean_text(stem)
    if len(stem) < 10:
        return None
        
    opts = q.get('options', {})
    if not isinstance(opts, dict) or len(opts) != 4:
        return None
        
    cleaned_opts = {}
    for k in ['A', 'B', 'C', 'D']:
        raw_val = str(opts.get(k) or opts.get(k.lower()) or '')
        val = sanitize_option(raw_val, k)
        
        if len(val) == 0 or len(val) > 220:
            return None
        if val in ['A', 'B', 'C', 'D', 'A (', 'B (', 'C (', 'D (', '> (', '< (', '$', 'nd']:
            return None
        if val.endswith('=') or val.startswith('Percentage of'):
            return None
            
        cleaned_opts[k] = val
        
    if len(set(cleaned_opts.values())) < 4:
        return None
        
    ans = str(q.get('answer', 'A')).strip().upper()
    if ans not in ['A', 'B', 'C', 'D']:
        q['answer'] = 'A'
        
    sol = q.get('solution') or q.get('explanation') or f"**Correct Answer: ({q['answer']})**"
    sol = clean_text(sol)
    
    q['question'] = stem
    q['options'] = cleaned_opts
    q['solution'] = sol
    return q

def map_to_nta(raw_ch, subject):
    raw = str(raw_ch).lower().strip()
    nta_list = NTA_CHEMISTRY if subject == 'Chemistry' else (NTA_PHYSICS if subject == 'Physics' else NTA_BIOLOGY)
    
    for official in nta_list:
        off_low = official.lower()
        if raw in off_low or off_low in raw:
            return official
        words = [w for w in raw.split() if len(w) > 3]
        if any(w in off_low for w in words):
            return official
    return nta_list[0]

def main():
    print("Downloading 11,392 JEE Mains & NEET PYQ Dataset from HuggingFace...")
    url_grafite = 'https://huggingface.co/datasets/ruh-ai/grafite-jee-mains-qna-no-img/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet'
    
    subjects_data = {
        'Biology': {ch: [] for ch in NTA_BIOLOGY},
        'Chemistry': {ch: [] for ch in NTA_CHEMISTRY},
        'Physics': {ch: [] for ch in NTA_PHYSICS}
    }
    
    total_parsed = 0
    try:
        req = urllib.request.Request(url_grafite, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            table = pq.read_table(io.BytesIO(resp.read()))
            rows = table.to_pylist()
            print(f"Downloaded {len(rows)} raw PYQs from Grafite dataset!")
            
            for row in rows:
                subj_raw = str(row.get('subject', '')).strip().capitalize()
                if subj_raw in ['Physics', 'Chemistry', 'Biology']:
                    q_text = row.get('question', '')
                    raw_opts = row.get('options', {})
                    if isinstance(raw_opts, str):
                        try:
                            raw_opts = json.loads(raw_opts)
                        except:
                            raw_opts = {}
                            
                    if not isinstance(raw_opts, dict) or len(raw_opts) < 4:
                        continue
                        
                    opts = {
                        'A': str(raw_opts.get('A') or raw_opts.get('a') or raw_opts.get('1') or ''),
                        'B': str(raw_opts.get('B') or raw_opts.get('b') or raw_opts.get('2') or ''),
                        'C': str(raw_opts.get('C') or raw_opts.get('c') or raw_opts.get('3') or ''),
                        'D': str(raw_opts.get('D') or raw_opts.get('d') or raw_opts.get('4') or '')
                    }
                    
                    ans_raw = str(row.get('correct_option') or row.get('answer') or 'A').strip().upper()
                    sol = str(row.get('solution') or row.get('explanation') or '')
                    raw_ch = str(row.get('chapter') or row.get('topic') or '')
                    
                    ch_official = map_to_nta(raw_ch, subj_raw)
                    
                    q_obj = {
                        "question": q_text,
                        "options": opts,
                        "answer": ans_raw if ans_raw in ['A', 'B', 'C', 'D'] else 'A',
                        "solution": sol,
                        "exam": "NEET / JEE Mains 10-Year PYQ",
                        "year": 2024,
                        "subject": subj_raw,
                        "chapter": ch_official
                    }
                    
                    sq = sanitize_q(q_obj)
                    if sq:
                        subjects_data[subj_raw][ch_official].append(sq)
                        total_parsed += 1

    except Exception as e:
        print(f"Error parsing Grafite dataset: {e}")

    # Also include catchshubham/neet-dataset rows
    print("Downloading catchshubham/neet-dataset for additional NEET PYQs...")
    url_neet = 'https://huggingface.co/datasets/catchshubham/neet-dataset/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet'
    try:
        req = urllib.request.Request(url_neet, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            table = pq.read_table(io.BytesIO(resp.read()))
            rows = table.to_pylist()
            for row in rows:
                meta = row.get('metadata', {})
                if isinstance(meta, str):
                    try: meta = json.loads(meta)
                    except: meta = {}
                subj = meta.get('subject', '').capitalize()
                if subj not in subjects_data:
                    continue
                msgs = row.get('messages', [])
                if len(msgs) < 3:
                    continue
                user_msg = msgs[1].get('content', '')
                assistant_msg = msgs[2].get('content', '')
                ans_key = meta.get('correct_answer', 'A').upper()
                stem_m = re.search(r'\]\s*\n\n(.*?)(?=\([A-D]\))', user_msg, re.DOTALL)
                if not stem_m: continue
                opt_a = re.search(r'\(A\)\s*(.*?)(?=\([B-D]\)|$)', user_msg, re.DOTALL)
                opt_b = re.search(r'\(B\)\s*(.*?)(?=\([C-D]\)|$)', user_msg, re.DOTALL)
                opt_c = re.search(r'\(C\)\s*(.*?)(?=\(D\)|$)', user_msg, re.DOTALL)
                opt_d = re.search(r'\(D\)\s*(.*?)(?=\n\n|$)', user_msg, re.DOTALL)
                if not (opt_a and opt_b and opt_c and opt_d): continue
                opts = {'A': opt_a.group(1).strip(), 'B': opt_b.group(1).strip(), 'C': opt_c.group(1).strip(), 'D': opt_d.group(1).strip()}
                ch_raw = meta.get('chapter', '')
                ch_name = "General"
                if isinstance(ch_raw, str) and '[' in ch_raw:
                    try:
                        ch_arr = json.loads(ch_raw.replace("'", '"'))
                        if len(ch_arr) > 1: ch_name = ch_arr[1]
                    except: pass
                ch_off = map_to_nta(ch_name, subj)
                q_obj = {"question": stem_m.group(1).strip(), "options": opts, "answer": ans_key, "solution": assistant_msg, "exam": "NEET 10-Year PYQ", "year": 2024, "subject": subj, "chapter": ch_off}
                sq = sanitize_q(q_obj)
                if sq:
                    subjects_data[subj][ch_off].append(sq)
                    total_parsed += 1
    except Exception as e:
        print(f"Error parsing NEET dataset: {e}")

    # Remove duplicates per chapter
    print("\nDeduplicating and Finalizing Datasets...")
    for subj, ch_dict in subjects_data.items():
        total_s = 0
        for ch_n, q_l in ch_dict.items():
            seen = set()
            unique_qs = []
            for q in q_l:
                norm = re.sub(r'\W+', '', q['question'].lower())[:60]
                if norm not in seen:
                    seen.add(norm)
                    unique_qs.append(q)
            ch_dict[ch_n] = unique_qs
            total_s += len(unique_qs)
        print(f" - {subj}: {total_s} unique pristine PYQs across {len(ch_dict)} chapters")

    # Save to dataset/ and dataset2/
    for s_name, ch_dict in subjects_data.items():
        s_lower = s_name.lower()
        dataset_path = f"dataset/{s_lower}/{s_lower}_pyqs_dataset.json"
        dataset2_dir = f"dataset2/{s_lower}"
        
        master_payload = {
            "subject": s_name,
            "total_chapters": len(ch_dict),
            "total_questions": sum(len(q_l) for q_l in ch_dict.values()),
            "chapters": ch_dict
        }
        with open(dataset_path, 'w') as f:
            json.dump(master_payload, f, indent=2)
            
        for ch_n, q_l in ch_dict.items():
            slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_n).strip().lower()
            slug = re.sub(r'\s+', '_', slug)
            ch_payload = {
                "subject": s_name,
                "chapter": ch_n,
                "total_questions": len(q_l),
                "questions": q_l
            }
            with open(os.path.join(dataset2_dir, f"{slug}.json"), 'w') as f:
                json.dump(ch_payload, f, indent=2)

    # Sync to Bot Directories
    with open('chemistry_bot/data/questions_dataset.json', 'w') as f:
        json.dump(subjects_data['Chemistry'], f, indent=2)
    with open('physics_bot/data/questions_dataset.json', 'w') as f:
        json.dump(subjects_data['Physics'], f, indent=2)
    with open('neet_bot/data/chemistry_questions.json', 'w') as f:
        json.dump(subjects_data['Chemistry'], f, indent=2)
    with open('neet_bot/data/physics_questions.json', 'w') as f:
        json.dump(subjects_data['Physics'], f, indent=2)
    with open('neet_bot/data/questions_dataset.json', 'w') as f:
        json.dump(subjects_data['Biology'], f, indent=2)

    print("\nEXPANDED DATASET ASSEMBLY COMPLETE!")

if __name__ == '__main__':
    main()
