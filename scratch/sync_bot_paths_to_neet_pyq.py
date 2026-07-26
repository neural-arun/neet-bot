import json
import os

def update_bot_image_paths(filepath):
    if not os.path.exists(filepath):
        return
    ds = json.load(open(filepath))
    chapters = ds.get('chapters', {})
    
    for ch_name, q_list in chapters.items():
        for q in q_list:
            img = q.get('image_path') or q.get('image_url')
            if img:
                fname = os.path.basename(img)
                q['image_path'] = f"neet_pyq/images/{fname}"
                
    with open(filepath, 'w') as f:
        json.dump(ds, f, indent=2)

def main():
    print("Updating all bot files to reference neet_pyq/images/ ...")
    update_bot_image_paths('chemistry_bot/data/questions_dataset.json')
    update_bot_image_paths('physics_bot/data/questions_dataset.json')
    update_bot_image_paths('neet_bot/data/chemistry_questions.json')
    update_bot_image_paths('neet_bot/data/physics_questions.json')
    update_bot_image_paths('neet_bot/data/questions_dataset.json')
    print("Bot file image paths updated!")

if __name__ == '__main__':
    main()
