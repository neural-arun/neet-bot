import asyncio
import json
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_reveal():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # Block ad scripts
        await page.route("**/*vignette*", lambda route: route.abort())
        await page.route("**/*google*", lambda route: route.abort())
        await page.route("**/*doubleclick*", lambda route: route.abort())
        
        target_url = "https://questions.examside.com/past-years/medical/question/pconsider-that-sigmas-kb-b-represents-stefan-boltzm-neet-physics-units-and-measurement-r6p9wdbbidtgeojo"
        print(f"Navigating to {target_url} ...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Find all "Check Answer" buttons
        check_btns = await page.query_selector_all("text=Check Answer")
        print(f"Found {len(check_btns)} 'Check Answer' buttons.")
        
        for idx, btn in enumerate(check_btns):
            try:
                await btn.click()
                await page.wait_for_timeout(1000)
                print(f"Clicked 'Check Answer' button {idx+1}")
            except Exception as e:
                print(f"Error clicking button {idx+1}: {e}")
                
        # Re-inspect page content
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Save HTML with revealed solutions
        with open("scratch/examside_revealed_page.html", "w") as f:
            f.write(html_content)
            
        print("\nSaved revealed page HTML to scratch/examside_revealed_page.html")
        
        # Extract images from solution
        imgs = [img['src'] for img in soup.find_all('img', src=True)]
        print(f"Found {len(imgs)} total images after revealing solutions.")
        for img in imgs:
            if not any(ignore in img for ignore in ['logo', 'warning', 'translate', 'svg']):
                print("   Diagram/Solution Image:", img)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_reveal())
