import json
import re
import html
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'neet_bot', 'data')

def clean_mathml(text):
    if not text:
        return ""
    
    # 1. Unescape HTML entities first
    text = html.unescape(str(text))
    
    # 2. Extract content inside <math ...>...</math> if present
    def parse_math(match):
        inner = match.group(0)
        # Convert common MathML entities inside
        inner = inner.replace('&#956;', 'μ').replace('&#197;', 'Å').replace('&#176;', '°')
        # Strip all HTML/MathML tags
        clean = re.sub(r'<[^>]+>', '', inner)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    text = re.sub(r'<math[^>]*>.*?</math>', parse_math, text, flags=re.DOTALL)

    # 3. Strip any leftover HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # 4. Replace non-breaking space and weird Unicode spaces with standard space
    text = text.replace('\u00a0', ' ').replace('\u200b', '').replace('\u2009', ' ')
    
    # 5. Clean up extra whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

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
            cleaned_q = clean_mathml(orig_q)
            if cleaned_q != orig_q:
                q['question'] = cleaned_q
                cleaned_count += 1

            opts = q.get('options', {})
            for opt_key in list(opts.keys()):
                orig_opt = opts[opt_key]
                cleaned_opt = clean_mathml(orig_opt)
                if cleaned_opt != orig_opt:
                    opts[opt_key] = cleaned_opt
                    cleaned_count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned {filepath}: fixed {cleaned_count} MathML / Unicode instances!")

clean_dataset_file(os.path.join(DATA_DIR, 'questions_dataset.json'))
clean_dataset_file(os.path.join(DATA_DIR, 'physics_questions.json'))
clean_dataset_file(os.path.join(DATA_DIR, 'chemistry_questions.json'))
