#!/usr/bin/env python3
"""Does consensus beat the BEST SINGLE TOOL on OWASP Benchmark v1.2?
Base rate is the coin flip; the single-tool comparator is the real bar."""
import json, os, sys, csv, math
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", "..", "src"))  # was hard-coded
import audit
from audit import _norm_uri
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus  # noqa: E402  (path resolution only)

HERE = _corpus.corpus_root()
SB = os.path.join(HERE, "owasp", "sb.sarif")
SG = os.path.join(HERE, "owasp", "sg_java2.sarif")
KEY = os.path.join(HERE, "owasp", "BenchmarkJava-master", "expectedresults-1.2.csv")

key = {}
for r in csv.DictReader(open(KEY)):
    key[r["# test name"].strip()] = r[" real vulnerability"].strip().lower() == "true"
BASE = sum(1 for v in key.values() if v) / len(key)


def name(uri):
    b = os.path.splitext(os.path.basename(uri))[0]
    return b if b in key else None


def two_prop_z(x1, n1, x2, n2):
    """Two-proportion z-test, two-sided. Returns (z, p)."""
    if not n1 or not n2:
        return float("nan"), float("nan")
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return float("nan"), float("nan")
    z = (p1 - p2) / se
    pval = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return z, pval


# ---- per-tool findings, with and without the class-resolution filter ------
def tool_stats(path):
    """Return (all_findings, class_resolved_findings) as lists of (testname, vuln)."""
    agg = audit.ingest_sarif([path])
    allf, resf = [], []
    for f in agg["ranked"]:
        t = name(f["uri"])
        if t is None:
            continue
        rec = (t, key[t])
        allf.append(rec)
        if f.get("cwe_class"):
            resf.append(rec)
    return allf, resf


sb_all, sb_res = tool_stats(SB)
sg_all, sg_res = tool_stats(SG)

agg = audit.ingest_sarif([SB, SG])
merges = [f for f in agg["ranked"] if f["n_tools"] > 1]
mg = [(name(f["uri"]), key[name(f["uri"])]) for f in merges if name(f["uri"])]


def prec(rows):
    n = len(rows)
    x = sum(1 for _, v in rows if v)
    return x, n, (x / n if n else float("nan"))


print("=== PER-FINDING PRECISION (fraction landing on vulnerable-labelled files) ===")
print(f"  benchmark base rate: {100*BASE:.1f}%\n")
rows = [("SpotBugs+FSB  ALL findings", sb_all),
        ("semgrep       ALL findings", sg_all),
        ("SpotBugs+FSB  class-resolved", sb_res),
        ("semgrep       class-resolved", sg_res),
        ("CONSENSUS     merges", mg)]
res = {}
for lbl, r in rows:
    x, n, p = prec(r)
    res[lbl.strip()] = (x, n, p)
    print(f"  {lbl:<30} {x:6}/{n:<6} = {100*p:5.1f}%   ({100*(p-BASE):+5.1f}pp vs base)")

print("\n=== THE COMPARISON THAT MATTERS: consensus vs BEST SINGLE TOOL ===")
mx, mn, mp = prec(mg)
cands = {"SpotBugs+FSB (class-resolved)": prec(sb_res),
         "semgrep (class-resolved)": prec(sg_res)}
best_lbl = max(cands, key=lambda k: cands[k][2])
bx, bn, bp = cands[best_lbl]
print(f"  best single tool : {best_lbl} = {100*bp:.1f}%  (n={bn})")
print(f"  consensus        : {100*mp:.1f}%  (n={mn})")
print(f"  difference       : {100*(mp-bp):+.1f}pp")
z, pv = two_prop_z(mx, mn, bx, bn)
print(f"  two-proportion z = {z:.2f},  p = {pv:.3g}")
print(f"  -> {'SIGNIFICANT at 0.05' if pv < 0.05 else 'NOT significant at 0.05'}")

print("\n  (also vs the other tool)")
for lbl, (x, n, p) in cands.items():
    if lbl == best_lbl:
        continue
    z2, pv2 = two_prop_z(mx, mn, x, n)
    print(f"  vs {lbl:<32} {100*(mp-p):+.1f}pp   z={z2:.2f} p={pv2:.3g}")

# ---- file-level view (matches Lipp's ROC-AUC framing) --------------------
print("\n=== FILE-LEVEL (each file counted once; matches Lipp's framing) ===")
def files_of(rows):
    return {t for t, _ in rows}
for lbl, r in [("SpotBugs+FSB class-resolved", sb_res),
               ("semgrep class-resolved", sg_res),
               ("CONSENSUS merges", mg)]:
    fs = files_of(r)
    x = sum(1 for t in fs if key[t])
    print(f"  {lbl:<30} {x:5}/{len(fs):<5} = {100*x/len(fs):5.1f}%   ({100*(x/len(fs)-BASE):+5.1f}pp)")
fsb, fsg, fmg = files_of(sb_res), files_of(sg_res), files_of(mg)
bestf = max([("SpotBugs+FSB", fsb), ("semgrep", fsg)],
            key=lambda kv: sum(1 for t in kv[1] if key[t]) / max(1, len(kv[1])))
bx2 = sum(1 for t in bestf[1] if key[t]); bn2 = len(bestf[1])
mx2 = sum(1 for t in fmg if key[t]); mn2 = len(fmg)
z3, pv3 = two_prop_z(mx2, mn2, bx2, bn2)
print(f"\n  best single (file-level): {bestf[0]} = {100*bx2/bn2:.1f}%")
print(f"  consensus  (file-level): {100*mx2/mn2:.1f}%   diff {100*(mx2/mn2-bx2/bn2):+.1f}pp")
print(f"  z = {z3:.2f}, p = {pv3:.3g} -> {'SIGNIFICANT' if pv3 < 0.05 else 'NOT significant'} at 0.05")
