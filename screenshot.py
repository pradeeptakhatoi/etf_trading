import asyncio, sys
from playwright.async_api import async_playwright

BASE = "http://localhost:8502"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(BASE, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(8000)

        # Tab indices: 0=Overview, 1=Watchlist, 2=Gainers/Losers, 3=Sector View, 4=Screener
        tabs_info = [
            (1, "watchlist"),
            (2, "gainers"),
            (3, "sector"),
            (4, "screener"),
        ]
        for tab_idx, name in tabs_info:
            await page.evaluate(f"""() => {{
                const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                if (tabs[{tab_idx}]) tabs[{tab_idx}].click();
            }}""")
            await page.wait_for_timeout(3500)
            await page.screenshot(path=f"D:/work/etf_trading/ss_0{tab_idx+1}_{name}.png")
            sys.stdout.buffer.write(f"Saved: {name}\n".encode())
            sys.stdout.buffer.flush()

        await browser.close()
        sys.stdout.buffer.write(b"All done.\n")

asyncio.run(run())
