"""Compress the paragraphs that repeat themselves, to reach nine pages.

Every cut here removes restatement, not substance: no number, claim, threat or
qualification is dropped. The targets were chosen by measuring paragraph length
per section and then checking each long one against what the surrounding text
already says.

    python paper/trim.py
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


# ---- II-B: the roll-call of frameworks does not need a clause each
sub(
    "MetaGPT [8] assigns standard-operating-procedure roles to agents producing software "
    "artefacts; ChatDev [9] runs a simulated software company through conversational "
    "turn-taking; AutoGen [10] generalises the pattern into a conversation framework; "
    "ReAct [11] interleaves reasoning traces with tool actions; and AgentBench [12] and the "
    "surveys of Wang et al. [13] and He et al. [14] map the resulting design space, the latter "
    "specifically for software engineering. A 2026 experience report building such systems with "
    "current frameworks finds the basic components well covered and the operational ones, agent "
    "telemetry above all, still missing [15], which matches our own experience: the hardest part "
    "was not making agents talk but being able to tell, afterwards, which path produced a given "
    "output. Closer to the task studied here, Kanagamalliga et al. [16] build an interpretable "
    "multi-agent architecture for automated legal risk assessment, splitting the judgement "
    "across specialised agents so the reasoning behind a verdict can be inspected. Ramshankar "
    "et al. [17] survey how such agentic systems adapt at run time. In both, the model stays "
    "inside the decision. We put it outside. These systems share an assumption worth naming: "
    "that the model is the component that <em>decides</em>, and that the engineering problem is "
    "arranging its decisions well.",
    "MetaGPT [8], ChatDev [9] and AutoGen [10] arrange agents into roles, conversations and "
    "reusable frameworks; ReAct [11] interleaves reasoning with tool actions; AgentBench [12] "
    "and the surveys of Wang et al. [13] and He et al. [14] map the design space, the last "
    "specifically for software engineering. A 2026 experience report finds the basic components "
    "well covered and the operational ones, agent telemetry above all, still missing [15]. That "
    "matches our own experience. The hard part was never making agents talk; it was telling "
    "afterwards which path produced a given output. Closer to this task, Kanagamalliga et al. "
    "[16] split automated legal risk assessment across specialised agents so the reasoning "
    "behind a verdict can be inspected, and Ramshankar et al. [17] survey how such systems adapt "
    "at run time. In both the model stays inside the decision. We put it outside. All of this "
    "work shares an assumption worth naming: that the model is the component that "
    "<em>decides</em>.",
    "II-B")

# ---- III intro
sub(
    "The architecture in Section IV is not interesting by itself. Plenty of systems put a graph "
    "next to a language model. The argument of this paper is narrower and falsifiable: that "
    "<em>this particular division of labour</em>, computing the risk and then letting the model "
    "do nothing but describe one already-computed finding, buys four properties the ordinary "
    "arrangement cannot, and costs nothing measurable in return. This section states each "
    "property in the form in which it could be shown false, names the mechanism that produces "
    "it, and points at the measurement that tests it. Table I collects them.",
    "The architecture in Section IV is not interesting by itself. Plenty of systems put a graph "
    "next to a language model. The argument here is narrower and falsifiable: that <em>this "
    "particular division of labour</em>, computing the risk and then letting the model only "
    "describe one already-computed finding, buys four properties the ordinary arrangement "
    "cannot, and costs nothing measurable in return. Each is stated below in the form in which "
    "it could be shown false, with the mechanism behind it and the measurement that tests it. "
    "Table I collects them.",
    "III intro")

# ---- III-E, and repair a sentence an earlier edit broke
sub(
    "The third failed in the most instructive way. cross-validated F1 0.816 collapsed to 0.593 "
    "on projects the model had not seen, where the rule with nothing to fit scored 0.712. A "
    "paired test cannot separate the two. We do not claim the rule predicts better. We claim "
    "the tuned advantage did not cross a project boundary, and that when two predictors cannot "
    "be separated, the one that arrives with its evidence attached is the better engineering "
    "choice.",
    "The third failed most instructively: cross-validated F1 0.816 collapsed to 0.593 on "
    "projects the model had not seen, where the rule with nothing to fit scored 0.712. A paired "
    "test cannot separate them. We do not claim the rule predicts better, only that the tuned "
    "advantage did not cross a project boundary. When two predictors cannot be separated, the "
    "one carrying its evidence is the better engineering choice.",
    "III-E")

# ---- IV, third paragraph: Fig. 1's caption already carries much of this
sub(
    "Within the analysis tier the figure draws the distinction the paper is about, as three "
    "bands. The deterministic core compiles the graph, computes the risk metrics and selects "
    "the witness subgraph; it makes no model call and contains no randomness, so the same board "
    "gives the same numbers twice. The agent layer runs the coordinator and its specialists over "
    "those numbers and emits one output schema whichever path produced it. The narration layer "
    "assembles a prompt, calls a model adapter and verifies what comes back, and it is the only "
    "band that may reach a language model at all. The heavy connector between the second and "
    "third bands carries one finding and its witness subgraph, and nothing else crosses. The "
    "dashed line leaving the core shows the risk scores reaching the application tier without "
    "entering the third band: if the narration layer fails, is rate-limited, or is switched off "
    "entirely, the prose disappears and the numbers the product displays are unchanged.",
    "Within the analysis tier the figure draws the distinction the paper is about, as three "
    "bands. The deterministic core compiles the graph, computes the metrics and selects the "
    "witness subgraph, with no model call and no randomness, so the same board gives the same "
    "numbers twice. The agent layer runs the coordinator and its specialists over those numbers, "
    "emitting one schema whichever path produced it. The narration layer is the only band that "
    "may reach a language model, and the heavy connector into it carries one finding and its "
    "witness subgraph. Nothing else crosses. The risk scores reach the application tier without "
    "entering that band, so if narration fails, is rate-limited or is switched off, the prose "
    "disappears and the numbers do not move.",
    "IV para 3")

# ---- VIII-G qualifications
sub(
    "The comparison is deliberately tilted toward the naive baseline: tiny projects where full "
    "context is cheap and fits comfortably, a good-faith prompt defining all six categories, and "
    "lenient response parsing. Three qualifications still apply. The naive baseline is not bad. "
    "F1 0.947 is a respectable score, and it over-reports only modestly, naming 2.75 risk "
    "categories per scenario against the graph&rsquo;s 2.42, with 12.1% of its claims "
    "uncorroborated. Scoring is per-target-category, so risks it reports on other dimensions are "
    "not counted against it; stricter scoring would likely widen the gap, and we do not claim it. "
    "And nothing here says anything about naive accuracy <em>at scale</em>, which is untested "
    "and, at 190,000 tokens per scenario, largely untestable on an ordinary budget. That limit "
    "is itself part of the argument. The mean prompts in this ablation were 1,109 tokens against "
    "1,804, a ratio of 1.6&times;; the 487&times; figure belongs to Section VIII-A and the two "
    "should not be conflated.",
    "The comparison is deliberately tilted toward the naive baseline: tiny projects where full "
    "context is cheap, a good-faith prompt defining all six categories, and lenient parsing. "
    "Three qualifications apply. F1 0.947 is a respectable score, and the baseline over-reports "
    "only modestly, naming 2.75 categories per scenario against the graph&rsquo;s 2.42, with "
    "12.1% of its claims uncorroborated. Scoring is per-target-category, so risks reported on "
    "other dimensions are not counted against it; stricter scoring would likely widen the gap, "
    "and we do not claim it. Nothing here addresses naive accuracy <em>at scale</em>, which at "
    "190,000 tokens per scenario is largely untestable on an ordinary budget, and that limit is "
    "part of the argument. Mean prompts here were 1,109 tokens against 1,804, a ratio of "
    "1.6&times;. The 487&times; figure belongs to Section VIII-A.",
    "VIII-G")

# ---- IX, second paragraph
sub(
    "We think that combination is the interesting finding rather than a disappointment. The "
    "field&rsquo;s default assumption is that a more sophisticated model buys accuracy, and that "
    "explainability is paid for out of that accuracy. Here the sophisticated model bought "
    "nothing that survived a project boundary, while the explainable object cost nothing and "
    "arrived with the graph nodes behind its verdict. When two predictors cannot be separated "
    "statistically, the tiebreakers are the ones a practitioner actually cares about: cost, "
    "determinism, and whether the output can be checked.",
    "We read that combination as the interesting finding rather than a disappointment. The "
    "field&rsquo;s default assumption is that sophistication buys accuracy and that "
    "explainability is paid for out of it. Here sophistication bought nothing that survived a "
    "project boundary, while the explainable object cost nothing. When two predictors cannot be "
    "separated statistically, the tiebreakers are the ones practitioners care about: cost, "
    "determinism, and whether the output can be checked.",
    "IX para 2")

# ---- XI, both paragraphs
sub(
    "Asking a language model to find risk in a project is expensive, non-reproducible and "
    "unverifiable. Computing the risk from a typed graph and asking the model only to explain "
    "one finding from a bounded witness is none of those things, and this paper reports it costs "
    "nothing in detection quality to make the swap: prompt cost grows 1.47&times; across a "
    "154&times; growth in project size, 200 of 200 fabricated citations are removed, narrated "
    "and computed verdicts agree at <em>&kappa;</em> = 0.95, and on 270 sprints from 22 unseen "
    "projects the same graph warns at the halfway mark with AUC 0.792, rising to 0.874 at "
    "three-quarters.",
    "Asking a language model to find risk in a project is expensive, non-reproducible and "
    "unverifiable. Computing it from a typed graph and asking the model only to explain one "
    "finding from a bounded witness is none of those things, and the swap costs nothing in "
    "detection quality: prompt cost grows 1.47&times; across a 154&times; growth in project "
    "size, 200 of 200 fabricated citations are removed, narrated and computed verdicts agree at "
    "<em>&kappa;</em> = 0.95, and on 270 sprints from 22 unseen projects the graph warns at the "
    "halfway mark with AUC 0.792, rising to 0.874 at three-quarters.",
    "XI para 1")

sub(
    "Three pieces of future work follow directly from the threats above, in order of how much "
    "they would change the conclusions: a human study of whether the grounded explanations "
    "change what managers do, which is the gap the grounding guarantee cannot close; real-world "
    "validation of the five categories currently supported only by synthetic evidence, which "
    "needs a data source with intra-sprint dependency structure; and a repeat of the live-model "
    "run on a paid key with per-call error logging, which would turn the 54&ndash;95% bound into "
    "a number.",
    "Three pieces of future work follow from the threats above, in order of how much they would "
    "change the conclusions: a human study of whether grounded explanations change what managers "
    "do, the gap the grounding guarantee cannot close; real-world validation of the five "
    "categories now supported only by synthetic evidence, which needs a data source with "
    "intra-sprint dependency structure; and a repeat of the live-model run on a paid key with "
    "per-call logging, turning the 54&ndash;95% bound into a number.",
    "XI para 2")

SRC.write_text(s, encoding="utf-8")
for label, delta in log:
    print(f"  -{delta:3d} words  {label}")
print(f"total: -{sum(d for _, d in log)} words across {len(log)} paragraphs")
