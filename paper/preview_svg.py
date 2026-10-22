"""Render an SVG to PNG at 3x so the layout can be eyeballed before it ships.

    python paper/preview_svg.py paper/figures/fig1_architecture_blocks.svg
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright


async def main(src: Path, scale: int = 3) -> None:
    svg = src.read_text(encoding="utf-8")
    page_html = (
        "<!doctype html><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;background:#fff}"
        "svg{display:block}</style>" + svg
    )
    tmp = src.with_suffix(".preview.html")
    tmp.write_text(page_html, encoding="utf-8")
    dest = src.with_suffix(".png")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=scale)
        await page.goto(tmp.resolve().as_uri())
        el = await page.query_selector("svg")
        await el.screenshot(path=str(dest))
        await browser.close()
    tmp.unlink(missing_ok=True)
    print(f"wrote {dest}")


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1])))
