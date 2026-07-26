#!/usr/bin/env python3
"""verify_cross_tool_key.py — regression harness for the _result_key
two-algorithm split (HANDOFF §7 item 2).

Guards the fix recorded in docs/SCOPE_shipped_consensus_defect.md: before it,
`_result_key` used a tool's own fingerprint as the CROSS-tool identity, so the
shipped flawfinder+cppcheck pair could never produce n_tools>1 on any input.

Runs with no scanners installed and no network — the SARIF fixtures beside this
file are CAPTURED real output (see regen_fixtures.sh).

    python3 examples/fixtures/verify_cross_tool_key.py
"""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import audit  # noqa: E402

FF = os.path.join(HERE, "flawfinder_min.sarif")
CC = os.path.join(HERE, "cppcheck_min.sarif")

_fail = []


def check(ok, label, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not ok:
        _fail.append(label)


def sarif(tool, results):
    return {"version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": tool}}, "results": results}]}


def res(rid, uri, line, msg="", fingerprint=None):
    r = {"ruleId": rid, "level": "warning", "message": {"text": msg},
         "locations": [{"physicalLocation": {
             "artifactLocation": {"uri": uri}, "region": {"startLine": line}}}]}
    if fingerprint:
        r["fingerprints"] = {"contextHash/v1": fingerprint}
    return r


def ingest(*docs):
    """Write docs to temp SARIF files and ingest, returning the aggregate."""
    tmp = tempfile.mkdtemp()
    paths = []
    for i, d in enumerate(docs):
        p = os.path.join(tmp, f"t{i}.sarif")
        json.dump(d, open(p, "w"))
        paths.append(p)
    return audit.ingest_sarif(paths)


print("verify_cross_tool_key — two-algorithm dedup key\n")

# ── 1. THE FIX: real captured output from the shipped tool pair now merges ──
agg = audit.ingest_sarif([FF, CC])
merged = [f for f in agg["ranked"] if f["n_tools"] > 1]
check(len(merged) == 1, "1 cross-tool merge on REAL captured fixtures",
      f"{len(merged)} merged; n_tools max={max(f['n_tools'] for f in agg['ranked'])}")
if merged:
    m = merged[0]
    check(sorted(m["tools"]) == ["Cppcheck", "Flawfinder"] and m["line"] == 15,
          "merged finding is the genuine overlap",
          f"{m['uri']}:{m['line']} tools={sorted(m['tools'])}")

# The two sides had DIFFERENT ruleIds and one carried fingerprints — the exact
# combination that was structurally unmergeable before the fix.
ff_raw = json.load(open(FF))["runs"][0]["results"]
check(all(r.get("fingerprints") for r in ff_raw),
      "fixture flawfinder side really does emit fingerprints",
      f"{sum(1 for r in ff_raw if r.get('fingerprints'))}/{len(ff_raw)}")

# ── 2. SAME-TOOL dedup must not regress ─────────────────────────────────────
dup = res("CWE-476", "src/a.c", 10, "null deref", fingerprint="samehash")
agg = ingest(sarif("ToolA", [dup, json.loads(json.dumps(dup))]))
check(agg["deduplicated_count"] == 1 and agg["ranked"][0]["n_tools"] == 1,
      "same-tool duplicate collapses, n_tools stays 1",
      f"{agg['deduplicated_count']} finding(s), n_tools={agg['ranked'][0]['n_tools']}")

# Same tool, same location, same class, DIFFERENT rules must NOT merge into
# self-agreement — that would let one tool inflate its own consensus.
agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null deref"),
                             res("CWE-825", "src/a.c", 10, "stale pointer")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 1,
      "same-tool findings never inflate n_tools",
      f"n_tools max={max(f['n_tools'] for f in agg['ranked'])}")

# ── 3. Fingerprints must no longer block CROSS-tool agreement ───────────────
agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null", fingerprint="aaa")]),
             sarif("ToolB", [res("nullDeref", "src/a.c", 10, "null deref CWE-476")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 2,
      "fingerprint on one side no longer blocks cross-tool merge")

# ── 4. Path normalization (the _norm_uri fix) ───────────────────────────────
for a, b, label in [("src/a.c", "./src/a.c", "./ prefix"),
                    ("src/a.c", "x/../src/a.c", "../ segment"),
                    ("src/a.c", "src//a.c", "double slash")]:
    agg = ingest(sarif("ToolA", [res("CWE-476", a, 10, "null")]),
                 sarif("ToolB", [res("CWE-476", b, 10, "null")]))
    check(max(f["n_tools"] for f in agg["ranked"]) == 2,
          f"path forms unify: {label}", f"{a} vs {b}")

# ── 5. CONSERVATISM: false merges are worse than missed ones ────────────────
agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null")]),
             sarif("ToolB", [res("CWE-120", "src/a.c", 10, "overflow")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 1,
      "different CWE classes at one location do NOT merge")

agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null")]),
             sarif("ToolB", [res("CWE-476", "src/a.c", 11, "null")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 1,
      "off-by-one lines do NOT merge at the scoring layer (TOL is display-only)")

for denied in ("CWE-398", "CWE-664", "CWE-758"):
    agg = ingest(sarif("ToolA", [res(denied, "src/a.c", 10, "generic")]),
                 sarif("ToolB", [res(denied + "x", "src/a.c", 10, "generic " + denied)]))
    check(max(f["n_tools"] for f in agg["ranked"]) == 1,
          f"junk-drawer {denied} does not merge")

# ── 6. Determinism and order-independence ───────────────────────────────────
a1 = audit.ingest_sarif([FF, CC])
a2 = audit.ingest_sarif([CC, FF])
strip = lambda a: [(r["score"], r["uri"], r["line"], r["ruleId"], r["n_tools"])
                   for r in a["ranked"]]
check(strip(a1) == strip(a2), "ranking is input-order independent")
check(strip(audit.ingest_sarif([FF, CC])) == strip(a1), "ranking is deterministic across runs")

print()
if _fail:
    print(f"FAILED ({len(_fail)}): " + "; ".join(_fail))
    sys.exit(1)
print("all checks passed")
