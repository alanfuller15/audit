# We measured tool agreement at the wrong unit for two sessions

### A negative result about consensus ranking, and a correction to a negative result we nearly published about consensus itself

*Written for someone deciding whether to attempt this. Not a confession and not
a changelog — a report of what did not work, so the next person can skip it or
attack it from a better angle.*

**Scope, stated once and meant: one tool, four scanners, two languages, three
corpora, one rule registry.** Nothing here establishes that multi-tool consensus
cannot work.

**AN EARLIER DRAFT OF THIS DOCUMENT WAS TITLED "methodologically diverse static
analyzers do not produce co-located agreement". THAT CLAIM IS FALSE**, and our
own records already said so when it was written. It is true at LINE level and
false at FUNCTION level: the same tool pairs that produce zero agreement when
matched line-to-line produce hundreds when matched function-to-function.
Correcting it is §1, and the correction is more useful than the claim was.

---

## Why this document exists

Null results are valued and almost never published. Springer Nature surveyed
**11,000+ researchers across 166 countries** `[fetched]`: **98%** recognise the
value of sharing null results, **53%** have generated them, and only about
**30%** have ever submitted them to a journal.

The cost is duplicated effort. Curry et al., *Ending publication bias*, PLoS
Biology 2025 `[fetched]`, verbatim: unpublished null studies "waste resources,
slow the pace of science" and lead "unwitting researchers [to] expend time and
money conducting similar experiments, not realizing that prior work has yielded
null results: time and money that could have been spent pursuing new and more
promising ideas." They note that "fewer than 2 in 100 articles on prognostic
markers or animal models of stroke report null findings."

That efficiency argument is the entire justification for this file. The premise
here — *different tools have different blind spots, so their agreement is
independent evidence* — is intuitive, widely assumed, and commercially
attractive. Someone will try it again. This is what happened when we did.

---

## 1. THE FINDING — the unit of measurement was the variable, not the tools

We ran three scanner pairings on real code and got zero or near-zero cross-tool
agreement each time. We attributed that to methodology: the premise wants tools
with different methods, the mechanism needs them to point at the same place, and
those seemed to pull against each other.

**That was wrong, and the data that refutes it was already ours.** Matching the
same findings at FUNCTION level rather than LINE level, on Lipp et al.'s real
CVE corpus:

```
TOOL PAIR                   line-lvl  func-lvl   methodologies
CommSCA + Flawfinder               2     1,191   commercial x PATTERN
CodeQL + Flawfinder               37       669   INTERPROCEDURAL x PATTERN
Flawfinder + Infer                 2       274   PATTERN x INTERPROCEDURAL
CodeChecker + Flawfinder           0       136   dataflow x PATTERN
Cppcheck + Flawfinder              0        66   <- EXACTLY OUR ZLIB PAIR
cross-methodology total        1,169     7,514   (6.4x)

overall multi-tool rate      1.56%    35.95%     (23x)
```

**Same tools. Same corpus. Same findings. Different ruler.** Our zlib zero was a
granularity artifact. Cross-methodology agreement is observable; we were not
looking at the level where it occurs.

**And then a second measurement narrowed it again.** Running function-level
matching through the actual pipeline rather than counting co-occurrences: tools
co-locate 3.5x more often at function level (1,507 → 5,269 units), but of those
5,269 co-occurrences only **410 (7.8%)** have the tools agreeing on the CWE
class. **92.2% co-locate and then disagree about what the bug is.** Because a
merge correctly requires class agreement — merging two different bugs in one
function would be a false merge — actual merges rise only 4.9%.

So the accurate statement is neither of the two we have held. Not "diverse tools
do not co-locate", which is false. And not "granularity fixes it", which
overstates. It is: **they co-locate readily at the right unit, and then disagree
about what they found.**

The three failures below are real observations and are retained — but all three
were matched at line level, which is the one thing they had in common and the
thing we did not vary.

| # | configuration | corpus | proximate cause | merges |
|---|---|---|---|---|
| 1 | flawfinder + cppcheck | zlib 1.3.1, **15 C files / 712 findings** | **anti-correlated class coverage** — flawfinder fmt/buf, cppcheck null/uninit/int. 14 exact co-locations, 10 with a class resolved on both sides, **0 class matches** | 0 |
| 2 | + semgrep (3rd tool) | zlib 1.3.1, **wider scan: 44–59 files / 1,164 raw, 1,135 dedup** | 2 merges (0.18%) — and both between the **two most methodologically similar** tools, in benchmark code, none in library sources. At this scope the pair alone co-locates 43 times, 11 classed on both sides, **0 matching** | ~0 |
| 3 | SpotBugs + semgrep | Apache Struts (real Java) | **anchoring convention** — classes matched *exactly* (redirect/redirect), locations did not: semgrep at the taint SOURCE (line 244), SpotBugs at the SINK (247) | 0 |

Three different proximate causes, one consequence. Cases 1 and 3 are the same
finding from opposite directions: in one the locations matched and the classes
did not; in the other the classes matched and the locations did not.

**Rows 1 and 2 are not the same scan, and the corpus column used to say they
were** (corrected 2026-07-26). Same library, different scope: row 1 is a 15-file
scan producing 712 findings, row 2 a wider one over 44–59 files producing 1,164.
That is why the pair's co-location count differs between them — 14 against 43 —
and neither number is wrong. **Do not read the two rows as one progression, and
do not compare their counts directly.** The finding survives the distinction
intact: the pair produces zero cross-tool merges at BOTH scopes, which is a
stronger result than either row alone, since it holds across a 1.6x change in
findings and a 3-4x change in files scanned.

**Adding tools does not fix it.** A fourth tool brings a fourth anchoring
convention. An interprocedural engine (CodeQL) anchors differently again. We
recorded, before spending anything: *nothing purchasable resolves this*, and
then declined to buy.

### The sharpest version of the finding
The single cross-methodology agreement ever observed on real code — case 3's
near-miss — turned out to be **a rule agreeing with its own ancestor.** semgrep's
`unvalidated-redirect` declares `source-rule-url:
find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT`, and the SpotBugs rule it
nearly agreed with is `UNVALIDATED_REDIRECT`, whose own `helpUri` is the
**byte-identical** string. Not an inference — a pointer match.

**So on real code, AT LINE LEVEL, in our own runs, the count of independent
cross-methodology agreements is zero.** Every qualifier in that sentence is
load-bearing. It is not a statement about the premise: at function level on
Lipp's data the same methodology pairing produces hundreds of agreements, and
whether those survive a rule-lineage filter has not been measured.

---

## 2. THE RANKING NULL — effect sizes and intervals, not p-values

Consensus-based ranking did not beat a size-matched control. Reported as effect
sizes because that is what a reader needs to judge whether it is worth
attempting.

**Ranking by file size alone, reading no tool output whatsoever, beats the
consensus signal on the metric the field quotes:**
```
consensus ROC-AUC (published 0.755; reproduced here 0.763)
ManualDown — sort files by DESCENDING SIZE                     0.845
```

Effort-aware (review budget in lines of code, not units):
```
FILE level      consensus PofB@20%LOC   0.228
                LOC baseline            0.081     consensus WINS
                finding-count           0.114     consensus WINS
                best single tool (Infer) 0.317    consensus LOSES

FUNCTION level  consensus PofB@20%LOC   0.185
                size-only floor         0.185     IDENTICAL
                random                  0.199     at or below chance
```

Four pre-registered formulations, all measured against a size-matched control:
```
                              PofB@20   IFA    PMI@20   vs size-matched random
A logistic n_tools+log(LOC)     0.185      2    0.022   collapses ONTO the floor
B size-residualized             0.185    142    0.161   P(rand>=)=0.468  no
C density n_tools/LOC           0.170   1334    0.571   P(rand>=)=0.603  no
raw consensus                   0.185    142    0.161   P(rand>=)=0.443  no
SIZE-ONLY floor                 0.185      2    0.022
```
Candidate C was pre-registered as *predicted to fail* on the grounds that
dividing by a common denominator induces correlation with that denominator
(Kronmal 1993). It failed, and reproduced ManualUp almost exactly.

**The mechanism is a confound, and it is measurable:** Spearman(n_tools, unit
size) = **+0.629** at file level, **+0.304** at function level. Agreement count
is substantially a size proxy, which is why every ranking claim built on it died
against a size-matched control and not against a weaker one.

---

## 2a. THE CONVERGENT RESULT — recovering more agreement has not once improved the ranking

This is stronger than either result below it, and it is the one a reader
deciding whether to attempt this needs.

Two mechanisms were built to recover agreement the exact-line key was missing.
They have **different causes** and were evaluated independently, each against a
decision rule fixed before computing:

| mechanism | what it recovers | yield | ranking effect |
|---|---|---|---|
| **Direction B** — point-in-range containment | agreement where one tool reports a range and another a point inside it | **+427 edges**, 36.9% of merges; passed all four pre-registered gates | none |
| **Function-level matching** — ground-truth boundaries, no parser | agreement anywhere in the same function | **3.5x co-location** (1,507 → 5,269 units) | none |

**Both worked at what they were built to do. Neither moved the ordering.**
Function-level consensus scores PofB@20 = 0.185 — identical to ManualUp and to
sorting by size alone — with P(size-matched random ≥) = 0.447.

### The mechanism, which is now visible rather than inferred
At function level, of 5,269 recovered co-locations only **410 (7.8%)** have the
tools agreeing on the CWE class. **92.2% co-locate and then disagree about what
the bug is**, and those are correctly rejected — merging two different bugs in
one function is a false merge, the error direction that inflates the very signal
the tool reports.

So the agreement that survives a correct guard is **too sparse to reorder
anything.** That is why yield rose twice and the ranking moved neither time: the
recovered agreement is mostly not agreement about the same bug, and what remains
after filtering is a small fraction of a ranking already dominated by size.

**BOUND: two mechanisms, one corpus.** Both evaluations ran on Lipp's C/CVE
data. A third mechanism, or the same two on a different corpus, could behave
differently. What this rules out is the assumption that the exact-line key was
the binding constraint — it was not, twice, for different reasons.

---

## 3. WHAT SURVIVES — stated with equal care

**A precision effect, not a ranking one.** Functions flagged by two or more
tools are more likely to contain a real CVE than *size-matched* functions
flagged by one:
```
1.54% vs 1.02%          point estimate ~1.5x
stable across controls  1.51x (10 strata) · 1.47x (50) · 1.52x (200) · 1.31x (exact LOC)
continuous adjustment   OR 1.39 (binary multi vs single, + log LOC)
project bootstrap 95% CI  [0.99x, 2.58x]        <- touches 1.0
direction                 consistent in 9 of 9 projects
```
It is a **threshold, not a score**: adjusted for size, OR 1.47 at two tools,
1.35 at three, **0.67 at four or more** (207 units, 4 events — absence of
evidence that more helps, not evidence that more hurts).

**The engineering is sound even though the claim is not.** Seven defect classes
were found by running real scanners on real code and are held by 112 automated
checks that run from a clean clone with no corpora and no network: two-algorithm
dedup, engine-lineage guarding, degenerate-fingerprint detection, path-root
disclosure and reconciliation, hierarchy-aware CWE resolution, and a gated
size-correlation disclosure. **A null result about a signal is not a null result
about the machinery.**

---

## 4. BOUNDARY CONDITIONS — what would have to be different

If you are attempting this, these are the levers, and two of the three are
measured rather than speculated.

**Granularity is not a boundary condition — it is §1, the main result.** The
numbers are there. What belongs here is the consequence: matching at function
level is the difference between observing agreement and not, **but** function-
level *ranking* still fails effort-normalisation (§2). So granularity buys
OBSERVABILITY, not a working ranker. Those are separate results and fixing the
first does not fix the second.

**Tool selection: we cannot say, and previously implied we could.** An earlier
draft asserted that selecting for co-location selects against independence, on
the grounds that the few merges we saw came from the most *similar* pair. At
function level that inference does not hold — the largest cross-methodology
counts include INTERPROCEDURAL × PATTERN pairs (CodeQL+Flawfinder 669,
Flawfinder+Infer 274), which is the most methodologically distant pairing
available in that corpus. Whether diverse pairs agree *less* than similar ones,
per opportunity, is **unmeasured here**. We have no basis for the trade-off we
asserted.

**Corpus type determines the answer, and this is the caution we would most want
passed on.** Synthetic OWASP Benchmark produced 1,427 merges; real code produced
0–2. Every positive merge result in this project came from synthetic or
reconstructed data. A synthetic benchmark plants one bug per file from
categories both tools cover — close to the condition *least* like real code and
*most* favourable to consensus.

---

## 5. DESIGN LEARNINGS — the ones that cost most to find

These are transferable and each cost real time.

**Estimand mismatch can masquerade as a contradiction.** Two of our own analyses
appeared to disagree flatly: a logistic model gave the tool-count coefficient
p=0.582, while a matched test gave ~1.5x at p<0.0001. Neither was wrong. One
fitted `n_tools` as a **linear slope**; the other compared **two-or-more vs
one**. Different quantities. Fitting the matching contrast with the same
covariate gave OR 1.39 — agreeing. The linear slope averaged a real
one-to-two step against a flat-to-falling tail and returned ~0. *Before
concluding two results conflict, check they estimate the same thing.*

**Denominators multiply silently.** One finding legitimately produced five
correct percentages: 8.3% of rules loaded, 45.5% of rules fired, 36.8% of
findings, 30.4% of co-located rule pairs, 22.6% of co-located locations. All
correct, none interchangeable. We also found a list of four numbers summing to a
*pair* count being read as *finding* counts. *State the denominator in the same
breath as the number, always.*

**A resampling p-value that conditions on one arm is not a test of the
comparison.** Our own `p<0.0001` held the treatment group's count fixed and
resampled only controls. Varying both gives p≈0.03–0.08. The effect survived;
the certainty did not. *Check what the test holds fixed, not only what it
compares.*

**Interchange formats lose information, and the loss looks like absence.** SARIF
v2.1.0 Appendix D (Normative) permits a converter to "simply omit" anything with
no SARIF equivalent. Rule provenance (`source-rule-url`) is present in semgrep's
native JSON and appears **0 times** in its SARIF. A provenance measurement run on
SARIF returns a confident zero that reads exactly like clearance. *Any negative
finding derived from an interchange format is a claim about the format until
checked against native output.*

**A proxy can manufacture the effect it is testing for.** We nearly shipped a
size-correlation diagnostic using `max(reported line)` as a file-size proxy.
More tools → more findings → a higher **maximum** → apparent "bigger file",
independent of actual length (measured: median max-line 58 for 1-tool files vs
457 for 2-tool files). It would have reported rho=+0.402, p=0.0025 and **fired a
false alarm on a real run**; with real file lengths the same run gives +0.232,
p=0.086 and is correctly silent.

**"Independent tools" is a weaker notion than it sounds.** In one rule registry,
**23.4%** of rules declare derivation from another tool, across **seven**
upstreams where the vendor's own documentation names four. Among rules *known*
derived, name matching recovers 50%, attribution 5%, and **textual similarity
recovers 0%** — median token overlap 0.101 against their own upstream text.
**Ported rules are rewritten**, which is the mechanism by which a derived rule
comes to look independently authored. If you cannot distinguish a ported rule
from an original one, you cannot assess the independence your consensus assumes.

---

## 6. WHAT IS NOT ESTABLISHED — including that this null may itself be flawed

A null result can be wrong, and the failure mode is asymmetric: Johnson et al.
(*Frontiers in Psychiatry* 2023) `[fetched]` note that "'false-negative' data can
terminate the development of" a line of work. Their checks, applied honestly to
ours:

**Is it underpowered?** *In one documented case, yes, and we said so.* The
consensus-vs-best-single-tool comparison on OWASP had a minimum detectable
effect of ~4.0pp against an observed 2.1pp — it could not distinguish the effect
from zero, and both "adds ~2pp" and "adds nothing" remain consistent with it.
That test returns **no verdict**, not a negative one. The co-location findings
(§1) are not underpowered in the same way: zero merges out of 1,164 findings is
not a power problem.

**Is the subject selection right?** *Uncertain, and this is the biggest threat.*
Four scanners, and only free-tier ones. CodeQL was never tested — it needs
Rosetta, absent on this machine. An interprocedural engine could behave
differently. §4 argues it would anchor differently again, but that is a
prediction, not a measurement.

**Is treatment fidelity adequate?** *Partly.* Every Java cross-tool merge number
was measured on **hand-aligned paths** — a real defect worked around manually for
the measurement rather than fixed at the time. It has since been fixed and the
result reproduces, but the original numbers were taken under a repaired harness.

**Is the data transparent?** *Yes, and this is the strongest limb.* Every number
has a named script; corpora have fetch commands, pinned commit SHAs, Software
Heritage SWHIDs and sha256 checksums; 19 of 21 analysis scripts run from a clean
clone given a corpus root. Two do not and are documented as such.

### Not established, plainly
- That multi-tool consensus **cannot** work. Only that these configurations
  failed.
- That the 1.5x generalises. Nine projects; the interval touches 1.0x.
- That ~23% rule derivation holds beyond one registry.
- That the ranking is unprovable — only that it is unproven here, and that the
  co-location evidence suggests it may be unreachable with these tools.

---

## Self-assessment against null-result reporting criteria

| criterion | met? |
|---|---|
| Full methods, including deviations from plan | **Yes.** Pre-registrations were committed before computing; deviations (e.g. a capture-recapture addition, a post-hoc sensitivity) are labelled as such rather than folded in. |
| Effect sizes with intervals and robustness checks, over p-values | **Yes.** §2 and §3 lead with effect sizes; the surviving claim carries a bootstrap interval; the withdrawn p-value is discussed as a lesson. |
| FAIR data and code | **Partly.** Scripts committed and path-clean; corpora not redistributable but pinned by DOI/SHA/SWHID. One dependency (a rule registry) is fetched live and **cannot** be archived by us for licence reasons — a real gap, disclosed. |
| Interpretation with value — boundary conditions, alternative mechanisms, design learnings | **Yes.** §4, §5, §6. |

*Grounding note, per our own citation rule: the Springer survey figures and the
Curry and Johnson quotations above were fetched and verified. The four-criterion
reporting framework itself could NOT be located on the white paper's public
pages; it is used here as a sensible structure, not attributed to that source.*

---

## The README sentence — CORRECTED AND RE-APPLIED 2026-07-26

> **What did not work is written up separately** in
> [docs/NEGATIVE_RESULT.md](docs/NEGATIVE_RESULT.md): across three scanner
> pairings on real C and Java, methodologically different tools produced **zero**
> independent agreements at the same location — the one near-match was a rule
> agreeing with the rule it was copied from — and the ranking built on agreement
> measurably lost to sorting files by size.

TWO REVISIONS, RECORDED BECAUSE THE SECOND MATTERS MORE.

The first draft said tools "did not produce agreement at the same location
**often enough to rank on**" — a frequency claim. It was sharpened to "**zero**
independent agreements at the same location", which is stronger and, at line
level, true.

**Then the sharpened version turned out to be the wrong claim entirely.** It
generalised a line-level measurement into a statement about what scanners can
do. The applied sentence now leads with the measurement error instead, because
that is the part a reader can use: the finding was an artifact of our ruler, and
the ranking null — which is unaffected — is stated separately rather than
bundled with it.

Both prior versions are recorded rather than deleted, because the sequence is
the lesson: a claim can survive being tightened and still be false.
