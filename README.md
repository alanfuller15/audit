# audit — a multi-scanner consensus re-ranker for static analysis

**The idea in one line:** run several security scanners, then rank findings higher where
*independent tools agree* — because when different tools flag the same spot, it's much more
likely to be a real bug worth your time.

Static analysis tools are noisy: run one on real code and you get hundreds of warnings, most of
them false alarms. This is the #1 documented reason teams abandon these tools. `audit` attacks
the noise by trusting **consensus**: it ingests findings from multiple scanners (in the standard
SARIF format), merges the ones pointing at the same bug, and re-ranks so the agreed-upon,
review-worthy findings rise to the top.

## Does the idea actually work? (validated on real vulnerabilities, not synthetic benchmarks)

The **premise** — that agreement between independent tools predicts real vulnerabilities — was
tested against **135 real vulnerable functions across 9 real open-source C/C++ projects**
(binutils, ffmpeg, libpng, openssl, sqlite, and more — using their known CVEs as ground truth).
The figures below come from tool-agreement counts in that published dataset (Lipp et al.,
ISSTA'22), and they validate the signal `audit` is built on:

- **ROC-AUC 0.755** — rank files by how many independent tools agree, and a vulnerable file
  outranks a clean one ~3 times out of 4 (0.5 = coin flip).
- **Catch ~65% of vulnerable files by reviewing just the top 20%** of ranked files.
- **~13x concentration** — files flagged by 4 tools were ~13x more likely to be truly vulnerable
  than files flagged by just 1.

These line up with independent published research (combining tools beats the best single tool by
~17 percentage points, arXiv:2407.12241).

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

- **The premise is validated; this implementation's ranking is not.** The figures above measure
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
- **0.755 is useful, not magic.** It beats a coin flip and the best single tool; it's not an oracle.
- The newest piece (cross-tool duplicate display) handles the case where tools agree on *location*.
  Harder cases (a bug whose source and sink are in different functions) are documented as an open
  problem, not solved.

## Why trust the numbers
Every claim here was measured against real CVEs and reported honestly — including results that
weren't flattering. The methodology (external grounding, significance-testing surprising results,
golden-master safety checks) is documented in the repo. Feedback and criticism very welcome.

*(License: see LICENSE. This is a research-grade tool / proof of concept.)*
