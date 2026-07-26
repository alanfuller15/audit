#!/usr/bin/env python3
"""Does function-level agreement carry SIGNAL, or just more merges?
Lipp artifact: CVE ground truth + function boundaries, all on disk."""
import json, os, math, itertools
from collections import defaultdict, Counter

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lipp", "dataset")


def two_prop_z(x1, n1, x2, n2):
    if not n1 or not n2:
        return float("nan"), float("nan")
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return float("nan"), float("nan")
    z = (p1 - p2) / se
    return z, 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


line_units = []      # (n_tools, vulnerable, tools)
func_units = []      # (n_tools, vulnerable, tools, size)
file_units = defaultdict(lambda: [set(), False])

for p in sorted(os.listdir(B)):
    d = os.path.join(B, p)
    if not os.path.isdir(d):
        continue
    fi = json.load(open(f"{d}/sca_results.json"))["findings"]
    fns = json.load(open(f"{d}/functions.json"))
    fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
    cve = json.load(open(f"{d}/cve_data.json"))

    vuln_fn = set()
    for c in cve.values():
        for f in c.get("functions", []):
            vuln_fn.add((f["file"], f["name"]))

    byfile = defaultdict(list)
    for f in fnl:
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))

    def enclosing(fpath, line):
        for lo, hi, nm in byfile.get(fpath, []):
            if lo <= line <= hi:
                return nm, hi - lo
        return None, None

    # every function is a unit (flagged or not) — the honest denominator
    ftools = {(f["file"], f["name"]): set() for f in fnl}
    fsize = {(f["file"], f["name"]): f["line_range"][1] - f["line_range"][0] for f in fnl}

    for x in fi:
        nm, _ = enclosing(x["file"], x["line"])
        vul = (x["file"], nm) in vuln_fn if nm else False
        line_units.append((len(x["found_by"]), vul, tuple(sorted(x["found_by"]))))
        if nm:
            ftools[(x["file"], nm)].update(x["found_by"])
        fu = file_units[(p, x["file"])]
        fu[0].update(x["found_by"])
    for f in fnl:
        if (f["file"], f["name"]) in vuln_fn:
            file_units[(p, f["file"])][1] = True

    for k, v in ftools.items():
        if v:  # only FLAGGED functions are comparable to flagged lines
            func_units.append((len(v), k in vuln_fn, tuple(sorted(v)), fsize[k]))

print("=" * 72)
print("1-2. PRECISION AND ENRICHMENT BY GRANULARITY")
print("=" * 72)


def report(units, label, base_units):
    tot = len(units)
    vul = sum(1 for u in units if u[1])
    base = 100 * vul / tot
    multi = [u for u in units if u[0] > 1]
    single = [u for u in units if u[0] == 1]
    pm = 100 * sum(1 for u in multi if u[1]) / max(1, len(multi))
    ps = 100 * sum(1 for u in single if u[1]) / max(1, len(single))
    print(f"\n{label}")
    print(f"  flagged units            : {tot}   vulnerable {vul} ({base:.2f}%) <- base rate")
    print(f"  SINGLE-tool units        : {len(single):6}  precision {ps:5.2f}%")
    print(f"  MULTI-tool  units        : {len(multi):6}  precision {pm:5.2f}%"
          f"   enrichment {pm-base:+.2f}pp vs base, {pm-ps:+.2f}pp vs single")
    z, pv = two_prop_z(sum(1 for u in multi if u[1]), len(multi),
                       sum(1 for u in single if u[1]), len(single))
    print(f"  multi vs single          : z={z:.2f}  p={pv:.3g}  "
          f"{'SIGNIFICANT' if pv < 0.05 else 'not significant'}")
    return base


bl = report(line_units, "LINE LEVEL  (file, line, CWE)", None)
bf = report(func_units, "FUNCTION LEVEL  (flagged functions)", None)

fu = [(len(v[0]), v[1]) for v in file_units.values()]
tot = len(fu); vul = sum(1 for x in fu if x[1])
multi = [x for x in fu if x[0] > 1]; single = [x for x in fu if x[0] == 1]
print("\nFILE LEVEL  (flagged files)")
print(f"  flagged units            : {tot}   vulnerable {vul} ({100*vul/tot:.2f}%) <- base rate")
print(f"  SINGLE-tool units        : {len(single):6}  precision "
      f"{100*sum(1 for x in single if x[1])/max(1,len(single)):5.2f}%")
print(f"  MULTI-tool  units        : {len(multi):6}  precision "
      f"{100*sum(1 for x in multi if x[1])/max(1,len(multi)):5.2f}%")

print("\n" + "=" * 72)
print("3. n_tools MONOTONICITY")
print("=" * 72)
for label, units in [("LINE", line_units), ("FUNCTION", func_units)]:
    print(f"\n  {label} level:")
    by = defaultdict(lambda: [0, 0])
    for u in units:
        by[u[0]][0] += 1
        by[u[0]][1] += 1 if u[1] else 0
    for k in sorted(by):
        n, v = by[k]
        print(f"    {k} tool(s): {n:6} units, {v:5} vulnerable = {100*v/n:6.2f}%")
by = defaultdict(lambda: [0, 0])
for n_t, v in fu:
    by[n_t][0] += 1
    by[n_t][1] += 1 if v else 0
print("\n  FILE level (the granularity VALIDATION.md's 0.9%->11.6% was computed at):")
for k in sorted(by):
    n, v = by[k]
    print(f"    {k} tool(s): {n:6} units, {v:5} vulnerable = {100*v/n:6.2f}%")

print("\n" + "=" * 72)
print("4. FUNCTION-LEVEL CONSENSUS vs BEST SINGLE TOOL")
print("=" * 72)
tools = sorted({t for u in func_units for t in u[2]})
best = None
for t in tools:
    sel = [u for u in func_units if t in u[2]]
    x = sum(1 for u in sel if u[1])
    pr = 100 * x / max(1, len(sel))
    print(f"  {t:<14} flags {len(sel):6} functions, precision {pr:5.2f}%")
    if best is None or pr > best[1]:
        best = (t, pr, x, len(sel))
multi = [u for u in func_units if u[0] > 1]
mx = sum(1 for u in multi if u[1])
print(f"\n  CONSENSUS (>1 tool) flags {len(multi):6} functions, precision "
      f"{100*mx/len(multi):5.2f}%")
print(f"  best single tool: {best[0]} at {best[1]:.2f}%")
z, pv = two_prop_z(mx, len(multi), best[2], best[3])
print(f"  consensus - best single = {100*mx/len(multi)-best[1]:+.2f}pp   "
       f"z={z:.2f}  p={pv:.3g}  {'SIGNIFICANT' if pv < 0.05 else 'NOT significant'}")

print("\n" + "=" * 72)
print("5. FALSE-MERGE SIGNATURE: precision by ENCLOSING FUNCTION SIZE")
print("=" * 72)
buckets = [(0, 10), (11, 25), (26, 50), (51, 107), (108, 300), (301, 10**9)]
print(f"  {'size (lines)':<16}{'multi n':>9}{'multi prec':>12}"
      f"{'single n':>10}{'single prec':>13}{'gain':>9}")
for lo, hi in buckets:
    m = [u for u in func_units if u[0] > 1 and lo <= u[3] <= hi]
    s = [u for u in func_units if u[0] == 1 and lo <= u[3] <= hi]
    if not m or not s:
        continue
    pm = 100 * sum(1 for u in m if u[1]) / len(m)
    ps = 100 * sum(1 for u in s if u[1]) / len(s)
    rng = f"{lo}-{'inf' if hi > 10**8 else hi}"
    print(f"  {rng:<16}{len(m):>9}{pm:>11.2f}%{len(s):>10}{ps:>12.2f}%{pm-ps:>+8.2f}pp")
