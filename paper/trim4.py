"""Final compression pass, sized to the 224pt still needed for nine pages.

    python paper/trim4.py
"""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "ieee_paper.html"
s = SRC.read_text(encoding="utf-8")
log: list[tuple[str, int]] = []


def sub(old: str, new: str, label: str) -> None:
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
    n = len(pat.findall(s))
    if n != 1:
        print(f"  MISS ({n}) {label}")
        return
    s = pat.sub(lambda m: new, s, count=1)
    log.append((label, len(old.split()) - len(new.split())))


sub("A reader should suspect that confining the model this tightly must cost accuracy "
    "somewhere. The claim is that it does not, and it is tested by running both architectures "
    "over identical scenarios against identical ground truth, and by checking whether the "
    "model&rsquo;s narrated severity agrees with the computed one on the same input. If the "
    "narration quietly disagreed with the computation, the system would be deciding twice and "
    "reporting once.",
    "A reader should suspect that confining the model this tightly costs accuracy somewhere. The "
    "claim is that it does not. It is tested by running both architectures over identical "
    "scenarios against identical ground truth, and by checking whether the narrated severity "
    "agrees with the computed one on the same input. If narration quietly disagreed with the "
    "computation, the system would be deciding twice and reporting once.",
    "III-D")

sub("The middle parameter is the one that matters, and we only learned that by getting it "
    "wrong. An earlier implementation expanded every neighbour of every seed. Real project "
    "graphs have hubs: a release milestone touching four hundred tasks, a tech lead assigned to "
    "a third of the board. One high-degree seed dragged a large fraction of the project back "
    "into the prompt, and measured prompt growth was 4.31&times; across the size sweep. Capping "
    "neighbours per seed brought it to 1.007&times;. The bound on prompt size is not a property "
    "of taking one hop; it is a property of refusing to follow a hub.",
    "The middle parameter is the one that matters, and we learned that by getting it wrong. An "
    "earlier implementation expanded every neighbour of every seed. Real project graphs have "
    "hubs: a release milestone touching four hundred tasks, a tech lead on a third of the board. "
    "One such seed dragged much of the project back into the prompt, and measured growth was "
    "4.31&times; across the size sweep. Capping neighbours per seed brought it to 1.007&times;. "
    "The bound comes from refusing to follow a hub, not from taking one hop.",
    "V-C")

sub("The implementation is roughly 21,000 lines. Three suites run on every push: 109 backend "
    "tests against both SQLite and PostgreSQL&nbsp;16, among them a 185-check role-by-endpoint "
    "matrix; 85 analysis-service tests; and 63 frontend tests. A replay of the demonstration "
    "runs beside them, re-checking every number the demonstration script quotes.",
    "The implementation is roughly 21,000 lines. Three suites run on every push: 109 backend "
    "tests on both SQLite and PostgreSQL&nbsp;16, including a 185-check role-by-endpoint matrix; "
    "85 analysis-service tests; and 63 frontend tests. A replay of the demonstration runs beside "
    "them, re-checking every number it quotes.",
    "VIII-I")

sub("The results support a narrower claim than the architecture might invite. What is "
    "demonstrated is that confining a language model to narration costs nothing measurable in "
    "detection quality, buys two orders of magnitude in prompt cost at realistic project sizes, "
    "and converts evidence fabrication from a hazard into a closed-set membership test. What is "
    "<em>not</em> demonstrated is that the graph projection is a better predictor of lateness "
    "than simple alternatives. On ranking it is not better than counting open work, and against "
    "a tuned learned model the comparison is statistically a draw.",
    "The results support a narrower claim than the architecture might invite. Confining a "
    "language model to narration costs nothing measurable in detection quality, buys two orders "
    "of magnitude in prompt cost at realistic sizes, and turns evidence fabrication from a "
    "hazard into a closed-set membership test. What is <em>not</em> demonstrated is that the "
    "graph projection predicts lateness better than simple alternatives. On ranking it does not "
    "beat counting open work, and against a tuned model the comparison is a draw.",
    "IX para 1")

sub("Across a test corpus in which fabricated references were injected deliberately, 200 of 200 "
    "were removed, leaving no unresolvable citation in any output. The guarantee is narrow and "
    "should be stated narrowly: every surviving citation names a node that exists in the witness "
    "the model was shown. It does not follow that the surviving citation is the <em>most "
    "relevant</em> node, and nothing here measures whether the resulting explanation helps a "
    "manager. See Section X.",
    "Across a corpus with fabricated references injected deliberately, 200 of 200 were removed, "
    "leaving no unresolvable citation in any output. The guarantee is narrow and should be "
    "stated narrowly: every surviving citation names a node present in the witness the model was "
    "shown. It does not follow that it is the <em>most relevant</em> node, and nothing here "
    "measures whether the explanation helps a manager. See Section X.",
    "VIII-C")

sub("The prompt contains one finding, its witness, and an instruction to explain the finding in "
    "prose, citing node identifiers from the witness. It does not contain the project, the other "
    "five risk categories, or the score. The model is not asked whether the finding is correct, "
    "and its answer is not used to compute anything. Section VIII-F reports how closely its "
    "narrated severity tracks the deterministic one; the point of that measurement is to confirm "
    "the model is narrating rather than quietly re-deciding.",
    "The prompt contains one finding, its witness, and an instruction to explain it in prose "
    "citing node identifiers from that witness. It contains neither the project, nor the other "
    "five categories, nor the score. The model is never asked whether the finding is correct, "
    "and its answer computes nothing. Section VIII-F reports how closely its narrated severity "
    "tracks the deterministic one, confirming it narrates rather than quietly re-decides.",
    "V-D")

sub("Detection quality is reported as precision, recall and F1, with accuracy included but "
    "de-emphasised given the class balance; AUC-ROC for threshold-independent ranking; and the "
    "Brier score for calibration. Paired comparisons use exact McNemar tests on the same "
    "sprints, and interval estimates use a cluster bootstrap that resamples <em>projects</em> "
    "with replacement over 2,000 replicates [35], matching the unit of the split.",
    "Detection quality is reported as precision, recall and F1, with accuracy de-emphasised "
    "given the class balance, AUC-ROC for threshold-independent ranking, and the Brier score for "
    "calibration. Paired comparisons use exact McNemar tests on the same sprints; intervals use "
    "a cluster bootstrap resampling <em>projects</em> over 2,000 replicates [35], matching the "
    "unit of the split.",
    "VII-E")

SRC.write_text(s, encoding="utf-8")
for label, delta in log:
    print(f"  -{delta:3d} words  {label}")
print(f"total: -{sum(d for _, d in log)} words")
