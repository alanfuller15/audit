# Provenance fields — step 4 of 5, semantic layering

**Tier: `[self-tested]`.** A design. No field is populated for any existing
claim; no enforcement is built (step 5). Drift filed in §9.

---

## 0. SOURCES

Located from description, per rule 8a.

| source | retrieval-depth achieved | note |
|---|---|---|
| **W3C PROV-DM** (W3C Recommendation, 2013) | **primary** — w3.org/TR/prov-dm | all definitions below quoted from it |
| **Wang et al., "From Agent Traces to Trust", arXiv v4, June 2026** | **rendering** — arXiv HTML | §5.1 quoted verbatim; **Table 2 / Appendix A "Mapping to W3C PROV-DM" was NOT readable in the render I obtained** |

**A reflexive bound, recorded because this document defines the field that
records it:** the survey's PROV mapping is the one thing I was asked to re-read
and the one thing I could not reach. Its Appendix A exists and is titled
"Mapping to W3C PROV-DM"; its contents were not in the render. **So §6's mapping
is MY OWN, derived against PROV-DM directly — not a check against theirs.** In
this document's own vocabulary that artifact ref carries
`retrieval-depth: rendering`, `coverage: partial`.

Verbatim, load-bearing:

> **Entity** — "a physical, digital, conceptual, or other kind of thing with
> some fixed aspects; entities may be real or imaginary."
> **Activity** — "something that occurs over a period of time and acts upon or
> with entities…"
> **Agent** — "something that bears some form of responsibility for an activity
> taking place, for the existence of an entity, or for another agent's activity."

> **wasDerivedFrom** — "a transformation of an entity into another, an update of
> an entity resulting in a new one, or the construction of a new entity based on
> a pre-existing entity."
> **wasRevisionOf** — "a derivation for which the resulting entity is a revised
> version of some original."
> **wasAttributedTo** — "the ascribing of an entity to an agent."
> **wasInvalidatedBy** — "the start of the destruction, cessation, or expiry of
> an existing entity by an activity."

> **PROV declines to record quality.** "provenance…can be used to form
> assessments about its quality, reliability or trustworthiness. PROV itself
> does not evaluate or record quality metrics — it documents the lineage
> enabling users to make their own assessments."

> Survey §5.1: "Each memory write should carry source and lineage metadata,
> including **source type, timestamp, authoring agent, supporting evidence,
> transformation operation, confidence, and update history**."

---

## 1. WHERE THE SURVEY'S FRAMING BITES — STATED BEFORE ADOPTING ANYTHING

The survey models **execution provenance**: "the complete typed representation
of an **agent run**". A run is bounded, its agent is present, and its confidence
is computed at write time.

**A claim record is none of those things.** It persists across sessions, its
authoring agent is gone, and the question asked of it later is not *how did this
come to be* but **is it still true**.

Three consequences, each of which changes what we adopt:

| survey assumption | our reality | what changes |
|---|---|---|
| the agent is present and can be asked | the authoring session is gone; the next session inherits text | provenance must be **self-describing**, not reconstructable by asking |
| confidence is computed at write time | the world moves after write; rule 11 has three forms and eight instances of exactly that | we need **re-check time**, not just write time |
| "update history" is within one trace | our updates span sessions with different agents and months | revision must be **externally anchored** (version control), not narrated |

**So the survey's seven memory-write fields are adopted selectively.** Source
type, timestamp, authoring agent and update history transfer directly.
*Supporting evidence* is already ARTIFACT REF. *Transformation operation* is
already the re-derivation command. **`confidence` is deliberately NOT adopted as
a provenance field** — step 3 established that certainty is a property of the
inference, so storing it beside the artifact would rebuild the exact conflation
steps 2 and 3 took apart.

---

## 2. FIELDS ON A CLAIM

| field | records | writer | mutable | what goes stale if wrong |
|---|---|---|---|---|
| `asserted-at` | when the claim was first made | **hand**, once | **no** | nothing — immutable by construction, so it cannot decay |
| `asserted-by` | the session/commit that made it | **machine** (git) | no | attribution; who to ask, if anyone remains |
| `restated-at` | when the claim TEXT last changed | **machine** (git log for the claim's location) | auto | **the form-3 check** — if wrong, a correction that never re-derived its numbers goes undetected |
| `grounds-checked-at` | when the grounds were last re-derived | **machine**, written by the re-derivation command | auto | **form-3 false negative** — stale grounds look current |

> **[AMENDED BY §10, 2026-07-28 — both rows above.]** "The claim's location" is
> one line range in one file, and `grounds-checked-at` was a field on the CLAIM.
> Two timestamps derived from one file move together, so this pair is blind to
> form 3's recorded instance, where a claim was corrected in three documents
> while its grounds sat un-re-derived in a fourth. §10 moves
> `grounds-checked-at` onto an addressable GROUNDS record and ranges
> `restated-at` over the claim's **occurrences**, not one location. **Measured,
> not argued:** the amended check fires on the `1,131` case at the pre-fix
> commit where the rule above is silent.

`asserted-at` and `grounds-checked-at` are inherited from step 2 unchanged, as
instructed. **`restated-at` is the extension step 2's TIME needed and did not
have.**

### Why `restated-at`, and why it is machine-written
Step 2 promoted TIME on the argument that rule 11's third form is a divergence
between when a claim was corrected and when its grounds were derived. But step 2
stored only `asserted-at` — *first* assertion — which is not when the claim was
*corrected*. **The comparison form 3 requires was therefore not computable from
step 2's fields.** That is a gap in step 2, found by trying to populate it here.

It is machine-written because it already exists: the last commit touching the
claim's lines. Deriving it from version control rather than storing a hand-set
date means it cannot itself go stale — a hand-maintained `restated-at` would be
a record of when the record was updated, which is the failure mode in miniature.

**The form-3 check is then one comparison:**
```
grounds-checked-at  <  restated-at     →  D4 staleness fires
```
Both sides machine-written. No session has to remember.

> **[SUPERSEDED BY §10.]** It is still one comparison, but not between these two
> values. Both sides are now aggregates — `min` over the claim's grounds against
> `max` over the claim's occurrences — because the single-location form cannot
> see a divergence that lives between two files, which is the only form 3
> instance this project has actually recorded.

---

## 3. FIELDS ON AN ARTIFACT REF

Extending step 2's `locator` + `integrity` + `re-derivation command`.

| field | values | writer | mutable | what goes stale if wrong |
|---|---|---|---|---|
| `origin` | `fetched` · `in-repo` · `captured` · `supplied` · `absent` | machine where derivable from the retrieval channel, else hand | no | the claim's independence — a `supplied` artifact read as `fetched` hides rule 8 |
| `artifact-type` | `publication` · `standard` · `dataset` · `source-code` · `tool-output` | hand | no | authority — a paper read as a normative standard |
| `artifact-kind` | `captured` · `reconstructed` · `synthetic` | hand | no | **the 0.755 attribution error exactly** — a reconstructed SARIF envelope read as captured output |
| `retrieval-depth` | `primary` · `rendering` · `secondary` · `snippet` · `absent` | **machine sets a ceiling; hand may only lower it** (§4) | no | **instance 6 of rule 8a** — a secondary read as a primary |
| `retrieved-at` | timestamp | machine | no | link rot goes unnoticed |
| `coverage` | `full` · `partial` · `excerpt` | hand | no | a partial read presented as a complete one — this document's own §0 |
| `derived-from` | locator of the upstream artifact | hand | no | rule lineage; the 0f finding |

### Each justified against a failure it would have caught
- **`origin`** — rule 8: an inventor-supplied artifact treated as independently
  obtained. `supplied` makes that visible without argument.
- **`artifact-type`** — see §5: step 3's disposition for `[standard-checked]`
  has no home without it.
- **`artifact-kind`** — the ROC-AUC 0.755 attribution. The envelope was
  *reconstructed*; every downstream claim treated it as captured scanner output,
  and the correction consumed a session.
- **`retrieval-depth`** — rule 8a instances 1–6.
- **`coverage`** — this document. I read the survey's §5.1 and not its Appendix
  A, and without `coverage` that ref would look complete.
- **`derived-from`** — the semgrep rule that declares a FindSecBugs ancestor;
  PROV's `wasDerivedFrom` with a locator.

---

## 4. RETRIEVAL-DEPTH, DEFINED PROPERLY

The step's required question. **A field a session cannot assign is decorative**,
so each depth carries an operational test applied *at retrieval time*, and the
untrustworthy direction is machine-blocked.

| depth | operational test — answerable at retrieval | example from this project |
|---|---|---|
| **primary** | *Is the object I obtained the one its publisher issued, containing the full text or data I am citing?* | PROV-DM from w3.org; the Lipp corpus from its Zenodo DOI; our own `src/audit.py` |
| **rendering** | *Is this a faithful re-presentation of the primary, issued by someone else?* (HTML mirror, ar5iv, API abstract, cached copy) | the survey via arXiv HTML; the Chapman/Hawkins material via ar5iv |
| **secondary** | **Is the object I obtained itself citing something else for this claim?** | the Cochrane supplementary-advice page on publication bias (instance 6) |
| **snippet** | *Did I see only an extract selected by a third party, without surrounding context?* | a search-result summary |
| **absent** | *Did I fail to obtain it at all?* | the York PDF of Hawkins (font encoding); Springer (auth wall) |

**The `secondary` test is the one instance 6 needed and the one previously
missing.** All prior discipline asked "did you fetch it?" — instance 6 *was*
fetched, correctly, at a correct locator. The distinguishing question is not
whether you retrieved something but **whether what you retrieved is itself
citing**, which is visible on the page.

### Who assigns it: the machine sets a ceiling, the session may only lower it

Hand-assignment alone would be unreliable — a session that cannot tell it read a
secondary is exactly the session that will mark it primary. So:

```
retrieval channel                        machine-set CEILING
─────────────────────────────────────────────────────────────
web search result                        snippet
fetch of a non-publisher host            secondary
fetch of a known publisher/standards host  primary
file read inside this repository         primary
artifact absent / retrieval failed       absent
```

**The session may set the value at or below the ceiling, never above it.**
Over-claiming — the direction every recorded failure went — is structurally
impossible. Under-claiming remains possible and is the safe direction.

This does not make the field automatic; it makes the *error* one-directional.
That is the same shape as every other guard in this project: uncertainty
resolves toward the conservative side.

---

## 5. STEP 3'S DISPOSITIONS — CHECKED, AND ONE IS A DEFECT

The brief requires checking that step 3's tier dispositions are satisfiable.

| tier | step 3 said | satisfiable? |
|---|---|---|
| `[fetched]` | provenance field | **yes** — `origin: fetched` |
| `[corroborated]` | upgrade domain U3 | yes — not a field; needs ≥2 artifact refs, which §7 supports |
| `[externally-grounded]` | default input | yes — read off `origin` + `asserted-by` |
| `[externally-verified]` | default input | yes — same |
| `[self-tested]` | default input + D5 trigger | yes — same |
| **`[standard-checked]`** | **"provenance field (`origin: fetched`, `artifact-kind: published standard`)"** | **NO — DEFECT IN STEP 3** |

**The defect, reported rather than absorbed.** Step 3 assigned
`[standard-checked]` the value `artifact-kind: published standard`, but step 3's
own `artifact-kind` axis is `captured | reconstructed | synthetic` — how the
*data was produced*. "Published standard" is what the artifact *is*. Step 3
wrote a value into a field that could not hold it, because it defined the field
and the disposition in different sections and never populated one against the
other.

**Fix, made here:** `artifact-type` is a separate field (§3). `[standard-checked]`
becomes `origin: fetched` + `artifact-type: standard`. The two axes are
independent — a standard can be captured or reconstructed like anything else.

**This is a small instance of the failure this whole sequence is about:** a
disposition that looked complete because nothing had tried to use it. It was
found by populating the falsification set, not by re-reading step 3.

---

## 6. MAPPING TO PROV — AND WHERE WE EXCEED IT

| our field | PROV counterpart | note |
|---|---|---|
| `asserted-by` | **wasAttributedTo** | "the ascribing of an entity to an agent" — direct |
| `restated-at` | **wasRevisionOf** | a revision is "a derivation for which the resulting entity is a revised version of some original" |
| `derived-from` | **wasDerivedFrom** | direct |
| `origin` (partly) | **wasGeneratedBy** / **used** | an Activity generated or used the artifact |
| status `WITHDRAWN` | **wasInvalidatedBy** *(partial)* | PROV's is "the start of the destruction, cessation, or expiry" — ours does **not** destroy; the record persists. Same divergence step 1 recorded. |
| `retrieved-at` | Activity time | direct |
| `integrity` | **NONE** | PROV has no content-hash concept |
| `re-derivation command` | **NONE** | PROV records what *happened*, not a recipe to repeat it |
| `grounds-checked-at` | **NONE** | PROV timestamps generation and use; it has **no notion of re-checking an entity that already exists** |
| `retrieval-depth` | **NONE, BY DESIGN** | PROV: "does not evaluate or record quality metrics" |
| `artifact-kind`, `coverage` | **NONE, BY DESIGN** | same clause |

### The direction in which we exceed PROV differs from the survey's

The survey extends PROV **relationally** — it adds Support, Depend-on,
Contradict, Invalidate, Trigger, Update, which are *new edges between nodes*
within an execution.

**We extend PROV on two axes it explicitly declines and the survey did not
address:**

1. **Epistemic quality of the retrieval.** `retrieval-depth`, `artifact-kind`,
   `coverage` all record *how well we know what we think we know* about an
   artifact. PROV states outright that it "does not evaluate or record quality
   metrics" and leaves assessment to users. We record the assessment because
   ours is the failure mode: six attribution errors, none of which PROV could
   represent, because in PROV terms every one of them was a perfectly
   well-formed `used` edge to a real Entity.
2. **Validity over time after generation.** `grounds-checked-at` and
   `restated-at` exist to detect a record decaying relative to the world. PROV
   is retrospective-constructive — it answers *how did this come to be* — and
   has no vocabulary for *is it still so*. Neither does the survey, whose
   confidence is computed at write time within a bounded run.

**So: the survey adds edges; we add decay and doubt.** Both exceed PROV, in
different directions, for different reasons.

---

## 7. THE FALSIFICATION SET

Multiple ARTIFACT REFs per grounds are permitted; that is what makes cases 3
and 4 representable.

### Case 1 — the 1.5x
```
CLAIM   asserted-at        2026-07-26
        asserted-by        commit 2224b8b
        restated-at        2026-07-26 (machine, git)
        grounds-checked-at 2026-07-26 (machine, run_0j.py)
        → grounds-checked-at >= restated-at : D4 does not fire
ARTIFACT REF #1   locator          analysis/scripts/run_0j.py
                  origin           in-repo      artifact-type  source-code
                  artifact-kind    captured     retrieval-depth primary
                  coverage         full         integrity      git blob
                  re-derivation    AUDIT_CORPUS_ROOT=... python3 run_0j.py
ARTIFACT REF #2   locator          DOI 10.5281/zenodo.6515687
                  origin           fetched      artifact-type  dataset
                  artifact-kind    captured     retrieval-depth primary
                  coverage         full         integrity      sha256 manifest
```

### Case 2 — the fp:/rk: deduction
```
ARTIFACT REF      locator          src/audit.py :: _result_key
                  origin           in-repo      artifact-type  source-code
                  artifact-kind    captured     retrieval-depth primary
                  coverage         full         integrity      git blob
                  re-derivation    (none — the grounds are the text itself)
```
**`re-derivation` is legitimately empty for a DEDUCTION.** Nothing was run, so
`grounds-checked-at` cannot be machine-written — it falls back to the commit
that last touched the cited lines, which is `restated-at` of the artifact rather
than of the claim. **Noted as a wrinkle: for deductive grounds the two
timestamps collapse onto the same source, so D4 can never fire.** That is
correct — a proof does not go stale while its text is unchanged — but it means
D4 silently does not apply to an entire grounds kind, which §8 records.

### Case 3 — the Hawkins confidence-argument split
```
ARTIFACT REF #1   locator          ar5iv / search rendering of SSS 2011
                  origin           fetched      artifact-type  publication
                  retrieval-depth  rendering    coverage       excerpt
ARTIFACT REF #2   locator          search summary
                  origin           fetched      artifact-type  publication
                  retrieval-depth  snippet      coverage       excerpt
ARTIFACT REF #3   locator          www-users.york.ac.uk/~rdh2/papers/HawkinsSSS11.pdf
                  origin           fetched      retrieval-depth absent
                  note             obtained but not extractable (font encoding)
ARTIFACT REF #4   locator          Springer chapter
                  retrieval-depth  absent       note  auth wall
→ NO ref at depth `primary`.  Two independent refs agree (U3 available),
  but D5 fires on max-depth = rendering.
```
**This is the honest shape of C3's foundation**, and the fields say so without
narration.

### Case 4 — the publication-bias figure — **THE TEST**
```
ARTIFACT REF #1   locator          Cochrane group supplementary author advice
                  origin           fetched      artifact-type  publication
                  artifact-kind    captured     retrieval-depth SECONDARY
                  coverage         full
                  note             the page is itself citing GRADE for this claim
                  content          "publication bias: downgrade at most one level"
ARTIFACT REF #2   locator          gdt.gradepro.org/app/handbook Table 5.2
                  origin           fetched      artifact-type  standard
                  retrieval-depth  primary      coverage       partial
                  content          "publication bias: ↓ 1 or 2 levels"
→ TWO refs, DIFFERENT depths, CONTRADICTORY content.
  Resolution rule: the ref at the shallower depth loses.
```

### Does the field set distinguish case 4 from case 1? **Yes, on two fields.**
- `retrieval-depth`: case 1's refs are `primary`; case 4's ref #1 is
  `secondary`. That single value is the entire difference between "I read the
  source" and "I read someone reading the source".
- `artifact-type`: case 4's contradicting ref is a `standard`, which outranks a
  `publication` describing it.

**The failure that produced these fields is representable in them.** Had ref #1
carried `retrieval-depth: secondary` at the time it was quoted, the disagreement
with a primary would have been predictable rather than discovered.

---

## 8. WHAT THE FIELDS CANNOT RECORD

1. **Whether a secondary source's summary is FAITHFUL.** `secondary` says the
   page is citing; it does not say whether it cited correctly. In case 4 the
   Cochrane page may be accurately reporting a different GRADE edition. The
   fields locate the disagreement and cannot adjudicate it.
2. **Why two refs disagree.** §7's resolution rule (shallower loses) is a
   convention, not an explanation, and it would be wrong if the deeper source
   were an outdated edition.
3. **Mixed-provenance artifacts.** A corpus we assembled from fetched parts and
   local builds has one `origin` and several truths. OWASP-with-`target/classes`
   is `fetched` upstream and `in-repo` after building; the field forces a choice.
4. **Liveness.** Nothing records whether an artifact is *still* at its locator.
   SWHIDs mitigate for archived repos and nothing covers the rest — and link rot
   is a decay the whole design is otherwise built to catch.
5. **D4 for deductive grounds** (case 2). With no re-derivation command,
   `grounds-checked-at` collapses onto the artifact's own revision date, so the
   staleness domain cannot fire for an entire grounds kind. Defensible — a proof
   does not decay — but it is a silent exemption, not a stated one.
6. **Provenance of the provenance.** No field records *who assigned*
   `retrieval-depth` or when. The ceiling rule (§4) constrains the error
   direction; it does not create an audit trail for the judgment itself.
7. **The authoring agent's identity beyond a commit.** `asserted-by` is a git
   commit. Which model, which session, under what instruction — none of it is
   recoverable, and the survey's "authoring agent" assumes more than we can
   supply.

---

## 9. DRIFT NOTICED, NOT FIXED

- **(a)** ~~Carried unfixed through steps 2, 3 and now 4:
  `VALIDATION.md:3110` still reads "P(size-matched control >= multi) = 0.0000
  SURVIVES" and "highly significant", language the 0j work withdrew.~~
  **CLOSED 2026-07-28** — forward-pointer banner added at the overturned entry,
  per the rule VALIDATION.md derived for itself at §"THE CENTRAL OPEN QUESTION".
  The residue's note that the section was "banner-marked further up" was wrong:
  it had no banner, and the withdrawal sat ~300 lines below under a heading
  sharing no vocabulary with it — the same shape as the failure that rule exists
  to prevent.
- **(b)** ~~Carried unfixed through steps 1–4: `docs/AUDIT.md` and
  `docs/GENESIS_TEMPLATE.md` use `[externally-verified]` in senses that may
  predate the current definition.~~
  **CLOSED 2026-07-28** — audited. The drift is specific: all three sites (and
  `VALIDATION.md:15`, which none of the five filings named) define
  `[externally-verified]` as *"a non-Claude engine/judge against non-Claude
  input"*, which is verbatim HANDOFF §5's test for **`[externally-grounded]`**.
  The two tiers collapse into one, licensing the stronger label on the weaker
  evidence. Conformed to HANDOFF §5 in `AUDIT.md` and by note in `VALIDATION.md`;
  `GENESIS_TEMPLATE.md` III.7 is ratified charter text and was annotated, not
  amended. **Scoped out, deliberately, and not a sixth filing because it is a
  different item:** the four sites where the tier is *asserted*
  (`VALIDATION.md:436/447/489/568`) were not re-audited. 436/447/489 sit inside
  the 2026-07-26 SUPERSEDED banner; **568 does not**, and restates the retired
  tier without a marker. That is the one live residue of this item.

---

## 10. S1's CROSS-FILE BLINDNESS — THE DEFECT, THE FIX, AND WHAT IT COSTS

> **[THE THREAD THIS FEEDS WAS STOPPED 2026-07-28 — read before implementing
> anything here.]** This amendment is **correct and unpopulated, and will stay
> that way**. The population thread closed (HANDOFF §7 item 9), partly *on the
> evidence in §10.5*: the amended check fires on its motivating case and is
> 3-for-3 false on a clean tree. **This section is not a to-do.** It is retained
> because it is the measurement that closed the thread, and because §10.2's
> `signature`-vs-`anchor` distinction is the transferable finding. See
> RECONCILIATION.md §13 for what is in use and what is specified-and-unused.

**This section amends §2 and §3.** It exists because the population pilot ran S1
against the case S1 was designed for and S1 was silent (POPULATION_PILOT.md §4).

### 10.1 The defect, stated exactly

§2 specified the form-3 check as one comparison:

```
grounds-checked-at  <  restated-at
```

Both values are derived from **the same file**, because `restated-at` is
"git log for the claim's location" and a location is one line range in one
document. **Two timestamps computed from one file move together.**

Form 3's recorded instance does not have that shape. Commit `80d1817` — "Correct
a false claim that reached the README, at its source and everywhere it spread" —
touched `README.md`, `docs/HANDOFF.md` and `docs/NEGATIVE_RESULT.md`, and **did
not touch `docs/VALIDATION.md` at all**, where the grounds lived. So at the
record owning the grounds, nothing was textually restated, `restated-at` never
advanced, and S1 was silent at precisely the place the number needed re-deriving.

**The claim is one thing; the record of it is many. §2 modelled the record.**

### 10.2 The change

Three amendments. The first is the one the handoff identified; the second is
what makes it operable; the third is what the run forced.

**(1) GROUNDS become addressable.** `grounds-checked-at` moves off the CLAIM
(§2) and onto the GROUNDS, which gains a `grounds-id`. A claim references
grounds by id. One grounds record can serve several claims in several files, and
re-deriving it updates one timestamp that every referencing claim sees. Under
§2, N copies of a claim carried N independent `grounds-checked-at` values for
one derivation — which is the sidecar-drift failure (D1) inside a single field.

**(2) CLAIM gains `occurrences`, and `restated-at` ranges over all of them.**

```
occurrences  = every tracked line matching the claim's SIGNATURE
restated-at  = max( blame(occurrence) for occurrence in occurrences )

S1 fires when:   min(grounds-checked-at over the claim's grounds)
                   <  max(restated-at over the claim's occurrences)
```

**(3) SIGNATURE is a new field, and it is NOT the pilot's `anchor`.** The pilot
reused `locator.anchor` to find occurrences. That was wrong and the run proved
it: an anchor's job is to re-find one claim in one file after edits shift line
numbers; a signature's job is to match every restatement corpus-wide and nothing
else. `anchor` is chosen for local findability, `signature` for corpus-wide
distinctiveness. **Operational test, applied at population time, in the same
shape as §4's retrieval-depth ceiling:** grep the candidate signature across the
tree and read the hits. If any hit is a line the session would not call a
restatement of this claim, the signature is wrong and must be narrowed before
the claim is stored. The occurrence count is reported at population time so the
test cannot be skipped by not looking.

### 10.3 Why not the alternatives

- **Hand-listing occurrences.** Rejected. It inherits D3's unverifiability
  multiplied by N, and it fails in one specific direction: a hand-listed set
  misses exactly the copy nobody remembered making, which is the failure. The
  `1,131` run below found a third occurrence in `SPEC_java_admission.md` that
  the pilot — which had studied this case closely — did not know existed.
- **Designating one line per claim.** Already rejected and still rejected; see
  SESSION_HANDOFF_2026-07-28 §2. This amendment is what that section said the
  problem actually needed.

### 10.4 False-positive modes — STATED BEFORE THE RUN, then measured

The mechanical layer's lesson (SESSION_HANDOFF_2026-07-28 §4) is that pre-stating
FP modes catches the category visible from filenames and misses the ones that
come from the *semantics of the matched string*. Stated in advance:

| | predicted mode | predicted because |
|---|---|---|
| **FP-A** | **signature overloading** — the string means something else elsewhere | the `checks` case: 30 findings, essentially all false |
| **FP-B** | **quotation, not assertion** — a document quoting the claim as a worked example counts as an occurrence and carries a fresh blame | RECONCILIATION §12's FP-3 |
| **FP-C** | **self-inflicted by this project's own conventions** — a forward-pointer banner added by a reconciliation sweep is a new occurrence dated today | the banners at VALIDATION.md 434 / 2078 / 3789, and the one added today for §9(a) |
| **FP-D** | **D2 amplified N-fold** — a typo fix at ANY occurrence advances `restated-at` | D2's known cost, times the occurrence count |

### 10.5 What the run actually found

`analysis/scripts/s1_crossfile.py`, over the 12 populated claims.

**The motivating case, replayed at `e524c60d` (the commit before the fix):**

```
C07  1,131 denominator        FIRED     3 occurrences
     docs/VALIDATION.md:908         2026-07-26T02:52:03  adf2a0d3   <- grounds live here
     docs/HANDOFF.md:1211           2026-07-26T03:01:05  a82702eb
     docs/SPEC_java_admission.md:160 2026-07-26T03:06:35 0821044d   <- restated-at
     grounds-checked-at 02:52:03  <  restated-at 03:06:35  => FIRES
     (old S1, same commit, same claim: SILENT)
```

**The amendment does what it was written to do, on the case that motivated it.**
It also shows the propagation was wider than recorded: three files, not the two
POPULATION_PILOT §4 identified.

**On the current tree: `fired 3 · silent 7 · unassessable 1 · malformed 1`.**
Adjudicated, **all three firings are false positives**, and they are the
predicted modes rather than new ones:

| claim | occ | why it fired | mode |
|---|---|---|---|
| C12 `source-rule-url` | **30, then 31, then 32 — see below** | the signature is a FIELD NAME discussed across 9 documents (`SPEC_rule_provenance_measurement.md` alone: 12) | **FP-A** |
| C09 `0f REGISTRY ARM` | 5 | the signature is a SECTION HEADING, so every cross-reference to the section is an occurrence | **FP-A** |
| C06 `ZERO cross-tool merges` | 5 | newest hit is `EVIDENCE_SCALE.md:357`, which *quotes* the claim as a worked example in step 3 | **FP-B** |

**FP-C fired while this section was being written, three times, and that is the
most useful result here.** C12's occurrence count went **30 → 31 → 32** over the
course of writing this one section: 31 when §10.4 named `source-rule-url` as an
example of an overloaded signature, 32 when the paragraph you are reading named
it again. **The document predicting the false-positive mode created an instance
of it, then created another by describing the first, in under an hour, without
leaving the file.** No number is quoted for C12 above because the number is a
function of how much this project writes about C12 — which is the finding. The
general form:
*any reconciliation convention that writes about a claim — a banner, a worked
example, a post-mortem — is indistinguishable from a restatement of it under a
grep.* This is not a bug in the check; it is a real property of a corpus that
documents its own failures in the same tree it stores its claims in.

**FP-D was not exercised** — recorded so the next session knows which modes are
measured and which are still only predicted.

**The honest reading: 1 true positive on the historical case, 3 false positives
on the current one, and every false positive traces to the SIGNATURE, not to the
timestamp comparison.** That is why (3) above is a field and not a footnote. It
also settles a question §5 left open: this amendment **strengthens** the case for
S1 being SEMI-mechanical. It raises recall on the failure that motivated the
whole design and raises the false-positive rate at the same time. A check whose
output is 3-for-3 false on a clean tree must never be allowed to act without a
reader.

### 10.6 A record defect the run exposed

`claims.json` stored C02's `grounds-checked-at` as
`"2026-07-26T01:57:16-08:00 (DECISION_4)"` — a timestamp with a provenance note
glued onto it. No machine check can read it. The pilot reported **1**
unassessable claim; the true figure is **1 unassessable + 1 malformed**, and
those are different things: absent grounds is a fact about the claim, an
unreadable field is a defect in the record. The check now reports them
separately, because collapsing them would let a record defect hide inside an
honest "we cannot know".

### 10.7 What this does NOT fix

1. **The deductive exemption (§8.5) is untouched.** D4/S1 still cannot fire for
   `grounds.kind = DEDUCTION`. Occurrences do not help: the exemption is about
   the grounds having no re-derivation, not about where they live.
2. **C03 remains unassessable.** A claim whose evidence was never retained has
   no `grounds-checked-at` to compare against, however many occurrences it has.
   S1 is still silent on the class of claim most likely to be stale.
3. **Occurrence discovery is only as good as the signature**, and choosing a
   signature is J3/J4-adjacent reading, not machine work. This amendment
   therefore **raises** per-claim population cost — a twelfth field, and one
   with a corpus-wide grep and a read of its hits attached.
4. **Nothing yet checks that a stored occurrence set is still current** — the
   sidecar-drift gap (D1) now has a second surface.
