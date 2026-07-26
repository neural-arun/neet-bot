import json
import os
import shutil
import re

os.makedirs('neet_pyq/chemistry', exist_ok=True)
os.makedirs('neet_pyq/physics', exist_ok=True)
os.makedirs('neet_pyq/biology', exist_ok=True)
os.makedirs('neet_pyq/images', exist_ok=True)

# Copy all diagram images to neet_pyq/images/
if os.path.exists('dataset/images'):
    for fname in os.listdir('dataset/images'):
        src = os.path.join('dataset/images', fname)
        dst = os.path.join('neet_pyq/images', fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)

def build_subject_folder(subj_name, dataset_path, folder_dir):
    if not os.path.exists(dataset_path):
        return
    ds = json.load(open(dataset_path))
    chapters = ds.get('chapters', {})
    
    # Update image paths to neet_pyq/images/
    for ch_name, q_list in chapters.items():
        for q in q_list:
            img = q.get('image_path') or q.get('image_url')
            if img:
                fname = os.path.basename(img)
                q['image_path'] = f"neet_pyq/images/{fname}"
                
    # Save master file inside neet_pyq/
    master_file = f"neet_pyq/{subj_name.lower()}_pyqs.json"
    with open(master_file, 'w') as f:
        json.dump(ds, f, indent=2)
        
    # Save standalone chapter files inside neet_pyq/<subject>/
    for ch_name, q_l in chapters.items():
        slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_name).strip().lower()
        slug = re.sub(r'\s+', '_', slug)
        ch_payload = {
            "subject": subj_name,
            "chapter": ch_name,
            "total_questions": len(q_l),
            "questions": q_l
        }
        with open(f"{folder_dir}/{slug}.json", 'w') as f:
            json.dump(ch_payload, f, indent=2)
            
    print(f"Built neet_pyq/{subj_name.lower()}/: {len(chapters)} chapter files ({ds['total_questions']} questions).")

def main():
    print("Building neet_pyq/ directory structure...\n")
    build_subject_folder('Chemistry', 'dataset/chemistry/chemistry_pyqs_dataset.json', 'neet_pyq/chemistry')
    build_subject_folder('Physics', 'dataset/physics/physics_pyqs_dataset.json', 'neet_pyq/physics')
    build_subject_folder('Biology', 'dataset/biology/biology_pyqs_dataset.json', 'neet_pyq/biology')

    print("\nneet_pyq/ build complete!")

if __name__ == '__main__':
    main()
