import json
import os
import re

def clean_file(filepath):
    if not os.path.exists(filepath):
        return 0
    ds = json.load(open(filepath))
    chapters = ds.get('chapters', {})
    
    cleaned_ch = {}
    total_q = 0
    for ch_name, q_list in chapters.items():
        valid_qs = []
        for q in q_list:
            opts = q.get('options', {})
            if isinstance(opts, dict) and len(opts) == 4:
                vals = [str(opts.get(k, '')).strip() for k in ['A', 'B', 'C', 'D']]
                if all(len(v) > 0 for v in vals) and len(set(vals)) == 4:
                    valid_qs.append(q)
        cleaned_ch[ch_name] = valid_qs
        total_q += len(valid_qs)
        
    ds['chapters'] = cleaned_ch
    ds['total_questions'] = total_q
    with open(filepath, 'w') as f:
        json.dump(ds, f, indent=2)
    return ds

def sync_all():
    print("Sanitizing and Syncing Datasets across all directories...")
    chem_ds = clean_file('dataset/chemistry/chemistry_pyqs_dataset.json')
    phys_ds = clean_file('dataset/physics/physics_pyqs_dataset.json')
    bio_ds = clean_file('dataset/biology/biology_pyqs_dataset.json')

    # Sync dataset2 chapter files
    for subj_name, ds, dataset2_dir in [('Chemistry', chem_ds, 'dataset2/chemistry'), ('Physics', phys_ds, 'dataset2/physics'), ('Biology', bio_ds, 'dataset2/biology')]:
        os.makedirs(dataset2_dir, exist_ok=True)
        for ch_name, q_l in ds['chapters'].items():
            slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_name).strip().lower()
            slug = re.sub(r'\s+', '_', slug)
            ch_payload = {
                "subject": subj_name,
                "chapter": ch_name,
                "total_questions": len(q_l),
                "questions": q_l
            }
            with open(f"{dataset2_dir}/{slug}.json", 'w') as f:
                json.dump(ch_payload, f, indent=2)

    # Sync Telegram bot files
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

    print("Sanitization and Sync Complete!")

if __name__ == '__main__':
    sync_all()
