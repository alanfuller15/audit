#!/usr/bin/env python3
"""
verify_dedup_render.py — the cross-tool DISPLAY path.

Runs the shipped chain against captured real fixtures. Companion to
verify_cross_tool_key.py, which guards the SCORING key; this one guards what
survives to the rendered report.

Usage, from the repo root:
    python3 examples/fixtures/verify_dedup_render.py

Exit 0 = no regressions. Stages marked PEND are known-unimplemented work
(HANDOFF §7 item 4, the badge) and do NOT fail the run — they are reported so
the gap stays visible without masking a real regression.

REWRITTEN 2026-07-26. The previous version asserted that the co-located
same-class overlap did NOT merge at scoring, and its fixtures were hand-authored
around a tool pair that does not exist (wrong flawfinder ruleId namespace, no
fingerprints, a CWE authored into a cppcheck message). Both are fixed: the
fixtures are now captured real output, and the two-algorithm key fix means that
overlap SHOULD merge. The display pass's remaining job is the residual cases
scoring deliberately declines — chiefly near-miss line offsets within TOL.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import audit                 # noqa: E402
import audit_dedup_display   # noqa: E402
import audit_html_report     # noqa: E402

A = os.path.join(HERE, "flawfinder_min.sarif")
B = os.path.join(HERE, "cppcheck_min.sarif")

# The captured fixtures' genuine overlap: flawfinder FF1001 and cppcheck
# CWE-788 both flag overlap.c:15, both class "buf". Different ruleIds, and the
# flawfinder side carries real fingerprints.
EXPECT_URI = "examples/fixtures/overlap.c"
EXPECT_LINE = 15
EXPECT_TOOLS = {"Cppcheck", "Flawfinder"}

failures, pending = [], []


def check(stage, ok, detail, pend=False):
    mark = "ok  " if ok else ("PEND" if pend else "FAIL")
    print(f"  [{mark}] {stage}: {detail}")
    if not ok:
        (pending if pend else failures).append(stage)


print("verify_dedup_render — cross-tool display path\n")

# --- stage 1: ingest ---------------------------------------------------------
agg = audit.ingest_sarif([A, B])
agg["signal_assessment"] = audit.signal_informativeness(agg["ranked"])
tools = set(agg.get("tools", []))
check("1 ingest", len(tools) == 2,
      f"{len(agg['ranked'])} findings from {len(tools)} tools {sorted(tools)}")

# --- stage 2: the overlap MERGES at scoring (the two-algorithm key fix) ------
# Pre-fix this was 2 separate findings with n_tools=1 each, because flawfinder
# emits fingerprints and cppcheck does not, so their keys could never collide.
at_loc = [r for r in agg["ranked"]
          if r.get("uri") == EXPECT_URI and r.get("line") == EXPECT_LINE]
merged_ok = (len(at_loc) == 1 and at_loc[0].get("n_tools") == 2
             and set(at_loc[0].get("tools") or []) == EXPECT_TOOLS)
check("2 scoring", merged_ok,
      f"{len(at_loc)} finding(s) at {EXPECT_URI}:{EXPECT_LINE}, "
      f"n_tools={[r.get('n_tools') for r in at_loc]}, "
      f"tools={sorted(at_loc[0].get('tools') or []) if at_loc else []}")

# --- stage 3: display pass covers the RESIDUAL case --------------------------
# Scoring requires an exact line match on purpose (a tolerance window makes
# merging order-dependent, and a false merge inflates n_tools). Near-miss
# offsets are the display layer's job, at TOL=3.
tmp = tempfile.mkdtemp()


def _mk(tool, rid, line, msg):
    p = os.path.join(tmp, f"{tool}.sarif")
    json.dump({"version": "2.1.0", "runs": [{
        "tool": {"driver": {"name": tool}},
        "results": [{"ruleId": rid, "level": "warning", "message": {"text": msg},
                     "locations": [{"physicalLocation": {
                         "artifactLocation": {"uri": "src/near.c"},
                         "region": {"startLine": line}}}]}]}]}, open(p, "w"))
    return p


near = audit.ingest_sarif([_mk("ToolA", "CWE-476", 42, "null deref"),
                           _mk("ToolB", "nullPointer", 44, "null pointer CWE-476")])
pre = max(r["n_tools"] for r in near["ranked"])
near, ngrouped = audit_dedup_display.annotate(near)
check("3 dedup", pre == 1 and ngrouped == 1,
      f"line-offset case: scoring left it separate (n_tools={pre}), "
      f"display grouped it ({ngrouped} group)")

# --- stage 4: the renderer surfaces it (KNOWN PENDING — item 4) --------------
agg2, _ = audit_dedup_display.annotate(json.loads(json.dumps(near)))
html = audit_html_report.build(agg2)
rendered = ("also flagged by" in html.lower() or "display_also_flagged_by" in html
            or "cross-tool" in html.lower())
check("4 render", rendered,
      "HTML surfaces cross-tool agreement" if rendered
      else "HTML does not surface display groups — HANDOFF §7 item 4, not yet built",
      pend=True)

# --- stage 5: ranking untouched by the display layer -------------------------
ranks = [r.get("rank") for r in near["ranked"]]
check("5 invariant", ranks == sorted(ranks) and len(set(ranks)) == len(ranks),
      f"rank order intact: {ranks}")

print()
if pending:
    print(f"PENDING (known, not a regression): {', '.join(pending)}")
if failures:
    print(f"FAILED at: {', '.join(failures)}")
    sys.exit(1)
print("No regressions.")
sys.exit(0)
