import os
import io
import json
import re
import html
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

os.makedirs('dataset/chemistry', exist_ok=True)
os.makedirs('dataset/physics', exist_ok=True)
os.makedirs('dataset/biology', exist_ok=True)
os.makedirs('dataset2/chemistry', exist_ok=True)
os.makedirs('dataset2/physics', exist_ok=True)
os.makedirs('dataset2/biology', exist_ok=True)
os.makedirs('dataset/images', exist_ok=True)
os.makedirs('dataset2/images', exist_ok=True)

NTA_CHAPTERS = {
    'Chemistry': [
        "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements and Periodicity",
        "Chemical Bonding and Molecular Structure", "States of Matter and Thermodynamics", "Equilibrium",
        "Redox Reactions and Electrochemistry", "Chemical Kinetics", "p-Block Elements", "d- and f-Block Elements",
        "Coordination Compounds", "Organic Chemistry: Basic Principles", "Hydrocarbons",
        "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids",
        "Amines", "Biomolecules"
    ],
    'Physics': [
        "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane", "Laws of Motion",
        "Work, Energy and Power", "System of Particles and Rotational Motion", "Gravitation",
        "Mechanical Properties of Solids and Fluids", "Thermal Properties and Thermodynamics",
        "Kinetic Theory of Gases", "Oscillations and Waves", "Electrostatics and Capacitance",
        "Current Electricity", "Moving Charges and Magnetism", "Electromagnetic Induction and AC",
        "Electromagnetic Waves", "Ray Optics and Wave Optics", "Dual Nature of Radiation and Matter",
        "Atoms and Nuclei", "Semiconductor Electronics"
    ],
    'Biology': [
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
}

SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def clean_text(text):
    if not isinstance(text, str): return ""
    s = html.unescape(text)
    s = re.sub(r'</?(p|span|style|tg|td|table|tr|div)[^>]*>', ' ', s, flags=re.IGNORECASE)
    s = s.replace('≤ft(', '(').replace('\\left(', '(').replace('≤ft', '').replace('right)', ')').replace('\\right)', ')')
    s = s.replace('$', '').replace('$$', '').replace('~', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def sanitize_option(opt_raw, label_letter):
    s = clean_text(opt_raw)
    s = re.sub(rf'^{label_letter}\.?\s*{label_letter}?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^[A-D]\.\s*', '', s, flags=re.IGNORECASE)
    return s.strip()

def map_to_nta(raw_ch, subject):
    raw = str(raw_ch).lower().strip()
    nta_list = NTA_CHAPTERS.get(subject, NTA_CHAPTERS['Chemistry'])
    for official in nta_list:
        off_low = official.lower()
        if raw in off_low or off_low in raw:
            return official
        words = [w for w in raw.split() if len(w) > 3]
        if any(w in off_low for w in words):
            return official
    return nta_list[0]

def fetch_single_question(item):
    subj, ch_url, q_url = item
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    req = urllib.request.Request(q_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract question text and options
            full_text = soup.get_text()

            # Find options
            opt_a = re.search(r'A\s+([^\n]+)', full_text)
            opt_b = re.search(r'B\s+([^\n]+)', full_text)
            opt_c = re.search(r'C\s+([^\n]+)', full_text)
            opt_d = re.search(r'D\s+([^\n]+)', full_text)
            
            if not (opt_a and opt_b and opt_c and opt_d):
                return None
                
            ch_name_raw = ch_url.split('/')[-1].replace('-', ' ')
            official_ch = map_to_nta(ch_name_raw, subj)
            
            stem = full_text.split('A ')[0].strip()
            stem = re.sub(r'.*?NEET\s+\d+\s+MCQ[^:]*', '', stem, flags=re.DOTALL).strip()
            stem = clean_text(stem)
            
            if len(stem) < 10:
                return None
                
            ans_m = re.search(r'Correct Answer[:\s]*([A-D])', full_text, re.IGNORECASE)
            ans_key = ans_m.group(1).upper() if ans_m else 'A'
            
            sol_m = re.search(r'Explanation\s*(.*)', full_text, re.DOTALL)
            sol_text = clean_text(sol_m.group(1)[:400]) if sol_m else f"**Correct Answer: ({ans_key})**"
            
            # Find diagram image
            img_url = None
            for img in soup.find_all('img', src=True):
                src = img['src']
                if not any(ig in src for ig in ['logo', 'warning', 'translate', 'svg']):
                    img_url = src
                    break
                    
            opts = {
                "A": sanitize_option(opt_a.group(1), 'A'),
                "B": sanitize_option(opt_b.group(1), 'B'),
                "C": sanitize_option(opt_c.group(1), 'C'),
                "D": sanitize_option(opt_d.group(1), 'D')
            }
            
            if len(set(opts.values())) < 4:
                return None
                
            return {
                "subject": subj,
                "chapter": official_ch,
                "question": stem,
                "options": opts,
                "answer": ans_key,
                "solution": sol_text,
                "remote_img": img_url,
                "exam": "NEET PYQ (ExamSIDE)",
                "year": 2024
            }
    except Exception as e:
        return None

def main():
    links_file = 'scratch/examside_detail_links.json'
    if not os.path.exists(links_file):
        print("Error: scratch/examside_detail_links.json not found!")
        return
        
    items = json.load(open(links_file))
    print(f"Loaded {len(items)} question detail links from disk.")
    print("Launching Multi-Threaded Fast Downloader (25 Worker Threads)...\n")
    
    master_scraped = {
        'Physics': {ch: [] for ch in NTA_CHAPTERS['Physics']},
        'Chemistry': {ch: [] for ch in NTA_CHAPTERS['Chemistry']},
        'Biology': {ch: [] for ch in NTA_CHAPTERS['Biology']}
    }
    
    img_counter = 1
    processed = 0
    success = 0
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(fetch_single_question, item): item for item in items}
        for future in as_completed(futures):
            processed += 1
            if processed % 200 == 0 or processed == len(items):
                print(f"Progress: [{processed}/{len(items)}] | Scraped: {success} valid questions...")
                
            res = future.result()
            if res:
                subj = res['subject']
                ch = res['chapter']
                
                # Check image download
                if res.get('remote_img'):
                    src = res['remote_img']
                    ext = '.jpg' if '.jpg' in src.lower() else '.png'
                    fname = f"examside_img_{img_counter:04d}{ext}"
                    lp1 = os.path.join('dataset2/images', fname)
                    lp2 = os.path.join('dataset/images', fname)
                    try:
                        req = urllib.request.Request(src, headers=headers)
                        with urllib.request.urlopen(req, timeout=10) as resp, open(lp1, 'wb') as f1:
                            buf = resp.read()
                            f1.write(buf)
                            with open(lp2, 'wb') as f2:
                                f2.write(buf)
                        res['image_path'] = lp1
                        img_counter += 1
                    except: pass
                    del res['remote_img']
                    
                master_scraped[subj][ch].append(res)
                success += 1

    print("\n==================================================")
    print(f"EXTRACTED {success} VALID QUESTIONS FROM EXAMSIDE!")
    print("==================================================")
    
    # Save master & dataset2 files
    for s_name, ch_dict in master_scraped.items():
        total_s = 0
        for ch_n, q_l in ch_dict.items():
            seen = set()
            uniq = []
            for q in q_l:
                norm = re.sub(r'\W+', '', q['question'].lower())[:60]
                if norm not in seen:
                    seen.add(norm)
                    uniq.append(q)
            ch_dict[ch_n] = uniq
            total_s += len(uniq)
            
        s_lower = s_name.lower()
        dataset_path = f"dataset/{s_lower}/{s_lower}_pyqs_dataset.json"
        master_payload = {
            "subject": s_name,
            "total_chapters": len(ch_dict),
            "total_questions": total_s,
            "chapters": ch_dict
        }
        with open(dataset_path, 'w') as f:
            json.dump(master_payload, f, indent=2)
            
        print(f" -> {s_name}: Saved {total_s} pristine questions across {len(ch_dict)} NTA chapters.")
        
        for ch_n, q_l in ch_dict.items():
            slug = re.sub(r'[\:\—\-\,\&\(\)]+', ' ', ch_n).strip().lower()
            slug = re.sub(r'\s+', '_', slug)
            ch_payload = {
                "subject": s_name,
                "chapter": ch_n,
                "total_questions": len(q_l),
                "questions": q_l
            }
            with open(f"dataset2/{s_lower}/{slug}.json", 'w') as f:
                json.dump(ch_payload, f, indent=2)

    # Sync to Bot directories
    with open('chemistry_bot/data/questions_dataset.json', 'w') as f:
        json.dump(master_scraped['Chemistry'], f, indent=2)
    with open('physics_bot/data/questions_dataset.json', 'w') as f:
        json.dump(master_scraped['Physics'], f, indent=2)
    with open('neet_bot/data/chemistry_questions.json', 'w') as f:
        json.dump(master_scraped['Chemistry'], f, indent=2)
    with open('neet_bot/data/physics_questions.json', 'w') as f:
        json.dump(master_scraped['Physics'], f, indent=2)
    with open('neet_bot/data/questions_dataset.json', 'w') as f:
        json.dump(master_scraped['Biology'], f, indent=2)

    print("\nFAST MULTI-THREADED EXAMSIDE EXTRACTION COMPLETE!")

if __name__ == '__main__':
    main()
