import asyncio
import json
import os
from playwright.async_api import async_playwright

async def test_no_ads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # Block ad domains and vignettes
        await page.route("**/*vignette*", lambda route: route.abort())
        await page.route("**/*google*", lambda route: route.abort())
        await page.route("**/*doubleclick*", lambda route: route.abort())
        await page.route("**/*adservice*", lambda route: route.abort())
        
        target_url = "https://questions.examside.com/past-years/medical/neet/physics/units-and-measurement"
        print(f"Navigating to {target_url} without ads ...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        practice_btn = await page.query_selector("text=Start Practice")
        if practice_btn:
            print("Clicking 'Start Practice'...")
            await practice_btn.click()
            await page.wait_for_timeout(4000)
            
            print("New Page Title:", await page.title())
            print("New Page URL:", page.url)
            
            # Inspect question prompt container
            q_text = await page.eval_on_selector_all("p, div, span", "elements => elements.map(e => (e.innerText || '').strip()).filter(t => t.length > 50)")
            print(f"\nExtracted {len(q_text)} text blocks from practice UI:")
            for t in q_text[:10]:
                print(" ->", t[:120])
                
            # Inspect options / buttons
            buttons = await page.eval_on_selector_all("button, div.option, label", "elements => elements.map(e => (e.innerText || '').strip()).filter(t => t.length > 0)")
            print(f"\nExtracted {len(buttons)} interactive buttons/options:")
            for b in buttons[:10]:
                print(" ->", b[:80])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_no_ads())
