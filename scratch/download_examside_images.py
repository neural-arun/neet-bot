import json
import os
import urllib.request
import re

os.makedirs('dataset/images', exist_ok=True)
os.makedirs('dataset2/images', exist_ok=True)

def download_and_localize_images(filepath):
    if not os.path.exists(filepath):
        return
        
    ds = json.load(open(filepath))
    chapters = ds.get('chapters', {})
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    img_counter = 1
    
    for ch_name, q_list in chapters.items():
        for q in q_list:
            img_url = q.get('image_path') or q.get('image_url')
            if img_url and img_url.startswith('http'):
                ext = '.jpg' if '.jpg' in img_url.lower() else '.png'
                filename = f"examside_img_{img_counter:04d}{ext}"
                local_path1 = os.path.join('dataset2/images', filename)
                local_path2 = os.path.join('dataset/images', filename)
                
                try:
                    req = urllib.request.Request(img_url, headers=headers)
                    with urllib.request.urlopen(req) as resp, open(local_path1, 'wb') as f1:
                        content = resp.read()
                        f1.write(content)
                        with open(local_path2, 'wb') as f2:
                            f2.write(content)
                            
                    print(f"Downloaded image: {img_url} -> {local_path1}")
                    q['image_path'] = local_path1
                    img_counter += 1
                except Exception as e:
                    print(f"Failed to download image {img_url}: {e}")
                    # If image fails to download, remove image field so question has no broken link
                    del q['image_path']
                    
    with open(filepath, 'w') as f:
        json.dump(ds, f, indent=2)

def main():
    print("Downloading all remote Examside diagram images to local disk...\n")
    download_and_localize_images('dataset/chemistry/chemistry_pyqs_dataset.json')
    download_and_localize_images('dataset/physics/physics_pyqs_dataset.json')
    download_and_localize_images('dataset/biology/biology_pyqs_dataset.json')
    print("\nImage downloading and localization complete!")

if __name__ == '__main__':
    main()
