import asyncio
import json
import os
import re
import html
import urllib.request
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

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

async def scrape_full_examside():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        await page.route("**/*vignette*", lambda route: route.abort())
        await page.route("**/*google*", lambda route: route.abort())
        await page.route("**/*doubleclick*", lambda route: route.abort())
        
        master_scraped = {
            'Physics': {ch: [] for ch in NTA_CHAPTERS['Physics']},
            'Chemistry': {ch: [] for ch in NTA_CHAPTERS['Chemistry']},
            'Biology': {ch: [] for ch in NTA_CHAPTERS['Biology']}
        }
        
        img_counter = 1
        
        for subj_name in ['Physics', 'Chemistry', 'Biology']:
            subj_url = f"https://questions.examside.com/past-years/medical/neet/{subj_name.lower()}"
            print(f"\n==================================================")
            print(f"SCRAPING ALL CHAPTERS FOR {subj_name.upper()}: {subj_url}")
            print(f"==================================================")
            
            try:
                await page.goto(subj_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: (e.innerText || e.textContent || '').trim(), href: e.href}))")
                ch_links = [l for l in links if f"/past-years/medical/neet/{subj_name.lower()}/" in l['href']]
                
                unique_urls = {}
                for cl in ch_links:
                    u = cl['href'].split('#')[0]
                    if u not in unique_urls:
                        raw_title = cl['text'].split('\n')[0].strip()
                        unique_urls[u] = raw_title
                        
                print(f"Discovered {len(unique_urls)} chapter links for {subj_name}.")
                
                for ch_url, ch_title in unique_urls.items():
                    official_ch = map_to_nta(ch_title, subj_name)
                    print(f" -> Scraping Chapter: '{ch_title}' -> NTA: '{official_ch}' ({ch_url})")
                    
                    try:
                        await page.goto(ch_url, wait_until="domcontentloaded", timeout=60000)
                        await page.wait_for_timeout(2000)
                        
                        # Click Check Answer buttons to reveal solutions & answers
                        check_btns = await page.query_selector_all("text=Check Answer")
                        for btn in check_btns:
                            try:
                                await btn.click()
                                await page.wait_for_timeout(300)
                            except: pass
                            
                        # Also check if pagination / question links exist on page
                        q_links = await page.eval_on_selector_all("a[href*='/question/']", "elements => elements.map(e => e.href)")
                        print(f"    Found {len(q_links)} question detail links on page.")
                        
                        html_content = await page.content()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract all text blocks containing MCQs
                        text_blocks = soup.find_all(['div', 'article', 'section'])
                        for block in text_blocks:
                            b_text = block.text.strip()
                            if ('MCQ' in b_text or 'NEET' in b_text) and ('Check Answer' in b_text or 'Correct Answer' in b_text or 'Explanation' in b_text):
                                opt_a = re.search(r'A\s+([^\n]+)', b_text)
                                opt_b = re.search(r'B\s+([^\n]+)', b_text)
                                opt_c = re.search(r'C\s+([^\n]+)', b_text)
                                opt_d = re.search(r'D\s+([^\n]+)', b_text)
                                
                                if opt_a and opt_b and opt_c and opt_d:
                                    stem = b_text.split('A ')[0].strip()
                                    stem = re.sub(r'.*?NEET\s+\d+\s+MCQ[^:]*', '', stem, flags=re.DOTALL).strip()
                                    stem = clean_text(stem)
                                    
                                    if len(stem) > 10:
                                        ans_m = re.search(r'Correct Answer[:\s]*([A-D])', b_text, re.IGNORECASE)
                                        ans_key = ans_m.group(1).upper() if ans_m else 'A'
                                        
                                        sol_m = re.search(r'Explanation\s*(.*)', b_text, re.DOTALL)
                                        sol_text = clean_text(sol_m.group(1)[:400]) if sol_m else f"**Correct Answer: ({ans_key})**"
                                        
                                        q_obj = {
                                            "question": stem,
                                            "options": {
                                                "A": sanitize_option(opt_a.group(1), 'A'),
                                                "B": sanitize_option(opt_b.group(1), 'B'),
                                                "C": sanitize_option(opt_c.group(1), 'C'),
                                                "D": sanitize_option(opt_d.group(1), 'D')
                                            },
                                            "answer": ans_key,
                                            "solution": sol_text,
                                            "exam": "NEET PYQ (ExamSIDE)",
                                            "year": 2024,
                                            "subject": subj_name,
                                            "chapter": official_ch
                                        }
                                        
                                        # Download image if present
                                        for img in block.find_all('img', src=True):
                                            src = img['src']
                                            if not any(ig in src for ig in ['logo', 'warning', 'translate', 'svg']):
                                                ext = '.jpg' if '.jpg' in src.lower() else '.png'
                                                fname = f"examside_img_{img_counter:04d}{ext}"
                                                lp1 = os.path.join('dataset2/images', fname)
                                                lp2 = os.path.join('dataset/images', fname)
                                                try:
                                                    req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                                                    with urllib.request.urlopen(req) as resp, open(lp1, 'wb') as f1:
                                                        buf = resp.read()
                                                        f1.write(buf)
                                                        with open(lp2, 'wb') as f2:
                                                            f2.write(buf)
                                                    q_obj['image_path'] = lp1
                                                    img_counter += 1
                                                except: pass
                                                break
                                                
                                        if len(set(q_obj['options'].values())) == 4:
                                            master_scraped[subj_name][official_ch].append(q_obj)
                                            
                    except Exception as e:
                        print(f"    Error scraping {ch_title}: {e}")

            except Exception as e:
                print(f"Error scraping subject {subj_name}: {e}")

        await browser.close()
        
        # Deduplicate & Save
        print("\n==================================================")
        print("DEDUPLICATING & SAVING FULL EXAMSIDE DATASET")
        print("==================================================")
        
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
                
            print(f" -> {s_name}: Saved {total_s} questions across {len(ch_dict)} chapters to {dataset_path}")
            
            # Save dataset2 chapter files
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

    print("\nFULL EXAMSIDE SCRAPING & ASSEMBLY COMPLETE!")

if __name__ == '__main__':
    asyncio.run(scrape_full_examside())
