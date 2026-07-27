# Artifact self-assessment against external standards

Written 2026-07-26. **Orientation for two pending decisions (0g and §6.2 Q3),
not a decision.** Nothing in the README was changed to produce it.

Three external standards, all `[fetched]` and verified rather than paraphrased:

- **ACM Artifact Review and Badging** — the badge vocabulary.
- **"Reasonable efforts"**, SIGSOFT Empirical Standards, quoted in
  arXiv:2508.15503 verbatim: *"We must neither accept research absent
  reasonable efforts to improve reproducibility, nor reject research for
  failing to obtain an impossible goal."* The reviewer's operational question:
  *"have the authors done what they could to minimize limitations?"*
- **Artifact durability**, arXiv:2512.00651, *Large Language Models for
  Software Engineering: A Reproducibility Crisis* (640 papers, 2017–2025):
  *"Over 40% of 'functional' artifacts in the corpus from 2024–2025 fail within
  months due to drifting dependencies, unpinned versions, incomplete
  environments, or unclear licensing."*

One finding from the third source reframes the first and is worth stating up
front: **badges "evaluate momentary functionality — checking whether artifacts
worked during review, but not whether they are engineered for long-term
reproducibility."** So a badge self-classification is a snapshot, and §3 below
is the part with a shelf life.

---

## 1. Self-classification against the badge vocabulary

The badge criteria, verbatim where quoted:

| badge | requirement |
|---|---|
| **Available** | "made permanently available for retrieval" |
| **Functional** | "documented, consistent, complete, exercisable, and include appropriate evidence of verification and validation" |
| **Reusable** | Functional, plus "very carefully documented and well-structured to the extent that reuse and repurposing are facilitated" |

These are four genuinely different cases and collapsing them would be the main
error available here.

### (a) The correctness properties — the strongest case
Cross-tool dedup, engine-lineage guard, degenerate-fingerprint detection,
path-root disclosure, suffix linkage, hierarchy-aware CWE resolution, gated
size-correlation disclosure.

- **Available: YES.** Public repo.
- **Functional: YES, on all five criteria.** *Documented* — README + VALIDATION
  + inline rationale. *Consistent* — these are exactly the claims the README
  makes. *Complete* — `src/` and the fixtures ship together. *Exercisable* —
  **the 112-check harness runs from a clean clone with no corpora and no
  network**, which is the criterion most artifacts fail. *Evidence of V&V* — the
  harness is that evidence, and each check names the defect it guards.
- **Reusable: PARTIAL.** The code is structured and heavily commented, but
  "reuse and repurposing" for an analysis artifact usually means someone else
  running it on their data, which works, versus extending it, which is
  undocumented. I would not claim this badge.

**Assessment: Available + Functional. Not Reusable.**

### (b) The 1.5x finding — available but not exercisable as delivered
- **Available: YES, but indirectly.** `run_0j.py` is committed; the Lipp corpus
  is not, and does not need to be — it has a DOI (10.5281/zenodo.6515687) and
  is itself permanently retrievable, with our fetch manifest and checksums.
- **Functional: NO.** It fails *exercisable*: the script does not run from a
  clean clone. A recipient must rebuild the corpus first. Everything else
  (documented, consistent, complete, V&V) is satisfied.
- **Reusable: NO.**

**Assessment: Available. Functional only after a rebuild step that is documented
but not automated.** This is the honest gap between "the numbers are checkable"
and "the numbers are checkable *by you, today*".

### (c) The ranking — UNBADGEABLE, and for a reason worth stating precisely
The ranking claim is not weakly supported; **it was never established.** Badges
attach to artifacts supporting a result, and here there is no positive result to
support.

But the distinction that matters: **the NULL is badgeable even though the CLAIM
is not.** `manualup.py`, `effort_aware.py`, `run_0i.py`, `size_confound.py` are
the artifacts behind a *finding* — that consensus ranking does not beat a
size-matched control — and that finding is as real as a positive one. They sit
in case (b): Available, exercisable after a rebuild.

**Assessment: the ranking claim is unbadgeable because it does not exist. The
null result supporting its absence is Available, and Functional after rebuild.**

### (d) The 0f provenance measurement — strongest methodology, weakest durability
An instructive inversion, and the reason to keep these four cases separate.

- **Available: NO, and this is the real problem.** The population is fetched
  **live** from `semgrep.dev` at run time. The registry is not versioned, not
  archived by us, and **has already been observed to drift** — the Struts re-run
  found an `owasp: A01:2025` tag absent from the original capture. A rerun next
  year measures a different registry and silently reports a different number
  under the same name. The FindSecBugs jar it compares against lives in a temp
  directory and is not committed either.
- **Functional: PARTIAL.** The script runs and is documented, but it is not
  *consistent* over time in the sense the badge intends — it cannot regenerate
  the numbers in VALIDATION.md, only new ones.

**Assessment: not Available, and only momentarily Functional.** The
pre-registration, the multi-signal design and the bias analysis are the most
carefully constructed work in the project, attached to the least durable
artifact. That is exactly the failure mode arXiv:2512.00651 describes.

---

## 2. "Reasonable efforts" applied to 0g

The standard deliberately does not ask whether the ranking was proven. It asks
whether reasonable effort was made and the limitations honestly disclosed:
*"have the authors done what they could to minimize limitations?"*

### Was the effort reasonable? — YES, and the record is specific
Against the ranking claim the project has run: ManualUp and ManualDown baselines
from the defect-prediction literature; effort-aware PofB@20%**LOC** rather than
per-unit; size-matched random controls; four *pre-registered* formulations (0i,
including the one the literature predicted would fail, which did); a single-tool
comparator with a computed power analysis rather than an assumed one (0d); and
size-correlation diagnostics at two granularities. Five claims were retired as a
result, three of them the README's own headline numbers.

That is more adversarial self-testing than the standard requires. The failures
were found *here*, not by a reviewer.

### Was it accurately disclosed? — YES
The README states the ranking "has **not** been shown to beat a size-matched
baseline on the corpus where it was properly tested", gives the confound
(Spearman +0.63), and volunteers the most damaging single fact — that ranking
files by size alone scores *higher* on ROC-AUC than the consensus signal. It
also says earlier performance figures "did not survive controlled baselines and
have been removed."

### So: **the current README meets the bar.** One thing would strengthen it.
The disclosure says the ranking is **unproven**. The evidence in §6.2 supports a
stronger and more useful statement: it may be **unprovable with available
tools** — methodological diversity and co-location pull against each other, this
has now failed three times in three configurations for three different proximate
reasons, and no purchasable tool resolves it.

That distinction is precisely what "reasonable efforts" protects. *Unproven*
invites a reader to wait for the next version. *Unprovable with these tools* is
the honest state and tells them not to. Under the standard, declining to prove
an impossible goal is explicitly not a defect — but only if you say the goal may
be impossible.

**Recommendation (yours to take or not): 0g does not need a re-headline on an
effort-aware metric. What it needs is one sentence separating "we did not prove
this" from "this may not be provable with tools that exist." That is a smaller
change than 0g contemplates and it is the one the standard actually asks for.**

This overlaps §6.2 Q3 and I have not acted on either.

---

## 3. Durability of `analysis/` — measured, and the verdict is negative

arXiv:2512.00651's failure modes are drifting dependencies, unpinned versions,
incomplete environments, unclear licensing. **We have three of the four.**

### Measured against the tree
```
scripts total                                        21
hard-code an absolute path                           12   (57%)
  ... to the session scratchpad (a TEMP dir)           5   <- gone on reboot
  ... to /Users/caitlinfuller/audit/src                7
require a corpus that is not committed               19   (90%)
run from a clean clone with no corpora                0   (0%)
```
**Zero of 21 scripts would run for a recipient without both editing paths and
rebuilding corpora.**

VERIFIED BY ACTUALLY DOING IT, not by inspection: `git clone` to a fresh
directory, then run. The 112-check harness and the render harness both PASS with
no corpora and no network — confirming case (a). Every `analysis/` script tried
FAILS there — confirming this verdict. The claim in (a) and the verdict here are
the same experiment read from both ends. Five reference a directory that no longer exists on *this*
machine after a reboot, let alone anyone else's.

### Unpinned sources, in order of how fast they move
| source | pinned? | risk |
|---|---|---|
| semgrep registry (live fetch) | **NO** | **already observed drifting** |
| `github.com/apache/struts` @ `main` | **NO** | branch head moves |
| `github.com/OWASP-Benchmark/BenchmarkJava` @ `master` | **NO** | branch head moves |
| FindSecBugs jar | not committed | in a temp dir |
| `zlib.net/zlib-1.3.1.tar.gz` | yes | fine |
| Lipp artifact (Zenodo DOI) | yes | fine — a DOI is the right pattern |

### What we do have, and why it is not enough
sha256 for all 23 derived inputs, exact tool versions read from SARIF, and fetch
commands. That is better than most artifacts and it is genuinely useful — but
**checksums let you verify a rebuild, they do not let you perform one** once the
upstream has moved. A hash of a file you can no longer obtain documents a
failure rather than preventing it.

### Honest verdict
**`analysis/` would not survive being handed to someone else today.** It is
*Available* in the sense that it exists publicly, and it is a good working
record for a session that still has the scratchpad. As a third-party artifact it
is non-functional.

### Minimum fix — SCOPED, NOT BUILT, in priority order
1. **Snapshot the semgrep registry** (~1 MB for nine packs) and the FindSecBugs
   `messages.xml` extract (~100 KB) into `analysis/data/`, with the live-fetch
   path kept behind a flag. **Highest priority because this source is already
   drifting**, and it is the only fix that makes 0f's numbers regenerable at
   all. Small, self-contained, and licensing needs a check (semgrep rules carry
   the Semgrep Rules License; the FSB extract is LGPL) — the "unclear licensing"
   failure mode is real and applies here.
2. **One corpus-root resolver.** A single `AUDIT_CORPUS_ROOT` env var plus a
   3-line helper, replacing 12 hard-coded paths. Unblocks every script at once
   and is the cheapest item by ratio.
3. **Pin the two moving corpora to commit SHAs.** GitHub commit SHAs are
   permanent and retrievable; branch names are not. Record them next to the
   existing checksums.
4. **A `verify` entry point** that runs everything runnable without corpora and
   reports what it skipped and why, so a recipient learns in 30 seconds what
   works rather than by failure.

Items 1–3 are what move `analysis/` from *Available* to *Functional*. Item 4 is
what stops a future reader mistaking "I could not run it" for "it is broken."

**Not built. This is a scope, per instruction.**
