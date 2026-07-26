import asyncio
import json
import os
from playwright.async_api import async_playwright

async def inspect_examside():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        print("Navigating to https://questions.examside.com/past-years/medical/neet ...")
        await page.goto("https://questions.examside.com/past-years/medical/neet", wait_until="domcontentloaded", timeout=60000)
        
        title = await page.title()
        print("Page Title:", title)
        
        # Get all links on page cleanly
        links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: (e.innerText || e.textContent || '').trim(), href: e.href}))")
        print(f"Found {len(links)} links on the NEET landing page.")
        
        neet_links = [l for l in links if 'past-years/medical/neet' in l['href']]
        print(f"\nFound {len(neet_links)} NEET subject/chapter links:")
        for l in neet_links[:20]:
            print(f" - {l['text']}: {l['href']}")
            
        if neet_links:
            target_url = neet_links[1]['href'] if len(neet_links) > 1 else neet_links[0]['href']
            print(f"\nNavigating to sample chapter: {target_url}")
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            await page.wait_for_timeout(3000)
            
            sub_links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: (e.innerText || e.textContent || '').trim(), href: e.href}))")
            print(f"Found {len(sub_links)} sub-links on chapter page.")
            for sl in sub_links[:15]:
                print(f"   -> {sl['text']}: {sl['href']}")
                
            body_text = await page.inner_text("body")
            print("\nPage Text Preview (First 800 chars):\n", body_text[:800])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect_examside())
