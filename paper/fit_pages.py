"""Search for the figure placement that wastes the least page.

A `column-span: all` figure that does not fit in what is left of a page pushes
the whole page break, so where a wide figure sits in the source decides how much
white space the paper carries. IEEE only asks that a figure appear at or after
its first reference, which leaves several legal positions for each one; this
tries them and keeps the arrangement with the fewest pages, breaking ties on
total unused space.

    python paper/fit_pages.py
"""
from __future__ import annotations

import asyncio
import itertools
import re
import shutil
from pathlib import Path

import fitz
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "ieee_paper.html"
WORK = HERE / "_fit.html"
PDF = HERE / "_fit.pdf"

# legal positions for each figure: anchors it may be inserted *before*
SLOTS = {
    "fig2_token": [
        "<h3>D. Mid-sprint early warning on unseen projects</h3>",
        "<h3>E. Sprint-end evaluation, and a learned comparator</h3>",
        "AFTER_TABLE_III",
    ],
    "fig3_holdout": [
        "<h3>F. Three attempts that failed</h3>",
        "<h3>G. Does grounding cost accuracy?</h3>",
        "<h3>H. Does the model narrate, or quietly re-decide?</h3>",
    ],
}


def figure_block(s: str, marker: str) -> str:
    m = re.search(r'<figure class="wide">\s*<img src="figures/' + marker + r'.*?</figure>\r?\n', s, re.S)
    assert m, marker
    return m.group(0)


def place(base: str, choice: dict[str, str]) -> str:
    s = base
    blocks = {k: figure_block(s, k) for k in choice}
    for b in blocks.values():
        s = s.replace(b, "")
    for marker, anchor in choice.items():
        blk = blocks[marker].strip()
        if anchor == "AFTER_TABLE_III":
            tbl = re.search(r'<div class="tablewrap wide">.*?</div>\r?\n', s, re.S).group(0)
            s = s.replace(tbl, tbl + "\n" + blk + "\n", 1)
        else:
            assert anchor in s, anchor
            s = s.replace(anchor, blk + "\n\n" + anchor, 1)
    return s


async def render(html: str) -> tuple[int, float]:
    WORK.write_text(html, encoding="utf-8")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(WORK.as_uri(), wait_until="networkidle")
        await page.emulate_media(media="print")
        await page.pdf(path=str(PDF), prefer_css_page_size=True, print_background=True,
                       margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        await browser.close()
    doc = fitz.open(PDF)
    waste = 0.0
    for i, pg in enumerate(doc, 1):
        if i == doc.page_count:
            continue
        blocks = pg.get_text("blocks")
        imgs = [pg.get_image_bbox(x) for x in pg.get_images(full=True)] if pg.get_images() else []
        waste += 720 - max([b[3] for b in blocks] + [b.y1 for b in imgs] + [0])
    n = doc.page_count
    doc.close()
    return n, waste


async def main() -> None:
    base = SRC.read_text(encoding="utf-8")
    best = None
    for combo in itertools.product(*SLOTS.values()):
        choice = dict(zip(SLOTS, combo))
        try:
            html = place(base, choice)
        except AssertionError as e:
            print(f"  skip ({e})")
            continue
        pages, waste = await render(html)
        tag = " | ".join(a[:46] for a in combo)
        print(f"{pages:>3} pages  waste {waste:7.1f}pt   {tag}")
        if best is None or (pages, waste) < (best[0], best[1]):
            best = (pages, waste, html, tag)
    pages, waste, html, tag = best
    SRC.write_text(html, encoding="utf-8")
    print(f"\nkept: {pages} pages, {waste:.1f}pt unused\n      {tag}")
    for f in (WORK, PDF):
        f.unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(main())
