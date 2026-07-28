# Session handoff — 2026-07-28 (second session that day)

Residue only. Everything with a conclusion is committed — the population thread
is STOPPED (HANDOFF §7 item 9), and **RECONCILIATION.md §13 is the document to
read first**. This file holds the reasoning those records do not carry.

Read `SESSION_HANDOFF_2026-07-28.md` (the earlier one) for the residue of steps
1–5 and the pilot. This file does not repeat it.

---

## 1. IN FLIGHT

**Nothing.** Tree clean, `main` == `origin/main`, reconcile 4/4, verify 112 +
render, no regressions.

**The next action is not a task.** The population thread is closed and §13 says
what runs. A session arriving with no other instruction should read §13, run
`.claude/reconcile.sh`, and stop — there is no queued work. The one small open
item is §5 below.

---

## 2. THE STOP RESTS ON A 3-FOR-3 RESULT, AND ONE OF THE THREE IS A JUDGMENT CALL

This is the most important thing in this file, because the headline number is
load-bearing and it is not purely mechanical.

`s1_crossfile.py` fired on three claims and I adjudicated all three as false
positives. **C12 and C09 are not close calls** — the signatures are a field name
and a section heading, matching 32 and 5 lines of documents that merely discuss
them. **C06 is a call I made and a later session could reasonably reverse.** It
fired because `EVIDENCE_SCALE.md:357` reads:

```
CLAIM        "the shipped pair produces ZERO cross-tool merges on real zlib"
```

I classified that FP-B — a worked example, quoted as an example, not an
assertion. **The opposite reading is defensible:** step 3 quoting the claim *is*
a propagation of it into a fourth document, which is exactly what form 3
describes. Under that reading the result is 2 FP / 1 TP.

**Why it does not change the decision:** 2-of-3 false on a clean tree is still a
check that cannot act without a reader, and the stop rests equally on the
structural argument (§10.4 FP-C, which no signature rule fixes) and on the
partition argument (J3/J4 were always judgment). **But do not quote "3-for-3" as
though it were a measurement with no judgment in it.** It has exactly one.

**If it had gone 2 TP / 1 FP, I would not have recommended stopping**, and the
inventor's argument (b) would have been much weaker. The decision was closer to
its evidence than the committed record makes it look.

---

## 3. HOW THE COUNT WAS ACTUALLY DONE, AND WHY IT IS NOT TIGHTER

The `~390` is a **hand count over a systematic 1-in-7 sample** of `##` records —
9 records, 538 of 4,106 lines, 56 claims — extrapolated two ways that agreed
(6.2/record × 62 ≈ 385; 0.104 claims/line × 4,106 ≈ 427).

**The interval `~300–470` is ±1 SE on the record mean, and it is wide because
the sample straddles both extremes**: it happened to include the front-matter
"three tiers" section (0 claims — pure definitions) and the design-claim audit
(14 — an 11-row table). sd ≈ 4.1 across 9 records. **I did not narrow it, on
purpose:** the question asked was "200 or 400", and the lower bound already
answered it. A session wanting a tighter figure should count more records — not
re-derive from headings, which is where `~200` came from in the first place.

**Why no mechanical count exists.** There is no marker for a claim in
VALIDATION.md. Every mechanical proxy — headings, bold sentences, table rows —
is a proxy for *one of the three rules*, not for "a claim". I tried headings
first; that is exactly the `~190`. The reason it is not the answer is C04: the
pilot treated a single table row as a claim, inside a heading that contains
eleven of them.

---

## 4. FP-C WAS FOUND BY LUCK, NOT BY METHOD

The prior residue's §4 lesson — *run it against the corpus as part of writing
the check, not as validation after* — is the reason FP-A and FP-B were caught.
**FP-C was not caught by that.** I re-ran the check after an unrelated edit (the
C02 malformed-timestamp fix) and happened to notice the occurrence count had
moved 30 → 31. Then it moved to 32 when I wrote the paragraph describing the
first move.

**A session that wrote §10, committed, and did not re-run would have missed it
entirely** — and FP-C is the mode that makes the problem structural rather than
tunable, so missing it would have left the stop resting on two arguments instead
of three. The transferable rule is narrower than the prior residue's: **re-run
the check after writing the prose about the check**, because in this corpus the
prose is part of the corpus the check reads.

---

## 5. THE ONE OPEN ITEM I LEFT, DELIBERATELY

**`VALIDATION.md:568` restates a retired tier without a marker.** It reads "the
one carried to `[externally-verified]` at file level (ROC-AUC 0.755)". That tier
was retired by the SUPERSEDED banner at `VALIDATION.md:434` — but 568 sits in a
*different* section (the "Narrowed bound" record), outside that banner's scope.

It is recorded in HANDOFF §7 item 9's sibling (the tier-drift closure, commit
`9f90482`) and in `PROVENANCE_FIELDS.md` §9(b). **Cost to fix: ~5 minutes** — one
inline marker, same pattern as the banner at 434.

**Why I did not fix it:** the `[externally-verified]` item had been filed five
times, and I closed the *definitions* drift, which was the filed item. Re-auditing
the four sites where the tier is *asserted* is a different job with a real
judgment in it (does ROC-AUC 0.755 on the Lipp corpus meet "external judge on
real data"?), and doing it under cover of the definitions fix would have been
scope creep on an item that was already overdue. Three of the four are inside
the 434 banner. **568 is the only live one, and it is small.**

---

## 6. TRAPS AND CONSTRAINTS THAT SHAPED METHOD

**`docs/claims.json` is hand-formatted and MUST be edited with targeted string
edits.** I round-tripped it through `json.dump(indent=1)` and turned 225 lines
into 630 — 847 lines of diff churn hiding three lines of content. I reverted and
re-edited by hand. **Do not parse-and-reserialise this file.** It cost a
commit-splitting detour and it will cost the next session the same.

**`reconcile.sh` C1/C2 require every new `docs/*.md` to appear in HANDOFF §5.1**,
or the next SessionStart reports a finding. This file is indexed. **And it must
be `git add`ed before reconcile goes clean** — C2 compares against
`git ls-files`, so a new-but-untracked document that you have already indexed
reports as `C2 phantom: … listed in §5.1, absent from tree`. That is the check
behaving correctly and it looks like a bug for about thirty seconds. C2 extracts
only `\.md` paths, so `analysis/scripts/*.py` is invisible to it — which is why
`s1_crossfile.py` is **not** indexed. That was a decision, not an oversight: no
other script is indexed, and an entry that nothing checks is worse than none.
`PROVENANCE_FIELDS.md` §10.5 names the path instead.

**§13 is numbered 13, not 12, because §12 was already taken** by the built
mechanical layer. The instruction said "§12"; the number moved, the content did
not.

---

## 7. THREADS NOTICED AND NOT PULLED

- **`[unverified]` and `[snippet]` are bracket-form tokens in tier position that
  are not in the six-tier scale** (TERMS_INVENTORY §5(b)). Unresolved there,
  unresolved here. Adjacent to the tier drift I *did* fix, and deliberately not
  bundled with it.
- **`README_correction_0j_draft.md` is titled "draft" and marked APPLIED
  internally** (TERMS_INVENTORY §5(c)). Filename/status mismatch, still open.
- **The claims.json → VALIDATION.md locator link still has no check** (pilot §2
  D1). **Its disposition has changed and nobody should now build that check:**
  the file is frozen as a pilot artifact, so its twelve stored line ranges will
  rot as VALIDATION.md grows, and that is *acceptable* — the anchors are
  retained as evidence of what was populated, not as live pointers. Building a
  drift check for a frozen file would be work in service of a stopped thread.
- **C4 has still never fired in anger.** Unchanged from the prior residue.

---

## 8. WHAT I WOULD TELL THE NEXT SESSION

**The specification was not wrong; it was aimed at the rarest failure it
documented.** Rule 11 records eight instances — seven are header staleness, one
more is caught by C3, and orphaning is covered completely by C1/C2. **Form 3,
the only form requiring per-claim fields, has exactly one recorded instance.**
Five design steps and a pilot went into the field layer that addresses it.

That is not a story about a bad design. Every step was sound in isolation, and
§13's line — *what runs reads the tree; what does not reads fields* — was
invisible until something tried to populate the fields and count what it was
populating. **The generalisable form: a specification's cost is discovered by
enumeration, not by review.** Nothing in five rounds of reading found this; the
first attempt to count found it immediately.

**Do not restart the population thread to "finish" steps 2–4.** They are
finished. They are a reader's specification, and §13 says so.
