#!/usr/bin/env python3
"""EFFORT-AWARE comparison of granularities on the Lipp artifact.
Budget is LINES OF CODE reviewed, not units — comparing unit-normalised numbers
across granularities flatters the coarser one mechanically."""
import json, os, math, random
from collections import defaultdict
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus  # noqa: E402  (path resolution only)

B = _corpus.corpus("lipp", "dataset")
random.seed(11)

func = {}   # (proj,file,name) -> dict(loc, tools:set, vuln)
filu = {}   # (proj,file)      -> dict(loc, tools:set, vuln, nfind)

for p in sorted(os.listdir(B)):
    d = os.path.join(B, p)
    if not os.path.isdir(d):
        continue
    fi = json.load(open(f"{d}/sca_results.json"))["findings"]
    fns = json.load(open(f"{d}/functions.json"))
    fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
    cve = json.load(open(f"{d}/cve_data.json"))
    vuln_fn = {(f["file"], f["name"]) for c in cve.values() for f in c.get("functions", [])}

    byfile = defaultdict(list)
    for f in fnl:
        loc = f.get("LOC") or (f["line_range"][1] - f["line_range"][0] + 1)
        key = (p, f["file"], f["name"])
        func[key] = {"loc": max(1, loc), "tools": set(), "vuln": (f["file"], f["name"]) in vuln_fn,
                     "n": 0}
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
        fk = (p, f["file"])
        e = filu.setdefault(fk, {"loc": 0, "tools": set(), "vuln": False, "n": 0})
        e["loc"] += max(1, loc)
        if (f["file"], f["name"]) in vuln_fn:
            e["vuln"] = True

    for x in fi:
        fk = (p, x["file"])
        if fk in filu:
            filu[fk]["tools"].update(x["found_by"])
            filu[fk]["n"] += 1
        for lo, hi, nm in byfile.get(x["file"], []):
            if lo <= x["line"] <= hi:
                k = (p, x["file"], nm)
                func[k]["tools"].update(x["found_by"])
                func[k]["n"] += 1
                break


def pofb(units, score, budget=0.20, tiebreak="small"):
    """Proportion of vulnerable units found within a budget of `budget` of TOTAL LOC."""
    tot_loc = sum(u["loc"] for u in units)
    tot_v = sum(1 for u in units if u["vuln"])
    if not tot_v:
        return float("nan")
    if tiebreak == "small":
        order = sorted(units, key=lambda u: (-score(u), u["loc"]))
    else:
        order = sorted(units, key=lambda u: (-score(u), random.random()))
    seen = spent = 0
    cap = budget * tot_loc
    for u in order:
        if spent + u["loc"] > cap:
            break
        spent += u["loc"]
        if u["vuln"]:
            seen += 1
    return seen / tot_v


def auc(units, score):
    pairs = sorted(((score(u), u["vuln"]) for u in units), key=lambda z: z[0])
    n = len(pairs); ranks = [0.0] * n; i = 0
    while i < n:
        j = i
        while j + 1 < n and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    pos = sum(1 for _, v in pairs if v); neg = n - pos
    if not pos or not neg:
        return float("nan")
    rs = sum(r for r, (_, v) in zip(ranks, pairs) if v)
    return (rs - pos * (pos + 1) / 2.0) / (pos * neg)


def boot(units, s1, s2, n=400, budget=0.20):
    """Bootstrap p-value for PofB(s1) > PofB(s2)."""
    d0 = pofb(units, s1, budget) - pofb(units, s2, budget)
    wins = 0
    for _ in range(n):
        samp = [random.choice(units) for _ in units]
        if pofb(samp, s1, budget) - pofb(samp, s2, budget) <= 0:
            wins += 1
    return d0, wins / n


CONS = lambda u: len(u["tools"])
LOC = lambda u: u["loc"]
NFIND = lambda u: u["n"]

for label, units in [("FUNCTION level", [u for u in func.values() if u["tools"]]),
                     ("FILE level", [u for u in filu.values() if u["tools"]])]:
    tot_loc = sum(u["loc"] for u in units)
    tot_v = sum(1 for u in units if u["vuln"])
    print("=" * 74)
    print(f"{label}: {len(units)} flagged units, {tot_loc:,} LOC, {tot_v} vulnerable")
    print("=" * 74)
    print(f"  {'ranker':<28}{'PofB@20%LOC':>13}{'ROC-AUC*':>11}   (*not effort-aware)")
    for nm, sc in [("CONSENSUS (n_tools)", CONS), ("baseline: LOC alone", LOC),
                   ("baseline: finding count", NFIND)]:
        print(f"  {nm:<28}{pofb(units, sc):>12.3f}{auc(units, sc):>11.3f}")
    tools = sorted({t for u in units for t in u["tools"]})
    for t in tools:
        sc = (lambda tt: (lambda u: 1 if tt in u["tools"] else 0))(t)
        print(f"  {'single: ' + t:<28}{pofb(units, sc):>12.3f}{auc(units, sc):>11.3f}")
    print()
    for nm, sc in [("LOC alone", LOC), ("finding count", NFIND)]:
        d, pv = boot(units, CONS, sc)
        print(f"  consensus vs {nm:<16} PofB delta {d:+.3f}   bootstrap p={pv:.3f}"
              f"   {'SIGNIFICANT' if pv < 0.05 else 'not significant'}")
    best = max(tools, key=lambda t: pofb(units, lambda u: 1 if t in u["tools"] else 0))
    scb = (lambda tt: (lambda u: 1 if tt in u["tools"] else 0))(best)
    d, pv = boot(units, CONS, scb)
    print(f"  consensus vs best single ({best}): PofB delta {d:+.3f}  p={pv:.3f}"
          f"   {'SIGNIFICANT' if pv < 0.05 else 'not significant'}")
    print()
