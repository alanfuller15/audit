# Extending `analysis/` — the conventions a new script must follow

One page. This closes the gap between *Functional* (it runs) and *Reusable*
(someone else can extend it) — the distinction in
`docs/ARTIFACT_SELF_ASSESSMENT.md` §1.

---

## 1. Resolving inputs — never hard-code a path

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus

_corpus.add_src()                      # puts the repo's src/ on sys.path
B = _corpus.corpus("lipp", "dataset")  # resolves under $AUDIT_CORPUS_ROOT
HERE = _corpus.corpus_root()           # the root itself
```

Two rules, both learned the expensive way:

- **No absolute paths.** 12 of 21 scripts once carried one, five into a temp
  scratchpad. Zero scripts ran from a clean clone.
- **Relative-to-`__file__` is not a fix.** Nine scripts resolved corpora next to
  themselves, which fails for a recipient in exactly the same way. If it is a
  corpus, it comes from `_corpus`.

A script that needs a corpus and cannot find one should exit via
`_corpus.corpus_root()`, which prints what is missing and where the fetch
commands are. Do not fail with a stack trace on a stale path.

## 2. Committed data goes in `analysis/data/`, and needs a licence check first

Before committing any upstream artifact, check whether you may redistribute it.
The answer has already differed between two sources in this project:

- **FindSecBugs** is LGPL-3.0 → redistribution permitted → committed extract
  **and** a Software Heritage SWHID.
- **semgrep registry rules** are not redistributable — *"This license does not
  allow you to distribute the rules"* → **SWHID only**, no snapshot.

Where you cannot copy, preserve by reference: nominate the upstream at
`archive.softwareheritage.org/save/` (anyone may submit a public repo) and
record the SWHID. Pin corpora by **commit SHA and SWHID** — a SHA alone is not
enough, because history rewriting can remove a commit from a live repository.

If you commit an extract, make it **byte-faithful** to what the code previously
read, and verify that by running both paths and comparing. An extract that
"tidies" whitespace is a different input.

## 3. Provenance tiers — tag every claim

From the project charter, strongest to weakest:

| tier | means |
|---|---|
| `[fetched]` | validated against a fetched published source |
| `[corroborated]` | multiple independent sources agree |
| `[standard-checked]` | validated against a fetched published standard |
| `[externally-grounded]` | a non-Claude engine or dataset anchors it |
| `[externally-verified]` | an external judge on real data confirms the implementation |
| `[self-tested]` | sandbox pass — weakest, this is us grading us |

**Searching moves DESIGN tiers. Only an external judge on real data moves
IMPLEMENTATION tiers.** Most analysis scripts are `[self-tested]` analysis over
`[externally-grounded]` inputs; say both, not just the flattering half.

## 4. When your number lands in `VALIDATION.md`

Record all of these. Each exists because omitting it cost something.

1. **The script and its output path.** A number with no named script is not
   reproducible, and we have had one (the original 1.5x was run inline and lost).
2. **The denominator, in the same breath as the number.** One finding here
   legitimately produced five correct percentages — 8.3% of rules loaded, 45.5%
   of rules fired, 36.8% of findings, 30.4% of rule pairs, 22.6% of locations.
   All correct, none interchangeable. A bare percentage is not a result.
3. **Effect size with an interval**, not only a p-value. And check what your test
   holds fixed: a resampling p-value that conditions on one arm is not a test of
   the comparison — ours read `p<0.0001` where an honest test gives ~0.03–0.08.
4. **The honest bound.** Corpus type, tool pair, language, sample size. State
   what the result does *not* establish.
5. **Deviations from plan, labelled as deviations.** If the work was
   pre-registered, say what changed and why. Additions discovered mid-analysis
   are legitimate; presenting them as pre-planned is not.

**Pre-register anything that is a decision rather than a measurement** — fix the
thresholds and the decision rule in a committed file *before* computing, so the
result cannot select its own criterion.

## 5. Reading tool output

- **Capture native format alongside SARIF, always.** SARIF v2.1.0 Appendix D
  permits a converter to "simply omit" what has no SARIF equivalent. Rule
  provenance is present in semgrep's JSON and appears **0 times** in its SARIF.
- **Any absence derived from SARIF is a claim about SARIF** until checked against
  native output. A zero from an interchange format is never clearance.
- **Watch for circular proxies.** A size proxy built from `max(reported line)`
  rises with the number of findings, hence with tool count — it manufactures the
  correlation it is meant to detect. Prefer a real measurement or report NOT
  APPLICABLE.

## 6. Do not change an instrument to fix a result

The scripts in `scripts/` produced the numbers recorded in `VALIDATION.md`.
Changing how one computes changes what its recorded number means.

- Path resolution, and adapting to a renamed `src/` field: **fine.**
- Changing a threshold, a metric, a unit, or a population: **that is a new
  measurement.** Give it a new name and record it as one.

Where a `src/` field has been renamed, pick the replacement by asking **what the
script reports**, not by applying one answer uniformly. Worked example:
`cross_tool_merges` was split into three fields with different units, and both
`merge_audit.py` and `pairwise.py` needed `cross_tool_merged_findings` — but for
independent reasons. `merge_audit.py` audits the findings carrying `n_tools>1`,
so its headline must count the same population it inspects; `pairwise.py` prints
the count beside an `n_tools` distribution, and findings and edges diverge once
three tools are involved (one finding, three edges). Getting this wrong once made
"351" look like a shortfall against "427".

## 7. Before you commit

```sh
python3 examples/fixtures/verify_cross_tool_key.py   # 112 checks, no corpora needed
python3 examples/fixtures/verify_dedup_render.py
```
If you touched `src/`, add a regression check naming the defect it guards. If
you found a stale claim in `HANDOFF.md` or `VALIDATION.md`, **correct it in the
same commit as the discovery** — deferring is how three headers drifted into
describing the project as more broken than it was.
