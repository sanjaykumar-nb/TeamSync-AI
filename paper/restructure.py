"""One-off restructure of paper/ieee_paper.html.

Four changes, applied together because they interlock:

  1. A new Section III states the claims the paper is built on, so the novelty
     is the spine of the argument rather than something a reader has to
     assemble from the results. Everything after it shifts by one numeral, and
     every cross-reference moves with it.
  2. Fig. 4 goes. Eleven of its twelve bars sat at 1.00, so it took a quarter
     of a page to say what one sentence says: five categories tie, coordination
     does not. The numbers stay in the text and in the new Table.
  3. Recent work is cited where it belongs — in particular two 2026 papers that
     measure how often generated citations do not survive checking, which is
     the premise the grounding verifier exists to address.
  4. Fig. 1's caption is rewritten for the three-band diagram.

Run once:  python paper/restructure.py
"""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "ieee_paper.html"
s = SRC.read_text(encoding="utf-8")


def sub1(old: str, new: str, what: str) -> None:
    """Match on words, not on where the source happens to wrap its lines."""
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
    n = len(pat.findall(s))
    assert n == 1, f"{what}: expected 1 occurrence, found {n}"
    s = pat.sub(lambda m: new, s, count=1)


# ---------------------------------------------------------------- 1. renumber
# placeholders first, so a replacement is never re-matched
SECTION_SHIFT = {
    "X": "XI", "IX": "X", "VIII": "IX", "VII": "VIII",
    "VI": "VII", "V": "VI", "IV": "V", "III": "IV",
}
for old, new in SECTION_SHIFT.items():
    s = s.replace(f"<h2>{old}.&ensp;", f"<h2>@@{new}@@.&ensp;")
    s = re.sub(rf"\bSection {old}\b", f"Section @@{new}@@", s)
s = s.replace("Sections III&ndash;IV", "Sections @@IV@@&ndash;@@V@@")
s = re.sub(r"@@([IVX]+)@@", r"\1", s)

for old, new in [("Table IV", "Table V"), ("Table III", "Table IV"),
                 ("Table II", "Table III"), ("Table I", "Table II")]:
    s = s.replace(old, f"@@{new}@@")
s = re.sub(r"@@Table ([IVX]+)@@", r"Table \1", s)

# ---------------------------------------------------------------- 2. claims
CLAIMS = """<h2>III.&ensp;What Is Claimed, and How It Is Tested</h2>

<p class="first">The architecture in Section IV is not interesting by itself. Plenty of
systems put a graph next to a language model. The argument of this paper is narrower and
falsifiable: that <em>this particular division of labour</em>&mdash;compute the risk, then let
the model do nothing but describe one already-computed finding&mdash;buys four properties the
ordinary arrangement cannot, and costs nothing measurable in return. This section states each
property in the form in which it could be shown false, names the mechanism that produces it,
and points at the measurement that tests it. Table I collects them.</p>

<h3>A. Risk is a graph invariant, not a model&rsquo;s opinion</h3>

<p class="first">The usual pattern gives a language model the project and asks what is wrong.
Here the question is never asked. Each of six coordination risks is defined as a property of a
typed graph&mdash;the longest path through the dependency DAG, the articulation points
separating a person from a component, weighted degree over assignments, the ratio of
commenting to assignment&mdash;and computed by an ordinary graph algorithm with no fitted
parameter. The model is handed the answer, not the question.</p>

<p>This is the claim everything else rests on, and it is the one most easily falsified: if the
computed verdict disagreed with what a careful reader of the same data would conclude, nothing
downstream would matter. It is tested twice, from opposite directions&mdash;against synthetic
scenarios whose ground truth holds by construction, and against 987 real sprints where the
outcome is known.</p>

<h3>B. Prompt cost follows the number of anomalies, not the size of the project</h3>

<p class="first">Because the model only ever sees a witness subgraph around one anomaly, and
that subgraph is bounded by construction&mdash;one hop, at most eight neighbours per seed, at
most sixty nodes&mdash;the prompt stops tracking the board. The falsifiable form is a growth
rate: if prompt size grew with project size, the claim fails. It does not. Across a project
grown 154&times;, the prompt grows 1.47&times;.</p>

<p>The bound is less obvious than it looks, and we had it wrong at first. Capping the hop
count alone is not enough, because one high-degree node&mdash;a release milestone touching four
hundred tasks&mdash;drags the project back into the prompt through a single hop. The
per-seed cap is what makes the bound hold, and Section V-C reports the measurement that
exposed it.</p>

<h3>C. Fabricated evidence becomes decidable rather than unlikely</h3>

<p class="first">Grounding a model in retrieved text makes invention less likely; it does not
make it checkable. Recent measurements are blunt about the residual: across frontier deep
research agents, link validity stays above 94% while factual accuracy of the attributions
falls between 39% and 77% [27], and the tools built to catch bad citations are themselves
limited by metadata and coverage gaps [28].</p>

<p>The mechanism here sidesteps that problem rather than improving on it. Because the model is
shown a bounded subgraph, the set of identifiers it is <em>entitled</em> to cite is finite and
known before generation. Checking a citation is therefore a membership test against a closed
set, not a judgement about plausibility&mdash;which is why the result can be stated as a
guarantee instead of a rate. The falsifiable form: inject fabricated references and see
whether any survives.</p>

<h3>D. The inversion costs nothing in detection quality</h3>

<p class="first">A reader should suspect that confining the model this tightly must cost
accuracy somewhere. The claim is that it does not, and it is tested by running both
architectures over identical scenarios against identical ground truth, and by checking whether
the model&rsquo;s narrated severity agrees with the computed one on the same input. If the
narration quietly disagreed with the computation, the system would be deciding twice and
reporting once.</p>

<h3>E. A reported failure: added complexity did not survive unseen projects</h3>

<p class="first">The fifth finding is not a claim in our favour and is reported because it
bears directly on the four above. Three attempts to improve on the zero-parameter rule&mdash;a
threshold sweep, individualised due dates, and a tuned logistic model&mdash;failed, and the
third failed in the most instructive way: cross-validated F1 0.816 collapsed to 0.593 on
projects the model had not seen, where the rule with nothing to fit scored 0.712. A paired
test cannot separate the two. We do not claim the rule predicts better. We claim the tuned
advantage did not cross a project boundary, and that when two predictors cannot be separated,
the one that arrives with its evidence attached is the better engineering choice.</p>

<div class="tablewrap">
  <p class="tcap">Table I<br><span class="n">The claims, the mechanism behind each, and where each is tested</span></p>
  <table>
    <thead>
      <tr><th>Claim</th><th>Mechanism</th><th>Result</th><th class="c">&sect;</th></tr>
    </thead>
    <tbody>
      <tr><td>Risk is computed</td><td>graph invariants</td><td>F1 1.00 synth.</td><td class="c">VIII-B</td></tr>
      <tr><td>Bounded prompt</td><td>witness subgraph</td><td>1.47&times; vs 154&times;</td><td class="c">VIII-A</td></tr>
      <tr><td>Evidence decidable</td><td>closed-set check</td><td>200/200 stripped</td><td class="c">VIII-C</td></tr>
      <tr><td>Nothing lost</td><td>narration only</td><td>F1 1.000; &kappa; 0.95</td><td class="c">VIII-G, H</td></tr>
      <tr><td>Complexity failed</td><td>held-out split</td><td>0.816 &rarr; 0.593</td><td class="c">VIII-F</td></tr>
    </tbody>
  </table>
</div>

"""
sub1("<h2>IV.&ensp;System Architecture</h2>", CLAIMS + "<h2>IV.&ensp;System Architecture</h2>",
     "insert the claims section")

# ---------------------------------------------------------------- 3. Fig. 4 out
fig4 = re.search(r'<figure class="wide">\s*<img src="[^"]*fig4_ablation.*?</figure>\r?\n', s, re.S)
assert fig4, "Fig. 4 block not found"
s = s.replace(fig4.group(0), "")

sub1(
    "full-dataset prompting scores 0.947, with per-category results\nidentical on five of six (Fig. 4). The entire gap is coordination risk, where the naive path\nreaches F1 0.75 at precision 0.60.",
    "full-dataset prompting scores 0.947. The per-category results are identical on five of the "
    "six&mdash;dependency, knowledge, workload, delay and silent member all score 1.000 under both "
    "architectures&mdash;so the entire difference is coordination risk, where the naive path reaches "
    "F1 0.75 at precision 0.60. Coordination is the category that depends on the shape of the "
    "collaboration graph rather than on any single task&rsquo;s attributes, which is the one place a "
    "reader of the serialised board has to infer what the graph states outright.",
    "fold Fig. 4 into prose")

# ---------------------------------------------------------------- 4. new citations
sub1("most\nprominently by Choetkiertikul et al. [18], whose Deep-SE model learns effort from issue text.",
     "most\nprominently by Choetkiertikul et al. [18], whose Deep-SE model learns effort from issue text.",
     "anchor check")
sub1(
    "a learned model that lost on held-out data instead of quietly\ndropping it.</p>",
    "a learned model that lost on held-out data instead of quietly\ndropping it. The question has not gone quiet: a 2026 evaluation across sixteen projects reports "
    "that language models given no training examples at all estimate story points better than "
    "supervised models fitted to 80% of the data [29], which is a further reason to be careful about "
    "what a tuned number on one project set is worth on another.</p>",
    "cite 2026 story-point work")

sub1(
    "and AgentBench [6] and the survey of Wang et\nal. [21] map the resulting design space.",
    "and AgentBench [6] and the surveys of Wang et\nal. [21] and He et al. [30] map the resulting design space, the latter specifically for software "
    "engineering. A 2026 experience report building such systems with current frameworks finds the "
    "basic components well covered and the operational ones&mdash;agent telemetry above all&mdash;still "
    "missing [31], which matches our own experience: the hardest part was not making agents talk but "
    "being able to tell, afterwards, which path produced a given output.",
    "cite TOSEM survey and 2026 experience report")

sub1(
    "and Jiarpakdee et al. [10] apply them specifically to defect-prediction models in software engineering.",
    "and Jiarpakdee et al. [10] apply them specifically to defect-prediction models in software engineering; a 2026 study extends the same idea to explaining the "
    "risk of individual code changes [32].",
    "cite 2026 code-change risk explanation")

sub1(
    "Pan et al. [24] survey the\nbroader union of language models and knowledge graphs.",
    "Pan et al. [24] and Peng et al. [33] survey the\nbroader union of language models and knowledge graphs, and the graph-structured retrieval built on "
    "it. That line of work has since had to confront the same failure mode from the other side: when "
    "the graph itself is imperfect, retrieval drifts and the generated text inherits the error [34].",
    "cite GraphRAG survey and robust-GraphRAG")

sub1(
    "This is a closed-set membership test, not a plausibility judgement, which is the whole\nreason it can be stated as a guarantee rather than a tendency.</p>",
    "This is a closed-set membership test, not a plausibility judgement, which is the whole\nreason it can be stated as a guarantee rather than a tendency &mdash; and it is worth noting that "
    "the alternative, checking citations after the fact against the open world, is measurably hard: "
    "current detection tools are limited by reference extraction, metadata gaps and inconsistent "
    "verification [28].</p>",
    "cite citation-checking limits in the verifier subsection")

REFS = """<li>H. Onweller, E. Lumer, A. Huber, P. Ramchandani, V. K. Subbiah, and C. Feld, &ldquo;Cited but not verified: Parsing and evaluating source attribution in LLM deep research agents,&rdquo; 2026, arXiv:2605.06635.</li>
<li>F. Badalova and P. Mayr, &ldquo;Detecting hallucinated and suspicious citations: What current tools can and cannot do,&rdquo; 2026, arXiv:2607.22693.</li>
<li>P. P. Shetty, A. Balakrishnan, M. Xu, X. Xi, and Z. Yu, &ldquo;Story point estimation using large language models,&rdquo; 2026, arXiv:2603.06276.</li>
<li>J. He, C. Treude, and D. Lo, &ldquo;LLM-based multi-agent systems for software engineering: Literature review, vision and the road ahead,&rdquo; <em>ACM Trans. Softw. Eng. Methodol.</em>, vol. 34, no. 5, pp. 1&ndash;30, 2025, doi: 10.1145/3712003.</li>
<li>M. C. S. De Oliveira, M. O. Ibiyo, M. Gianrusso, C. Di Sipio, D. Di Ruscio, and P. T. Nguyen, &ldquo;Developing LLM-based multi-agent systems in software engineering: A mixed-method experience report,&rdquo; 2026, arXiv:2608.11965.</li>
<li>Y. Liu <em>et al.</em>, &ldquo;A preliminary study on explaining risk of code changes using LLM-based prediction models,&rdquo; 2026, arXiv:2607.02782.</li>
<li>B. Peng, Y. Zhu, Y. Liu, X. Bo, H. Shi, C. Hong, Y. Zhang, and S. Tang, &ldquo;Graph retrieval-augmented generation: A survey,&rdquo; <em>ACM Trans. Inf. Syst.</em>, 2025, doi: 10.1145/3777378.</li>
<li>Y. Ma, J. Xu, T. Wen, Q. Chen, J. Li, R. Wang, M. Li, S. Liang, and K. Qin, &ldquo;Toward robust GraphRAG: Mitigating retrieval drift and hallucination from imperfect knowledge graphs,&rdquo; 2026, arXiv:2603.14828.</li>
</ol>"""
sub1("</ol>", REFS, "append the new references")

# ---------------------------------------------------------------- 5. Fig. 1 caption
old_cap = re.search(r'<figcaption><span class="lbl">Fig\. 1\.</span>.*?</figcaption>', s, re.S)
assert old_cap, "Fig. 1 caption not found"
s = s.replace(old_cap.group(0), (
    '<figcaption><span class="lbl">Fig. 1.</span>&ensp;System architecture. Blocks are deployed '
    'subsystems; lines are interfaces between them; nothing here is a decision or a step in time. '
    'The analysis tier is drawn as three bands because that is where the claims of Section III '
    'live. Band 1 computes every number the product reports, with no model call and no fitted '
    'parameter. Band 2 runs the specialists and aggregates them, emitting one schema whichever '
    'path produced it. Band 3 is the only place a language model may be called, and the heavy '
    'connector marks the only artefact that reaches it: one finding and its witness subgraph. '
    'The risk scores travel to the application tier without entering band 3 at all (dashed), so '
    'a model that is absent, rate-limited or switched off changes the prose and not the numbers '
    '&mdash; which is the configuration under which every result in Section VIII was measured.'
    '</figcaption>'))

SRC.write_text(s, encoding="utf-8")
print("restructured")
