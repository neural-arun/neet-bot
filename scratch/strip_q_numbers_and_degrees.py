import json
import re
import html
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'neet_bot', 'data')

def clean_text_deep(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    
    # Strip Q121: / Q1: / Q45: prefix at the start
    s = re.sub(r'^Q\d+:\s*', '', s)
    
    # Replace ^circ, ^\circ, \circ with °
    s = s.replace('^circ', '°').replace('^\\circ', '°').replace('\\circ', '°')
    
    return s.strip()

def clean_dataset_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping missing file: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_count = 0
    chapters = data.get('chapters', {})

    for ch_name, q_list in chapters.items():
        for q in q_list:
            orig_q = q['question']
            cleaned_q = clean_text_deep(orig_q)
            if cleaned_q != orig_q:
                q['question'] = cleaned_q
                cleaned_count += 1

            opts = q.get('options', {})
            for opt_key in list(opts.keys()):
                orig_opt = opts[opt_key]
                cleaned_opt = clean_text_deep(orig_opt)
                if cleaned_opt != orig_opt:
                    opts[opt_key] = cleaned_opt
                    cleaned_count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned {filepath}: stripped Q-number prefixes & fixed {cleaned_count} degree entries!")

clean_dataset_file(os.path.join(DATA_DIR, 'questions_dataset.json'))
clean_dataset_file(os.path.join(DATA_DIR, 'physics_questions.json'))
clean_dataset_file(os.path.join(DATA_DIR, 'chemistry_questions.json'))
