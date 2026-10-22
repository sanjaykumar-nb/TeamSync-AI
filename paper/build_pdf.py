"""Render paper/ieee_paper.html to a print-ready PDF.

Chrome does the pagination, so the @page rule in the stylesheet is what decides
the trim size and the margins — preferCSSPageSize keeps Playwright from imposing
its own.

    python paper/build_pdf.py
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "ieee_paper.html"
OUT = HERE.parent / "TeamSync_IEEE_Paper.pdf"


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(SRC.as_uri(), wait_until="networkidle")
        await page.emulate_media(media="print")
        await page.pdf(
            path=str(OUT),
            prefer_css_page_size=True,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        await browser.close()
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    asyncio.run(main())
