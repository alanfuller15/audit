## Quickstart (copy-paste, ~2 minutes)

```bash
# 1. Scan your code with two scanners (installs: brew install flawfinder cppcheck)
flawfinder --sarif ./yourcode/ > flawfinder.sarif
cppcheck --enable=all --output-format=sarif ./yourcode/ > cppcheck.sarif

# 2. Re-rank the findings by review-worthiness
python3 audit.py --ingest flawfinder.sarif cppcheck.sarif

# 3. (optional) save machine-readable output
python3 audit.py --ingest flawfinder.sarif cppcheck.sarif --json out.json
```

Keep `audit.py` and `tool_quality_weighting.py` in the same folder. Python 3, no
extra packages needed. Full explanation below.

---

# audit.py — a review-worthiness re-ranker for static-analysis findings

## What this does, in one paragraph

You run one or more static-analysis security scanners (cppcheck, flawfinder,
CodeQL, etc.) on your C/C++ code. Each spits out findings — often hundreds,
in no useful order, with duplicates across tools. `audit.py` ingests those
findings (in standard SARIF format), removes duplicates, and re-ranks them by
**review-worthiness**: which findings are most worth a human's attention first.
It does this deterministically — same input, same ranking, every time — so it's
an auditable triage layer, not a black box.

## What it is NOT (read this — it prevents misuse)

- It does **not** find vulnerabilities. Your scanners do that. This re-ranks
  what they found.
- It does **not** rank by exploitability or real-world severity. It has no
  threat feeds. It ranks by *review-worthiness* — a signal built from how many
  distinct tools flagged a thing, tool quality, finding severity, and location.
- It is **not** a replacement for human review. It puts the findings most
  worth looking at first. A human still decides what's real.

## Why it helps

Two scanners on the same code often produce 200+ raw findings with heavy
duplication and no priority. Manually triaging that is the bottleneck. This tool:
- **Deduplicates** across tools (same file+line+rule = one finding).
- **Rewards agreement**: a finding multiple *distinct* tools flag is more likely
  real — this is grounded in published research (tools with different methods
  have different blind spots, so agreement is signal).
- **Weights tool quality**: an agreement between two strong tools counts more
  than two weak ones (disclosed per run; see "Honesty" below).
- **Ranks deterministically** so the triage is reproducible and auditable.

## How to run it

Requirements: Python 3 (no external packages needed for the core tool).

1. Run your scanners, exporting SARIF. Examples:
   ```
   flawfinder --sarif ./yourcode/ > flawfinder.sarif
   cppcheck --enable=all --output-format=sarif ./yourcode/ > cppcheck.sarif
   ```
   (For cppcheck, add include paths with `-I` for more accurate results:
   `cppcheck --enable=all -I ./yourcode/include --output-format=sarif ...`)

2. Ingest and re-rank:
   ```
   python3 audit.py --ingest flawfinder.sarif cppcheck.sarif
   ```
   Add `--json out.json` or `--sarif out.sarif` to save machine-readable output.

3. Read the top findings. They're ordered by review-worthiness, with the
   scanners that flagged each one shown in brackets.

`tool_quality_weighting.py` must sit in the same folder as `audit.py` — it's a
required companion, not optional.

## Honesty (the tool tells you what it's doing)

Every run discloses its weighting mode:
- **MEASURED** — you gave it a labeled benchmark, so it computed tool weights
  from your actual data.
- **PRIOR** — no answer key, so it applied *coarse* cross-dataset tool-quality
  priors (e.g. commercial tools weighted above basic ones), clearly labeled as
  priors that may not hold for your specific codebase.
- **INACTIVE** — it didn't recognize your tools, so it fell back to treating all
  agreements equally (flat), and says so.

You always see which mode ran. The tool never silently pretends to know more
than it does.

## What's been verified, and what hasn't

This tool is honest about its own validation status (see VALIDATION.md for the
full ledger). In short:
- **Verified on real scanner output**: ingesting, deduplicating, and ranking
  real flawfinder and cppcheck findings on real C code works and is reproducible.
- **The agreement/diversity principle is grounded** in published research on a
  real 193-CVE dataset.
- **Not yet verified**: whether the ranking order is *correct* for your specific
  review priorities — that needs a human reviewer's judgment on your own code.
  Treat the ranking as a strong starting point, not a verdict.

## The other files in this bundle

The remaining docs (GENESIS_TEMPLATE, HANDOFF, VALIDATION, etc.) are the
tool's *development and validation record* — how it was built and checked. You
don't need them to use the tool. They're here for transparency and for anyone
continuing the development.

---

## Using it in GitHub Actions (automated on every commit)

This repo is also a reusable GitHub Action. To run the scan-and-rerank pipeline
on your own C/C++ code automatically, add this workflow to your repository at
`.github/workflows/audit.yml`:

```yaml
name: audit
on: [push, pull_request]
permissions:
  security-events: write   # to upload findings to the Security tab
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alanfuller/audit@v1        # this action
        with:
          path: ./src                    # your C/C++ directory
          cppcheck: 'true'
          upload-sarif: 'true'
```

On every push or pull request, it will:
1. Run flawfinder and cppcheck on your code,
2. Re-rank the findings by review-worthiness (this tool),
3. Upload the ranked findings to your repo's **Security tab** (native GitHub
   annotations), and
4. Attach the **HTML triage report** as a downloadable build artifact.

**On build-gating (deliberately omitted):** this action does *not* fail your
build based on findings. That's a design choice, not an oversight — this tool
*re-ranks* what your scanners found; it does not decide what's a real
vulnerability. Gating a build on a re-ranker's score would over-claim what the
tool knows. It surfaces and prioritizes; a human still decides. If you want
hard build-gating, gate on your scanner's own severity threshold, not on this.

## Repo layout

```
action.yml                     the reusable composite action
src/audit.py                   the re-ranker (core tool)
src/tool_quality_weighting.py  consensus weighting (required companion)
src/audit_html_report.py       HTML report generator
src/cppcheck_xml_to_sarif.py   cppcheck XML->SARIF (CI-robust, no 3rd-party dep)
examples/sample_c/demo.c       deliberately-flawed C so the demo produces findings
.github/workflows/demo.yml     runs the action on the sample code
docs/                          development + validation record (GENESIS, VALIDATION, etc.)
```
