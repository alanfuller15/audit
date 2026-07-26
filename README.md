# audit — a multi-scanner consensus re-ranker for static analysis

**The idea in one line:** run several security scanners, then rank findings higher where
*independent tools agree* — because when different tools flag the same spot, it's much more
likely to be a real bug worth your time.

Static analysis tools are noisy: run one on real code and you get hundreds of warnings, most of
them false alarms. This is the #1 documented reason teams abandon these tools. `audit` attacks
the noise by trusting **consensus**: it ingests findings from multiple scanners (in the standard
SARIF format), merges the ones pointing at the same bug, and re-ranks so the agreed-upon,
review-worthy findings rise to the top.

## What's established, and what isn't

**The premise is validated — by others, on real data.** Lipp et al. (ISSTA'22) evaluated six
static C analyzers against 192 validated CVEs across 27 real projects and found that combining
tools detects substantially more vulnerabilities than the best single tool. That is *their*
result on *their* data, and it is why this tool is built the way it is.

**One finding measured here, on that same corpus:** functions flagged by *multiple independent
tools* are about **1.5x more likely to contain a real CVE** than comparable functions flagged by
one (1.54% vs 1.02%, p < 0.0001, against real CVE ground truth). That figure is **size-matched** —
larger functions attract both more tool attention and more bugs, so the comparison controls for
size. Uncontrolled, the same gap looks like 2.7x; roughly 40% of it is size. The agreement signal
is real, and it is smaller than it first appears.

**What that does not establish — and this distinction is the point:** that a *ranker* built on
that signal helps you triage. This implementation's ranking has **not** been shown to beat a
size-matched baseline on the corpus where it was properly tested. At file level, agreement count
correlates strongly with size (Spearman +0.63), and once size is controlled the ranking advantage
is not statistically significant. Ranking files by size alone scores *higher* on ROC-AUC than the
consensus signal does.

So: the signal exists; turning it into a useful ordering is unproven. Earlier versions of this
README quoted performance figures for the ranking. They did not survive controlled baselines and
have been removed.

## What has been checked

The ranking is unproven; the machinery underneath it is tested. Each of these is covered by
regression tests in `examples/fixtures/`, and every one was found by running real scanners on
real code:

- **Cross-tool deduplication** — two algorithms, as the DefectDojo model intends: a tool's own
  fingerprint for same-tool dedup, location + CWE class for cross-tool. Using the former for both
  made cross-tool agreement impossible for the shipped scanner pair.
- **Engine-lineage guard** — SpotBugs and FindBugs are one engine under two names; counting them
  as two would manufacture consensus out of self-agreement. Agreement is counted per *engine*.
- **Degenerate-fingerprint detection** — semgrep run unauthenticated emits one constant
  fingerprint for every result; flawfinder's context hash collides on repeated code. Trusting
  either silently destroys findings. Both are detected and worked around.
- **Path-root mismatch disclosure** — bytecode-based and source-based analyzers report paths
  relative to different roots, which silently yields zero cross-tool matches. Detected and
  reported rather than left as an unexplained zero.
- **CWE resolution from structured SARIF taxa**, falling back to rule text only where a tool
  declares no taxon.

None of these are performance claims. They are things that were broken, are now not, and stay
that way because tests hold them.

## Try it in ~2 minutes (C/C++)

```bash
# 1. get findings from two scanners (SARIF format)
flawfinder --sarif your_code/ > flawfinder.sarif
cppcheck --enable=all --xml --xml-version=2 your_code/ 2> cppcheck.xml
python3 src/cppcheck_xml_to_sarif.py cppcheck.xml cppcheck.sarif

# 2. re-rank by consensus (with two scanners this column is usually
#    empty — see Honest scope)
python3 src/audit.py --ingest flawfinder.sarif cppcheck.sarif --json out.json

# 3. (optional) collapse cross-tool duplicates in the display
python3 src/audit_dedup_display.py out.json out_display.json
```
The top of `out.json` is your review queue, ordered by review-worthiness.

## Honest scope (what it is and isn't)

- **The premise is validated; this implementation's ranking is not.** The figure above measures
  tool agreement in a published CVE dataset. How well `audit` reproduces that on live scanner
  output has not been measured against CVE ground truth — it implements an externally validated
  premise, and how well it implements it is a separate, open question. See `docs/VALIDATION.md`.
- **The default pair rarely agrees, and that is a property of the scanners, not a bug.**
  flawfinder pattern-matches risky functions; cppcheck does dataflow. They look for different
  things, so they seldom flag the same line for the same reason. On real zlib (1,164 findings)
  they produced **2 cross-tool merges, both in benchmark code and none in library sources**.
  Consensus needs tools with *partial* overlap — different enough that agreement is independent
  evidence, similar enough that they can agree at all. Adding a third scanner with genuinely
  different coverage is the lever that helps; expect a sparse consensus column with two.
- **The premise was measured on C/C++** using findings from the six analyzers in the source study
  — flawfinder, cppcheck, CodeQL, CodeChecker, Infer, and CommSCA, the anonymized commercial tool
  that was the strongest single performer. `audit` itself has been run against live output from
  flawfinder, cppcheck, and semgrep. Other languages/tools: unproven, not disproven — the engine
  is language-agnostic (works on SARIF), but the consensus signal hasn't been validated elsewhere
  yet.
- It's a **triage aid** — it surfaces review-worthy code. It does **not** prove exploitability.
- The newest piece (cross-tool duplicate display) handles the case where tools agree on *location*.
  Harder cases (a bug whose source and sink are in different functions) are documented as an open
  problem, not solved.

## Why trust this
Because the record includes what failed, and you can check it. `docs/VALIDATION.md` carries every
performance claim this project made, the baseline that broke it, and the numbers — including
ManualUp/ManualDown from the defect-prediction literature and the size-matched controls that
retired three separate headline figures. Feedback and criticism very welcome.

*(License: see LICENSE. This is a research-grade tool / proof of concept.)*
