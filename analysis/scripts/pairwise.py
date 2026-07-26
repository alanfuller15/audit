#!/usr/bin/env python3
"""Pairwise cross-tool merge analysis: is the DEFAULT TOOL SET the defect?"""
import json, sys, os, itertools
sys.path.insert(0, "/Users/caitlinfuller/audit/src")
import audit
from audit import _cwe_class_of, _norm_uri
from collections import Counter

LIB = "/private/tmp/claude-501/-Users-caitlinfuller-audit/e15ca3d8-3ea0-4097-85ed-21cccfc71b0a/scratchpad/lib"
TOOLS = {"ff": f"{LIB}/zf.sarif", "cc": f"{LIB}/zc.sarif", "ql": f"{LIB}/zq.sarif"}
NAME = {"ff": "flawfinder", "cc": "cppcheck", "ql": "CodeQL"}

avail = {k: v for k, v in TOOLS.items() if os.path.exists(v)}
print("available:", ", ".join(NAME[k] for k in avail))

def profile(p):
    d = json.load(open(p))
    out = []
    for run in d.get("runs", []):
        for r in run.get("results", []):
            locs = r.get("locations") or []
            if not locs:
                continue
            pl = locs[0].get("physicalLocation", {})
            uri = _norm_uri((pl.get("artifactLocation") or {}).get("uri", ""))
            line = (pl.get("region") or {}).get("startLine")
            rid = r.get("ruleId", "")
            msg = ((r.get("message") or {}).get("text") or "")
            out.append((uri, line, rid, _cwe_class_of(rid, msg, uri)))
    return out

print("\n=== per-tool class profile ===")
prof = {}
for k, p in avail.items():
    prof[k] = profile(p)
    c = Counter(x[3] for x in prof[k])
    resolved = sum(v for kk, v in c.items() if kk)
    print(f"  {NAME[k]:<11} {len(prof[k]):>5} findings, {resolved:>4} class-resolved  "
          + str({kk: v for kk, v in sorted(c.items(), key=lambda z: -z[1]) if kk}))

print("\n=== pairwise + triple cross-tool merges (via real ingest) ===")
combos = []
for n in (2, 3):
    combos += list(itertools.combinations(sorted(avail), n))
for combo in combos:
    agg = audit.ingest_sarif([avail[k] for k in combo])
    merges = agg["cross_tool_merges"]
    dist = dict(sorted(Counter(f["n_tools"] for f in agg["ranked"]).items()))
    label = "+".join(NAME[k] for k in combo)
    print(f"  {label:<34} merges={merges:<4} n_tools={dist}")

print("\n=== why: co-location and class agreement per pair ===")
for a, b in itertools.combinations(sorted(avail), 2):
    A = {(x[0], x[1]): x[3] for x in prof[a] if x[1] is not None}
    B = {(x[0], x[1]): x[3] for x in prof[b] if x[1] is not None}
    co = set(A) & set(B)
    both = [k for k in co if A[k] and B[k]]
    match = [k for k in both if A[k] == B[k]]
    print(f"  {NAME[a]:>11} vs {NAME[b]:<11} files-in-common="
          f"{len({x[0] for x in A} & {x[0] for x in B}):<4} co-located={len(co):<5} "
          f"both-classed={len(both):<4} classes-MATCH={len(match)}")
    if match[:3]:
        for k in sorted(match)[:3]:
            print(f"        match: {k[0].split('/')[-1]}:{k[1]}  {A[k]}")
