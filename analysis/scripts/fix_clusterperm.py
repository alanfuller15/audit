"""Corrected cluster permutation: the statistic must be computed over the
INFORMATIVE (mixed) cells only, for both the observed value and every
permutation. Pure cells carry no information about the multi-vs-single
contrast; letting them contribute a fixed offset narrows the null and makes
the p-value anti-conservative."""
import json, os, math, random, statistics as st
from collections import defaultdict
random.seed(31)
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lipp", "dataset")
U = []
for p in sorted(os.listdir(B)):
    d = os.path.join(B, p)
    if not os.path.isdir(d): continue
    fi = json.load(open(f"{d}/sca_results.json"))["findings"]
    fns = json.load(open(f"{d}/functions.json"))
    fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
    cve = json.load(open(f"{d}/cve_data.json"))
    vf = {(f["file"], f["name"]) for c in cve.values() for f in c.get("functions", [])}
    byfile = defaultdict(list); idx = {}
    for f in fnl:
        loc = max(1, f.get("LOC") or (f["line_range"][1]-f["line_range"][0]+1))
        idx[(f["file"], f["name"])] = {"loc": loc, "tools": set(),
            "vuln": (f["file"], f["name"]) in vf, "proj": p}
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
    for x in fi:
        for lo, hi, nm in byfile.get(x["file"], []):
            if lo <= x["line"] <= hi:
                idx[(x["file"], nm)]["tools"].update(x["found_by"]); break
    U += [r for r in idx.values() if r["tools"]]
for u in U:
    u["multi"] = 1 if len(u["tools"]) > 1 else 0

def strata(units, K):
    b = sorted(units, key=lambda u: u["loc"])
    return {id(u): min(K-1, (i*K)//len(b)) for i, u in enumerate(b)}

for K in (10, 50, 200):
    sid = strata(U, K)
    cells = defaultdict(list)
    for u in U:
        cells[(u["proj"], sid[id(u)])].append(u)
    mixed = [c for c in cells.values()
             if 0 < sum(u["multi"] for u in c) < len(c)]
    nu = sum(len(c) for c in mixed)
    def diff(assign):
        vm = nm = vs = ns = 0
        for c, lab in zip(mixed, assign):
            for u, L in zip(c, lab):
                if L: nm += 1; vm += u["vuln"]
                else: ns += 1; vs += u["vuln"]
        return (vm/nm - vs/ns) if nm and ns else float("nan")
    obs = diff([[u["multi"] for u in c] for c in mixed])
    ge = 0; PERM = 4000
    for _ in range(PERM):
        a = []
        for c in mixed:
            k = sum(u["multi"] for u in c)
            lab = [1]*k + [0]*(len(c)-k)
            random.shuffle(lab); a.append(lab)
        if diff(a) >= obs: ge += 1
    print(f"K={K:<5} informative cells {len(mixed):4} covering {nu:6,}/{len(U):,} units "
          f"({100*nu/len(U):.1f}%)   observed diff {100*obs:+.2f}pp   "
          f"p = {ge/PERM:.4f}  ({ge}/{PERM})")
