# Claim structure — step 2 of 5, semantic layering

**Tier: `[self-tested]`.** A design, not a measurement. Nothing here has been
applied to the corpus beyond the six falsification cases, and no external
reviewer has checked it.

**Design only.** No scale, no tier assignments, no `TERMS.md`. Drift noticed is
filed in §7, not fixed.

---

## 0. SOURCE CHECK — two of the four given IDs are wrong

Reported before use, per instruction.

| given | verdict |
|---|---|
| GSN elements/connectors and its traceability limitation (arXiv:2403.15236 §2.2) | **taken as given**, as instructed |
| Toulmin's six-element layout | **taken as given**, as instructed |
| **arXiv:2402.12804** for ISO/IEC 15026 | **WRONG PAPER.** That ID is *Modular Assurance of Complex Systems Using Contract-Based Design Principles*, McGeorge & Glomsrud (DNV), v2, 8 Aug 2024. It concerns contract-based design and assurance-case modules. I could not locate ISO/IEC 15026 in it — the HTML render 404s and my text extraction of the PDF failed on font encoding, so this is "not found", not "confirmed absent". **The 15026 framing is NOT used below.** |
| **arXiv:2003.05388** for assured safety arguments | **WRONG PAPER.** That ID is *A Methodology for Automating Assurance Case Generation*, Ramakrishna et al., v1, 11 Mar 2020. It does not define assured safety arguments. |

**The confidence-argument split is real, and the source is Hawkins, Kelly, Habli
& Calinescu, "A New Approach to Creating Clear Safety Arguments", SSS 2011.**
Retrieved definition: *assured safety arguments are "a new structure for arguing
safety in which the safety argument is accompanied by a confidence argument that
documents the confidence in the structure and bases of the safety argument",*
separating "the major components that have traditionally been confused within a
single safety argument structure".

**BOUND ON THAT QUOTE:** obtained from a search summary and a Springer listing,
corroborated across two retrievals. The York PDF and the Springer chapter page
both defeated extraction (font encoding; auth redirect). I have **not** read the
publisher's bytes. C3 is decided on a corroborated-but-not-primary reading, and
that is weaker ground than the rest of this document.

---

## 1. THE STRUCTURE

Ten parts. Each is justified in §2 by a case that fails without it.

```
CLAIM ─────────────┬── asserts ────────────────── what is being said
   │               ├── kind ───────────────────── DESCRIPTIVE | PROSCRIPTIVE
   │               └── status ─────────────────── LIVE | WITHDRAWN | SUPERSEDED | RETIRED
   │
   ├── GROUNDS ────── the evidence, by kind:  OBSERVATION | DEDUCTION | REPRODUCTION
   │      └── ARTIFACT REF ── locator + integrity + a re-derivation command
   │
   ├── WARRANT ────── why these grounds license THIS claim
   │      └── ESTIMAND ── the quantity actually measured
   │
   ├── COMPARATOR ─── what the claim was tested AGAINST
   │
   ├── QUALIFIER ──── the force the grounds confer, in virtue of the warrant
   │
   ├── BOUND ──────── the scope beyond which the claim is not licensed
   │
   ├── DEFEATER ───── a stated condition under which the claim would fail
   │
   ├── SUCCESSION ─── forward/back pointers when status ≠ LIVE
   │
   └── TIME ───────── asserted-at          when the claim was made
                      grounds-checked-at   when the grounds were last re-derived
                      (machine-written by the re-derivation command, not by hand)
```

Plus one structure that is **not** part of a claim:

```
CONFIDENCE ARGUMENT ── a separate argument about whether the claim's own
                       argument is sound. Adopted; see §3.
```

`CORRECTED` is deliberately absent. Step 1 established it is an **operation on
the document**, not a status of a claim. It belongs in version control, which
already records it.

---

## 2. JUSTIFICATION PER PART — each named against a case that needs it

**CLAIM.asserts** — Toulmin's claim, GSN's Goal. Needs no defence.

**CLAIM.kind (DESCRIPTIVE | PROSCRIPTIVE)** — required by **case 6**. "Adding
scanners is the wrong lever" is not a statement about the world that could be
true or false; it is advice about what to do. It can be *right* while every
descriptive claim under it is *uncertain*, and it can survive its supporting
findings changing. Neither GSN nor Toulmin distinguishes these: GSN's Goal and
Toulmin's claim both cover "X is true" and "do not do X" without marking which.
Collapsing them is how a finding becomes a policy without anyone deciding to
promote it.

**CLAIM.status (LIVE | WITHDRAWN | SUPERSEDED | RETIRED)** — required by **case
4**, and carried forward from step 1, where these were shown to be three
distinct concepts rather than synonyms: *invalid* / *has a successor* / *not
current*. A single `deprecated` flag cannot represent them.

**GROUNDS.kind (OBSERVATION | DEDUCTION | REPRODUCTION)** — required by **case
2**. The fp:/rk: finding is a *proof from the code*: nothing was executed, and
executing something would not have strengthened it. GSN's **Solution** is
defined as "a reference to an evidence item" — a proof is not an evidence item
in that sense, and Toulmin's grounds are conventionally the facts adduced.
Without this distinction a deduction must masquerade as a weak observation.
REPRODUCTION is separate again: **case 5**'s zlib zero was re-run after the
mechanism changed, and re-deriving a number is not the same act as first
observing it.

**GROUNDS.ARTIFACT REF** — required by **C2 of the design constraints** and by
step 1's list-C item *"a claim recorded with no retrievable evidence attached"*.
GSN cannot do this and says so. See §4.

**WARRANT** — Toulmin's warrant. Required throughout, but decisive in **case
2**, where the same grounds license one claim strongly and another weakly. Its
presence is what makes the qualifier a property of the inference rather than of
the evidence (§3, C1).

**WARRANT.ESTIMAND** — required by **case 3**, and it is the part I would most
expect a reviewer to argue with. In case 3 two results appeared to contradict
each other and did not: one fitted a linear slope, the other a binary contrast.
Both warrants were valid; they warranted *different claims*. Naming the estimand
inside the warrant is what makes the non-contradiction visible without a
separate rebuttal. Step 1 found `estimand` occurs 3 times in 10,267 lines — the
project has the concept and almost no word for it.

**COMPARATOR** — required by **case 1**, and it is the part with no counterpart
in either source model. The 1.5x is meaningless without "against size-matched
single-tool functions". This project's history is claims dying to better
comparators — five of them — and neither GSN nor Toulmin has a slot for *what
the claim was tested against*. Toulmin's backing supports the warrant, not the
contrast. I considered folding it into grounds and rejected that: the
comparator is not evidence *for* the claim, it is the alternative the claim had
to beat.

**QUALIFIER** — Toulmin's qualifier, "the degree of force which the grounds
confer on the claim in virtue of the warrant". Required by **case 1** (an
interval touching 1.0) and **case 2** (deductively certain for one claim, weak
for another). Step 2 does not populate it; step 3 does.

**BOUND** — required by **case 1**. "Nine projects; the interval touches 1.0x"
is not a qualifier — it does not weaken the claim within its scope, it says
where the scope ends. Toulmin has no element for it. GSN's **Context** is the
nearest, but Context is defined as "a contextual artefact — a statement or a
reference", i.e. what the claim is *relative to*, not what it *does not extend
to*. Related but not the same, so BOUND is its own part.

**DEFEATER** — Toulmin's rebuttal, "a situation in which the claim might be
defeated". Required by **case 5**: the zlib conclusion had a stated mechanism,
the mechanism was refuted, and the conclusion survived on a different one. That
is only expressible if the condition-of-failure is recorded separately from the
grounds. Note Toulmin's rebuttal "is itself an argument" — so a defeater may
carry its own claim structure, recursively.

**TIME (asserted-at, grounds-checked-at)** — **PROMOTED from §6 on the second
pass. The argument is from the corpus and it is stronger than I first judged.**

Rule 11 now has **three forms and eight instances** (verified in HANDOFF, not
recalled). Every form is a statement about time:

| form | what decayed | the temporal question it needed |
|---|---|---|
| staleness — wrong text | text written at T1, world moved by T2 | when was this last checked against the tree? |
| orphaning — missing text | document created at T1, index never updated | when was reachability last verified? |
| **correction that never re-derives** | **claim corrected at T2, numbers derived at T1** | **do the grounds predate the claim's last correction?** |

**The third form settles the design question.** Its own description: *"TEXT THAT
IS NOW CORRECT CARRYING NUMBERS THAT WERE NEVER RE-DERIVED"*, and it is recorded
as harder to catch than the other two because *"the sweep reports success
honestly"* — nothing in the record is false. The morning's pass corrected the
co-location claim genuinely everywhere and carried `1,131` and `1,164 findings
(0.18%)` through untouched; both were wrong.

That failure is exactly **a divergence between two timestamps that nothing
recorded**. The claim's time advanced; the grounds' time did not. So:

- **asserted-at alone cannot represent it** — the claim was correctly updated.
- **grounds-checked-at alone cannot represent it** — the grounds were never
  wrong at the time they were derived.
- **Both are required, and the diagnostic is the ORDERING between them:**
  *grounds-checked-at older than the claim's last correction* is the signature
  of form three, and it is machine-checkable.

**Is grounds-checked-at derivable from ARTIFACT REF's re-derivation command
rather than stored? NO — and the distinction matters.** The command records
*how* to re-derive, not *when* it last happened. Deriving it on demand means
running the command, which is the very act that form three shows nobody performs
— a value available only to whoever thinks to look is no control at all. What
makes it a control is that the **stored** value visibly ages next to a claim
that has moved.

**The cost, stated because promoting this creates a new failure surface:** a
timestamp is itself a record that can go stale, so a hand-maintained one would
make the structure subject to its own dominant failure mode. The design answer
is that **`grounds-checked-at` is written by the re-derivation command when it
runs**, never by hand. `asserted-at` is hand-set once and never updated, so it
cannot decay. This ties TIME to ARTIFACT REF and keeps the only mutable
timestamp machine-owned.

**I considered leaving it in §6 and concluded that would be wrong.** A structure
for *this* project that cannot express when a claim's grounds were last checked
cannot represent the failure mode it hits most — three named forms, eight
instances, and the most recent one found by the next sweep on the same day.

**SUCCESSION** — required by **case 4**. VALIDATION.md's own convention is that
"the OVERTURNED entry gets the forward pointer", so the pointer lives on the
superseded claim, not only on the new one.

### GSN and Toulmin elements that earn no place

| element | verdict |
|---|---|
| GSN **Strategy** | **EARNS A PLACE, renamed.** Strategy is "the nature of the INFERENCE between a goal and its supporting goals" — that is exactly WARRANT. Kept as WARRANT because Toulmin's name is the one that carries the qualifier relationship C1 depends on. |
| GSN **Solution** | **Subsumed** by GROUNDS + ARTIFACT REF, and deliberately widened: Solution cannot represent a deduction (case 2). |
| GSN **Context** | **NO PLACE as a distinct part.** Its two jobs split: what the claim is relative to → ESTIMAND and COMPARATOR; what it does not extend to → BOUND. Keeping Context as well would leave every claim with an under-specified catch-all. |
| GSN **Assumption** | **NO PLACE.** In this corpus, unexamined assumptions are exactly what fails — the pessimistic-header asymmetry, the circular size proxy. Giving them a first-class slot legitimises leaving them unexamined. An assumption here must be written as a BOUND (it limits the claim) or a DEFEATER (it could fail). This is a deliberate departure from GSN and I would defend it as a project-fit decision, not a general improvement. |
| GSN **Justification** | **NO PLACE.** "A statement of rationale" is what WARRANT already is. |
| GSN **Undeveloped** | **NO PLACE as a claim part** — it is a *board* state (open item), already tracked in HANDOFF. Marking a claim undeveloped inside the claim confuses "not yet argued" with "argued weakly", which QUALIFIER handles. |
| Toulmin **Backing** | **NO PLACE, and this is the closest call.** Backing assures the warrant's trustworthiness — which is precisely the *confidence argument* (§3). Rather than a field inside the claim, it becomes the separate structure Hawkins et al. describe. If C3 were rejected, Backing would have to return as a field. |

---

## 3. THE THREE DESIGN CONSTRAINTS, ANSWERED

### C1 — a tier is a property of the INFERENCE. **Constraint accepted; current practice does not satisfy it.**

Toulmin's qualifier is the force grounds confer *in virtue of the warrant*. Our
tiers attach to evidence: `[fetched]` describes where a source came from,
`[self-tested]` describes who ran the test. Neither mentions the claim.

Case 2 is the demonstration. One artifact — the `_result_key` source — grounds
two claims:

- *"an `fp:` key can never equal an `rk:` key"* — deductively certain
- *"the headline consensus signal is inert in the shipped product"* — a
  prediction about behaviour on unseen inputs, which was later **refuted in its
  mechanism** while surviving in its conclusion (case 5)

Same grounds, same evidence tier, radically different force. **Any scale that
attaches to GROUNDS alone cannot separate these.** So this structure puts
QUALIFIER on the claim and makes WARRANT mandatory, so that the qualifier has
something to be *in virtue of*.

I am not carrying the existing tier vocabulary forward into that slot, because
step 3 is where a scale gets designed and I was told not to design one. What
step 2 fixes is only the *location*: the qualifier hangs off the inference.

**Consequence, stated because it is a cost:** the six existing tiers cannot be
lifted into QUALIFIER unchanged. `[fetched]` is a property of an artifact and
belongs on ARTIFACT REF; only something like "how strongly does this warrant
carry" belongs on QUALIFIER. Step 3 inherits that problem.

### C2 — artifact traceability. **SACM's approach adopted, in reduced form.**

GSN cannot do it: *"GSN and CAE permit only structured arguments and not
external artifact traceability."* Our evidence is scripts, corpora, checksums
and SWHIDs, so a Solution that names evidence without locating it is
insufficient — and step 1 recorded a case where exactly that lost a published
number (the original 1.5x, "run inline and never written to a file").

Adopted from SACM:
- **ArtifactPackage → ARTIFACT REF.** Every ground carries a locator, an
  integrity value, and a re-derivation command. This is already the de-facto
  practice (`analysis/README.md` §4's checksums, §3a's SWHIDs) and the design
  only makes it structural.
- **ImplementationConstraint → the re-derivation command.** SACM's constraints
  are executable rules run to evaluate whether evidence still holds; ours is a
  command that reproduces the number. The clean-clone test is that mechanism
  used once by hand.

**Not adopted:** SACM's full package model (AssuranceCasePackage /
ArgumentPackage / TerminologyPackage). TerminologyPackage is what steps 1 and 4
are building, and importing SACM's container hierarchy would add three levels of
nesting for a repository with one assurance case. Deferred rather than rejected.

### C3 — the confidence-argument split. **ADOPTED.**

Hawkins et al.'s structure separates the argument for a claim from the argument
that the first argument is trustworthy. Two reasons to take it here, both from
this project's own history:

1. **Case 5 is unrepresentable without it.** The zlib conclusion survived while
   its mechanism was refuted. In a single structure that reads as a claim whose
   grounds were withdrawn but which stayed LIVE — incoherent. With the split, the
   *claim* kept its status and the *confidence argument* was rebuilt on a
   different mechanism.
2. **The project already writes confidence arguments and calls them nothing.**
   Rule 11's asymmetry analysis, the three-independent-negative-biases section,
   the "instrument works, S4=0 is real" check — all are arguments about whether
   an argument can be trusted, not evidence for a claim.

**Consequence: a claim's argument and its tier are two structures, not one
field**, exactly as C3 anticipated. The qualifier is the *output* of the
confidence argument, not a label pasted on the claim.

**And the honest cost:** this is decided on a corroborated-but-not-primary
reading of Hawkins (§0). If the primary source turns out to define the split
differently, C3 should be revisited — the two project-internal reasons above
would still stand on their own, but the borrowed structure would not.

---

## 4. THE SIX REPRESENTATIONS

### Case 1 — the 1.5x
```
CLAIM     asserts  functions flagged by >=2 tools are ~1.5x more likely to
                   contain a real CVE than size-matched single-tool functions
          kind     DESCRIPTIVE
          status   LIVE
GROUNDS   kind     REPRODUCTION (0j re-derived a prior session's inline result)
          artifact analysis/scripts/run_0j.py
                   corpus: Lipp, DOI 10.5281/zenodo.6515687
                   integrity: sha256 manifest, analysis/README.md §4
                   re-derive: AUDIT_CORPUS_ROOT=... python3 run_0j.py
WARRANT            multi-tool and single-tool functions matched on size differ
                   only in tool count, so a rate difference is attributable to
                   tool count
          estimand P(vulnerable | n_tools>1) / P(vulnerable | n_tools=1),
                   BINARY contrast — not a per-tool slope
COMPARATOR         size-matched single-tool functions (NOT: all single-tool
                   functions, which gives 2.67x)
QUALIFIER          [step 3]
BOUND              nine projects; project-bootstrap 95% CI [0.99x, 2.58x];
                   threshold not a score — flat at 3 tools, lower at >=4
DEFEATER           if the size control were coarser than the confound, the
                   effect would be residual confounding. TESTED: strata refined
                   10->200, effect stable. Defeater discharged, retained.
SUCCESSION         supersedes the p<0.0001 variant (status WITHDRAWN)
TIME      asserted-at         2026-07-26 (0j)
          grounds-checked-at  2026-07-26, machine-written by run_0j.py
                              — equal, so no form-three divergence
```

### Case 2 — the fp:/rk: collision
```
CLAIM A   asserts  an `fp:`-prefixed key can never equal an `rk:`-prefixed key
          kind     DESCRIPTIVE ; status LIVE
GROUNDS   kind     DEDUCTION          <-- the part GSN's Solution cannot hold
          artifact src/audit.py `_result_key`, read not run
WARRANT            distinct literal prefixes cannot produce equal strings;
                   property of the key construction, not of any sample
QUALIFIER          [step 3] — but note: deductive, so nothing observable
                   could raise or lower it
BOUND              holds for this key construction only

CLAIM B   asserts  the headline consensus signal is inert in the shipped product
          kind     DESCRIPTIVE ; status SUPERSEDED
GROUNDS   same artifact as CLAIM A, plus n_tools distribution {1: 15}
WARRANT            if no two findings can share a key, no merge can occur, so
                   n_tools>1 is unreachable
DEFEATER           the warrant assumes the key construction is the ONLY
                   blocker. FIRED — item 2 split the key and the claim's
                   conclusion survived on a different mechanism (case 5)
SUCCESSION         forward -> HANDOFF §6.1 corrected block
```
**Same grounds, two claims, different force — C1 demonstrated.**

### Case 3 — the estimand mismatch
```
CLAIM X   asserts  n_tools carries no precision signal once size is controlled
          grounds  0i logistic, linear slope   b=+0.057, p=0.582
          warrant.estimand   d(log-odds)/d(n_tools), LINEAR
          status   WITHDRAWN — the estimand did not match the question asked

CLAIM Y   asserts  multi-tool functions are ~1.5x more likely (case 1)
          warrant.estimand   binary multi vs single contrast
          status   LIVE

RELATION  NOT a contradiction. Both warrants valid; different estimands.
```
**Decision, as asked: this is NEITHER Toulmin's rebuttal NOR GSN's Context.**
A rebuttal is a condition under which a claim fails — neither claim fails here.
Context is what a claim is relative to — but the two claims share their context
entirely (same corpus, same units, same control). What differs is *the quantity
each measured*, which is why ESTIMAND is a field of the warrant rather than a
relation between claims. The apparent conflict dissolves at the point where the
warrants are compared, and needs no relation of its own.

### Case 4 — a withdrawn claim with a forward pointer
```
CLAIM     asserts  multi-tool enrichment is significant at p<0.0001
          kind     DESCRIPTIVE
          status   WITHDRAWN        (invalid — not SUPERSEDED, not RETIRED)
GROUNDS   kind     REPRODUCTION ; 2,000-draw resampling
WARRANT            resampling the control distribution estimates the null
          DEFEATER the warrant assumes both arms vary. FIRED: the test held the
                   multi arm FIXED, so it did not test the comparison
SUCCESSION forward -> the 1.5x with honest p ~0.03-0.08 (case 1)
           record   RETAINED IN PLACE, banner-marked
```
Status WITHDRAWN and the record persisting are **not in tension** — this is
Invalidate in the step-1 mapping, not deletion.

### Case 5 — the zlib zero, mechanism refuted, conclusion survived
```
CLAIM     asserts  the shipped flawfinder+cppcheck pair produces ZERO
                   cross-tool merges on real zlib
          kind     DESCRIPTIVE ; status LIVE
GROUNDS   kind     OBSERVATION (712 raw findings, 0 merges) — UNCHANGED
CONFIDENCE ARGUMENT v1   mechanism: fp:/rk: key collision   -> REFUTED by item 2
CONFIDENCE ARGUMENT v2   mechanism: anti-correlated CWE classes; 14 exact
                         co-locations, 10 class-resolved both sides, 0 matches
TIME      asserted-at         earlier than the item-2 fix
          grounds-checked-at  re-derived AFTER the fix (712 findings, 0 merges)
                              — the grounds were re-checked, which is why the
                              claim could survive its mechanism being refuted.
                              Had they not been, this would be form three.
```
**The claim never changed status. Its confidence argument was replaced.** This
is the case that made C3 non-optional: in a single structure, a claim whose
stated reasoning was refuted but which stays LIVE is incoherent.

### Case 6 — "adding scanners is the wrong lever"
```
CLAIM     asserts  do not acquire further scanners to obtain consensus
          kind     PROSCRIPTIVE          <-- the part that needs its own marker
          status   LIVE
GROUNDS   kind     OBSERVATION, three configurations
WARRANT            diversity and co-location trade off, so an added tool brings
                   another anchoring convention rather than more agreement
          status   the WARRANT was OVERTURNED (granularity, not methodology)
                   while the CLAIM stayed LIVE
BOUND              free-tier scanners; no interprocedural engine ever run here
DEFEATER           a tool that co-locates by construction would defeat it.
                   NOT TESTED — CodeQL blocked on Rosetta.
```
**Two separations tested at once.** A proscriptive claim survived its warrant
being overturned, because the recommendation is now *better* supported — a
fourth tool would also have been measured at the wrong unit. A descriptive claim
cannot behave that way; this is why `kind` is a field.

---

## 5. CARRIED FORWARD FROM STEP 1

| item | placement |
|---|---|
| **four senses of "verified"** | Three become GROUNDS.kind values: against-tree → DEDUCTION or OBSERVATION on a repo artifact; by-execution → REPRODUCTION; against-source → OBSERVATION with an external ARTIFACT REF. The fourth, `[externally-verified]`, is **not** a grounds kind — it is a QUALIFIER value, because externality of the judge is a property of the inference's trustworthiness. **This structure separates them; it does not rename them.** |
| **WITHDRAWN / SUPERSEDED / RETIRED** | CLAIM.status, three values, as three distinct concepts. |
| **CORRECTED** | **No place, deliberately.** An operation on the document, recorded by git. |
| **five orphan bracket tokens** (`[checked]`, `[reconstructed]`, `[unconfirmed]`, `[unverified]`, `[snippet]`) | **No place in step 2**, and that is a finding rather than an omission: they are tier-position tokens, and step 2 has established only that the tier slot is QUALIFIER-on-the-inference. Whether each is a QUALIFIER value, an ARTIFACT REF property, or informal noise is a step-3 question. Filed, not resolved. |
| **six unmapped concepts** | Five become parts: honest bound → BOUND; comparator → COMPARATOR; pre-registration → a property of WARRANT (fixed before grounds existed); RETIRED → a status; evidence-strength-as-scale → QUALIFIER, populated in step 3. **The sixth, staleness/orphaning, gets NO place** — it is a property of the *record*, not of any claim, and forcing it in would be the same error as giving CORRECTED a status. |

---

## 6. WHAT THIS STRUCTURE CANNOT REPRESENT

Stated explicitly, as required.

1. **Aggregate or emergent claims.** The convergent result — *two mechanisms
   recovered agreement, neither improved ranking* — is a claim over two other
   claims. There is no part for a claim whose grounds are other claims. GSN
   handles this natively with nested Goals; this structure does not, and case 6
   only avoided it because its grounds are observations.
2. **Confidence in the confidence argument.** C3 gives one level of separation.
   Nothing stops the regress and nothing terminates it.
3. **Degree of defeater discharge.** Case 1's defeater was tested and
   discharged; case 6's was never tested. Both are `DEFEATER`. There is no field
   for *tested and survived* versus *untested*.
4. **Claims about the project's own process.** Rules 8a, 10, 11 are claims — with
   grounds (base rates, worked instances) and warrants. They are not claims about
   the world the tool measures, and this structure has no place for them.
5. ~~**Time.**~~ **PROMOTED OUT OF THIS LIST into the structure — see §2,
   TIME.** The original entry said the absence of a temporal field "is a real
   gap and I am not sure it should be". It should not be: rule 11's third form
   is a divergence between when a claim was corrected and when its grounds were
   last derived, which no other part can express. Retained here, struck through,
   because the reasoning that moved it is part of the record.
   **What remains a genuine limitation:** ORDER between confidence arguments.
   Case 5's v1/v2 are sequenced by convention, and two timestamps on a claim do
   not order the arguments *about* that claim.
6. **Partial or graded status.** A claim is LIVE or one of three retired states.
   "Substantially discharged, one element remains by choice" — item 1's actual
   status — has no representation.
7. **Disagreement between people.** Every part assumes a single author. The
   inventor-versus-Claude disagreements recorded in HANDOFF §8 rule 8 have no
   place.

---

## 7. DRIFT NOTICED, NOT FIXED

- **(a)** VALIDATION.md:3110's block still reads "P(size-matched control >=
  multi) = 0.0000 SURVIVES" and "highly significant" — the language the 0j work
  withdrew. The section is banner-marked further up, but this line is quotable
  in isolation and reads as live.
- **(b)** `docs/AUDIT.md` and `docs/GENESIS_TEMPLATE.md` use
  `[externally-verified]` in ways that may predate the current definition
  (carried from step 1 §5(d), still unaudited).

Neither acted on.
