"""Third pass: remove the duplications rather than shave more sentences.

Table I restated Section III cell for cell, so it carried no information the
prose did not. The Discussion's middle paragraphs restated Section III-E and
the Conclusion. Those go. Remaining numbers, claims and threats are untouched.

    python paper/trim3.py
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


# ---- Table I: every cell repeats a sentence of Section III
m = re.search(r'<div class="tablewrap">\s*<p class="tcap">Table I<br>.*?</div>\s*', s, re.S)
assert m, "claims table not found"
s = s[:m.start()] + s[m.end():]
log.append(("Table I removed", 0))

sub("Each is stated below in the form in which it could be shown false, with the mechanism "
    "behind it and the measurement that tests it. Table I collects them.",
    "Each is stated below in the form in which it could be shown false, with the mechanism "
    "behind it and the measurement that tests it.",
    "Table I reference")

# the remaining tables shift down one numeral
for old, new in [("Table V", "@@Table IV@@"), ("Table IV", "@@Table III@@"),
                 ("Table III", "@@Table II@@"), ("Table II", "@@Table I@@")]:
    s = s.replace(old, new)
s = re.sub(r"@@Table ([IVX]+)@@", r"Table \1", s)

# ---- Discussion: three paragraphs become one, keeping the operating point and the ethics
sub("We read that combination as the interesting finding rather than a disappointment. The "
    "field&rsquo;s default assumption is that sophistication buys accuracy and that "
    "explainability is paid for out of it. Here sophistication bought nothing that survived a "
    "project boundary, while the explainable object cost nothing. When two predictors cannot be "
    "separated statistically, the tiebreakers are the ones practitioners care about: cost, "
    "determinism, and whether the output can be checked.",
    "We read that as the interesting finding rather than a disappointment. The field&rsquo;s "
    "default assumption is that sophistication buys accuracy and that explainability is paid for "
    "out of it. Here sophistication bought nothing that survived a project boundary. When two "
    "predictors cannot be separated statistically, the tiebreakers are cost, determinism and "
    "whether the output can be checked.",
    "IX para 2")

sub("The operating point deserves comment. The rule is high-sensitivity and over-flags: roughly "
    "half its sprint-end alarms are on sprints that finish on time. That is the correct trade "
    "only when a false alarm is cheap to dismiss and a miss is expensive, which is the usual "
    "shape of sprint risk but is not universal. A team drowning in alerts will ignore all of "
    "them, and no confidence interval in this paper addresses that.",
    "The operating point deserves comment. The rule over-flags: roughly half its sprint-end "
    "alarms land on sprints that finish on time. That trade is right only when a false alarm is "
    "cheap and a miss is not, which is the usual shape of sprint risk but not a universal one. A "
    "team drowning in alerts ignores all of them, and no interval here addresses that.",
    "IX para 3")

sub("Finally, a system that scores people can be used against them. It names the overloaded "
    "engineer, the silent team member, the single point of failure. The design choices here "
    "reduce but do not eliminate the risk: the output is an explanation with its evidence rather "
    "than a bare score, which at least makes a claim about a person contestable by the person. "
    "We would not deploy this as an input to performance review, and we think a paper proposing "
    "it should say so.",
    "Finally, a system that names the overloaded engineer, the silent member and the single "
    "point of failure can be used against them. The design reduces but does not eliminate that "
    "risk: output carries its evidence rather than a bare score, which makes a claim about a "
    "person contestable by that person. We would not deploy this as an input to performance "
    "review, and a paper proposing it should say so.",
    "IX para 4")

# ---- VIII-D and VIII-E qualifications
sub("What the table also shows, and we would rather say it than have a reviewer find it, is "
    "that the graph projection does not <em>rank</em> better than a trivial alternative. Simply "
    "measuring the share of work still open gives AUC 0.802 at the halfway point against the "
    "projection&rsquo;s 0.792, and 0.881 against 0.874 at three-quarters. The projection earns "
    "its place in the system by being the same object that explains the risk and carries its "
    "evidence, not by ordering sprints more accurately than counting unfinished issues.",
    "The table also shows something we would rather state than have a reviewer find: the "
    "projection does not <em>rank</em> better than a trivial alternative. The share of work still "
    "open gives AUC 0.802 at halfway against the projection&rsquo;s 0.792, and 0.881 against "
    "0.874 at three-quarters. The projection earns its place by being the same object that "
    "explains the risk and carries its evidence, not by ordering sprints better than counting "
    "unfinished issues.",
    "VIII-D")

sub("The second caution concerns what may be concluded about the learned model. The rule&rsquo;s "
    "F1 exceeds the composite&rsquo;s point estimate, but a paired test cannot separate them: "
    "exact McNemar gives <em>p</em> = 0.78, and the bootstrap difference is +0.119 with a 95% "
    "interval of [&minus;0.025, +0.291] spanning zero. Against flagging every sprint, by "
    "contrast, the difference is +0.055, [+0.030, +0.080], <em>p</em> &lt; 0.001, a real effect. "
    "The defensible claim is therefore not that the rule predicts better than the learned model. "
    "It is that the learned model&rsquo;s tuned advantage did not survive the move to unseen "
    "projects, and that the simpler object is the one that arrives with its evidence attached.",
    "The second concerns the learned model. The rule&rsquo;s F1 exceeds the composite&rsquo;s "
    "point estimate, but a paired test cannot separate them: exact McNemar gives <em>p</em> = "
    "0.78, and the bootstrap difference is +0.119 with a 95% interval of [&minus;0.025, +0.291] "
    "spanning zero. Against flagging every sprint the difference is +0.055, [+0.030, +0.080], "
    "<em>p</em> &lt; 0.001, a real effect. So the defensible claim is not that the rule predicts "
    "better, but that the learned model&rsquo;s tuned advantage did not survive unseen projects.",
    "VIII-E")

# ---- VIII-H
sub("Schema validity needs two numbers rather than one, and we report both. Over all 90 "
    "attempted calls, 41.1% returned a valid structure. Of the 24 individually diagnosed "
    "failures, 22 were HTTP 429 rate limits from a free-tier key. That is a property of the "
    "infrastructure, not of the model. Because the run logged only those 24 failures "
    "individually, validity over calls that actually reached the model cannot be computed, only "
    "bounded: between 54% and 95%. We quote 41.1% as the measured end-to-end rate and the range "
    "as a range. The commonly convenient figure of roughly 92% assumes the optimistic extreme, "
    "and this run has no per-call record that would support it.",
    "Schema validity needs two numbers, and we report both. Over all 90 attempted calls, 41.1% "
    "returned a valid structure. Of 24 diagnosed failures, 22 were HTTP 429 rate limits from a "
    "free-tier key, a property of the infrastructure rather than the model. Because only those "
    "24 were logged individually, validity over calls that reached the model cannot be computed, "
    "only bounded: between 54% and 95%. We quote 41.1% as the measured end-to-end rate and the "
    "range as a range. The convenient figure of roughly 92% assumes the optimistic extreme, and "
    "this run has no per-call record supporting it.",
    "VIII-H")

SRC.write_text(s, encoding="utf-8")
for label, delta in log:
    print(f"  -{delta:3d} words  {label}")
print(f"total: -{sum(d for _, d in log)} words, plus one table")
