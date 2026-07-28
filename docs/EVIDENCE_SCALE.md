# The graded scale — step 3 of 5, semantic layering

**Tier: `[self-tested]`.** A design. Applied to nothing beyond the six
falsification cases; no external reviewer has checked it.

**Design only.** No `TERMS.md`, no re-tiering of any existing claim. Drift filed
in §10.

---

## 0. SOURCE CHECK

Located from description and venue, as instructed. All quotations below were
fetched this session.

| source | status |
|---|---|
| **GRADE Handbook** (gradepro.org → gdt.gradepro.org/app/handbook) | fetched; four levels, continuum statement, indirectness-per-outcome all confirmed verbatim |
| **Cochrane Handbook ch. 14**, "Completing 'Summary of findings' tables and grading the certainty of the evidence" | fetched; per-outcome rating and the mandatory-documentation requirement confirmed verbatim |
| **RFC 2119** (Bradner 1997) | fetched from rfc-editor.org; all keyword definitions and §6 guidance confirmed verbatim |

**ONE DISCREPANCY IN THE BRIEF, reported rather than absorbed.** I was told
"publication bias may be downgraded at most one level." The GRADE Handbook's
Table 5.2 lists publication bias with the consequence **"↓ 1 or 2 levels"** —
two, not one. I may be reading a summarised rendering of that table rather than
its full footnotes, so this is "the handbook I fetched says 1 or 2", not "the
brief is wrong". It does not affect the design, since publication bias is not
one of our domains (§4).

Verbatim, load-bearing for §1:
> "Quality of evidence is a continuum; any discrete categorisation involves some
> degree of arbitrariness. Nevertheless, advantages of simplicity, transparency,
> and vividness outweigh these limitations."

> "Problems with indirectness may lead to rating down quality for one outcome
> and not another within a study or studies…"

> "The GRADE system entails an assessment of the certainty of a body of evidence
> for each individual outcome." (Cochrane 14)

> **C75 (Mandatory):** "Justify and document all assessments of the certainty of
> the body of evidence (e.g. downgrading or upgrading using GRADE)." (Cochrane 14)

---

## 1. THE OBSERVATION, RESOLVED — GRADE ALREADY SATISFIES C1, AND ITS DOMAINS DO NOT

The brief observes that GRADE's domains mix evidence-properties (risk of bias,
publication bias) with inference-properties (indirectness) and estimate-
properties (imprecision), and asks whether both kinds can move one qualifier.

**They can, and GRADE already demonstrates it — but at the level of the RATING,
not the domains.** GRADE's rating is *per outcome*, not per study. The same body
of evidence rates High for one outcome and Low for another, and indirectness is
named as the reason. **That is C1.** A GRADE rating is not a property of the
evidence; it is a property of the evidence *considered as support for a
particular outcome* — which is the inference.

So the resolution is:

- **ONE qualifier**, attached where step 2 put it — on the inference from
  grounds to claim, i.e. rated per (grounds, warrant, claim) triple.
- **Domains of both kinds feed it**, exactly as in GRADE. An evidence-property
  matters *because of* what it does to the inference: a degenerate instrument
  weakens every inference drawn through it.
- **The same grounds therefore carry different levels for different claims.**
  Case 2 is our instance of GRADE's indirectness example: one artifact, two
  claims, two levels.

**ESTIMAND is GRADE's indirectness under another name — the brief's hypothesis
holds, with one refinement.** Indirectness is the *gap*; ESTIMAND is the *field
that makes the gap visible*. Naming what was measured is what lets a reader see
that it is not what was claimed. So ESTIMAND is not itself the domain — it is
the field the domain is checked against, which is why step 2 put it in the
warrant rather than making it a qualifier input.

---

## 2. LEVELS

Four. Named for the state of the *inference*, not of the evidence.

Intensional definitions, ISO 704 form — superordinate concept plus delimiting
characteristic:

| level | definition |
|---|---|
| **ESTABLISHED** | *an inference* whose conclusion **could not be otherwise given the grounds** — either deductive, or with every applicable adjustment domain assessed and none adverse. |
| **SUPPORTED** | *an inference* whose conclusion **is licensed by the grounds against a stated comparator**, with any adverse domain identified and bounded. |
| **INDICATED** | *an inference* whose conclusion **is licensed only under conditions that are stated but not all discharged**. |
| **UNRESOLVED** | *an inference* whose grounds **cannot license the conclusion either way**. |

### The arbitrariness, stated as GRADE states it
Certainty here is a continuum and four cuts are a convenience. Verbatim from the
handbook: *"any discrete categorisation involves some degree of arbitrariness"*,
justified by *"advantages of simplicity, transparency, and vividness"*. The same
trade is being made and the same admission is owed.

### Why four, and why not six
Four rather than six because **the existing six tiers were not four levels plus
two — they were a mix of provenance facts and strength judgments** (§6). Once
provenance is moved to its own fields, the strength distinctions the corpus
actually makes reduce to four. I did not add a level to fit a case; §8 records
the case that does not fit.

### UNRESOLVED is named to prevent a documented misuse
GRADE's recorded misuse: *"Very Low" certainty does not mean the treatment does
not work; it means we are very uncertain about the estimate.* **This project has
made that exact error and had to correct it in writing** — item 0d's header
still carries "UNDERPOWERED TEST, NOT A MEASURED ABSENCE OF EFFECT", and the 0f
zlib zero required "UNINFORMATIVE, not clearance" in three places.

`UNRESOLVED` is chosen over `WEAK` or `VERY LOW` because it names the state of
the *question*, not of the claim. A reader cannot glide from "unresolved" to
"false" as easily as from "very low" to "probably not".

---

## 3. DEFAULT BY METHOD

GRADE defaults from study design. Ours defaults from **what kind of act produced
the grounds** — step 2's `GROUNDS.kind`, which was derived from the corpus, not
invented here.

| grounds kind | default | corpus basis |
|---|---|---|
| **DEDUCTION** — proof from an artifact, nothing executed | **ESTABLISHED** | case 2A: `fp:` cannot equal `rk:`. Running something could not strengthen it. |
| **REPRODUCTION** — re-derived, artifact present and re-runnable | **SUPPORTED** | case 1: 0j re-derived a prior session's number and hit it exactly. |
| **OBSERVATION** — measured once, artifact present | **INDICATED** | the zlib run, the Struts run: real but single. |
| **no retrievable ARTIFACT REF** | **UNRESOLVED, and un-upgradeable** | step 1 list-C: the original 1.5x, "run inline and never written to a file". |

The last row is a **ceiling rule**, not a default: absence of a retrievable
artifact caps the level regardless of how the grounds were produced. Step 2 made
ARTIFACT REF mandatory; this is what mandatory means in the scale.

---

## 4. ADJUSTMENT DOMAINS — DERIVED FROM THIS PROJECT'S FAILURES

Each domain below is a documented failure in this corpus, not an import.

### First: which candidates are domains, and which are DEFEATERs

The brief asks this explicitly. The test used:

> A **DOWNGRADE DOMAIN** is a property the inference *actually has now*.
> A **DEFEATER** is a condition that *would* break the claim *if it obtained*,
> and may be discharged by testing.

| candidate | verdict | why |
|---|---|---|
| estimand–claim gap | **DOMAIN** | present or absent as a fact about the pair |
| comparator adequacy | **DOMAIN** | the comparator either is or is not the one that matters |
| instrument validity | **DOMAIN** | a degenerate statistic is degenerate now |
| staleness (rule 11) | **DOMAIN** | machine-checkable from TIME |
| unverified provenance (rules 8, 8a) | **DOMAIN** | the source either was or was not opened |
| negative-from-proxy (rule 10) | **DOMAIN** | the claim is about a format until checked natively |
| "a tool that co-locates by construction would defeat this" | **DEFEATER** | contingent, untested, dischargeable |
| "if the size control were coarser than the confound" | **DEFEATER** | *was* tested (10→200 strata) and discharged |

**The distinction earns its place in case 1**, where the coarse-control worry is
a defeater that was tested and survived — so it must not permanently downgrade
the claim, which a domain would. Step 2 already has DEFEATER; the scale must not
duplicate it.

### DOWNGRADE domains

| domain | trigger | max |
|---|---|---|
| **D1 estimand–claim gap** *(= GRADE indirectness)* | the quantity measured is not the quantity claimed | −2 |
| **D2 comparator adequacy** | the claim is COMPARATIVE and its comparator does not support the comparison asserted (incl. a trivial baseline also beating it). See §9a for the sharpened definition and why this is a certainty judgment, not a relevance one. | −2 |
| **D3 instrument validity** | the measuring procedure cannot support the inference | −2 |
| **D4 staleness** | `grounds-checked-at` predates the claim's last correction | −1 |
| **D5 unverified provenance** | a cited source was not opened, or an artifact is attested but absent | −1 |
| **D6 negative-from-proxy** | an *absence* inferred from an interchange format or derived proxy, unchecked against native output | −1 |

Corpus basis, one instance each — all already documented:
- **D1** — case 3, the estimand mismatch: a linear slope read as answering a
  binary contrast.
- **D2** — five claims died to better comparators; ROC-AUC 0.755 lost to sorting
  files by size.
- **D3** — the `max(reported line)` size proxy would have manufactured the
  correlation it tested for; Spearman on near-constant `n_tools`; the `p<0.0001`
  that held one arm fixed.
- **D4** — rule 11, three forms, eight instances.
- **D5** — rules 8 and 8a; five failed attributions.
- **D6** — rule 10; `source-rule-url` present natively, 0 in SARIF.

### UPGRADE factors

GRADE upgrades non-randomised evidence for large effect, dose-response, and
opposing confounders. None transfer. These are ours:

| factor | trigger | max |
|---|---|---|
| **U1 survived an adversarial test it could have failed** | a pre-stated check that would have refuted the claim was run, and did not | +1 |
| **U2 pre-registered** | criteria fixed and committed before the grounds existed | +1 |
| **U3 independently re-derived by a different route** | a second instrument or path reaches the same value | +1 |

Corpus basis:
- **U1** — the 1.5x survived strata refined 10→200; item 2 was closed by a rule
  fixed in advance that it failed.
- **U2** — 0f, 0i, item 2 and Direction B were all pre-registered before
  computing, and the commit order proves it.
- **U3** — `1,156` re-derived as the `exact-line` component; the FindSecBugs
  extract byte-identical to the jar it replaced.

**U2 is the one I would most expect to be challenged.** Pre-registration does not
make a result more true; it removes the researcher degrees of freedom that let a
result be fitted after the fact. That is a property of the *inference* — the
warrant is stronger because the criteria could not have been chosen to suit the
grounds. So it belongs here rather than in provenance.

### FLOOR AND CEILING RULES
- **FLOOR.** Certainty cannot fall below `UNRESOLVED`, however many domains
  apply. (GRADE's rule, adopted unchanged.)
- **CEILING 1.** No retrievable ARTIFACT REF → `UNRESOLVED`, and no upgrade
  applies.
- **CEILING 2.** Upgrades may not raise a level above `SUPPORTED` unless the
  grounds kind is DEDUCTION. **Only a proof reaches `ESTABLISHED` by upgrade** —
  an empirical claim reaches it only by having no adverse domain at all, which on
  this corpus has not yet happened.

### REQUIRED RATIONALE
Per Cochrane C75, adopted verbatim in force: **every adjustment, up or down,
carries a written rationale naming the domain and the specific fact that
triggered it.** An adjustment without a rationale is malformed, not merely
undocumented.

---

## 5. CANONICAL REPORTING SENTENCES

A session must not compose its own phrasing. One sentence per level, GRADE's
practice.

| level | canonical sentence |
|---|---|
| **ESTABLISHED** | *"Given the grounds, this could not be otherwise. Adjustments: none adverse."* |
| **SUPPORTED** | *"The grounds license this against \<comparator\>. \<Bound\> limits where it applies."* |
| **INDICATED** | *"The grounds point this way under \<condition\>, which is stated and not discharged."* |
| **UNRESOLVED** | *"The grounds cannot settle this either way. This is not evidence against the claim."* |

The second sentence of `UNRESOLVED` is mandatory and not optional phrasing. It
exists because the project has twice had to add exactly that disclaimer by hand.

---

## 6. THE SIX EXISTING TIERS — WHAT HAPPENS TO EACH

None is renamed. Each becomes a default input, an adjustment domain, a
provenance field, or is retired.

| tier | disposition |
|---|---|
| **`[fetched]`** | → **PROVENANCE FIELD** on ARTIFACT REF (`origin: fetched`). It says where an artifact came from and nothing about any inference. |
| **`[corroborated]`** | → **ADJUSTMENT DOMAIN**, upgrade **U3**. "Multiple independent sources agree" is a re-derivation by a different route. |
| **`[standard-checked]`** | → **PROVENANCE FIELD** (`origin: fetched`, `artifact-kind: published standard`). It feeds U3 when a second source agrees, but is not itself a strength. |
| **`[externally-grounded]`** | → **DEFAULT INPUT.** Grounds produced by a non-Claude engine or dataset default one level above the same act performed by Claude alone. |
| **`[externally-verified]`** | → **DEFAULT INPUT**, the strongest for OBSERVATION: an external judge on real data defaults to `SUPPORTED` rather than `INDICATED`. |
| **`[self-tested]`** | → **DEFAULT INPUT and a D5 trigger.** Claude grading Claude defaults to `INDICATED` and takes −1 unless an external artifact is present. |

**The compound "`[self-tested]` analysis over `[externally-grounded]` inputs"**,
which step 1 flagged as ad-hoc, is now expressible without a compound: grounds
kind REPRODUCTION, provenance `externally-grounded`, D5 triggered by the
Claude-written analysis → net `INDICATED`. That it needed a compound before is
evidence the two axes were conflated.

---

## 7. THE FIVE ORPHAN BRACKET TOKENS

Each is a requirement on this design or an explicit rejection.

| token | disposition |
|---|---|
| **`[snippet]`** | **REQUIREMENT, ACCEPTED — and it is the most important of the five.** Becomes `retrieval-depth: primary \| rendering \| snippet` on ARTIFACT REF, and `snippet` triggers **D5**. Sessions reached for this because reading a search summary is not reading a source. **This is the token that carries the C3 bound (§9).** |
| **`[reconstructed]`** | **REQUIREMENT, ACCEPTED.** Becomes `artifact-kind: captured \| reconstructed \| synthetic`. Justified by the 0.755 attribution error, which turned entirely on a reconstructed SARIF envelope being read as captured output. |
| **`[unverified]`** | **REQUIREMENT, ACCEPTED** as a **D5** trigger value: *checked and failed to confirm* (the GrammaTech case). |
| **`[unconfirmed]`** | **REQUIREMENT, ACCEPTED, and it must stay distinct from `[unverified]`.** *Not yet checked* ≠ *checked and not confirmed*. The first maps to level `UNRESOLVED`; the second is a downgrade **from** a level. Collapsing them would lose the difference between an open question and a failed check. |
| **`[checked]`** | **REJECTED as a token; the requirement is met elsewhere.** What sessions wanted was "I looked at this recently" — which is `grounds-checked-at` in step 2's TIME, and machine-written. A hand-set `[checked]` would be a timestamp that can lie. |

Four of five were real requirements. That is a reasonable strike rate for
tokens invented under pressure, and it argues the scale they were reaching past
was genuinely missing distinctions rather than that sessions were careless.

---

## 8. THE FALSIFICATION SET

### Case 1 — the 1.5x
```
grounds kind  REPRODUCTION            default SUPPORTED
provenance    externally-grounded (Lipp CVE labels), captured, primary
D1 estimand   none — ESTIMAND names the binary contrast, and the claim is
              stated as that contrast                                    0
D2 comparator size-matched single-tool functions; a trivial baseline does
              NOT also beat it                                           0
D3 instrument the conditioning-on-one-arm defect was found and removed    0
D4 staleness  grounds-checked-at == claim's last correction               0
D5 provenance external artifact, primary retrieval                       0
D6 proxy      n/a — positive finding                                     0
U1 adversarial survived strata refined 10 -> 200, which could have killed it +1
U2 pre-registered  no — 0j's refinement was directed, not pre-committed   0
CEILING 2     empirical grounds cannot be raised to ESTABLISHED
LEVEL         SUPPORTED
BOUND         nine projects; project-bootstrap CI [0.99x, 2.58x]
SENTENCE      "The grounds license this against size-matched single-tool
              functions. Nine projects, CI touching 1.0x, limits where it
              applies."
```

### Case 2 — the fp:/rk: collision (two claims, one artifact)
```
CLAIM A  "an fp: key can never equal an rk: key"
grounds kind DEDUCTION               default ESTABLISHED
all domains  none applicable — no measurement, no comparator, no instrument
LEVEL        ESTABLISHED

CLAIM B  "the headline consensus signal is inert in the shipped product"
grounds kind DEDUCTION on the same artifact, plus one observation
D1 estimand  MISMATCH: what was proven is a property of the KEY; what is
             claimed is behaviour on all future inputs                    -2
D3 instrument the deduction assumed the key was the ONLY blocker           -1
LEVEL        UNRESOLVED (floor)
```
**The same artifact yields ESTABLISHED and UNRESOLVED.** This is the design
requirement of C1 met, and it is GRADE's per-outcome rule reproduced on our own
material.

### Case 3 — the estimand mismatch
```
CLAIM X  "n_tools carries no precision signal once size is controlled"
grounds kind REPRODUCTION            default SUPPORTED
D1 estimand  MISMATCH: a linear slope was read as answering a binary
             contrast                                                     -2
LEVEL        UNRESOLVED — and status WITHDRAWN, which is separate
```
Note the two are independent: D1 sets the level, `status` records that the claim
was retired. A claim can be UNRESOLVED and LIVE (an open question), or
SUPPORTED and SUPERSEDED (right, then replaced by something better).

### Case 4 — the withdrawn p<0.0001
```
grounds kind REPRODUCTION            default SUPPORTED
D3 instrument the test held one arm fixed, so it did not test the
             comparison it reported                                       -2
LEVEL        UNRESOLVED     status WITHDRAWN
SENTENCE     "The grounds cannot settle this either way. This is not evidence
             against the claim."   <- and indeed the 1.5x survived
```
The canonical sentence does real work here: the p-value was withdrawn, the
effect was not.

### Case 5 — the zlib zero — **TWO ASSESSMENTS**
```
CLAIM        "the shipped pair produces ZERO cross-tool merges on real zlib"
grounds kind OBSERVATION (712 findings)   default INDICATED
U3 re-derived after the item-2 fix, same result                          +1
D4 staleness grounds re-checked after the fix                             0
LEVEL        SUPPORTED

CONFIDENCE ARGUMENT v1  "because fp:/rk: keys cannot collide"
                        LEVEL: UNRESOLVED (refuted — see case 2 claim B)
CONFIDENCE ARGUMENT v2  "because the pair's CWE classes are anti-correlated"
                        grounds OBSERVATION, 14 co-locations, 0 class matches
                        LEVEL: SUPPORTED
```
**Answer to the brief's question: case 5 needs TWO levels, not one — but not
two scales.** The same four levels apply twice, to two different inferences: one
from grounds to claim, one from grounds to mechanism. This is C3's split doing
exactly the work it was adopted for, and it is the case that would be
unrepresentable with a single number per claim.

### Case 6 — "adding scanners is the wrong lever"
```
CLAIM.kind   PROSCRIPTIVE
CERTAINTY    NOT ASSIGNED — see §9
STRENGTH     STRONG  ->  canonical: "MUST NOT acquire further scanners on the
             theory that they will produce consensus."
basis        three configurations; and the recommendation grew STRONGER when
             its warrant was overturned, because a fourth tool would also have
             been measured at the wrong unit
BOUND        free-tier scanners; no interprocedural engine ever run here
DEFEATER     a tool that co-locates by construction — UNTESTED (Rosetta)
```

### The three questions answered

**1. Do case 2 and case 1 get different levels, and is that right?**
Yes — `ESTABLISHED` versus `SUPPORTED`. **And it is right, but it is also a trap
worth naming.** Case 2A is certainly true and nearly trivial; case 1 is
uncertain and is the project's most useful finding. **The scale measures
certainty, not importance, and ranks the trivial claim higher.** GRADE's
documented misuse is the same shape — confusing certainty with the direction or
size of effect. A reader who treats `ESTABLISHED` as "more valuable" has made
that error. §9 records that the scale cannot express importance.

**2. Does case 6 get a certainty level at all?**
**No — only a strength.** A proscriptive claim is not true or false, so
"certainty" has no referent. Its *supporting descriptive claims* carry certainty
individually. This is the payoff of step 2's `CLAIM.kind` field: without it,
case 6 would be forced to accept a certainty level it cannot bear.

**3. Case 5 — one level or two?**
**Two, as shown above.** One for the claim, one for each confidence argument.

---

## 9. RECOMMENDATION STRENGTH — A SEPARATE SCALE

GRADE's central structural move is splitting certainty of evidence from strength
of recommendation. Adopted.

**Two levels**, following GRADE's strong/conditional split rather than inventing
a finer one:

| strength | meaning | canonical keyword |
|---|---|---|
| **STRONG** | almost anyone in this position should act this way | **MUST** / **MUST NOT** |
| **CONDITIONAL** | reasonable people in this position would differ | **SHOULD** / **SHOULD NOT** |

**Decision on RFC 2119: adopt its KEYWORDS as the surface form, not its
semantics as the scale.** Justification:

- RFC 2119's definitions are exactly the two levels needed. **SHOULD**: *"there
  may exist valid reasons in particular circumstances to ignore a particular
  item, but the full implications must be understood and carefully weighed
  before choosing a different course."* That is GRADE's *conditional*, stated
  more precisely than GRADE states it.
- **MUST**: *"an absolute requirement of the specification"* — the force needed
  for case 6.
- **MAY / OPTIONAL is NOT adopted.** *"An item is truly optional"* is not a
  recommendation; it is the absence of one. A project that has retired five
  claims should not have a keyword for advice it does not mean.
- RFC 2119 §6's own caution transfers directly: the keywords *"must be used with
  care and sparingly"* and *"only used where it is actually required… or to limit
  behavior which has potential for causing harm."* That is precisely the
  discipline step 2's DESCRIPTIVE/PROSCRIPTIVE split exists to enforce — it
  makes promoting a finding into a policy a deliberate act.

**A recommendation's strength is not inherited from the certainty of its
supporting claims.** Case 6 is STRONG while its warrant was overturned and its
supporting claims range from UNRESOLVED to SUPPORTED. GRADE permits exactly this
asymmetry, and the corpus demonstrates it.

---

## 9a. SETTLED — D2 AND §10.1 ARE NOT THE SAME PROBLEM

Resolved 2026-07-27 on a direct question. The framing offered was that §10.1
(certainty ranks trivia above usefulness) and D2 (a relevance judgment inside a
certainty scale) are one problem with three candidate fixes. **The corpus
falsifies half of that: they are two problems, and only one of them is real.**

### D2 is not a relevance judgment. The corpus treated weak-comparator claims as INVALID.

The test is what the project actually *did* when a comparator failed. HANDOFF's
retirement of the file-level ranking row, verbatim:

> "Every one of those figures has been **withdrawn**:
>  * 0.755 is NOT effort-aware, and ManualDown … scores 0.845 on the same data.
>  * The effort-aware 'win' was measured against ManualDown, which is the
>    NON-effort-aware baseline. **Against ManualUp it is not significant.**
>  * The remaining IFA/PMI advantage **does not survive a SIZE-MATCHED control**."

Two of the three bullets are certainty statements outright — *not significant*,
*does not survive a control*. And the disposition applied to all three was
`WITHDRAWN`, the status meaning **epistemically invalid**, not "retained as
true but uninformative".

The reason is that **the claims were comparative in their own statement.** The
README said 0.755 *"beats a coin flip and the best single tool"*. A comparative
claim with the wrong comparator is not an uninformative true claim — it is an
**unwarranted** one. D2 is therefore a genuine certainty domain and stays where
it is.

**Sharpened definition, replacing §4's:**
> **D2 comparator adequacy.** Fires when the claim is COMPARATIVE and the
> comparator named does not support the comparison asserted — including when a
> trivial baseline also beats it. Does *not* fire on a claim stated as a bare
> measurement with no comparison asserted.

### The residue is a claim-statement defect, and option (c) is the fix

The apparent relevance-smuggling appears only when a claim states a
*measurement* and is read as a *comparison*: "AUC = 0.755" is true; "the tool
ranks usefully" is what a reader takes away. That is not a scale defect.

**Adopted, as option (c):** *a claim must be stated at the level its warrant
reaches.* If the warrant supports a measurement, the claim states the
measurement. If it supports a comparison, COMPARATOR is named **inside the
claim**, not only in its metadata. Step 2 already made COMPARATOR mandatory;
this says where it must be visible.

This is the mechanism option (c) was asked to supply, and it does carry what D2
appeared to be carrying — because once the claim is stated at warrant level, a
weak comparator produces a *weak claim*, not a strong claim about nothing.

### §10.1 is a real limitation, and option (a) is correct for it

**Option (c) does not fix §10.1 and nothing in it claims to.** Case 2A
("`fp:` cannot equal `rk:`") is still ESTABLISHED and still trivial, however it
is stated. Restating cannot make an uncertain useful claim outrank a certain
trivial one, because the axis is certainty and that is what it measures.

**Option (a) — accept and document — for three corpus reasons:**

1. **GRADE has the identical limitation and does not fix it either.** Fetched
   this session: magnitude of effect enters *strength of recommendation*, not
   certainty of evidence, and the handbook's own examples include recommendations
   "strong despite low certainty" and "weak … in the face of high confidence in
   effect estimates". GRADE has **no importance axis for evidence**. For
   descriptive claims that generate no recommendation, neither does it. This is a
   property of the whole family of approaches, not a defect introduced here.

2. **Option (b)'s second axis would be the most staleness-prone field in the
   system, in a project whose dominant failure is staleness.** And the corpus
   proves informativeness *does* decay: 0.755 was informative until ManualDown
   scored 0.845 on the same data — nothing about the claim changed, only the
   best known alternative. A stored informativeness rating goes stale the moment
   someone measures a better baseline, and **nothing would trigger re-rating**.
   Rule 11 has three forms and eight instances; adding a field with no
   invalidation trigger is adding a ninth.

3. **Importance is already readable without a rating.** COMPARATOR says what the
   claim beat; BOUND says where it stops applying. A reader wanting to know
   whether a claim matters reads those two fields. That is worse than a number
   for sorting and better than a number for being right, and this project has
   retired five numbers that were easy to sort by.

### The decision
- **D2 stays in the certainty scale**, with the sharpened comparative-claim
  definition above.
- **Option (c) adopted** as a claim-statement rule, which is what D2's residue
  actually needed.
- **Option (a) accepted for §10.1**, explicitly and with GRADE's precedent.
- **Option (b) rejected** on the staleness argument, which is a corpus argument
  rather than an aesthetic one.

**What this costs, stated plainly:** a reader who sorts by level still gets the
trivia first. That is now a documented property rather than an unexamined one,
and §10.1 stands unamended below.

---

## 10. WHAT THE SCALE CANNOT EXPRESS

1. **Importance.** `ESTABLISHED` outranks `SUPPORTED` while case 2A (trivial,
   certain) outranks case 1 (uncertain, the project's most useful finding). The
   scale is orthogonal to value and will mislead anyone who reads it as a
   ranking of worth. **SETTLED 2026-07-27 as accepted-and-documented, not fixed
   — see §9a.** GRADE carries the same limitation and routes magnitude to
   recommendation strength instead; a second axis was rejected because
   informativeness decays whenever a better baseline is measured and nothing
   would trigger re-rating.
2. ~~**The comparator strain.**~~ **RESOLVED 2026-07-27 — see §9a.** The
   original entry called D2 the weakest join, on the reading that a
   weak-comparator claim is certainly-true-but-uninformative. The corpus
   disagrees: such claims were `WITHDRAWN` as invalid, because they were stated
   comparatively and the comparison was unwarranted. D2 is a certainty judgment.
   Retained struck through because the reasoning that moved it is part of the
   record.
   **What remains** is a claim-statement requirement, not a scale defect: a claim
   must be stated at the level its warrant reaches.
3. **Aggregate claims** whose grounds are other claims — inherited unfixed from
   step 2 §6. The convergent result still has no representation, and now also no
   rule for combining the levels of its components.
4. **Combination of confidence-argument levels.** Case 5 has a SUPPORTED claim
   with one UNRESOLVED and one SUPPORTED confidence argument. Nothing says what
   the pair means together.
5. **Recoverability of a staleness downgrade.** D4 fires when grounds are older
   than the claim. Re-running the artifact presumably clears it — but the scale
   does not say so, and if it does clear automatically then D4 is a prompt rather
   than a judgment.
6. **Degree of defeater discharge** — inherited from step 2 and still open.
   Case 1's defeater was tested; case 6's was not; the scale sees neither.
7. **Claims about the project's own process.** Rules 8a, 10, 11 have grounds and
   warrants but are not claims about the measured world. Inherited from step 2,
   unfixed.

---

## 11. INHERITED BOUND ON C3 — NOT STRENGTHENED

Step 2's constraint C3 (the confidence-argument split) rests on Hawkins, Kelly,
Habli & Calinescu, SSS 2011, **corroborated across two retrievals and never read
at the publisher's bytes.**

**Does step 3 depend on it more heavily than step 2 did? YES.** Step 2 adopted
the split as a structural convenience. Step 3 makes it load-bearing: §8's case 5
is resolved *only* by rating two inferences separately, and that is the split.
If the primary source defines the split differently, case 5's resolution needs
re-deriving.

**Recorded in this design's own vocabulary:** the C3 grounds carry
`retrieval-depth: snippet`, which triggers **D5**. The design classifies its own
foundation as downgraded — which is the correct behaviour and worth noting as a
small check that the scale is not self-flattering.

---

## 12. DRIFT NOTICED, NOT FIXED

- **(a)** Carried from step 2 §7(a), still live: `VALIDATION.md:3110` reads
  "P(size-matched control >= multi) = 0.0000 SURVIVES" and "highly significant",
  language the 0j work withdrew. Quotable in isolation and reads as current.
- **(b)** `docs/AUDIT.md` and `docs/GENESIS_TEMPLATE.md` use
  `[externally-verified]` in senses that may predate the current definition —
  carried from step 1 §5(d) and step 2 §7(b), still unaudited across three steps.
