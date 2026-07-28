# Concept inventory — step 1 of 5, semantic layering

**Tier: `[self-tested]` throughout.** This is one reading of the corpus by the
agent that wrote much of it, not an external measurement. Nobody else has
adjudicated these judgments and no claim here has been checked against a source
outside the repository except the Phase 3 mapping.

**Inventory only.** This pass changes no claim, corrects no drift, and edits no
existing file. Drift noticed while reading is filed in §6, not fixed.

---

## PHASE 1 — MECHANICAL EXTRACTION

**Corpus** enumerated with `git ls-files '*.md'`, excluding `vendor/`:
**19 files, 10,267 lines.** README.md included.

### Raw extraction, rules applied mechanically
```
distinct surface strings   3,385
total extraction hits      6,827

by rule:  a_backtick    1,293
          b_bracket       249
          c_bold          767
          c_caps        3,678
          d_listlead      225
          d_tablecell     615
```

### !! THE EXTRACTION RULE PARTLY FAILED, AND THAT IS A FINDING !!
Reported rather than silently patched, per instruction.

**Rule (c) — "BOLD or CAPITALISED used as a label rather than emphasis" — is
not mechanically applicable.** The label/emphasis distinction is exactly the
judgment the rule is supposed to defer, so a regex cannot apply it. Rule (c)
produced 3,678 of 6,827 hits (54%), and the large majority are emphasis:
`ZERO`, `BOTH`, `ONLY`, `THIS`, `CANNOT`, `DIFFERENT`, `MORE`, plus multi-word
runs like `DO NOT` and `THE ACTUAL CONSTRAINT`. This corpus uses capitalisation
for stress constantly, so the rule over-collects here more than it would
elsewhere.

I did not substitute a different rule. I applied it as written and pushed the
label/emphasis judgment into the filter, where it is visible and recorded below.

### Filter to project concepts
```
pre-filter distinct   3,385
dropped                 520   (mechanical categories)
remaining             2,865
```
Mechanical drop categories: filename 174 · number 157 · bare emphasis 71 ·
code identifier 47 · rule/CWE identifier 43 · tool/standard/person name 24 ·
structural 4.

2,865 is still overwhelmingly rule-(c) residue, so a **salience floor of ≥4
occurrences** was applied (209 candidates), then the semantic test — *does the
project rely on this, and would it have to define it for a stranger?*

**Final set: 58 concepts.** Under the 60 cap, so no truncation was needed and
nothing was cut for space.

### Judgment calls the filter made, stated so they can be disputed
1. **Tool names kept when the project redefined them.** `ManualUp`/`ManualDown`
   are kept — the project uses them as baselines with specific construction, not
   as citations. `flawfinder`, `semgrep`, `SpotBugs` are dropped: ordinary
   meaning throughout.
2. **`n_tools` dropped as a code identifier, `consensus` kept.** They denote
   nearly the same thing, but `n_tools` is a field name; `consensus` is the
   concept. This is arguably wrong — `n_tools` carries a project-specific
   counting rule (engines, not driver names) that its ordinary reading does not.
   Flagged rather than resolved.
3. **`SARIF`, `CWE`, `SWHID` dropped** as external standards used in their
   ordinary sense — but see §6(a): `SARIF` is arguably redefined here, because
   the project treats "absent from SARIF" as a distinct epistemic state.
4. **Tier tokens kept in bracket form** (`[fetched]`), since the brackets are
   part of the term as the project uses it.
5. **Status verbs kept despite being ordinary English** (`WITHDRAWN`,
   `SUPERSEDED`), because §2-A shows the project has given them non-ordinary,
   mutually exclusive meanings.

---

## PHASE 2 — CLASSIFICATION

Test applied per pair, per ISO 704: a characteristic is **essential** if its
absence fundamentally changes the concept. Two uses are two concepts when some
characteristic is essential to one and absent from the other. Named, not felt.

### A. ONE TERM, TWO CONCEPTS

---

#### A1. **verified** — 105 occurrences, 34 read (every 3rd)
**Four concepts, and the clash is with the project's own tier.**

The essential characteristic that separates them is **who or what does the
checking, and whether it is external to the agent making the claim.**

| sense | essential characteristic | example |
|---|---|---|
| **verified-against-tree** | the checker is the agent; the referent is repo state | `docs/HANDOFF.md:271` — "Verified against src/audit.py, not inherited." |
| **verified-by-execution** | something was *run*; referent is observed behaviour | `docs/ARTIFACT_SELF_ASSESSMENT.md:173` — "VERIFIED BY ACTUALLY DOING IT, not by inspection: `git clone` to a fresh" |
| **verified-against-source** | referent is an external published document | `docs/VALIDATION.md:2898` — "Definitions verified in arXiv:2302.00394 `[fetched]`" |
| **`[externally-verified]`** (the tier) | **an external judge, on real data** | `docs/HANDOFF.md:109` — "external judge on real data confirms the IMPLEMENTATION" |

**The essential characteristic in conflict: EXTERNALITY OF THE JUDGE.** It is
essential to the tier — remove it and `[externally-verified]` collapses into
`[self-tested]`, which the project explicitly calls the weakest tier. It is
absent from the first two prose senses, where Claude checks its own work.

So the corpus uses one word for both the strongest and the weakest epistemic
positions it recognises. **The hypothesis is confirmed and understated** — it
predicted four senses split by referent; the sharper problem is that one sense
*is a defined tier* and the others are not, so prose "verified" silently reads
as tier language.

---

#### A2. **bound** — 119 occurrences
**Two concepts, no shared characteristic.**

| sense | essential characteristic | example |
|---|---|---|
| **honest bound** — a limit on what a claim licenses | scope restriction on an *inference* | `docs/HANDOFF.md:218` — "HONEST BOUND: real findings + real overlap, but the SARIF ENVELOPE was reconstructed" |
| **lower/upper bound** — a numeric limit on an *estimate* | direction of a quantity | `docs/SPEC_rule_provenance_measurement.md:212` — "Declared provenance is a **LOWER BOUND and can only ever be one.**" |

**Essential characteristic: whether the thing bounded is an INFERENCE or a
QUANTITY.** An honest bound has no numeric direction; a lower bound says nothing
about scope. Neither characteristic appears in the other.

---

#### A3. **control** — 97 occurrences
| sense | essential characteristic | example |
|---|---|---|
| **statistical control** — hold a confounder constant | a comparison group or covariate | `README.md:140` — "the size-matched controls that" |
| **control** — a mechanism that prevents a failure | an enforced constraint | `docs/HANDOFF.md` rule 11 — "THE CONTROL: … the header gets corrected in the same commit" |

**Essential: whether it operates on a MEASUREMENT or on a PROCESS.** Rule 11's
control cannot be size-matched; a size-matched control enforces nothing.

---

#### A4. **signal** — 158 occurrences
| sense | essential characteristic | example |
|---|---|---|
| **the consensus signal** — the thing being measured | a property of findings | throughout: "the headline consensus signal" |
| **signal gate** — the tool's own informativeness detector | a runtime component | `docs/HANDOFF.md:315` — "the signal gate correctly reports" |
| **stop signal** — a cue to the agent | a behavioural trigger | rule 11 — "quoting a number that contradicts your own thesis is a stop signal" |

**Essential: whether it is DATA, a COMPONENT, or an INSTRUCTION.** Three
different kinds of thing under one word.

---

#### A5. **gate** — 61 occurrences
`COMMIT GATE` (a procedure the agent executes) versus the `signal gate` /
dispersion gate (code that decides whether to report). **Essential: whether the
gate constrains the AGENT or the OUTPUT.**

---

### B. TWO TERMS, ONE CONCEPT

**B1 is the only clean case found. The status verbs are NOT synonyms — see the
falsified hypothesis in §5.**

#### B1. **honest bound** ≈ **BOUND** ≈ **HONEST BOUND** ≈ "stated bound"
Same concept, four surface forms, 14 occurrences of the phrase and 119 of the
head word. **Preferred: `honest bound`**, because it is the form the charter
uses when defining the obligation ("state its honest bound"), and the bare word
collides with A2's numeric sense.

#### B2. **pre-registration** / **pre-registered** / **decision rule fixed before computing**
10 + 55 + 14 occurrences. One concept: *criteria fixed before the result
exists*. **Preferred: `pre-registration`** for the artifact, `pre-registered`
for the property. "Decision rule fixed before computing" is a definition, not a
third term, and should stop being used as one.

#### B3. **stale** / **drift**
36 + 21. Near-synonyms in use, but **not** fully: `drift` is used for the
*process* and `stale` for the *state*. Weak case for B — recorded here as
provisional, because the corpus does occasionally use them interchangeably
("staleness accumulates" vs "drift accumulates"). **Preferred: `staleness` for
the state, `drift` for the accumulation.**

---

### C. CONCEPTS WITH NO TERM

#### C1. A claim recorded with **no retrievable evidence attached**
The project has hit this repeatedly and has no name for it.
- `analysis/EXTENDING.md:74` — "A number with no named script is not
  reproducible, and we have had one (the original 1.5x was run inline and lost)."
- `analysis/README.md:366` — "run inline and never written to a file"

It is not `[self-tested]` (nothing was tested), not `[unverified]` (that means
checked-and-failed), and not absence of a claim — the claim was *published*. The
nearest existing token is `[unconfirmed]`, which the corpus uses for something
else. **Unnamed.**

#### C2. **A number that reproduces exactly while its comparator was wrong**
- The `1,156` merge count reproduced perfectly as the `exact-line` component
  while the *total* had moved to 1,427 — the number was right and the
  denominator had changed underneath it.
- `p<0.0001` was arithmetically correct and tested the wrong null.

The project's word for this is currently a paragraph. **Unnamed**, and it is the
failure mode the corpus hits most often.

#### C3. **Reconciliation** — the sweep itself
`reconcile`/`reconciliation` appear 24 times, but almost always as the ordinary
verb. The *practice* — a systematic pass comparing every header against the tree
— is described in rule 11 and performed twice, but the noun is never defined as
a project term. Two occurrences of the unnamed practice in use:
- `docs/GENESIS_TEMPLATE.md:197` — "PENDING (reconcile before acting on any new
  message — I.3)"
- `docs/SESSION_HANDOFF_2026-07-26b.md` §2 — "Run a reconciliation sweep before
  starting anything."

#### C4. **The pessimistic-direction asymmetry**
Recorded as a numbered observation four times and named nowhere. It is a
property of the *document type*, not of any item.

#### C5. **Uninformative-not-clearance**
Used as a full sentence repeatedly ("a LOW number is UNINFORMATIVE, not
clearance"; "the zlib zero is UNINFORMATIVE AND MUST NOT BE READ AS CLEARANCE"),
never compressed to a term. It is a distinct epistemic state: *the measurement
ran, returned nothing, and the nothing carries no information.*

---

## PHASE 3 — MAP TO THE PUBLISHED VOCABULARY

**Source:** Wang Y. et al., *From Agent Traces to Trust: A Survey of Evidence
Tracing and Execution Provenance in LLM Agents*, arXiv:2606.04990. `[fetched]`

**Two corrections to the framing I was given:**
1. **The current version is v4** (submitted 3 June 2026, revised 28 June 2026),
   not v3.
2. **`Derive` is a PROV-compatible base relation, not an agent-specific one.**
   Verbatim: designers *"retain PROV-compatible base relations such as Use,
   Generate, and Derive, and add agent-specific relations needed for LLM
   execution: Support, Depend-on, Contradict, Invalidate, Trigger, and Update."*
   So the split is **3 PROV-compatible + 6 agent-specific = 9**, not "seven plus
   two". The brief placed Derive on the wrong side.

Verbatim on purpose: *"These relations separate semantic grounding from
procedural dependency. For example, a passage may Support a claim, a tool call
may Depend-on generated parameters, a new observation may Invalidate a plan, and
a failed action may Trigger recovery."*

| our concept | their relation | evidence |
|---|---|---|
| `[fetched]` / `[corroborated]` — a source backs a claim | **Support** | "a passage may Support a claim" — exactly the tier's job |
| rule lineage / ported rules / `source-rule-url` | **Derive** | a rule derived from an upstream rule; PROV-compatible |
| SARIF→our-claim chain; corpus→number chain | **Depend-on** | our numbers depend-on a corpus and a script |
| `WITHDRAWN` | **Invalidate** | claim marked epistemically invalid, record persists |
| `SUPERSEDED` | **Update** | a newer statement replaces an older one |
| conflicting measurements (0i vs 0j) | **Contradict** | two results in apparent conflict |
| a failure prompting a rule (rule 8a, 10, 11) | **Trigger** | "a failed action may Trigger recovery" |
| `[self-tested]`, `[externally-verified]`, `[standard-checked]` | **NONE** | tiers grade *strength of evidence*; no relation encodes strength |
| **honest bound** | **NONE** | scope limit on an inference; no counterpart |
| **size-matched control / comparator** | **NONE** | no relation for *what a claim was tested against* |
| **pre-registration** | **NONE** | temporal ordering of criteria vs result is unrepresented |
| `RETIRED` | **NONE** | not-current without being invalid or replaced |
| **uninformative-not-clearance** (C5) | **NONE** | a null that carries no information |
| **staleness / orphaning** (rule 11) | **NONE** | a record decaying relative to the world it describes |

### The three questions, answered

**1. Which of our concepts IS one of their relations under a different name?**
Five. `WITHDRAWN` **is** Invalidate. `SUPERSEDED` **is** Update. Rule lineage
**is** Derive. Tier `[fetched]`/`[corroborated]` **is** Support. A failure
prompting a new standing rule **is** Trigger.

The hypothesis about Invalidate is **confirmed**: the survey's Invalidate marks
a claim invalid *while the record persists*, and is explicitly distinguished
from PROV's `wasInvalidatedBy`, which ends an entity's existence. That is
precisely what `WITHDRAWN` does here — VALIDATION.md never deletes a withdrawn
claim, it banner-marks it in place.

**2. Which of their relations do we use constantly and have never named?**
- **Depend-on.** Every recorded number depends on a corpus, a script and a tool
  version. The project tracks this exhaustively — checksums, SWHIDs, pinned SHAs
  — and has no word for the relation itself.
- **Contradict.** The 0i-vs-0j episode and the §6.2 propagation were both
  contradiction-detection events, handled ad hoc each time with no shared name.
- **Trigger.** Rules 8a, 10 and 11 were each triggered by a specific failure.
  The pattern is visible only because each rule happens to record its own origin.

**3. Which of our concepts has no counterpart there — the contribution
candidates?** Separated deliberately, and I would not claim more than that
these are *unmapped*, not that they are novel:

- **Evidence STRENGTH as a graded scale** (the tier vocabulary). Their relations
  are typed but unweighted: Support does not distinguish a fetched standard from
  a sandbox pass. Our six-tier ordering has no counterpart.
- **The honest bound** — a first-class scope limit attached to a claim.
- **The comparator** — what a claim was tested *against*. This project's entire
  history is claims dying to better comparators, and no provenance relation
  encodes it.
- **Pre-registration** — the temporal relation *criteria fixed before result
  existed*, which is what makes a decision rule credible.
- **RETIRED** — not-current, not-invalid, not-replaced. Distinct from both
  Invalidate and Update.
- **Staleness/orphaning** — a record decaying relative to the world. Their model
  assumes the trace is written once and read as written.

---

## 4. HYPOTHESES — SCORED

| # | hypothesis | verdict |
|---|---|---|
| 1 | "verified" is list A with four senses | **CONFIRMED, understated.** Four senses found, but the sharper problem is that one *is a defined tier* while the others are prose. |
| 2 | tier scale underspecified at its edges | **CONFIRMED.** No tier exists for deductive-from-code-nothing-run; §6.1's original finding was exactly that and used prose. "`[self-tested]` analysis over `[externally-grounded]` inputs" occurs as an ad-hoc compound and is not in the six-tier scale. |
| 3 | withdrawn/retracted/superseded/corrected may be B | **PARTLY WRONG.** They are **not** synonyms — the test separates them cleanly (see below). And **"retracted" has ZERO occurrences**; it is not project vocabulary at all. |
| 4 | list C: reconcile, claim-with-no-evidence, number-with-wrong-comparator | **CONFIRMED, all three.** Recorded as C3, C1, C2. |
| 5 | every withdrawal is their Invalidate | **CONFIRMED**, including the contrast with `wasInvalidatedBy`. |

**On hypothesis 3, the distinguishing characteristics, since the hypothesis
asked for the test rather than the answer:**

| term | essential characteristic | claim wrong? | still in record? |
|---|---|---|---|
| `WITHDRAWN` (14) | the claim is **epistemically invalid** | yes | yes |
| `SUPERSEDED` (7) | **a successor exists** | not necessarily | yes |
| `RETIRED` (2) | **no longer current-state** | silent | yes |
| `OVERTURNED` (3) | a **conclusion reversed by evidence** | yes | yes |
| `CORRECTED` (9) | **the text was edited** — about the artifact, not the claim | n/a | n/a |

`CORRECTED` is in a different category from the other four: it describes an
operation on the document, not a status of the claim.

---

## 5. DRIFT NOTICED AND NOT FIXED (filed, per non-goals)

- **(a)** `SARIF` is treated as an ordinary standard name by the filter, but
  rule 10 gives "absent from SARIF" a project-specific epistemic meaning. The
  filter may have dropped a genuine concept.
- **(b)** `[checked]` (9), `[reconstructed]` (7), `[unconfirmed]` (7),
  `[unverified]` (6) and `[snippet]` (22) are bracket-form tokens in tier
  position that are **not in the six-tier scale** in HANDOFF §5 or
  VALIDATION.md's header. Either the scale is incomplete or these are informal.
  Not resolved here.
- **(c)** `docs/README_correction_0j_draft.md` is titled "draft" and is marked
  APPLIED internally — a filename/status mismatch.
- **(d)** `GENESIS_TEMPLATE.md` and `AUDIT.md` use `[externally-verified]` in
  ways that may predate the current definition; not audited.

None of these were acted on.

---

## 6. WHAT THIS PASS DOES NOT DO

No term was renamed, no conflict resolved, no `TERMS.md` written. Lists A and B
name conflicts; they do not settle them. The 58 concepts are one reading, by an
interested party, of a corpus that party largely wrote — which is the honest
bound on the whole document.
