"""Render the Archer diagrams to PNG.

    python3 assets/diagrams/render.py            # every *.html here
    python3 assets/diagrams/render.py method.html

Each page names its output with <meta name="out" content="../method.png">
(relative to this folder). Pages are 1200 CSS px wide, rendered at 2x.
Needs: pip install playwright && playwright install chromium
"""
import asyncio, pathlib, re, sys
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent


async def main(names):
    pages = [HERE / n for n in names] or sorted(HERE.glob("*.html"))
    async with async_playwright() as p:
        kw = {}
        chrome = pathlib.Path("/usr/bin/google-chrome")
        if chrome.exists():
            kw["executable_path"] = str(chrome)
        browser = await p.chromium.launch(**kw)
        page = await browser.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=2)
        for src in pages:
            out = re.search(r'<meta name="out" content="([^"]+)"', src.read_text()).group(1)
            await page.goto(src.as_uri())
            await page.evaluate("document.fonts.ready")
            await page.wait_for_timeout(300)
            target = (HERE / out).resolve()
            await page.locator(".canvas").screenshot(path=str(target))
            print(f"{src.name} -> {target.relative_to(HERE.parent.parent)}")
        await browser.close()


asyncio.run(main(sys.argv[1:]))
