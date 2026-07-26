#!/usr/bin/env python3
"""
verify_dedup_render.py — golden check for the cross-tool display path.

Runs the full shipped chain against the minimal fixture pair and asserts that
cross-tool agreement survives all the way to rendered HTML.

Usage, from the repo root:
    python3 examples/fixtures/verify_dedup_render.py

Exit 0 = the display path is intact.
Exit 1 = a stage dropped it. The failing stage is named.

Before the fix, stages 3 and 4 fail. That is the point: this script documents
the gap first, then proves the fix.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import audit
import audit_dedup_display
import audit_html_report

A = os.path.join(HERE, "flawfinder_min.sarif")
B = os.path.join(HERE, "cppcheck_min.sarif")

# The fixture's planted overlap: two tools, same file:line, different rule
# names, both carrying a resolvable CWE. This is the exact case the README
# calls the newest piece.
EXPECT_URI = "src/parse.c"
EXPECT_LINE = 42
EXPECT_TOOLS = {"Cppcheck", "flawfinder"}

failures = []


def check(stage, ok, detail):
    mark = "ok  " if ok else "FAIL"
    print(f"  [{mark}] {stage}: {detail}")
    if not ok:
        failures.append(stage)


print("verify_dedup_render — cross-tool display path")
print()

# --- stage 1: ingest ---------------------------------------------------------
agg = audit.ingest_sarif([A, B])
agg["signal_assessment"] = audit.signal_informativeness(agg["ranked"])
tools = set(agg.get("tools", []))
check(
    "1 ingest",
    len(agg["ranked"]) == 4 and len(tools) == 2,
    f"{len(agg['ranked'])} findings from {len(tools)} tools {sorted(tools)}",
)

# --- stage 2: the overlap is present but NOT merged by scoring ----------------
# This is correct and deliberate: the ingest merge keys on ruleId, so different
# rule names at one location stay separate. Asserted so a future change to the
# merge key is caught here rather than silently altering the scoring model.
at_loc = [
    r for r in agg["ranked"]
    if r.get("uri") == EXPECT_URI and r.get("line") == EXPECT_LINE
]
check(
    "2 scoring",
    len(at_loc) == 2 and all(r.get("n_tools") == 1 for r in at_loc),
    f"{len(at_loc)} separate findings at {EXPECT_URI}:{EXPECT_LINE}, "
    f"n_tools={[r.get('n_tools') for r in at_loc]} (expected 2x n_tools=1)",
)

# --- stage 3: dedup pass groups them -----------------------------------------
agg, ngrouped = audit_dedup_display.annotate(agg)
grouped = [
    r for r in agg["ranked"]
    if r.get("uri") == EXPECT_URI and r.get("line") == EXPECT_LINE
    and r.get("display_group") is not None
]
merged_tools = set()
for r in grouped:
    merged_tools |= set(r.get("display_also_flagged_by") or [])
check(
    "3 dedup",
    ngrouped == 1 and len(grouped) == 2 and merged_tools == EXPECT_TOOLS,
    f"{ngrouped} display group(s), {len(grouped)} member(s), "
    f"also_flagged_by={sorted(merged_tools)}",
)

# --- stage 4: the renderer surfaces it ---------------------------------------
# The gap this script was written for. build() must show that two independent
# tools agree; a report that renders these as unrelated single-tool findings
# demonstrates the opposite of the tool's thesis.
html = audit_html_report.build(agg)
rendered = all(t in html for t in EXPECT_TOOLS) and (
    "also flagged by" in html.lower()
    or "display_also_flagged_by" in html
    or "cross-tool" in html.lower()
)
check(
    "4 render",
    rendered,
    "HTML names both tools on the grouped finding"
    if rendered
    else "HTML does not surface cross-tool agreement (this is the gap)",
)

# --- stage 5: ranking untouched ----------------------------------------------
# The architectural invariant: the display layer annotates, it never reorders
# or rescores. If this fails, the post-processor has started corrupting the
# scoring file, which is the exact thing it was split out to avoid.
ranks = [r.get("rank") for r in agg["ranked"]]
check(
    "5 invariant",
    ranks == sorted(ranks) and len(set(ranks)) == len(ranks),
    f"rank order intact: {ranks}",
)

print()
if failures:
    print(f"FAILED at: {', '.join(failures)}")
    sys.exit(1)
print("All stages passed — cross-tool agreement survives to rendered output.")
sys.exit(0)
