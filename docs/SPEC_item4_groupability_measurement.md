# Spec — item 4: groupability / consensus-frequency measurement

Status: designed, NOT run. **Run AFTER the `_result_key` two-algorithm fix**, not
before — pre-fix groupability answers a question the fix makes obsolete.

Purpose: produce a number that (a) sizes the display badge, and (b) tells us
whether extending `_CWE_CLASS` is a larger win than the badge for less work.

Pre-registered here before any data exists, per GENESIS Part 3 method
("pre-register before probing"), so neither the badge design nor the map-
extension decision can be rationalized post-hoc.

---

## 1. Denominator cascade

Per project, per tool. Report all three; **D2 is the headline**.

| | definition |
|---|---|
| D0 | raw SARIF results |
| D1 | D0 − analysis diagnostics: `missingInclude`, `missingIncludeSystem`, `toomanyconfigs`, `checkersReport`, `purgedConfiguration`, `normalCheckLevelMaxBranches`. These are messages about the RUN, not findings about the code |
| **D2** | D1 − `_CWE_DENY` hits. **Triage-relevant findings — what a reviewer would actually look at** |

Numerator: findings for which `_cwe_class` resolves.

Rationale for excluding denied CWEs from the denominator rather than counting
them as a suppressor: `_CWE_DENY` rejecting CWE-398 (poor code quality),
CWE-563 (unused variable), CWE-561 (dead code) is the filter working as
designed. Counting correct rejection as a limitation inflates the apparent
problem. Report the raw D0 rate too, but do not lead with it.

## 2. Ungroupable split — THREE causes, not two

> **SCOPE CORRECTION (2026-07-26): this section is an INPUT TO THE `_result_key`
> FIX, not a measurement that follows it.** The two-algorithm fix keys cross-tool
> matching on location + CWE class, and the class comes from `_cwe_class` — so
> map coverage determines how often the FIXED KEY can match at all, not merely
> how often the display badge fires. Settling coverage is part of designing the
> fix; deferring it to this measurement would mean shipping a key whose hit rate
> was never measured. The U1/U2 split and the CWE-664/758 deny-vs-map judgment
> below now belong to HANDOFF §7 item 2. They are retained here because the
> measurement still has to report against them.

Within D2, every ungroupable finding falls into exactly one of:

- **U1 — no CWE available.** cppcheck emitted no `cwe` attribute, so the ruleId
  is a check name, and the message carries no CWE number. A cppcheck
  limitation; not fixable by us.
- **U2 — CWE present but not in `_CWE_CLASS`.** **Our map coverage gap. Fixable
  by editing a 28-entry dict.**

(Denied findings are outside D2 by construction and are not a third bucket.)

U2 was missed by the original framing of this problem and may dominate.
A-priori evidence from `cppcheck --errorlist` (342 checks, tool-authoritative,
already captured):

```
 14 CWEs map to a class      ->  31 checks
  7 CWEs correctly denied    -> 149 checks
 35 CWEs UNMAPPED            -> 116 checks   <- U2
 46 checks emit no CWE       ->  46 checks   <- U1
```

Unmapped CWEs cover ~4x more check TYPES than mapped ones. Candidate genuine
omissions, to be confirmed against real frequency rather than assumed:
CWE-786 (buffer access before start), CWE-131 (incorrect buffer size calc),
CWE-590 (free of non-heap memory), CWE-762 (mismatched memory management),
CWE-252 (unchecked return value), CWE-467 (sizeof on pointer).

Counter-note: CWE-664 (improper resource lifetime control, 20 checks) and
CWE-758 (undefined behaviour, 20 checks) are generic junk-drawer categories and
are plausibly **deny-list** candidates rather than map candidates. Do not
assume every unmapped CWE should be mapped.

Check types are not finding frequency — a handful of checks fire constantly.
The real measurement must weight by observed findings, not by check count.

## 3. What actually decides badge prominence

Per-finding groupability is necessary but NOT sufficient: a display group also
requires two tools co-located within `TOL=3` on the same class. So report the
realized end quantity, not just the per-finding property:

- **G1** — `display_groups_count` per project
- **G2** — % of ranked findings carrying a `display_group` badge *(the decision
  variable)*
- **G3** — count of `n_tools > 1` *(post-fix: the merge rate; this is also the
  direct measure of whether the `_result_key` fix worked)*

Pre-fix, G3 is expected to be 0 and serves as a control confirming the
structural finding at scale.

## 4. Two configurations

- **P** — exactly what `action.yml` runs today
- **I** — with `-I` include paths per project

`action.yml:57` passes no include paths, so P is production-faithful *and*
exhibits the misconfiguration. The P→I delta quantifies what that costs, and is
itself a bug report against `action.yml`.

## 5. Project set

Lipp-corpus overlap, cheap to obtain (network confirmed working on this
machine): **sqlite3, libpng, libxml2, libtiff**, plus **binutils** if time
permits.

Report **per-project AND pooled**. Per-project is not optional — if the rate
varies widely by codebase, that spread is itself the finding.

Caveat to state, not to drop: sqlite3 ships as an amalgamation (single
translation unit), which is atypical and may skew both co-location and
include-resolution behaviour.

## 6. Pre-registered decision rule

Committed before the number exists.

| G2 | badge design |
|---|---|
| ≥ 10% | prominent: per-row marker + summary stat |
| 3–10% | modest: small per-row marker + summary stat |
| < 3% | minimal: summary stat only, no per-row chrome |
| spread > 2x across projects | adaptive: keyed to that report's `display_groups_count` |

Separately, on the U1/U2 split:

| result | action |
|---|---|
| U2 > U1 | extend `_CWE_CLASS` first — cheaper than badge work and higher yield |
| U1 ≥ U2 | map extension is low-yield; the cppcheck limitation binds |

## 7. SECOND QUESTION — does the fixed shipped path reproduce VALIDATED
##    conditions? (added 2026-07-26; distinct from §1-6)

§1-6 measure **groupability**: how often the display/merge machinery CAN fire.
That is not the same question as whether the post-fix shipped path reproduces
the conditions ROC-AUC 0.755 was measured under. Both are needed; only the
first was originally scoped.

Why it matters: the "fix moves shipped toward validated" argument
(VALIDATION.md, 2026-07-26) is about DIRECTION only. It is a precondition
argument, not a transfer guarantee. The reconstructed Lipp envelope had a
particular merge topology; a location+class cross-tool key on real scanner
output may or may not reproduce it. If it does not, 0.755 must be **re-earned
on real scanner output, not inherited**.

### What to measure

A coarse comparison is enough to answer "does 0.755 plausibly transfer, or does
it need re-earning?" — this does not require re-running the full CVE study.

On a real library, post-fix, with the real scanner pair:

- **M1 — merge rate.** Fraction of findings participating in a cross-tool
  merge. Compare against the reconstructed envelope's rate (derivable from the
  recorded 22,403 raw → 21,061 unique / 1,318 overlaps: ~5.9% of raw findings
  were multi-tool).
- **M2 — `n_tools` distribution.** Post-fix histogram vs the envelope's. The
  envelope reached n_tools=3 on real overlaps; if the fixed shipped path is
  almost entirely n_tools∈{1,2}, the consensus signal has a materially
  different shape than the one validated.
- **M3 — merge composition.** Which CWE classes / rule kinds the merges land
  in. The envelope's merges were spread across tools with genuinely disjoint
  miss-sets; two tools with correlated blind spots would produce merges that
  look similar in count but carry less signal (the "good vs bad diversity"
  distinction already in the framing sweep).
- **M4 — sanity direction.** Does vulnerable-rate still rise monotonically with
  agreement, as it did in the validation (1 tool 0.9% → 4 tools 11.6%)? This
  needs ground truth, so it is only answerable on a corpus with known CVEs —
  i.e. the Lipp projects, run with REAL scanners this time rather than a
  reconstruction.

### Decision rule (pre-registered)

| outcome | conclusion |
|---|---|
| M1/M2 broadly resemble the envelope's | 0.755 **plausibly transfers**; record as plausible, still not re-verified |
| M1/M2 differ materially | 0.755 **does not transfer as inherited**; it must be re-earned on real scanner output before being quoted for the shipped path |
| M4 runnable and monotonic holds | strongest available in-reach evidence for transfer |
| M4 not runnable | say so; do not substitute M1-M3 agreement for it |

Note M4 is the only one of the four that touches ground truth. M1-M3 compare
SHAPE, not correctness — they can tell you the input looks like the validated
input, never that the ranking is right. Do not report M1-M3 agreement as
validation of the ranking.

## 8. Honest bound to carry into the report

The 11% groupability figure from the 25-line `demo.c` (n=9, 3 of which were
include-resolution artifacts) is a directional signal only and must not be
quoted as a rate. This spec exists because that number cannot bear the weight
of a design decision.
