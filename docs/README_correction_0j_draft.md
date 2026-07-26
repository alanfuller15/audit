# README correction #4 — DRAFT, NOT APPLIED

Produced by item 0j, 2026-07-26. Evidence: `docs/VALIDATION.md` "0j RESULT".
**Nothing in the README has been changed.** This is a proposal for the
inventor's decision.

---

## What 0j actually found (short version)

The correction that was anticipated is NOT the correction that is needed.

| claim | verdict |
|---|---|
| ~1.5x, size-matched | **HOLDS.** 1.51x at 10 strata, 1.52x at 200, 1.39x under continuous covariate adjustment, 1.31x under exact-LOC matching. Direction consistent in 9/9 projects. |
| `p < 0.0001` | **WITHDRAWN.** The statistic held one arm fixed. Honest p is ~0.03–0.08 unclustered, ~0.001 clustered on project. Project-bootstrap 95% CI [0.99x, 2.58x]. |
| "*multiple independent tools*" implying more agreement = more signal | **NOT SUPPORTED.** The effect is entirely the 1→2 step; flat at 3 tools, point-estimate negative at ≥4. |

So the README keeps a number, but loses a significance claim and needs its
wording narrowed. The premise (cited to Lipp) and the correctness inventory are
untouched.

---

## Proposed edit — README.md lines 20–25

### CURRENT

> **One finding measured here, on that same corpus:** functions flagged by *multiple independent
> tools* are about **1.5x more likely to contain a real CVE** than comparable functions flagged by
> one (1.54% vs 1.02%, p < 0.0001, against real CVE ground truth). That figure is **size-matched** —
> larger functions attract both more tool attention and more bugs, so the comparison controls for
> size. Uncontrolled, the same gap looks like 2.7x; roughly 40% of it is size. The agreement signal
> is real, and it is smaller than it first appears.

### PROPOSED

> **One finding measured here, on that same corpus:** functions flagged by **two or more** tools
> are about **1.5x more likely to contain a real CVE** than comparable functions flagged by one
> (1.54% vs 1.02%, against real CVE ground truth). That figure is **size-matched** — larger
> functions attract both more tool attention and more bugs, so the comparison controls for size.
> Uncontrolled, the same gap looks like 2.7x; roughly 40% of it is size.
>
> **The honest bounds on it, since they matter more than the number:** the effect is *marginal*,
> not overwhelming — p ≈ 0.03–0.08 depending on the test, and the 95% confidence interval across
> the nine projects in the corpus runs from 1.0x to 2.6x. It is stable under every size control
> tried (matching at 10 to 200 strata, exact-line-count matching, and continuous covariate
> adjustment) and the direction holds in all nine projects, so it is not an artifact of one
> project or one choice of control. But nine projects is a small sample to generalise from.
>
> It also supports **only** "two tools beat one." Going from two agreeing tools to three or more
> does not measurably increase the odds further, so this is a threshold, not a confidence score.

### Why each change

1. **Delete `p < 0.0001`.** It came from a resampling test that held the
   multi-tool group's own 81/5,269 fixed and resampled only the controls,
   ignoring sampling variability in the numerator. Tests that vary both arms
   give p = 0.041–0.054 (two-proportion z), 0.030–0.058 (within-stratum
   permutation), 0.076 (logistic with continuous log LOC). Quoting `<0.0001`
   overstates the certainty by roughly three orders of magnitude.

2. **Replace "*multiple independent tools*" with "two or more."** The italics on
   *independent* invite the reading that agreement is a graded confidence
   signal. It is not: OR 1.47 at two tools, 1.35 at three, 0.67 at four-plus.
   (Also: HANDOFF 0f found that on real code every cross-methodology agreement
   this project has observed was a semgrep rule agreeing with its own
   FindSecBugs ancestor, which makes "independent" a word to use carefully.)

3. **State the interval, not just the point estimate.** This project has retired
   three claims for being published without their control. The control here was
   applied and survived; publishing the interval alongside it is the same
   discipline applied to precision rather than to bias.

4. **Keep the number.** It survived a harder test than it was originally given.
   Removing it would be as inaccurate as the `p<0.0001` was.

---

## The alternative the session handoff anticipated — NOT recommended

SESSION_HANDOFF §2 pre-committed to: "If 0j goes against the 1.5x, the right
move is the fourth README correction — removing the number and leaving the
correctness inventory as the only claim."

**That branch did not fire.** 0j went *for* the 1.5x. Removing the number now
would mean the README understated its own evidence, which is a failure in the
same family as overstating it. Recorded here so a later session does not
execute the pre-commitment without checking which branch was taken.

§3e of the same handoff (whether the "What has been checked" section reads as
compensating if the 1.5x fell) is likewise moot — the section is no longer the
sole evidential content.

---

## Also worth the inventor's attention, found while checking the README

`docs/HANDOFF.md` item 0c describes the path-root mismatch as "HIGH PRIORITY —
LIVE PRODUCTION DEFECT … Scoped, NOT implemented." **It is implemented.**
`_path_root_mismatch` is at `src/audit.py:834`, wired in at `audit.py:1041`
and `:1339`, and rendered at `src/audit_html_report.py:74`. The README's
"Path-root mismatch disclosure" bullet is accurate; HANDOFF 0c is stale and
should be marked done rather than left as a live defect.

Note the scope of what shipped: it *discloses* the mismatch, per the
recommended sequence (b)-then-(a). It does not *merge* across roots, so the
suffix-matching half of 0c is genuinely still open.
