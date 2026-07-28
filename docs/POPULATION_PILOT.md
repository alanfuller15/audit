# Population pilot — 12 claims, measured

**Tier: `[self-tested]`.** A pilot over 12 of roughly 200 claims. Populated
fields are in `docs/claims.json`. Nothing beyond the 12 was populated and no
field spec was adjusted to make a claim fit.

> **[COUNT CORRECTED 2026-07-28 — the "~200" below was never counted, and the
> denominator depends on a rule this project has not fixed.]** Counted against
> VALIDATION.md at `e260631` (4,106 lines, 291 logical headings — the "~307"
> figure counted raw `#` lines, including one inside a code fence and 11
> continuation lines of multi-line headings):
>
> | counting rule | count | basis |
> |---|---|---|
> | **one claim = one dated record** (`##`) | **61** | exact; 6 are front-matter reference sections, 55 are records |
> | **one claim = one result-bearing subsection** (`###`), plus records with no subsections | **~190** | 177 + 13; keyword classification, ±~20 |
> | **one claim = one independently validatable assertion** — the granularity the pilot mostly used | **~390 (interval ~300–470)** | hand-count over a systematic 1-in-7 sample of records: 56 claims in 9 records / 538 lines (13.1% of the file) |
>
> **"~200" is the heading count, not the claim count.** It is right under the
> middle rule and roughly half the answer under the rule the pilot's own 12 were
> populated at. **The ambiguity is that the spec never fixes the claim unit, and
> the pilot did not either:** of its 12, C04 is a single table row, C02 an
> 8-line block, C01 and C03 two claims sharing one 15-line range, and C08/C09/C10
> whole `##` records. A single corpus-wide number cannot be quoted without
> naming which of these three rules produced it.
>
> **Consequence for §5.** The direction of the recommendation is unchanged and
> mildly strengthened — the case against full population gets stronger as the
> denominator grows. The *magnitude* changes: step 2 ("populate `status` alone,
> corpus-wide") is ~390 units of one field, not ~190, and §10 of
> PROVENANCE_FIELDS adds a twelfth field (`signature`) with a corpus-wide grep
> attached. **Fixing the claim unit is now a prerequisite to pricing anything**,
> and it is a step-2 spec gap, not a counting problem.

---

## 1. SELECTION RULE — fixed before populating

Cover the **design space**, not convenience. Seven slots fixed by the brief;
five more chosen to stress axes the required seven do not reach — a synthetic
corpus, multiple artifact refs at different depths, a pre-registered claim, a
negative-from-proxy, and a SUPERSEDED claim distinct from WITHDRAWN.

Deliberately excluded: claims already used as falsification cases in steps 2–4,
except where the brief required them (`fp:/rk:`, the 1.5x, the zlib zero).
Re-using them would test the spec against the cases it was built from.

| # | claim | slot it fills |
|---|---|---|
| C01 | the 1.5x | committed script over a fetched corpus |
| C02 | `fp:` ≠ `rk:` | deductive from source, nothing executed |
| C03 | `p<0.0001` | WITHDRAWN |
| C04 | SARIF conformance vs OASIS | fetched external source |
| C05 | close item 2 | recommendation, not a finding |
| C06 | the zlib zero | mechanism refuted, conclusion held |
| C07 | the 1,131 denominator | the recorded form-3 instance |
| C08 | granularity overturn | stress: a claim that overturned another |
| C09 | 0f registry arm | stress: live unversioned fetch, multiple refs |
| C10 | item 2 closed | stress: pre-registered (U2) |
| C11 | OWASP 1,427 merges | stress: synthetic corpus, reconstructed artifact |
| C12 | SARIF drops provenance | stress: negative-from-proxy (D6) |

---

## 2. AMBIGUITIES THE SPEC DID NOT DETERMINE — four, each marked a DECISION

Recorded in `claims.json:_meta` and summarised here. **None was resolved
silently.**

### D1 · Where populated fields live — *the spec never says*
Steps 2–4 define fields and never state where they are stored. **Chosen: a
sidecar `docs/claims.json`**, not inline in VALIDATION.md, because VALIDATION.md
is append-only and editing historical entries to add fields would violate that;
and machine-written fields need a parseable format. JSON not YAML — no yaml
module is installed.
**COST:** the sidecar can drift from VALIDATION.md, which is a fresh instance of
the exact failure this design targets, and **nothing currently checks the link.**

### D2 · `restated-at` for a claim that spans lines — *the decisive one*
The spec says "git log for the claim's location" and never defines a location.
**Chosen: the NEWEST blame across the claim's line range.**
**COST, and it is the known one:** a typo fix on any line in the range advances
`restated-at` and produces a false S1 candidate. That is precisely why
RECONCILIATION.md §5 demoted S1 to SEMI-mechanical, and populating **confirms
the demotion was correct rather than cautious.**
The alternative — blame of one designated line — was rejected because **no
session can identify that line reliably**: a claim's assertion and its number
are routinely on different lines. C07 is exactly that shape.

### D3 · What the claim's line range *is*
Hand-set at population time and stored with an anchor string.
**COST:** unverifiable, and an edit above the claim silently shifts it.

### D4 · `grounds-checked-at` for deductive grounds
No re-derivation command exists, so it cannot be machine-written. **Chosen: the
blame of the cited source lines.**
**COST:** it can then never be older than the artifact, so **S1 and D4 can never
fire for an entire grounds kind.** Already flagged at PROVENANCE_FIELDS.md §8.5;
populating confirms it is real rather than theoretical.

---

## 3. MEASUREMENTS

### Wall-clock
| | |
|---|---|
| populating 12 claims, once the ambiguities were settled | **151 s** (~12.6 s/claim) |
| settling the four ambiguities | ~2 sessions of design reading, **unamortised — paid once** |
| establishing the S1 test data (§4) | ~10 min, and it is not per-claim work |

**The 12.6 s/claim figure is misleading and should not be extrapolated.** Five
of the twelve (C01, C02, C03, C06, C07) had been analysed in depth during steps
2–5, so their marginal reading cost was near zero. The seven others required
reading the VALIDATION.md section, and that is where the time actually went.
**A fair estimate for an unfamiliar claim is minutes, not seconds** — dominated
by deciding `estimand`, `comparator` and `bound`, which are J3/J4 judgment work
by RECONCILIATION.md's own partition.

### Fields: machine-derivable vs read
| field | source | count |
|---|---|---|
| `restated_at` | **machine** — `git blame`, newest over range | 12/12 |
| `asserted_by` | **machine** — blame commit | 10/12 (2 unresolvable, below) |
| `grounds_checked_at` | **machine only if** a re-derivation command exists and was run | 6/12 machine, 5 hand, 1 null |
| everything else — asserts, kind, status, grounds.kind, all artifact-ref fields, warrant, estimand, comparator, bound, defeater, level, adjustments | **read** | 12/12 |

**Roughly 2 of 11 fields are reliably machine-derivable.** The remaining nine
require a session to read the claim and its history. That ratio is the single
most important number in this pilot.

### Decisions the spec did not determine
**Four structural** (§2) plus **three per-claim level calls** where two domains
could each have applied and I picked:
- C09 — D3 (live unversioned fetch) chosen over D5; the population is
  irreproducible rather than unverified.
- C11 — D1 at −1 for synthetic corpus; arguably a BOUND rather than a downgrade.
- C12 — D6 explicitly **not** fired, because the absence *was* checked natively.
  The spec does not say a domain can be recorded as considered-and-not-fired;
  I recorded it anyway, as it is the more useful record.

### Claims that could not be fully populated — 3 of 12
| claim | field | why |
|---|---|---|
| C03 | `grounds_checked_at` = null | the script was run inline and never written to a file. **No artifact ⇒ no re-derivation ⇒ no timestamp.** |
| C11, C12 | `asserted_by` = "unresolved-multi-commit" | the claim was built over several commits and blame gives a different one per line. **`asserted_by` assumes a claim has one author-commit; a claim edited repeatedly does not.** |

Neither gap is fatal, and **neither was patched by adjusting the spec.**

---

## 4. S1 AGAINST THE POPULATED SET — THE FINDING

### On the current tree: **0 of 12 fire**
```
fired 0 · silent 11 · unassessable 1
```
That is the expected and correct result — the corpus was reconciled three times
in two days, and C07's number was re-derived when it was corrected at `962efc33`.

**C03 is unassessable, and that matters more than the zero.** It has no grounds
artifact, so it has no `grounds-checked-at`, so **S1 cannot evaluate it at all.**
S1 is therefore silent on exactly the class of claim most likely to be stale:
the ones whose evidence was never retained.

### At the pre-fix commit — **S1 STILL DOES NOT FIRE on C07 in VALIDATION.md**
The real test, run at `e524c60d` (the commit before the fix):
```
claim line 908, VALIDATION.md
  restated-at         2026-07-26T02:52:03   (adf2a0d3)
  grounds-checked-at  2026-07-26T02:52:03   (adf2a0d3)
  => S1 SILENT
```
**Both timestamps are the same commit.** The claim and the number were written
together and neither was touched again until the fix.

### Why — and this is the design finding
The recorded form-3 failure was *"the morning's pass corrected the co-location
claim everywhere it had spread and never re-derived the numbers."* Verified:
**commit `80d1817` — the morning sweep — did not touch `docs/VALIDATION.md` at
all.** It changed `README.md`, `docs/HANDOFF.md`, `docs/NEGATIVE_RESULT.md`.

So form 3's actual failure **spans files**: the claim was corrected in three
documents while its grounds sat, untouched and un-re-derived, in a fourth.

**S1 as specified compares two timestamps on the same claim record. It cannot
see a divergence that lives between two records.** That is a defect in step 4's
design, not in this population.

### Where S1 *does* fire — and the asymmetry is the useful part
The same number was **copied into HANDOFF.md**, and there:
```
docs/HANDOFF.md, 1,131 region, at 80d1817
  restated-at         2026-07-26T03:01:05
  grounds-checked-at  2026-07-26T02:52:03
  => S1 FIRES
```
**S1 detects propagation staleness, not derivation staleness.** A number is
invisible to S1 precisely where it was computed, and visible where it was
copied — because only the copy sits in text that gets restated around it.

That is a genuine capability and it is *not* what step 4 claimed. Step 4 said
the form-3 check was "one comparison between two machine-written values". It is
one comparison, and it answers a narrower question than advertised.

---

## 5. RECOMMENDATION ON THE REMAINING ~190

**Populate nothing further for now.** Argued from the numbers, not from effort.

### The case against full population
1. **The check it unblocks does not do the job it was populated for.** S1 cannot
   see cross-file form-3 divergence (§4), which is the recorded instance. Paying
   ~190 × minutes to enable a check with a known blind spot at its motivating
   case is the wrong order of operations.
2. **2 of 11 fields are machine-derivable.** The other nine are judgment work —
   `estimand`, `comparator` and `bound` are J3/J4 by the project's own
   partition, and J3/J4 are recorded as the two failure modes that killed the
   most claims *and* the two least mechanisable. Population converts an
   automation project into ~190 units of the most expensive class of reading.
3. **The sidecar is a new drift surface with no check** (D1's cost). Populating
   190 claims into an unchecked sidecar creates 190 opportunities for exactly
   the failure the design exists to catch.

### The case for a narrow subset — and why it is still no
"Populate only claims quoted in public documents" is the strongest option: those
are the ones where staleness reaches a reader, and it is a small set (README,
NEGATIVE_RESULT, WHERE_IT_STANDS). **But S5 already covers that** — a
mechanical check on `status ≠ LIVE` at PreToolUse — and S5 needs only `status`,
one field, not eleven. **The narrow benefit is available for ~1/11 of the cost.**

### What to do instead, in order
1. **Fix S1's cross-file blindness before populating anything.** The check needs
   to compare a claim's `restated-at` against the `grounds-checked-at` of
   grounds that may live in another file — which means grounds need identity,
   not just a locator. That is a spec change, and it is cheap now and expensive
   after 190 claims carry the old shape.
2. **Populate `status` alone, corpus-wide.** One field, largely derivable from
   existing WITHDRAWN/SUPERSEDED/RETIRED markers, and it unblocks S5 — the check
   that would have caught WHERE_IT_STANDS.md quoting a withdrawn claim.
3. **Then reconsider**, with S1 fixed and one field's population cost measured
   at corpus scale rather than extrapolated from twelve.

### The partial-population problem — how to prevent "clean" being read as "checked"
A partially populated corpus makes S1 report clean over unpopulated claims,
which is the failure `reconcile.sh` was explicitly built to avoid.

**The fix is the contract `reconcile.sh` already keeps:** a check must never
report clean over something it did not examine. Concretely, S1 must report
**three** numbers and not one — `fired / silent / unassessable` — and the run
must be **INCONCLUSIVE, not clean, whenever `unassessable > 0`.** The §4 run
above already prints that shape: `fired 0 · silent 11 · unassessable 1`. Under
this rule the pilot's own result is **INCONCLUSIVE**, which is the honest
verdict for a set where one claim has no retrievable grounds.

That rule costs nothing to adopt and should be adopted **before** any further
population, not after.
