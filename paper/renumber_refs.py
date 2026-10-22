"""Renumber the reference list into order of first citation.

IEEE numbers references by where they are first cited, not by when they were
added to the list. Doing that by hand after an edit is how papers end up citing
[31] before [12], so this does it mechanically and refuses to run if anything
looks wrong.

Citation tokens are matched as [n] with one or two digits. The numeric
intervals in this paper — [0.610, 0.814], [+0.030, +0.080] — all contain a dot
or a comma, so they cannot be mistaken for citations.

    python paper/renumber_refs.py
"""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "ieee_paper.html"
CITE = re.compile(r"\[(\d{1,2})\]")


def main() -> None:
    html = SRC.read_text(encoding="utf-8")

    m = re.search(r'(<ol class="refs">)(.*?)(</ol>)', html, re.S)
    assert m, "reference list not found"
    body, refs_inner = html[: m.start()], m.group(2)

    items = re.findall(r"<li>.*?</li>", refs_inner, re.S)
    assert items, "no reference entries"

    order: list[int] = []
    for tok in CITE.findall(body):
        n = int(tok)
        if n not in order:
            order.append(n)

    cited = set(order)
    everything = set(range(1, len(items) + 1))
    missing = sorted(cited - everything)
    uncited = sorted(everything - cited)
    assert not missing, f"cited but not in the list: {missing}"
    if uncited:
        raise SystemExit(f"refusing to renumber: never cited in the text: {uncited}")

    mapping = {old: new for new, old in enumerate(order, 1)}
    body = CITE.sub(lambda mo: f"[{mapping[int(mo.group(1))]}]", body)
    reordered = "\n".join(items[old - 1] for old in order)

    out = body + m.group(1) + "\n" + reordered + "\n" + m.group(3) + html[m.end():]
    SRC.write_text(out, encoding="utf-8")

    moved = sum(1 for old, new in mapping.items() if old != new)
    print(f"{len(items)} references, {moved} renumbered into citation order")


if __name__ == "__main__":
    main()
