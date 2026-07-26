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

# ---------------------------------------------------------------------
# NTA NCERT CHAPTER MAPPER & SANITIZER
# ---------------------------------------------------------------------

SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def clean_chemical_math_text(text):
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
    s = re.sub(r'(\b[A-Z])\s+([A-Z]\b)', r'\1\2', s)
    
    # Convert element numbers to subscripts (e.g. H2SO4 -> H₂SO₄, CH3 -> CH₃)
    def sub_chem(m):
        elem = m.group(1)
        num = m.group(2)
        return elem + num.translate(SUBSCRIPTS)
        
    s = re.sub(r'([A-Za-z\)\)])(\d+)', sub_chem, s)
    
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def sanitize_option_val(opt_raw, label_letter):
    if not isinstance(opt_raw, str):
        return ""
        
    s = html.unescape(opt_raw).strip()
    
    # Remove letter prefixes
    s = re.sub(rf'^{label_letter}\.?\s*{label_letter}?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^[A-D]\.\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+[A-D]$', '', s)
    
    # Remove concatenated calculation labels
    s = re.sub(r'.*?%\s*of\s+\w+\s*=\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+[A-D]\s+%.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+[A-D]\b.*', '', s)
    
    s = clean_chemical_math_text(s)
    
    m = re.match(r'^(\d+[\.\d]*)$', s)
    if m:
        s = m.group(1) + "%"
        
    return s.strip()

def sanitize_question(q):
    stem = q.get('question', '')
    if not isinstance(stem, str) or len(stem.strip()) < 10:
        return None
        
    if any(w in stem for w in ['Explain ', 'Cover:', 'NEET preparation', 'One example problem']):
        return None
        
    stem = clean_chemical_math_text(stem)
    if len(stem) < 10:
        return None
        
    opts = q.get('options', {})
    if not isinstance(opts, dict) or len(opts) != 4:
        return None
        
    cleaned_opts = {}
    for k in ['A', 'B', 'C', 'D']:
        raw_val = str(opts.get(k) or opts.get(k.lower()) or '')
        val = sanitize_option_val(raw_val, k)
        
        if len(val) == 0 or len(val) > 200:
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
    sol = clean_chemical_math_text(sol)
    
    q['question'] = stem
    q['options'] = cleaned_opts
    q['solution'] = sol
    return q

def slugify(ch_name):
    slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_name).strip().lower()
    slug = re.sub(r'\s+', '_', slug)
    return slug

def main():
    print("Downloading HuggingFace NEET PYQ Datasets...")
    url_neet = 'https://huggingface.co/datasets/catchshubham/neet-dataset/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet'
    
    try:
        req = urllib.request.Request(url_neet, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            table = pq.read_table(io.BytesIO(resp.read()))
            rows = table.to_pylist()
            print(f"Successfully downloaded {len(rows)} raw PYQ rows from HuggingFace!")
    except Exception as e:
        print(f"Error downloading HF dataset: {e}")
        return

    # Parse and structure questions by Subject and Chapter
    subjects_data = {
        'Biology': {},
        'Chemistry': {},
        'Physics': {}
    }

    for row in rows:
        meta = row.get('metadata', {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
                
        subj = meta.get('subject', '')
        if subj not in subjects_data:
            continue
            
        msgs = row.get('messages', [])
        if len(msgs) < 3:
            continue
            
        user_msg = msgs[1].get('content', '')
        assistant_msg = msgs[2].get('content', '')
        ans_key = meta.get('correct_answer', 'A').upper()
        
        # Extract question stem & options from user message
        # Format: "[NEET PYQ | Subject]\n\nStem...\n\n(A) ...\n(B) ...\n(C) ...\n(D) ..."
        stem_m = re.search(r'\]\s*\n\n(.*?)(?=\([A-D]\))', user_msg, re.DOTALL)
        if not stem_m:
            continue
        q_stem = stem_m.group(1).strip()
        
        opt_a = re.search(r'\(A\)\s*(.*?)(?=\([B-D]\)|$)', user_msg, re.DOTALL)
        opt_b = re.search(r'\(B\)\s*(.*?)(?=\([C-D]\)|$)', user_msg, re.DOTALL)
        opt_c = re.search(r'\(C\)\s*(.*?)(?=\(D\)|$)', user_msg, re.DOTALL)
        opt_d = re.search(r'\(D\)\s*(.*?)(?=\n\n|$)', user_msg, re.DOTALL)
        
        if not (opt_a and opt_b and opt_c and opt_d):
            continue
            
        opts = {
            'A': opt_a.group(1).strip(),
            'B': opt_b.group(1).strip(),
            'C': opt_c.group(1).strip(),
            'D': opt_d.group(1).strip()
        }
        
        # Determine chapter
        ch_raw = meta.get('chapter', '')
        ch_name = "General"
        if isinstance(ch_raw, str) and '[' in ch_raw:
            try:
                ch_arr = json.loads(ch_raw.replace("'", '"'))
                if len(ch_arr) > 1:
                    ch_name = ch_arr[1]
            except:
                pass
                
        q_obj = {
            "question": q_stem,
            "options": opts,
            "answer": ans_key,
            "solution": assistant_msg,
            "exam": "NEET 10-Year PYQ",
            "year": 2024,
            "subject": subj,
            "chapter": ch_name
        }
        
        sq = sanitize_question(q_obj)
        if sq:
            ch_group = subjects_data[subj].setdefault(ch_name, [])
            ch_group.append(sq)

    print("\nParsed Raw PYQ Questions Breakdown:")
    for s_name, ch_dict in subjects_data.items():
        total_s = sum(len(q_l) for q_l in ch_dict.values())
        print(f" - {s_name}: {total_s} questions across {len(ch_dict)} chapters")

    # Generate Pristine Datasets & Save
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
            slug = slugify(ch_n)
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

    print("\nPristine Dataset Assembly & Bot Synchronization Complete!")

if __name__ == '__main__':
    main()
