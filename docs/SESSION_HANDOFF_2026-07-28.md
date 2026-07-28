# Session handoff — 2026-07-28

Residue only: reasoning that shaped decisions in steps 1–5 and the population
pilot but never became a formal entry. Everything with a conclusion is already
committed — see HANDOFF §5.1. **This file is the part a summary would flatten.**

---

## 1. IN FLIGHT

**Nothing.** Tree clean, `main` == `origin/main`, verify 112 + render clean,
reconcile 4/4 clean.

**The next action, deliberately NOT started:** fix S1's cross-file blindness
(POPULATION_PILOT.md §4–5). Do that **before** populating any further claims —
it is cheap now and expensive once ~190 claims carry the old field shape.

The shape of the fix, as far as I got: grounds need **identity**, not just a
locator, so a claim's `restated-at` can be compared against the
`grounds-checked-at` of grounds living in a different file. That is a step-4
spec change, not a check change. I did not design it.

---

## 2. WHY D2 RESOLVED AGAINST THE FIELD — and why C07 kills the alternative

This is the piece most likely to be re-litigated, because the losing option
looks better in the abstract.

`restated-at` needs "the claim's location". Two candidates:

**(a) newest blame across the claim's line range** — chosen.
**(b) blame of one designated line** — rejected.

(b) is *obviously* better on paper: it avoids the false positive where a typo
fix on any line in the range advances `restated-at` and manufactures an S1
candidate. That FP is real, and it is exactly why RECONCILIATION.md §5 demoted
S1 to semi-mechanical.

**C07 is why (b) cannot be built.** In the 1,131 case the claim's *assertion*
("adding a third tool did not rescue the default set") and its *number* (1,131)
are on **different lines**, and the correction block that later fixed it is on a
third. There is no single line that is "the claim". Designating one requires a
session to decide which line carries the claim's identity — and that decision is
unstable across exactly the edits the field exists to detect. A designated line
can be *moved by the edit you are trying to catch*.

So the choice was: a field with a known, bounded, well-understood false positive
(a), or a field whose correctness depends on a judgment no session can make
reliably (b). **Bounded-and-noisy beat unbounded-and-clean.**

**The payoff of that reasoning is that populating CONFIRMED the demotion.**
Step 5 demoted S1 to semi-mechanical on an argument. The pilot showed the
argument was right for a reason step 5 had not identified: not only does a typo
advance the timestamp, but there is no principled alternative to advance instead.
If a future session wants S1 to be mechanical, **it needs grounds identity
(§1's fix), not a better line-picking rule.** Do not re-open (b).

---

## 3. WHY 151 s / 12 CLAIMS IS MISLEADING

The pilot reports 151 s to populate 12 claims and immediately says not to
extrapolate. The reason is worth carrying because the number will be quoted.

**Five of the twelve — C01, C02, C03, C06, C07 — had been analysed in depth
during steps 2 through 5.** They were the falsification cases. Their `estimand`,
`comparator`, `bound` and `defeater` had already been argued out in prose; I was
transcribing, not deciding. Their marginal cost was near zero and they are 42%
of the sample.

**The seven others required reading the VALIDATION.md section and deciding.**
That is where the time actually went, and it is not evenly distributed either:
`asserts`, `kind` and `status` are quick; `estimand`, `comparator` and `bound`
are slow, because they are J3/J4 judgment work by the project's own partition —
the two classes recorded as both the most expensive and the least mechanisable.

**Honest per-claim cost for an unfamiliar claim: minutes, not seconds.** I would
not put a number on it from a sample this contaminated. **The right way to price
the remaining ~190 is to populate ten claims nobody has previously analysed and
time those** — which is a different pilot from the one I ran, and the one I
would run if the answer mattered.

The number that *is* safe to carry: **~2 of 11 fields are reliably
machine-derivable.** That ratio came from the whole sample and is not
contaminated by familiarity.

---

## 4. C3's TWO UNANTICIPATED FALSE-POSITIVE MODES — the next check should expect the same

The brief for the mechanical layer said: *state the false-positive mode before
writing the check.* I did. **I stated one of three, and it was the least
important one.** The pattern in what I missed is the transferable part.

**What I predicted:** dated snapshots legitimately record past counts. True, and
easy — I anticipated it because session handoffs are *named* for their date, so
the category was visible from the filenames.

**FP-1, missed: the word is overloaded.** `checks` in this corpus means our
harness, *and* cppcheck's 342 static-analysis checks, *and* the CWE coverage
cascade's 31/149/116/46/20, *and* OASIS's 46 schema constraints. First run: 30
findings, essentially all false.
**Why I missed it:** I was thinking about *which documents* could be wrong, not
about *what the string means elsewhere*. Scoping-by-document is the natural
frame when the failure you have in mind is a stale document.

**FP-2, missed: append-only records carry correct history.** VALIDATION.md logs
harness growth as it happened — "harness 67 → 84 checks" — and every entry is
right for its date.
**Why I missed it:** I had *established* that VALIDATION.md is append-only
earlier in the same session, while designing the reconcile scope. I knew the
fact and did not apply it to the check I was writing. Knowing a property of a
document is not the same as remembering it constrains a grep over that document.

**FP-3, found by the check itself:** it fired on §12 of RECONCILIATION.md, which
*quotes* `"harness 67 → 84 checks"` while explaining FP-2. A quoted example is
not an assertion.

**The generalisation for the next check:** pre-stating FP modes catches the
category you can see from filenames and misses the two that come from *semantics
of the matched string* and from *document role you already know but do not
recall at match-design time*. **Budget a first run against the whole corpus as
part of writing the check, not as validation after.** Every one of the three was
found in under a minute by running it; none was found by thinking harder.

---

## 5. CORPUS OBSERVATIONS NOTICED AND NOT ACTED ON

None of these was in scope; none is a defect I was asked to fix.

**a. `docs/AUDIT.md` and `docs/GENESIS_TEMPLATE.md` use `[externally-verified]`
in senses that may predate the current definition.** Filed in steps 1, 2, 3, 4
*and* 5 — five consecutive filings without action. **Five is past the point where
"filed" is a reasonable disposition.** It should be audited or explicitly
declared legacy. It is also the only drift item that S2 (grep the tree for what
a header says) would surface immediately if S2 existed.

**b. `VALIDATION.md:3110` still reads "P(size-matched control >= multi) = 0.0000
SURVIVES" and "highly significant"** — language the 0j work withdrew. The
section is banner-marked further up, so a reader arriving at the top is warned,
but **the line is quotable in isolation and reads as current.** Carried through
steps 2–5 unfixed. This is the same shape as the failure that put a false claim
in the README: correct in context, wrong when extracted.

**c. VALIDATION.md is ~4,100 lines and has ~307 section headings.** The "~200
claims" figure used throughout the pilot is my estimate from those headings, not
a count. Nobody has counted the claims. If population is ever priced properly,
that number needs establishing first — the recommendation in the pilot is
sensitive to whether it is 200 or 400.

**d. `docs/claims.json` is a new drift surface with no check.** POPULATION_PILOT
§2 D1 records this. Concretely: nothing verifies that a claim's stored
`locator.lines` still points at the anchor string, and VALIDATION.md is edited
often. **This is a mechanical check somebody should write before the sidecar
grows** — it is C4's shape (does a stored path resolve) applied to line ranges,
and it would cost about as much as C4 did.

**e. C4 has still never fired in anger.** It fired twice under injection and
never on real drift. Retained for the reason recorded in RECONCILIATION §12 — it
guards a failure mode C2 introduces — but a future session trimming checks
should know it has no historical hit, only a structural argument.

---

## 6. ONE THING I WOULD TELL THE NEXT SESSION

The five design steps produced a specification that is **more correct than it is
useful**, and the pilot is what revealed that. Every step was internally sound;
the composition has a hole at exactly the case that motivated it (S1 vs form 3,
POPULATION_PILOT §4).

That is not an argument against the sequence — it is an argument that **a
specification should be piloted against its motivating case before it is
populated**, and that the pilot should be run by someone willing to report that
the spec does not work. The pilot cost one session. Populating 190 claims first
and discovering the same thing would have cost considerably more.
