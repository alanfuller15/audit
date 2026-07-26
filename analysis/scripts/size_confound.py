#!/usr/bin/env python3
"""Check 1: is the consensus IFA/PMI advantage a SIZE effect?
Check 2: confirm the function-level below-random result properly."""
import json, os, math, random, statistics as st
from collections import defaultdict
import importlib.util
spec = importlib.util.spec_from_file_location(
    "mu", os.path.join(os.path.dirname(os.path.abspath(__file__)), "manualup.py"))
random.seed(101)

# rebuild units (same construction as manualup.py)
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lipp", "dataset")
func, filu = {}, {}
for p in sorted(os.listdir(B)):
    d = os.path.join(B, p)
    if not os.path.isdir(d):
        continue
    fi = json.load(open(f"{d}/sca_results.json"))["findings"]
    fns = json.load(open(f"{d}/functions.json"))
    fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
    cve = json.load(open(f"{d}/cve_data.json"))
    vf = {(f["file"], f["name"]) for c in cve.values() for f in c.get("functions", [])}
    byfile = defaultdict(list)
    for f in fnl:
        loc = max(1, f.get("LOC") or (f["line_range"][1] - f["line_range"][0] + 1))
        func[(p, f["file"], f["name"])] = {"loc": loc, "tools": set(),
                                           "vuln": (f["file"], f["name"]) in vf}
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
        e = filu.setdefault((p, f["file"]), {"loc": 0, "tools": set(), "vuln": False})
        e["loc"] += loc
        if (f["file"], f["name"]) in vf:
            e["vuln"] = True
    for x in fi:
        if (p, x["file"]) in filu:
            filu[(p, x["file"])]["tools"].update(x["found_by"])
        for lo, hi, nm in byfile.get(x["file"], []):
            if lo <= x["line"] <= hi:
                func[(p, x["file"], nm)]["tools"].update(x["found_by"]); break

FILES = [u for u in filu.values() if u["tools"]]
FUNCS = [u for u in func.values() if u["tools"]]


def order_cons(units):
    return sorted(units, key=lambda u: (-len(u["tools"]), u["loc"]))


def within(units, order, frac=0.20):
    cap = frac * sum(u["loc"] for u in units); spent = 0; out = []
    for u in order:
        if spent + u["loc"] > cap:
            break
        spent += u["loc"]; out.append(u)
    return out


def pofb_of(units, sel):
    tv = sum(1 for u in units if u["vuln"])
    return sum(1 for u in sel if u["vuln"]) / tv if tv else float("nan")


def ifa_of(order):
    for i, u in enumerate(order):
        if u["vuln"]:
            return i
    return len(order)


def spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0]*len(v); i = 0
        while i < len(s):
            j = i
            while j+1 < len(s) and v[s[j+1]] == v[s[i]]:
                j += 1
            avg = (i+j)/2.0 + 1
            for k in range(i, j+1):
                r[s[k]] = avg
            i = j+1
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx)/len(rx), sum(ry)/len(ry)
    num = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a-mx)**2 for a in rx) * sum((b-my)**2 for b in ry))
    return num/den if den else float("nan")


print("=" * 78)
print("CHECK 1 — SIZE CONFOUND (file level)")
print("=" * 78)
od = order_cons(FILES)
sel = within(FILES, od)
allloc = [u["loc"] for u in FILES]
sloc = [u["loc"] for u in sel]
print(f"  corpus         n={len(FILES):5}  mean LOC {st.mean(allloc):8.1f}  median {st.median(allloc):7.0f}")
print(f"  consensus@20%  n={len(sel):5}  mean LOC {st.mean(sloc):8.1f}  median {st.median(sloc):7.0f}"
      f"   ratio {st.mean(sloc)/st.mean(allloc):.2f}x mean, {st.median(sloc)/max(1,st.median(allloc)):.2f}x median")
rho = spearman([i for i, _ in enumerate(od)], [u["loc"] for u in od])
print(f"  Spearman(consensus RANK, LOC) = {rho:+.3f}   "
      f"({'strongly' if abs(rho) > .5 else 'moderately' if abs(rho) > .3 else 'weakly'} size-correlated)")
rho2 = spearman([len(u["tools"]) for u in FILES], [u["loc"] for u in FILES])
print(f"  Spearman(n_tools, LOC)        = {rho2:+.3f}")

# SIZE-MATCHED random: draw the same number of files, matched by size decile
print("\n  SIZE-MATCHED random baseline (same size distribution as consensus@20%):")
byloc = sorted(FILES, key=lambda u: u["loc"])
decile = {id(u): min(9, (i * 10) // len(byloc)) for i, u in enumerate(byloc)}
pools = defaultdict(list)
for u in FILES:
    pools[decile[id(u)]].append(u)
want = defaultdict(int)
for u in sel:
    want[decile[id(u)]] += 1
pofbs, ifas = [], []
for _ in range(500):
    pick = []
    for dc, k in want.items():
        pick += random.sample(pools[dc], min(k, len(pools[dc])))
    pofbs.append(pofb_of(FILES, pick))
    order = pick + [u for u in FILES if u not in pick]
    ifas.append(ifa_of(order))
print(f"    PofB@20 : consensus {pofb_of(FILES, sel):.3f}   size-matched random "
      f"{st.mean(pofbs):.3f} +/- {st.pstdev(pofbs):.3f}")
print(f"    IFA     : consensus {ifa_of(od):5}     size-matched random "
      f"{st.mean(ifas):8.1f} +/- {st.pstdev(ifas):.1f}")
better = sum(1 for x in pofbs if x >= pofb_of(FILES, sel)) / len(pofbs)
print(f"    P(size-matched random >= consensus on PofB@20) = {better:.3f}")

print("\n" + "=" * 78)
print("CHECK 2 — FUNCTION LEVEL vs RANDOM (500 draws, variance reported)")
print("=" * 78)
for lbl, units in [("FUNCTION", FUNCS), ("FILE", FILES)]:
    cod = order_cons(units)
    cp = pofb_of(units, within(units, cod))
    rs = []
    for _ in range(500):
        r = units[:]; random.shuffle(r)
        rs.append(pofb_of(units, within(units, r)))
    m, sd = st.mean(rs), st.pstdev(rs)
    p_worse = sum(1 for x in rs if x >= cp) / len(rs)
    print(f"  {lbl:<9} consensus PofB@20 {cp:.3f}   random {m:.3f} +/- {sd:.3f}"
          f"   P(random >= consensus) = {p_worse:.3f}")
    print(f"            budget = 20% of {sum(u['loc'] for u in units):,} LOC, "
          f"identical tie-break (asc LOC), identical unit set")
