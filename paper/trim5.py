"""Closing pass: the last 79pt."""
from __future__ import annotations
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "ieee_paper.html"
s = SRC.read_text(encoding="utf-8")
log = []

def sub(old, new, label):
    global s
    pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
    n = len(pat.findall(s))
    if n != 1:
        print(f"  MISS ({n}) {label}"); return
    s = pat.sub(lambda m: new, s, count=1)
    log.append((label, len(old.split()) - len(new.split())))

sub("The split between the two services is deliberate and is not merely about deployment "
    "convenience. The application tier is where data lives and where authorisation is enforced; "
    "the analysis tier is stateless, receives a project snapshot over an internal interface, and "
    "returns findings. A snapshot in, findings out means the analysis service can be run, tested "
    "and reasoned about without a database, and it is why the entire evaluation harness in "
    "Section VII can replay 987 historical sprints through exactly the code path the product "
    "uses.",
    "The split is deliberate, not merely about deployment. The application tier is where data "
    "lives and authorisation is enforced; the analysis tier is stateless, takes a project "
    "snapshot over an internal interface and returns findings. Snapshot in, findings out means it "
    "can be run and tested without a database, which is why the harness in Section VII replays "
    "987 historical sprints through exactly the code path the product uses.",
    "IV para 2")

sub("Projects, not sprints, are the unit of splitting. Sprints inside one project share a team, "
    "a codebase and a set of Jira conventions; splitting by sprint would let those conventions "
    "appear on both sides of the boundary. Nine projects and 717 sprints form the tuning set; 22 "
    "projects and 270 sprints (48.9% positive) form the held-out set, which was evaluated exactly "
    "once. Checkpoints, predictor and severity cut-offs were all fixed before the held-out "
    "projects were touched.",
    "Projects, not sprints, are the unit of splitting. Sprints inside one project share a team, a "
    "codebase and a set of Jira conventions, which splitting by sprint would let appear on both "
    "sides of the boundary. Nine projects and 717 sprints form the tuning set; 22 projects and "
    "270 sprints (48.9% positive) the held-out set, evaluated exactly once. Checkpoints, "
    "predictor and cut-offs were fixed before those projects were touched.",
    "VII-C")

sub("Interpretable agent architectures [16], [17] and explainable early-warning models [24] have "
    "been pursued separately. Neither line represents the project itself as a typed graph whose "
    "dependency, ownership and communication edges become the evidence a verdict cites. That is "
    "the gap this paper addresses. No comparator we are aware of combines all five of:",
    "Interpretable agent architectures [16], [17] and explainable early-warning models [24] have "
    "been pursued separately. Neither represents the project itself as a typed graph whose "
    "dependency, ownership and communication edges become the evidence a verdict cites. That is "
    "the gap addressed here. No comparator we know of combines all five of:",
    "II-E")

sub("We also report what did not work: a tuned logistic model reached cross-validated F1 0.816 "
    "and fell to 0.593 on unseen projects, where the zero-parameter graph rule scored 0.712, and "
    "the mid-sprint projection ranks no better than counting unfinished work.",
    "We also report what did not work: a tuned logistic model reached cross-validated F1 0.816 "
    "and fell to 0.593 on unseen projects, where a zero-parameter graph rule scored 0.712.",
    "abstract tail")

SRC.write_text(s, encoding="utf-8")
for label, delta in log:
    print(f"  -{delta:3d} words  {label}")
print(f"total: -{sum(d for _, d in log)} words")
