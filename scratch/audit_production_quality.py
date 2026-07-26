import json
import os

def audit_file(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File missing: {filepath}")
        return False, 0, 0
        
    ds = json.load(open(filepath))
    chapters = ds.get('chapters', {})
    
    total_q = 0
    defects = []
    
    for ch_name, q_list in chapters.items():
        for idx, q in enumerate(q_list):
            total_q += 1
            stem = q.get('question', '')
            opts = q.get('options', {})
            ans = q.get('answer', '')
            img = q.get('image_path') or q.get('image_url')
            
            if not stem or len(stem.strip()) < 8:
                defects.append(f"Chapter '{ch_name}' Q{idx}: Empty stem")
                
            if not isinstance(opts, dict) or len(opts) != 4:
                defects.append(f"Chapter '{ch_name}' Q{idx}: Invalid options dict")
            else:
                for opt_k in ['A', 'B', 'C', 'D']:
                    opt_v = str(opts.get(opt_k, '')).strip()
                    if not opt_v:
                        defects.append(f"Chapter '{ch_name}' Q{idx}: Option {opt_k} empty")
                        
                if len(set(opts.values())) < 4:
                    defects.append(f"Chapter '{ch_name}' Q{idx}: Duplicate options -> {opts}")

            if img and not os.path.exists(img):
                defects.append(f"Chapter '{ch_name}' Q{idx}: Image missing on disk -> '{img}'")

    print(f"📊 Audit Report for {os.path.basename(filepath)}:")
    print(f"   Total Questions: {total_q} | Defects: {len(defects)}")
    if defects:
        for d in defects[:5]:
            print(f"    - {d}")
        return False, total_q, len(defects)
    else:
        print("   ✅ 100% PRISTINE - ZERO DEFECTS!")
        return True, total_q, 0

def main():
    files = [
        'neet_pyq/chemistry_pyqs.json',
        'neet_pyq/physics_pyqs.json',
        'neet_pyq/biology_pyqs.json',
        'chemistry_bot/data/questions_dataset.json',
        'physics_bot/data/questions_dataset.json',
        'neet_bot/data/chemistry_questions.json',
        'neet_bot/data/physics_questions.json',
        'neet_bot/data/questions_dataset.json'
    ]
    
    total = 0
    defs = 0
    for f in files:
        ok, count, df = audit_file(f)
        total += count
        defs += df
        
    print(f"\nGRAND TOTAL: {total} Question Instances | Total Defects: {defs}")
    if defs == 0:
        print("🎉 ALL DATASETS 100% PRISTINE & PRODUCTION READY!")

if __name__ == '__main__':
    main()
