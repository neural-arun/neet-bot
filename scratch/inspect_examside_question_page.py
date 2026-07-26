import asyncio
import json
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def inspect_single_q():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # Block ads
        await page.route("**/*vignette*", lambda route: route.abort())
        await page.route("**/*google*", lambda route: route.abort())
        await page.route("**/*doubleclick*", lambda route: route.abort())
        
        target_url = "https://questions.examside.com/past-years/medical/question/pconsider-that-sigmas-kb-b-represents-stefan-boltzm-neet-physics-units-and-measurement-r6p9wdbbidtgeojo"
        print(f"Navigating to single question page: {target_url} ...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Extract HTML
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract images
        imgs = []
        for img in soup.find_all('img', src=True):
            imgs.append(img['src'])
        print(f"Found {len(imgs)} images on question page:")
        for img in imgs[:10]:
            print("   Image:", img)
            
        # Extract text blocks
        text_lines = [line.strip() for line in soup.get_text().split('\n') if len(line.strip()) > 0]
        print(f"\nExtracted {len(text_lines)} text lines from question page:")
        for t in text_lines[:40]:
            print("   ->", t[:100])
            
        # Save HTML for analysis
        with open("scratch/examside_single_question.html", "w") as f:
            f.write(html_content)
        print("\nSaved page HTML to scratch/examside_single_question.html")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect_single_q())
