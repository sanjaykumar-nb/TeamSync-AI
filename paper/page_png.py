"""Rasterise PDF pages so the layout can be inspected.

    python paper/page_png.py TeamSync_IEEE_Paper.pdf 1 2 3
"""
import sys
from pathlib import Path

import fitz

src = Path(sys.argv[1])
pages = [int(a) for a in sys.argv[2:]] or [1]
doc = fitz.open(src)
outdir = Path(__file__).resolve().parent / "_pages"
outdir.mkdir(exist_ok=True)
for n in pages:
    pix = doc[n - 1].get_pixmap(dpi=135)
    dest = outdir / f"p{n:02d}.png"
    pix.save(dest)
    print(dest)
