import json
import os
import re

def is_corrupt_question(q):
    stem = str(q.get('question', '')).strip()
    opts = q.get('options', {})
    
    # 1. Reject questions referring to missing external tables or textbook figures
    table_patterns = [
        r'\btable\s+\d+[\.\d]*\b',
        r'\bfigure\s+\d+[\.\d]*\b',
        r'\bgiven\s+in\s+table\b',
        r'\brefer\s+to\s+table\b',
        r'\bfrom\s+table\b',
        r'\bshown\s+in\s+table\b',
        r'\bfrom\s+the\s+given\s+table\b'
    ]
    for pat in table_patterns:
        if re.search(pat, stem, re.IGNORECASE):
            return True
            
    # 2. Reject mangled encoding / mojibake characters
    mojibake_chars = ['Ã', 'Â', 'â', 'ï', '¿', '½', 'Ã—', 'Ã', '&amp;', '\u200b']
    if any(c in stem for c in mojibake_chars):
        return True
        
    if not isinstance(opts, dict) or len(opts) != 4:
        return True
        
    for k in ['A', 'B', 'C', 'D']:
        v = str(opts.get(k, '')).strip()
        if len(v) == 0:
            return True
        if any(c in v for c in mojibake_chars):
            return True
        # Check broken incomplete formulas like "g 2 CrO 4" or "0 10 - M"
        if v.startswith('g 2 ') or v.startswith('g2 ') or ' 10 - M' in v or ' 10 -3 M' in v:
            return True
            
    # 3. Reject duplicate option values
    if len(set(opts.values())) < 4:
        return True
        
    return False

def purge_file(filepath):
    if not os.path.exists(filepath):
        return 0, 0
        
    ds = json.load(open(filepath))
    chapters = ds.get('chapters', {})
    
    new_chapters = {}
    total_before = 0
    total_after = 0
    purged_count = 0
    
    for ch_name, q_list in chapters.items():
        total_before += len(q_list)
        valid_qs = []
        for q in q_list:
            if not is_corrupt_question(q):
                valid_qs.append(q)
            else:
                purged_count += 1
                
        new_chapters[ch_name] = valid_qs
        total_after += len(valid_qs)
        
    ds['chapters'] = new_chapters
    ds['total_questions'] = total_after
    
    with open(filepath, 'w') as f:
        json.dump(ds, f, indent=2)
        
    print(f"Purged {os.path.basename(filepath)}: Removed {purged_count} corrupt table/mojibake questions ({total_before} -> {total_after} remaining).")
    return ds

def sync_dataset2(ds, subject_name, dataset2_dir):
    os.makedirs(dataset2_dir, exist_ok=True)
    for ch_name, q_list in ds['chapters'].items():
        slug = ch_name.lower().replace(':', '').replace('-', ' ').replace(',', '').strip().replace(' ', '_')
        slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_name).strip().lower()
        slug = re.sub(r'\s+', '_', slug)
        
        payload = {
            "subject": subject_name,
            "chapter": ch_name,
            "total_questions": len(q_list),
            "questions": q_list
        }
        ch_file = os.path.join(dataset2_dir, f"{slug}.json")
        with open(ch_file, 'w') as f:
            json.dump(payload, f, indent=2)

def main():
    print("Executing Aggressive Table & Mojibake Purge Pass...\n")
    
    chem_ds = purge_file('dataset/chemistry/chemistry_pyqs_dataset.json')
    phys_ds = purge_file('dataset/physics/physics_pyqs_dataset.json')
    bio_ds = purge_file('dataset/biology/biology_pyqs_dataset.json')

    print("\nSyncing clean datasets to dataset2 chapter files...")
    sync_dataset2(chem_ds, 'Chemistry', 'dataset2/chemistry')
    sync_dataset2(phys_ds, 'Physics', 'dataset2/physics')
    sync_dataset2(bio_ds, 'Biology', 'dataset2/biology')

    print("\nSyncing clean datasets to all Telegram Bot directories...")
    with open('chemistry_bot/data/questions_dataset.json', 'w') as f:
        json.dump(chem_ds, f, indent=2)
    with open('physics_bot/data/questions_dataset.json', 'w') as f:
        json.dump(phys_ds, f, indent=2)
    with open('neet_bot/data/chemistry_questions.json', 'w') as f:
        json.dump(chem_ds, f, indent=2)
    with open('neet_bot/data/physics_questions.json', 'w') as f:
        json.dump(phys_ds, f, indent=2)
    with open('neet_bot/data/questions_dataset.json', 'w') as f:
        json.dump(bio_ds, f, indent=2)

    print("\nPurge Pass Complete!")

if __name__ == '__main__':
    main()
