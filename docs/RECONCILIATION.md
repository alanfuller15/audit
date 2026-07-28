# Reconciliation as a trust function — step 5 of 5, semantic layering

**Tier: `[self-tested]`.** A design. No check is implemented. Drift filed in §10.

---

## 0. SOURCES

| source | retrieval-depth | note |
|---|---|---|
| Wang et al., agent-provenance survey, arXiv v4 | **rendering** | six trust functions quoted verbatim below |
| Assurance-case evolution / change-impact literature | **snippet** | search-level only; see §2 and the bound there |
| W3C PROV-DM | **primary** | used in step 4, not re-fetched |

**Discrepancy reported:** the brief locates the trust functions at §3.5. In the
render I obtained they are in **§2.1**. The definitions are as described; only
the section number differs, and I may have a differently-paginated render.

Verbatim, all six:

> **Verification** "asks whether claims or actions are supported by evidence"
> **Attribution** "identifies which evidence, tool output, memory item, or
> message contributed to a claim or action"
> **Debugging** "localizes failures within an execution"
> **Safety enforcement** "prevents untrusted or unauthorized influence from
> reaching sensitive actions"
> **Audit** "reconstructs executions for review and accountability"
> **Recovery** "uses provenance to retry, compensate, roll back, or repair
> affected states"

---

## 1. THE COLLAPSE TEST — RUN FIRST, AND IT PARTLY SUCCEEDS

The brief invites the finding that reconciliation collapses into one of the six.
**It partly does, and saying so is worth more than defending a seventh
function.**

Rule 11's three forms tested separately against all six:

| form | collapses into? | reasoning |
|---|---|---|
| **1. staleness** — header diverged from the tree | **YES — verification, repeated** | Verification "asks whether claims or actions are supported by evidence". A header claiming "not implemented" against code that implements it *is* an unsupported claim. Re-running verification catches it. **This is not a new function. It is an old function with no cadence.** |
| **3. correction that never re-derives** | **MOSTLY — verification at a granularity nobody chose** | The claim verifies fine; the numbers inside it do not. Verification scoped to the numerals would catch it. The failure is that *scope was never set*, not that a function was missing. |
| **2. orphaning** — a correct document nothing points at | **NO. No counterpart among the six.** | Nothing is unsupported, so not verification. Attribution runs claim→evidence; orphaning is an artifact contributing to *nothing*, the inverse direction, and attribution has no query for it. Not debugging (no execution), not audit (nothing to reconstruct), not safety, not recovery. |

**So the honest result is two findings, not one:**

1. **Two of three forms are verification without a schedule.** The survey's six
   functions are all *invoked* — something calls them. None is *scheduled*. A
   persistent record needs the same function to fire without being called, and
   the survey has no vocabulary for that because an execution ends.
2. **Reachability is genuinely absent.** Orphaning is not any of the six, in
   either direction. That is the one place where a seventh thing is warranted,
   and it is much smaller than "reconciliation".

**Definition, narrowed accordingly (§3) — I am not claiming a seventh trust
function of equal standing to the six.** I am claiming that two of them need a
cadence the survey does not model, and that one small thing is missing.

---

## 2. EXTERNAL PRECEDENT — IT EXISTS, PARTIALLY

**Found**, in the assurance-case maintenance literature: *"Changes in the
engineering artifacts may invalidate the assurance case, and so its integrity
must be checked through evaluation"*, and Kelly & McDermid's safety-case change
management process, which *"investigated changes in evidence, context,
assumption and requirements GSN nodes to determine how changes impact the safety
assurance case"* — but *"did not integrate traceability to automate the
process."* The same literature records that *"evidence completeness and change
impact for assurance cases are managed mostly manually using (sometimes even no)
traceability information."*

**Mapping to our three forms:**

| form | precedent? |
|---|---|
| 1. staleness | **YES, directly.** Our `src/` is the engineering artifact; HANDOFF/VALIDATION are the case. §6.1's stale root cause is precisely "the artifact changed and the case was not re-evaluated". |
| 3. correction without re-derivation | **PARTIAL.** Change-impact analysis assumes the change is in the artifact. Ours was in the *case text*, with the artifact untouched — the reverse direction. |
| 2. orphaning | **NO precedent found.** Change-impact is about propagation along traceability links; orphaning is the *absence* of a link, which impact analysis presupposes. |

**SACM's ImplementationConstraint** — executable validation attached to an
artifact reference — is the closest mechanism, and step 4 already adopted it as
the re-derivation command. It supports form 3's check and says nothing about
forms 1 or 2.

**BOUND, and it is weak:** all of §2 is `retrieval-depth: snippet`. I read search
summaries, not the Kelly & McDermid paper or the ACCESS paper's evolution
sections. **Under step 3's own D5 this section is downgraded**, and the claim
"no precedent found for orphaning" is a *failure to find*, not a demonstrated
absence.

---

## 3. THE FUNCTION, DEFINED

> **RECONCILIATION** — *a trust function* that **re-establishes agreement
> between a persistent claim record and the world it describes, on a schedule
> rather than on demand**, and additionally checks that every artifact in the
> record is reachable from its entry point.

| | |
|---|---|
| **input** | the claim record (its fields, per steps 2–4) and the current state of the tree |
| **output** | a set of divergence candidates, each classified mechanical / semi-mechanical / judgment (§5) |
| **distinct from verification** | not by *what it asks* but by *when* — verification is invoked when a claim is made; reconciliation fires when nothing has asked |
| **distinct from audit** | audit reconstructs for an external reader; reconciliation is internal and its output is a work list |
| **distinct from recovery** | recovery repairs state after a known failure; reconciliation's job is finding that a failure occurred at all |
| **contains one genuinely new element** | reachability (§1, form 2) |

---

## 4. WHAT IT CATCHES, AND THE DETECTION SIGNAL

| source | failure | detection signal |
|---|---|---|
| rule 11 form 1 | header claims work undone that is done | grep the tree for the artifact the header says is missing |
| rule 11 form 2 | document unreachable from the entry point | no inbound reference from HANDOFF §5.1 |
| rule 11 form 3 | claim corrected, numbers never re-derived | `grounds-checked-at < restated-at` |
| rule 8 | inventor assertion recorded as evidence | `origin: supplied` with no independent ref |
| rule 8a (6 instances) | citation not opened, or opened at the wrong depth | `retrieval-depth` ≠ `primary` on a load-bearing claim; ceiling violation |
| rule 10 | an absence inferred from SARIF | claim asserts absence ∧ artifact-type `tool-output` ∧ no native-format ref |

---

## 5. THE PARTITION

The brief warns that listing a judgment check as mechanical repeats step 1's
rule-(c) failure. **The partition is therefore drawn on a strict criterion:**

> **MECHANICAL** — the check's output can be **acted on without reading**.
> **SEMI-MECHANICAL** — the machine produces a **candidate list**; a reader
> decides.
> **JUDGMENT** — no machine candidate is constructible.

Under this criterion **`grounds-checked-at < restated-at` is SEMI-mechanical,
not mechanical**, though the brief offered it as the mechanical example. The
comparison is a fact; whether the restatement was substantive is a reading. A
typo fix trips it. Classifying it mechanical would be exactly the rule-(c)
error, so it is demoted.

### MECHANICAL — act without reading
| check | fields read | false-positive mode |
|---|---|---|
| **M1 orphan** — file under `docs/`/`analysis/` with no inbound pointer from §5.1 | filesystem + index | a document deliberately unlisted (none currently) |
| **M2 depth-ceiling violation** — `retrieval-depth` above what the channel permits | `retrieval-depth`, retrieval channel | none; it is a constraint, not an inference |
| **M3 artifact unreachable** — locator 404s or `integrity` mismatches | `locator`, `integrity` | transient network failure; re-run resolves |
| **M4 malformed claim** — no ARTIFACT REF and `grounds.kind ≠ DEDUCTION` | grounds fields | none |
| **M5 repo self-check** — `.claude/verify.sh` fails | — | environment breakage |

### SEMI-MECHANICAL — machine flags, reader adjudicates
| check | signal | why judgment is required |
|---|---|---|
| **S1 form-3 candidate** | `grounds-checked-at < restated-at` | was the restatement substantive? |
| **S2 form-1 candidate** | grep the tree for what a header says is absent | does the hit mean what the header meant? |
| **S3 numeral divergence** | the same figure appearing with different values across files | are they the same quantity? (the `1,131` case) |
| **S4 depth contradiction** | two refs, different `retrieval-depth`, different content | which is right — the deeper one usually, not always |
| **S5 stale quotation** | a public artifact quotes a claim whose `status ≠ LIVE` | is it quoted as current or as history? |

### JUDGMENT — irreducible
| check | why no candidate is constructible |
|---|---|
| **J1** does a conclusion survive its mechanism being refuted (case 5, §6.1) | requires understanding both mechanisms |
| **J2** is a secondary source's summary faithful | requires reading the primary |
| **J3** does the estimand match the claim | requires knowing what was asked |
| **J4** is the comparator the right one | requires knowing what would have been a fair test |

**J3 and J4 are the two that killed the most claims in this project, and they are
the two least mechanisable.** That is worth stating plainly: the checks that can
be automated are not the checks that have cost the most.

---

## 6. HOOK PLACEMENT — SPECIFIED, NOT IMPLEMENTED

**First, a finding:** the hook surface named in the brief is **not present in
this repository.** `.claude/` contains `settings.local.json` (permissions only)
and `verify.sh`, which runs the two harnesses. There is no
SessionStart/PreCompact/Stop/PreToolUse configuration here. The mapping below is
therefore an **interface contract against a surface this repo does not yet
expose**, not a description of anything wired.

| hook | checks | rationale |
|---|---|---|
| **SessionStart** | M1–M5, S1, S2 | **This is the cadence answer.** The handoff currently instructs "run a reconciliation sweep before starting anything" — a written instruction to a reader, which is the mechanism that has already failed. Firing the mechanical layer here makes it unconditional. |
| **PreCompact** | snapshot claim `status` for LIVE claims in context | compaction is where a claim's retired status is most likely to be lost while its text survives |
| **Stop** | M1, S1 restricted to files touched this session | catches "you corrected a claim — did you re-derive its numbers?" at the moment the correction is fresh, which is form 3's exact window |
| **PreToolUse** (write to a public artifact) | S5 | the narrow, high-value one: before the README or a published document is written, check that every claim it quotes is LIVE. This is the check that would have caught case 2 below. |

---

## 7. THE HARD QUESTION — RECONCILIATION IS ITSELF CLAIM-PRODUCING

A sweep reporting "eight items found, all corrected" is a claim about the
record, subject to every failure the record is. **Yes, it gets a certainty level
under step 3 and provenance fields under step 4.** No exemption.

**And the regress terminates — but only for part of it, which is why §5's
partition is load-bearing rather than tidy.**

| output class | grounds kind | level | does it need re-checking? |
|---|---|---|---|
| **mechanical** (M1–M5) | **DEDUCTION** over machine-written fields | **ESTABLISHED** | **No.** The output follows necessarily from field values. While the fields are unchanged the conclusion cannot be otherwise — step 3's deductive default, and the same reason case 2A needs no re-run. |
| **semi-mechanical** (S1–S5) | OBSERVATION — a human adjudicated | INDICATED | **Yes.** Ages like any observation and is swept like anything else. |
| **judgment** (J1–J4) | OBSERVATION | INDICATED, D5 if unverified | **Yes**, and these are the ones that have historically been wrong. |

**The regress terminates at the mechanical layer and nowhere else.** A sweep
that is entirely judgment-class produces claims that all need re-checking — a
sweep whose output requires another sweep. That is not a theoretical concern:

**Case 5 below is exactly that failure.** Two sweeps in 24 hours, by sessions
that had just written rule 11, missed six items. **Both sweeps were entirely
judgment-class.** There was no mechanical layer to terminate on, so their output
inherited the same fallibility as the record they were checking.

**The cost of the answer, stated:** every sweep now emits claims that must be
recorded with fields, which is more record to maintain — and more record is more
surface to decay. That is real and I do not think it is avoidable. What makes it
net-positive is that the mechanical fraction produces ESTABLISHED claims that
never need revisiting, so the maintained surface grows only with the judgment
fraction. If the mechanical layer were never built, this whole step would add
overhead without adding termination.

---

## 8. THE FALSIFICATION SET

| # | case | class | check |
|---|---|---|---|
| 1 | **§6.1's root cause removed by item 2 while its conclusion held** | **SEMI (S2) + JUDGMENT (J1)** | S2 greps for `_result_key`'s two-algorithm split and flags the header as a candidate. **But whether the conclusion survives on a different mechanism is J1 and cannot be mechanised** — that took reading both mechanisms. S2 would have raised it months earlier; J1 still had to resolve it. |
| 2 | **WHERE_IT_STANDS.md carrying a withdrawn claim because nothing pointed at it** | **MECHANICAL (M1) + SEMI (S5)** | M1 catches the orphan with no reading at all. S5 catches the withdrawn quotation at PreToolUse before the file is written. **This case is fully covered and would not recur.** |
| 3 | **the 1,131 denominator surviving a sweep that corrected the claim around it** | **SEMI (S1 + S3)** | S1 flags `grounds-checked-at < restated-at`; S3 flags `1,131` appearing where component figures give a different sum. Neither *decides* — a reader confirms 543+588 is a two-tool count describing a three-tool result. |
| 4 | **instance 6 — a correct locator to a secondary source** | **SEMI (S4), and only if a second ref exists** | S4 fires when two refs disagree at different depths. **With only the secondary ref present, nothing fires.** The depth would be recorded as `secondary`, which is a standing invitation to check — but no check fires on a single ref. **This case is only partially covered, and that is a real limit** (§9.3). |
| 5 | **two sweeps, six items missed** | **NOT A DETECTION FAILURE — A CADENCE AND CLASS FAILURE** | See below. |

### Case 5 — the test of whether the design addresses cadence

The six missed items were not missed for lack of a check. **Most were
mechanically detectable:** three orphans (M1, pure grep, zero reading) and the
`1,131`/`1,164` arithmetic (S3, a numeral scan). They were missed because **both
sweeps were human passes over a large corpus, and judgment does not scale with
attention.**

Rule 11's own third form already says this, verbatim: *"This is not carelessness;
it is a predictable consequence of doing the first job well, **which is why it
needs a control rather than more diligence.**"*

**The design's answer to case 5 is therefore not a better check. It is:**
1. **a mechanical layer that fires unconditionally at SessionStart**, so the
   cheapest checks never depend on someone remembering; and
2. **a partition that tells a sweep what it is doing** — a session that knows
   M1–M5 ran and S1–S5 produced candidates knows its remaining job is J-class,
   and knows its output is INDICATED rather than settled.

Neither existed for the two sweeps that failed. Both would have caught the
orphans and the arithmetic without any increase in diligence.

---

## 9. LIMITS

1. **A claim that was always wrong.** Reconciliation checks the record against
   the *world*; if the world and record agreed from the start and both are
   wrong, nothing fires. Verification-at-assertion is the only defence.
2. **J3 and J4 are unmechanisable and are the expensive ones.** Estimand and
   comparator errors killed five claims; no candidate can be generated for
   either. The design automates the cheap failures and leaves the costly ones.
3. **Single-reference depth problems** (case 4). Without a second, deeper ref
   there is nothing to contradict. Catching this needs *actively fetching the
   primary a secondary cites*, which is unbounded work, not a check.
4. **Semantic drift with no textual change.** A term whose meaning shifted while
   its text stayed fixed — precisely what steps 1–4 exist to prevent — is
   invisible to every check here.
5. **The record's own boundary.** Nothing checks whether a *claim that should
   exist* is missing. Absence of a claim has no locator.

**What catching more would cost:** items 2 and 3 both reduce to "read the
primary sources again", which is the unbounded case. Item 4 would require a
terminology store with versioned definitions — which is `TERMS.md`, downstream
of all five steps and deliberately out of scope here.

---

## 10. DRIFT NOTICED, NOT FIXED

- **(a)** Carried unfixed through steps 2, 3, 4 and now 5: `VALIDATION.md:3110`
  still reads "P(size-matched control >= multi) = 0.0000 SURVIVES" and "highly
  significant", language the 0j work withdrew.
- **(b)** Carried unfixed through all five steps: `docs/AUDIT.md` and
  `docs/GENESIS_TEMPLATE.md` use `[externally-verified]` in senses that may
  predate the current definition. **Five steps is past the point where "filed"
  is a reasonable disposition.** Both would be caught by S2 at SessionStart
  under this design, which is a small argument that the design is aimed at real
  targets.

---

## 11. WHAT STEPS 1–5 NOW CONSTITUTE, AND WHAT REMAINS UNBUILT

### What exists, as design
| step | artifact | what it settles |
|---|---|---|
| 1 | `TERMS_INVENTORY.md` | which terms carry two concepts, which two terms share one, what has no name |
| 2 | `CLAIM_STRUCTURE.md` | ten parts a claim carries; a separate confidence argument |
| 3 | `EVIDENCE_SCALE.md` | four certainty levels on the *inference*, defaults, six downgrade and three upgrade domains, a separate recommendation strength |
| 4 | `PROVENANCE_FIELDS.md` | four claim and seven artifact fields; retrieval-depth defined operationally |
| 5 | this file | reconciliation defined, partitioned, and placed against hooks |

**Together these are a claim record specification** — vocabulary, structure,
grading, provenance, and maintenance — derived throughout from this project's own
documented failures rather than imported wholesale.

### What remains unbuilt — all of it
1. **`TERMS.md`.** Downstream of all five and deliberately not written. Steps 1
   and 5 both point at it: step 1 found the conflicts, §9.4 identifies a
   versioned terminology store as the only defence against semantic drift.
2. **Every mechanical check.** M1–M5 are specified and none is implemented.
   M1 (orphan) is a few lines and would have caught three of this session's
   findings.
3. **The hook wiring.** The surface does not exist in this repo (§6).
4. **Any population of any field on any existing claim.** Every one of steps 2–4
   was design-only by instruction; nothing has been applied to the ~200 claims in
   VALIDATION.md, and doing so is a large, separate, and mostly manual job.
5. **External review.** Every one of the five documents is `[self-tested]` — one
   party's reading of a corpus that party largely wrote. In this design's own
   vocabulary the whole sequence is `INDICATED`, `origin: in-repo`,
   `retrieval-depth: primary`, and D5-downgraded for lack of an external judge.

### The honest summary
Five steps produced a specification and **zero enforcement**. That was the
instruction each time, and it is worth stating plainly at the end rather than
leaving the sequence to read as though something now runs. **Nothing in steps
1–5 would have caught anything on its own.** What they provide is the vocabulary
and the partition that make the cheap checks buildable — and §8's case 5 argues
that the cheap checks are where the recurring losses actually are.
