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

# Main Examside NEET Subject Landing Pages
EXAMSIDE_SUBJECTS = {
    'Physics': 'https://questions.examside.com/past-years/medical/neet/physics',
    'Chemistry': 'https://questions.examside.com/past-years/medical/neet/chemistry',
    'Biology': 'https://questions.examside.com/past-years/medical/neet/biology'
}

def clean_text(text):
    if not isinstance(text, str):
        return ""
    s = html.unescape(text)
    s = re.sub(r'</?(p|span|style|tg|td|table|tr|div)[^>]*>', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def sanitize_option(opt_raw, label_letter):
    s = clean_text(opt_raw)
    s = re.sub(rf'^{label_letter}\.?\s*{label_letter}?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^[A-D]\.\s*', '', s, flags=re.IGNORECASE)
    return s.strip()

async def scrape_all_examside():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # Block ad networks
        await page.route("**/*vignette*", lambda route: route.abort())
        await page.route("**/*google*", lambda route: route.abort())
        await page.route("**/*doubleclick*", lambda route: route.abort())
        
        scraped_data = {
            'Physics': {},
            'Chemistry': {},
            'Biology': {}
        }
        
        for subj_name, subj_url in EXAMSIDE_SUBJECTS.items():
            print(f"\n==================================================")
            print(f"Scraping Examside {subj_name} Subject Page: {subj_url}")
            print(f"==================================================")
            
            try:
                await page.goto(subj_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                
                # Extract all chapter links
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: (e.innerText || e.textContent || '').trim(), href: e.href}))")
                chapter_links = [l for l in links if f"/past-years/medical/neet/{subj_name.lower()}/" in l['href']]
                
                # Filter unique chapter URLs
                unique_ch_urls = {}
                for cl in chapter_links:
                    url = cl['href'].split('#')[0]
                    if url not in unique_ch_urls:
                        # Extract chapter name from text
                        name_lines = [line.strip() for line in cl['text'].split('\n') if len(line.strip()) > 0]
                        ch_name = name_lines[0] if name_lines else "General"
                        unique_ch_urls[url] = ch_name
                        
                print(f"Found {len(unique_ch_urls)} chapter links for {subj_name}:")
                for url, name in list(unique_ch_urls.items())[:10]:
                    print(f" - {name}: {url}")
                    
                # Iterate over chapters and scrape questions
                for ch_url, ch_name in list(unique_ch_urls.items())[:15]:
                    print(f"\n   Scraping Chapter: '{ch_name}' ({ch_url}) ...")
                    try:
                        await page.goto(ch_url, wait_until="domcontentloaded", timeout=60000)
                        await page.wait_for_timeout(3000)
                        
                        # Click all 'Check Answer' buttons to reveal solutions
                        check_btns = await page.query_selector_all("text=Check Answer")
                        for btn in check_btns[:10]:
                            try:
                                await btn.click()
                                await page.wait_for_timeout(500)
                            except:
                                pass
                                
                        html_content = await page.content()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract question cards or blocks
                        # Examside questions can be extracted by searching for text patterns
                        cards = soup.find_all(['div', 'article', 'section'], class_=lambda c: c and any(k in c for k in ['card', 'question', 'item', 'block']))
                        
                        ch_questions = []
                        
                        for card in cards:
                            text = card.text.strip()
                            if len(text) > 40 and ('MCQ' in text or 'NEET' in text or 'Check Answer' in text):
                                # Extract options
                                opt_a = re.search(r'A\s+([^\n]+)', text)
                                opt_b = re.search(r'B\s+([^\n]+)', text)
                                opt_c = re.search(r'C\s+([^\n]+)', text)
                                opt_d = re.search(r'D\s+([^\n]+)', text)
                                
                                if opt_a and opt_b and opt_c and opt_d:
                                    # Extract stem
                                    stem = text.split('A ')[0].strip()
                                    stem = re.sub(r'.*?NEET\s+\d+\s+MCQ[^:]*', '', stem, flags=re.DOTALL).strip()
                                    if len(stem) > 10:
                                        # Extract correct answer
                                        ans_m = re.search(r'Correct Answer[:\s]*([A-D])', text, re.IGNORECASE)
                                        ans_key = ans_m.group(1).upper() if ans_m else 'A'
                                        
                                        # Extract explanation
                                        sol_m = re.search(r'Explanation\s*(.*)', text, re.DOTALL)
                                        sol_text = sol_m.group(1).strip() if sol_m else f"**Correct Answer: ({ans_key})**"
                                        
                                        # Extract diagram image if present
                                        img_src = None
                                        for img in card.find_all('img', src=True):
                                            src = img['src']
                                            if not any(ig in src for ig in ['logo', 'warning', 'translate', 'svg']):
                                                img_src = src
                                                break
                                                
                                        q_obj = {
                                            "question": clean_text(stem),
                                            "options": {
                                                "A": sanitize_option(opt_a.group(1), 'A'),
                                                "B": sanitize_option(opt_b.group(1), 'B'),
                                                "C": sanitize_option(opt_c.group(1), 'C'),
                                                "D": sanitize_option(opt_d.group(1), 'D')
                                            },
                                            "answer": ans_key,
                                            "solution": clean_text(sol_text[:500]),
                                            "exam": "NEET PYQ (Examside)",
                                            "year": 2024,
                                            "subject": subj_name,
                                            "chapter": ch_name
                                        }
                                        if img_src:
                                            q_obj["image_path"] = img_src
                                            
                                        ch_questions.append(q_obj)
                                        
                        # Deduplicate chapter questions
                        seen = set()
                        unique_qs = []
                        for q in ch_questions:
                            norm = re.sub(r'\W+', '', q['question'].lower())[:60]
                            if norm not in seen and len(set(q['options'].values())) == 4:
                                seen.add(norm)
                                unique_qs.append(q)
                                
                        if unique_qs:
                            scraped_data[subj_name][ch_name] = unique_qs
                            print(f"     -> Successfully extracted {len(unique_qs)} clean questions for '{ch_name}'.")
                            
                    except Exception as e:
                        print(f"     -> Error scraping chapter {ch_name}: {e}")

            except Exception as e:
                print(f"Error loading subject page {subj_name}: {e}")

        await browser.close()
        
        # Save scraped dataset to disk
        for s_name, ch_dict in scraped_data.items():
            if ch_dict:
                s_lower = s_name.lower()
                master_path = f"dataset/{s_lower}/{s_lower}_pyqs_dataset.json"
                payload = {
                    "subject": s_name,
                    "total_chapters": len(ch_dict),
                    "total_questions": sum(len(ql) for ql in ch_dict.values()),
                    "chapters": ch_dict
                }
                with open(master_path, 'w') as f:
                    json.dump(payload, f, indent=2)
                print(f"\nSaved Examside {s_name} Master Dataset ({payload['total_questions']} questions) to {master_path}")

if __name__ == '__main__':
    asyncio.run(scrape_all_examside())
