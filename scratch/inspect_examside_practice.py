import asyncio
import json
import os
from playwright.async_api import async_playwright

async def test_practice():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        target_url = "https://questions.examside.com/past-years/medical/neet/physics/units-and-measurement"
        print(f"Navigating to {target_url} ...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click Start Practice or inspect all links containing /question/ or /neet/
        practice_btn = await page.query_selector("text=Start Practice")
        if practice_btn:
            print("Found 'Start Practice' button. Clicking...")
            await practice_btn.click()
            await page.wait_for_timeout(4000)
            
            print("New Page Title:", await page.title())
            print("New Page URL:", page.url)
            
            # Save inner text
            body_text = await page.inner_text("body")
            print("\nPractice Page Text (First 1200 chars):\n", body_text[:1200])
            
            # Extract images
            imgs = await page.eval_on_selector_all("img", "elements => elements.map(e => ({src: e.src, alt: e.alt}))")
            print(f"\nImages on practice page: {len(imgs)}")
            for img in imgs[:10]:
                print("   Image:", img)
                
            # Extract buttons (Options A, B, C, D)
            btns = await page.eval_on_selector_all("button", "elements => elements.map(e => ({text: (e.innerText || e.textContent || '').trim()}))")
            print(f"\nButtons on practice page: {len(btns)}")
            for b in btns[:10]:
                print("   Button:", b['text'][:80])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_practice())
