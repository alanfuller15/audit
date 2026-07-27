# Session handoff — 2026-07-26 (second session of the day)

Things the next session needs that are NOT already in HANDOFF.md or
VALIDATION.md. Read HANDOFF §0 and the new §5.1 DOCUMENT INDEX first; this is
the residue.

The previous session's handoff is `SESSION_HANDOFF_2026-07-26.md`. Its §1
("do the 0j stratification check first") is DONE — see HANDOFF 0j.

---

## 1. WHAT WAS IN FLIGHT WHEN THIS SESSION ENDED

**Nothing.** No half-run command, no uncommitted work, no open branch. Working
tree clean, local == origin/main, harness 112 passing.

That is deliberate rather than lucky: the one remaining open decision — §6.2
question 3 — was explicitly reserved by the inventor to come to fresh. **Do not
open it on their behalf.** If they raise it, the accumulated evidence is in
NEGATIVE_RESULT.md §1–2a and HANDOFF §6.1a.

---

## 2. THE THING I WOULD DO FIRST, AND IT IS NOT A WORK ITEM

**Run a reconciliation sweep before starting anything.** HANDOFF §8 rule 11 now
records the pessimistic-direction asymmetry as STRUCTURAL, at four instances and
four-for-four. This session found five stale headers in one sweep at the start,
and three more at the end, in a document that had just been reconciled.

The sweep is cheap: for each item you might act on, grep the tree for the thing
its header says is missing. Three of this session's finds took one grep each.

**Budget it as a first step, not as something to notice opportunistically.**
That is the specific behavioural change rule 11 asks for, and it is the one
thing in this handoff most likely to save you a day.

---

## 3. THE MISTAKE THAT MATTERS MOST, AND HOW IT FELT FROM THE INSIDE

This is the residue that is not in the rule.

I wrote `docs/NEGATIVE_RESULT.md`, a public document, asserting that
methodologically diverse scanners do not produce co-located agreement. **Our own
VALIDATION.md had refuted that days-of-commits earlier** — the granularity
overturn, 0→66 for our own zlib pair. I then put a sentence in the **README**
saying the same thing.

What is worth passing on is not that it happened but **how ordinary it felt**:

- I was reading HANDOFF §6.2, which was internally consistent, well-argued, and
  had never been updated. Nothing about it looked stale.
- I **quoted the refuting numbers in my own §4** while framing them as a minor
  "boundary condition". I had the disproof in hand and wrote around it.
- It passed the inventor's review too, for a different reason — they read it
  against memory of the session rather than against the evidence record.
- The document was coherent, cited, agreed by two readers, and false.

**The tell I should have caught: I was explaining why a figure I had just cited
did not undermine the claim I was making.** That explanation is where the
failure lived. Rule 11 now names it as a stop signal. If you catch yourself
doing it, stop and re-read the source.

Practical consequence, now in rule 11: **VALIDATION.md outranks HANDOFF.md**,
and anything entering a public artifact gets re-derived from VALIDATION.md — not
from a handoff item, not from what this session remembers.

---

## 4. WHAT SHAPED DECISIONS BUT DID NOT MAKE IT INTO A RECORD

**a. The convergent result is the finding of this session, and it was assembled
from two evaluations neither of which was designed to produce it.** Direction B
and function-level matching were built for different reasons, months apart in
project time, and each individually reads as "mechanism works, ranking flat".
Only side by side do they say something stronger: *recovering more observable
agreement has not once improved the ranking, and here is why* (92.2% of
recovered co-locations are class-disagreements, correctly rejected). It is in
NEGATIVE_RESULT §2a and HANDOFF §6.1a. **If a third recovery mechanism is
proposed, that section is the thing to argue against first.**

**b. I twice nearly shipped a measurement that would have manufactured its own
result**, and both were caught only by checking rather than by suspicion. The
`max(reported line)` size proxy would have fired a false size-correlation alarm
on a real run. The capture-recapture estimate initially paired mismatched
populations. Neither was flagged by anything except deliberately re-deriving the
number. **The habit that caught both: when a result is convenient, compute the
thing that would embarrass it.**

**c. The corpora live in a temp directory and are ONE REBOOT from gone.**
`AUDIT_CORPUS_ROOT` currently points at
`/private/tmp/claude-501/-Users-caitlinfuller-audit/e15ca3d8-.../scratchpad`.
The scripts, fetch commands, pinned SHAs, SWHIDs and checksums are all committed
— so this is recoverable — but rebuilding OWASP Benchmark with `target/classes`
is the slow part (269 MB, needs JDK 17 + maven). **If you plan corpus work,
rebuild early rather than discovering it mid-analysis.** analysis/README.md §2
and §3a have everything needed.

**d. A judgement call that could reasonably go the other way.** I recorded
`3e` (hierarchy-aware CWE resolution) as *implemented, correct, and currently
inert* — it changes nothing on any corpus on disk, because the taxa path already
resolves those cases. An equally defensible view is that shipping code with zero
measured effect is not worth its maintenance cost, and it should have been left
filed. I kept it because its value is conditional on a tool that emits no taxa,
which is a real case, and because the branch is tested. If a future session is
trimming, this is the first thing I would put on the table.

**e. The unexplored thread with the most reach is still 0f's.** How much of the
static-analysis ecosystem is ported rules? We measured ONE registry: 23.4%
declare derivation, seven upstreams where the vendor names four, and textual
similarity recovers 0 of 44 known-derived rules because ports get rewritten.
**The generalisation is untested and I deliberately did not extend to other
registries** — that is a different study, and doing it badly would be worse than
not doing it. But it is the question with reach past this project.

---

## 5. WHAT CHANGED IN THE SHIPPED TOOL

Only two things touched `src/` this session, both disclosure-only:
- **0h** — per-run size-correlation disclosure, gated. Reports NOT APPLICABLE
  rather than an unstable coefficient. Never filters or reweights.
- **0c option (a)** — deterministic suffix linkage behind a cardinality-1 guard.
  Reproduces hand-alignment exactly (Struts 0→1, OWASP 0→1,427).
- **3e** — hierarchy-aware CWE resolution (inert, see §4d).

Everything else was measurement, correction, or documentation.

---

## 6. STATE AT HANDOFF

- working tree clean, local == origin/main
- harness **112 checks passing** (was 67 at session start); render harness clean
- `analysis/` runs **19 of 21 scripts** from a clean clone given a corpus root;
  0 hard errors with no corpus. The 2 that fail do so deliberately — see
  analysis/README.md §3a.
- README carries: the 1.5x with its interval and threshold-not-a-score limit,
  the 22.6% derived-agreement bound, and a pointer to NEGATIVE_RESULT.md.
  **No performance claim for the ranking.**
- open board: §6.2 Q3 (reserved by the inventor), item 6 and item 8 (both need
  STUDY first). Blocked: item 3 (Rosetta, inventor's call, and NOT the
  priority), §6.2 Q2 (semgrep emits no logicalLocations), per-finding precision
  rho (permanent).
- items closed this session: 0c, 0e, 0f (both arms), 0g, 0h, 0j, 0k, 2, 3e.

---

## 7. IF YOU READ ONLY ONE THING

Rule 11, and its two forms. Staleness is wrong text; orphaning is missing text.
Four-for-four in the pessimistic direction. **When this file and the tree
disagree, the tree is probably further along than the file says.** Check first,
then act.

[UPDATED 2026-07-26 by two later sweeps, so this pointer does not undercount
what it points at: rule 11 now has THREE forms and EIGHT instances. The third
form is a correction that is complete in its own terms and never re-derives the
NUMBERS attached to the claim it corrected — which is how a figure in this
file's own §6 survived a sweep that had just corrected the sentence around it.
Go to rule 11 itself; this line is a pointer, not a summary.]
