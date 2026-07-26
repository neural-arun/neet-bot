import asyncio
import json
import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrape_examside_chapter(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        print(f"Scraping chapter page: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll down to load all dynamic question cards
        for _ in range(5):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1000)
            
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find question containers
        # On Examside, question blocks are typically inside cards or container divs
        cards = soup.find_all(['div', 'article'], class_=lambda c: c and ('card' in c or 'question' in c or 'item' in c))
        print(f"Found {len(cards)} potential card containers.")
        
        questions = []
        
        # Alternatively, extract by searching for question text patterns
        # Let's inspect all question cards
        for idx, card in enumerate(cards):
            text = card.text.strip()
            if len(text) > 40 and ('A.' in text or '(A)' in text or 'Option' in text or 'NEET' in text):
                # Extract image URLs if any
                imgs = [img['src'] for img in card.find_all('img', src=True)]
                questions.append({
                    "card_index": idx,
                    "text": text[:300],
                    "images": imgs
                })
                
        print(f"\nExtracted {len(questions)} clean questions from page.")
        for q in questions[:5]:
            print(f"\n--- Q{q['card_index']} ---")
            print("Text:", q['text'])
            print("Images:", q['images'])
            
        await browser.close()
        return questions

if __name__ == '__main__':
    asyncio.run(scrape_examside_chapter("https://questions.examside.com/past-years/medical/neet/physics/units-and-measurement"))
