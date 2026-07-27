#!/usr/bin/env python3
"""Probe: does same-location/same-CWE cross-tool agreement merge at the SCORING
layer (audit.py ingest_sarif), as the spec's framing implicitly denies?

Cases:
  A same uri+line, both ruleId 'CWE-476', no fingerprints        -> merge? (user hypothesis)
  B same, but tool2 emits partialFingerprints                     -> merge?
  C same, but uri forms differ ('src/x.c' vs './src/x.c')         -> merge?
  D same, but line off by 1 (43 vs 42)                            -> merge?
"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "Users", "caitlinfuller", "audit", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", "..", "src"))  # was hard-coded
import audit

def sarif(tool, results):
    return {"version": "2.1.0", "runs": [{"tool": {"driver": {"name": tool}}, "results": results}]}

def res(rid, uri, line, msg="null pointer dereference", extra=None):
    r = {"ruleId": rid, "level": "error", "message": {"text": msg},
         "locations": [{"physicalLocation": {"artifactLocation": {"uri": uri},
                                             "region": {"startLine": line}}}]}
    if extra:
        r.update(extra)
    return r

CASES = {
    "A same rid/uri/line, no fingerprints": (
        res("CWE-476", "src/parse.c", 42),
        res("CWE-476", "src/parse.c", 42)),
    "B tool2 emits partialFingerprints": (
        res("CWE-476", "src/parse.c", 42),
        res("CWE-476", "src/parse.c", 42, extra={"partialFingerprints": {"primaryLocationLineHash": "abc123"}})),
    "C uri forms differ (src/ vs ./src/)": (
        res("CWE-476", "src/parse.c", 42),
        res("CWE-476", "./src/parse.c", 42)),
    "D line off by one (42 vs 43)": (
        res("CWE-476", "src/parse.c", 42),
        res("CWE-476", "src/parse.c", 43)),
}

tmp = tempfile.mkdtemp()
print(f"{'case':42} {'#findings':>10} {'n_tools':>18}")
print("-" * 74)
for name, (r1, r2) in CASES.items():
    p1 = os.path.join(tmp, "t1.sarif"); p2 = os.path.join(tmp, "t2.sarif")
    json.dump(sarif("Cppcheck", [r1]), open(p1, "w"))
    json.dump(sarif("flawfinder", [r2]), open(p2, "w"))
    out = audit.ingest_sarif([p1, p2])
    ranked = out.get("ranked", [])
    nt = [f.get("n_tools") for f in ranked]
    print(f"{name:42} {len(ranked):>10} {str(nt):>18}")
