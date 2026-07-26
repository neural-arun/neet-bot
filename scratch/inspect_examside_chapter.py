import asyncio
import json
import os
from playwright.async_api import async_playwright

async def inspect_chapter_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        target_url = "https://questions.examside.com/past-years/medical/neet/physics/units-and-measurement"
        print(f"Navigating to {target_url} ...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        
        # Give JS time to render question components
        await page.wait_for_timeout(4000)
        
        # Extract images
        imgs = await page.eval_on_selector_all("img", "elements => elements.map(e => ({src: e.src, alt: e.alt}))")
        print(f"\nFound {len(imgs)} images on chapter page:")
        for img in imgs[:10]:
            print("   Image:", img)
            
        # Extract question blocks/cards
        page_html = await page.content()
        with open("scratch/examside_sample_page.html", "w") as f:
            f.write(page_html)
            
        print("\nSaved page HTML to scratch/examside_sample_page.html")
        
        # Get all text blocks
        text_content = await page.inner_text("body")
        print("\nFirst 1500 chars of page text:\n", text_content[:1500])
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect_chapter_page())
