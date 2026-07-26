import asyncio
import json
import os
from playwright.async_api import async_playwright

async def inspect_topic():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        target_url = "https://questions.examside.com/past-years/medical/neet/physics/units-and-measurement"
        print(f"Navigating to {target_url} ...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Get all sub-topic links
        links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: (e.innerText || e.textContent || '').trim(), href: e.href}))")
        topic_links = [l for l in links if 'units-and-measurement/' in l['href']]
        print(f"Found {len(topic_links)} sub-topic links:")
        for t in topic_links[:10]:
            print(f" - {t['text']}: {t['href']}")
            
        if topic_links:
            t_url = topic_links[0]['href']
            print(f"\nNavigating to topic page: {t_url}")
            await page.goto(t_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)
            
            # Save HTML
            html_content = await page.content()
            with open("scratch/examside_topic_page.html", "w") as f:
                f.write(html_content)
                
            print("Saved topic page HTML to scratch/examside_topic_page.html")
            
            # Inspect images and math elements
            imgs = await page.eval_on_selector_all("img", "elements => elements.map(e => ({src: e.src, alt: e.alt}))")
            print(f"Found {len(imgs)} images on topic page.")
            for img in imgs[:10]:
                print("   Image:", img)
                
            body_text = await page.inner_text("body")
            print("\nTopic Page Text Preview (First 1000 chars):\n", body_text[:1000])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect_topic())
