"""Second compression pass. Same rule as the first: restatement goes, substance stays.

    python paper/trim2.py
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


# ---- abstract: 267 words is over the 250 most IEEE venues allow
sub("This paper reports a system built on the opposite arrangement. Project state is "
    "compiled into a typed knowledge graph, six categories of coordination risk are computed "
    "from that graph by deterministic algorithms, and the language model is given only a "
    "bounded witness subgraph around one already-detected anomaly, with the single job of "
    "narrating it. Every citation the model produces is resolved against the node identifiers "
    "in that subgraph and discarded if it does not resolve. Across a project grown from 13 to "
    "2,003 tasks the prompt grew 1.47&times; while full-dataset prompting grew to 189,834 "
    "tokens, a 487&times; reduction at the largest size; 200 of 200 deliberately fabricated "
    "citations were removed; and agreement between the model&rsquo;s narrated verdict and the "
    "deterministic one reached Cohen&rsquo;s <em>&kappa;</em> = 0.95.",
    "This paper reports a system built on the opposite arrangement. Project state becomes a "
    "typed knowledge graph, six categories of coordination risk are computed from it by "
    "deterministic algorithms, and the model receives only a bounded witness subgraph around "
    "one already-detected anomaly, with the single job of narrating it. Every citation it "
    "produces is resolved against the node identifiers in that subgraph and discarded if it "
    "does not resolve. Across a project grown from 13 to 2,003 tasks the prompt grew "
    "1.47&times; against 189,834 tokens for full-dataset prompting, a 487&times; reduction; 200 "
    "of 200 fabricated citations were removed; and narrated and deterministic verdicts agreed "
    "at Cohen&rsquo;s <em>&kappa;</em> = 0.95.",
    "abstract")

# ---- Introduction
sub("The arrival of capable language models suggested a shortcut: serialise the project, ask "
    "the model what is going wrong, and read the answer. Having built that baseline and "
    "measured it, we think the shortcut is a poor trade for three separate reasons. Cost scales "
    "with the project, because the whole board has to enter the context window; a 2,000-task "
    "project costs roughly 190,000 prompt tokens per analysis, which rules out running the "
    "analysis on every change. Determinism is lost, because the same board can yield different "
    "verdicts on consecutive calls, and a risk score that moves when nothing moved is not a "
    "measurement. Finally, and most seriously for a tool whose output is meant to change what "
    "people do, the justification cannot be trusted: models cite issue keys and names that look "
    "exactly like real ones and are not [1].",
    "Capable language models suggested a shortcut: serialise the project, ask what is going "
    "wrong, read the answer. We built that baseline and measured it. It is a poor trade for "
    "three reasons. Cost scales with the project, since the whole board enters the context "
    "window; at 2,000 tasks that is roughly 190,000 prompt tokens per analysis, which rules out "
    "running it on every change. Determinism is lost, because the same board yields different "
    "verdicts on consecutive calls, and a score that moves when nothing moved is not a "
    "measurement. Worst, for a tool meant to change what people do, the justification cannot be "
    "trusted: models cite issue keys that look exactly like real ones and are not [1].",
    "intro: shortcut")

sub("This paper describes a system, TeamSync AI, built on the inversion of that arrangement. "
    "Here the risk is <em>computed</em>. Nothing infers it. Project state (people, tasks, "
    "milestones, dependencies, comments) is compiled into a typed knowledge graph, and each of "
    "six risk categories is expressed as a property of that graph: the longest path through the "
    "dependency DAG, articulation points separating a person from a component, weighted degree "
    "over assignments, the ratio of commenting to assignment, and so on. These are ordinary "
    "graph computations [2], they take milliseconds, and they give the same answer twice.",
    "This paper describes TeamSync AI, built on the inversion of that arrangement. Here the risk "
    "is <em>computed</em>. Nothing infers it. Project state (people, tasks, milestones, "
    "dependencies, comments) becomes a typed knowledge graph, and each of six risk categories is "
    "a property of it: the longest path through the dependency DAG, articulation points "
    "separating a person from a component, weighted degree over assignments, the ratio of "
    "commenting to assignment. These are ordinary graph computations [2]. They take "
    "milliseconds, and they give the same answer twice.",
    "intro: inversion")

sub("The model&rsquo;s task is to explain the finding in a sentence a manager can read, citing "
    "node identifiers. Afterwards, every identifier it cited is looked up in the subgraph it was "
    "given, and anything that fails to resolve is deleted before the output is shown. The model "
    "never sees the project, never computes the score, and cannot invent an issue key that "
    "survives to the user interface.",
    "Its task is to explain the finding in a sentence a manager can read, citing node "
    "identifiers. Every identifier it cites is then looked up in the subgraph it was given, and "
    "anything unresolvable is deleted before the output is shown. The model never sees the "
    "project, never computes the score, and cannot invent an issue key that reaches the "
    "interface.",
    "intro: confinement")

# ---- II-A
sub("Predicting whether agile work will land on time is an old problem with a sobering "
    "literature. J&oslash;rgensen and Shepperd&rsquo;s review of cost-estimation research [3] "
    "and Hall et al.&rsquo;s review of fault-prediction performance [4] both report that "
    "reported accuracy depends heavily on evaluation design, and that results rarely transfer "
    "between contexts. Deep learning has been applied directly to story-point estimation, most "
    "prominently by Choetkiertikul et al. [5], whose Deep-SE model learns effort from issue "
    "text. A subsequent replication by Tawosi et al. [6] found that Deep-SE beat a median "
    "baseline with statistical significance in only a small minority of cases. We read that pair "
    "of papers as a caution rather than a discouragement, and it is one reason the present work "
    "reports a learned model that lost on held-out data instead of quietly dropping it. The "
    "question has not gone quiet: a 2026 evaluation across sixteen projects reports that "
    "language models given no training examples at all estimate story points better than "
    "supervised models fitted to 80% of the data [7], which is a further reason to be careful "
    "about what a tuned number on one project set is worth on another.",
    "Predicting whether agile work lands on time is an old problem with a sobering literature. "
    "Reviews by J&oslash;rgensen and Shepperd [3] and Hall et al. [4] both report that accuracy "
    "depends heavily on evaluation design and rarely transfers between contexts. Deep learning "
    "has been applied to story-point estimation, most prominently by Choetkiertikul et al. [5]; "
    "a replication by Tawosi et al. [6] found their model beat a median baseline significantly "
    "in only a small minority of cases. We read that pair as a caution, and it is one reason we "
    "report a learned model that lost on held-out data instead of dropping it quietly. A 2026 "
    "evaluation across sixteen projects adds that models given no training examples estimate "
    "story points better than supervised models fitted to 80% of the data [7], which is further "
    "reason to distrust what a tuned number is worth on another project set.",
    "II-A")

# ---- II-C
sub("Post-hoc explanation methods such as LIME [18] and SHAP [19], surveyed broadly by Guidotti "
    "et al. [20] and Arrieta et al. [21], answer the question <em>why did this model predict "
    "that?</em>, and Jiarpakdee et al. [22] apply them specifically to defect-prediction models "
    "in software engineering; a 2026 study extends the same idea to explaining the risk of "
    "individual code changes [23]. The same instinct recurs outside software engineering. "
    "Nalinipriya et al. [24] apply explainable models to spotting threats early in large "
    "networks, on the reasoning that a warning nobody can interpret is a warning nobody acts on. "
    "They are the right tools when a learned model has made the prediction. Here they are not "
    "applicable, and the reason is structural rather than a claim of superiority: a "
    "critical-path share or an articulation point has no hidden decision to reconstruct. The "
    "explanation is the computation. What remains to be explained is only the <em>prose</em>, "
    "and the risk there is fabrication rather than opacity. That is why the mechanism in Section "
    "V-E is a verifier and not an attribution method.",
    "Post-hoc methods such as LIME [18] and SHAP [19], surveyed by Guidotti et al. [20] and "
    "Arrieta et al. [21], answer <em>why did this model predict that?</em>; Jiarpakdee et al. "
    "[22] apply them to defect prediction, and a 2026 study to the risk of individual code "
    "changes [23]. The instinct recurs elsewhere: Nalinipriya et al. [24] use explainable models "
    "to spot threats early in large networks, reasoning that a warning nobody can interpret is a "
    "warning nobody acts on. These are the right tools when a learned model made the prediction. "
    "Here they do not apply, for a structural reason rather than any claim of superiority: a "
    "critical-path share has no hidden decision to reconstruct. The explanation is the "
    "computation. Only the <em>prose</em> remains to be explained, and its risk is fabrication, "
    "not opacity. Hence a verifier in Section V-E rather than an attribution method.",
    "II-C")

# ---- II-D
sub("Retrieval-augmented generation [25] conditions a model on retrieved passages so that its "
    "output has a documentary basis, and the surrounding literature on hallucination [1] "
    "establishes how often that basis is still embellished. Pan et al. [26] and Peng et al. [27] "
    "survey the broader union of language models and knowledge graphs, and the graph-structured "
    "retrieval built on it. That line of work has since had to confront the same failure mode "
    "from the other side: when the graph itself is imperfect, retrieval drifts and the generated "
    "text inherits the error [28]. The distinction here is one of direction and of timing: "
    "retrieval conditions generation <em>beforehand</em> on text, while the present system "
    "verifies generation <em>afterwards</em> against a computed, typed structure whose "
    "legitimate identifiers form a closed set. Conditioning makes fabrication less likely; "
    "closed-set verification makes it detectable. The two are complementary, and the second is "
    "what this paper measures.",
    "Retrieval-augmented generation [25] conditions a model on retrieved passages so its output "
    "has a documentary basis; the hallucination literature [1] records how often that basis is "
    "still embellished. Pan et al. [26] and Peng et al. [27] survey language models joined to "
    "knowledge graphs, a line that has met the same failure from the other side: an imperfect "
    "graph makes retrieval drift, and the text inherits the error [28]. The distinction here is "
    "direction and timing. Retrieval conditions generation <em>beforehand</em> on text; this "
    "system verifies it <em>afterwards</em> against a computed, typed structure whose legitimate "
    "identifiers form a closed set. Conditioning makes fabrication less likely; closed-set "
    "verification makes it detectable. The two are complementary, and the second is what this "
    "paper measures.",
    "II-D")

# ---- VI
sub("A risk aggregator consumes the six computed scores, and a recommendation agent turns the "
    "aggregate into prioritised actions. Two further agents, covering meeting transcripts and "
    "chat traffic, are specified but not implemented, for the plain reason that the product has "
    "no such data source; they are listed here because omitting them from a system diagram would "
    "overstate what was built.",
    "A risk aggregator consumes the six scores, and a recommendation agent turns the aggregate "
    "into prioritised actions. Two further agents, for meeting transcripts and chat traffic, are "
    "specified but not implemented: the product has no such data source. They are listed because "
    "omitting them would overstate what was built.",
    "VI agents")

sub("The uniformity is what makes the fallback honest. A caller cannot tell from the schema "
    "whether a model was involved, so no downstream code is written to depend on one, and the "
    "deterministic path is not a degraded mode bolted on afterwards. It is the reference "
    "implementation, and the configuration in which this paper&rsquo;s results were produced.",
    "That uniformity is what makes the fallback honest. A caller cannot tell from the schema "
    "whether a model was involved, so no downstream code depends on one. The deterministic path "
    "is not a degraded mode bolted on afterwards; it is the reference implementation, and the "
    "configuration these results come from.",
    "VI schema")

# ---- VII-B
sub("Every issue in an archival dataset has long since been resolved. Using current status "
    "would leak the future into the prediction and produce excellent, meaningless numbers. Each "
    "sprint is therefore rebuilt as it stood at the moment of evaluation: only issues created by "
    "then exist, only issues resolved by then are complete, and the system clock is set to that "
    "moment. For the sprint-end evaluation the clock is the deadline plus one day; for the "
    "mid-sprint evaluation it is the 50% and 75% points of the sprint&rsquo;s duration.",
    "Every issue in an archival dataset has long since been resolved, so using current status "
    "would leak the future and produce excellent, meaningless numbers. Each sprint is rebuilt as "
    "it stood at the moment of evaluation: only issues created by then exist, only those "
    "resolved by then are complete, and the clock is set to that moment. At sprint end the clock "
    "is the deadline plus one day; mid-sprint it is the 50% and 75% points of the duration.",
    "VII-B")

# ---- VIII-A, second paragraph
sub("The shape of the curve matters more than the ratio. The graph-grounded series is "
    "effectively flat after a few hundred tasks, because the witness is bounded; the naive "
    "series is linear, because the board is the prompt. The practical consequence is a change in "
    "what the system can afford to do. Deterministic analysis of a 203-task project takes 10.96 "
    "ms at the median and 13.42 ms at p95 over 50 runs, which is fast enough to run on every "
    "board change, synchronously, without a job queue. Analysis that costs 190,000 tokens is "
    "something a team runs nightly, which returns us to detecting risk after it has happened.",
    "The shape of the curve matters more than the ratio. The graph-grounded series flattens "
    "after a few hundred tasks because the witness is bounded; the naive series is linear "
    "because the board is the prompt. That changes what the system can afford. Deterministic "
    "analysis of a 203-task project takes 10.96 ms at the median and 13.42 ms at p95 over 50 "
    "runs, fast enough to run on every board change, synchronously, with no queue. Analysis "
    "costing 190,000 tokens is something a team runs nightly, which returns us to detecting risk "
    "after it has happened.",
    "VIII-A")

# ---- VIII-B, second paragraph
sub("This number should be read for what it is. Deterministic threshold code evaluated on "
    "inputs constructed to be unambiguous is <em>expected</em> to score perfectly; the result is "
    "equivalent to a passing test suite, and it is evidence of correct implementation, not of "
    "generalisation. The genuinely falsifiable check in this family is the boundary sweep, which "
    "asks whether each detector changes its verdict exactly where its documentation says it "
    "does. The overdue-ratio detector flips exactly at 0.10 and the silent-member detector "
    "exactly at 0.30; the workload detector&rsquo;s flip is bracketed between 1.429 and 1.522 "
    "around its documented 1.50, which is the resolution the sweep can establish.",
    "This number should be read for what it is. Deterministic threshold code on unambiguous "
    "inputs is <em>expected</em> to score perfectly. The result is equivalent to a passing test "
    "suite: evidence of correct implementation, not of generalisation. The falsifiable check "
    "here is the boundary sweep, which asks whether each detector flips exactly where its "
    "documentation says. Overdue ratio flips at 0.10 and silent member at 0.30; the workload "
    "flip is bracketed between 1.429 and 1.522 around its documented 1.50, the resolution the "
    "sweep can establish.",
    "VIII-B")

SRC.write_text(s, encoding="utf-8")
for label, delta in log:
    print(f"  -{delta:3d} words  {label}")
print(f"total: -{sum(d for _, d in log)} words across {len(log)} paragraphs")
