#!/usr/bin/env python3
"""Consensus vs the FIELD'S baselines: ManualUp (ascending size, effort-aware
baseline) and ManualDown (descending size, non-effort-aware baseline), per
Zhou et al. 2018 as described in arXiv:2302.00394.
Metrics: PofB@k, Popt, IFA, PMI@20%."""
import json, os, math, random
from collections import defaultdict

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lipp", "dataset")
random.seed(23)

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
        func[(p, f["file"], f["name"])] = {"loc": loc, "tools": set(), "n": 0,
                                           "vuln": (f["file"], f["name"]) in vf}
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
        e = filu.setdefault((p, f["file"]), {"loc": 0, "tools": set(), "n": 0, "vuln": False})
        e["loc"] += loc
        if (f["file"], f["name"]) in vf:
            e["vuln"] = True
    for x in fi:
        if (p, x["file"]) in filu:
            filu[(p, x["file"])]["tools"].update(x["found_by"]); filu[(p, x["file"])]["n"] += 1
        for lo, hi, nm in byfile.get(x["file"], []):
            if lo <= x["line"] <= hi:
                func[(p, x["file"], nm)]["tools"].update(x["found_by"])
                func[(p, x["file"], nm)]["n"] += 1
                break


def order_by(units, score, asc=False):
    """Deterministic ordering. Ties broken by ascending LOC (review cheap first)."""
    return sorted(units, key=lambda u: (score(u) if asc else -score(u), u["loc"]))


def pofb(units, order, frac):
    tot_loc = sum(u["loc"] for u in units); tot_v = sum(1 for u in units if u["vuln"])
    if not tot_v:
        return float("nan")
    cap = frac * tot_loc; spent = hit = 0
    for u in order:
        if spent + u["loc"] > cap:
            break
        spent += u["loc"]
        hit += u["vuln"]
    return hit / tot_v


def pmi(units, order, frac=0.20):
    tot_loc = sum(u["loc"] for u in units)
    cap = frac * tot_loc; spent = k = 0
    for u in order:
        if spent + u["loc"] > cap:
            break
        spent += u["loc"]; k += 1
    return k / len(units)


def ifa(order):
    """Initial False Alarms: clean modules inspected before the FIRST true positive."""
    for i, u in enumerate(order):
        if u["vuln"]:
            return i
    return len(order)


def area(units, order):
    tot_loc = sum(u["loc"] for u in units); tot_v = sum(1 for u in units if u["vuln"])
    if not tot_v or not tot_loc:
        return 0.0
    x = y = a = 0.0
    for u in order:
        dx = u["loc"] / tot_loc
        y2 = y + (u["vuln"] / tot_v)
        a += dx * (y + y2) / 2.0
        x += dx; y = y2
    return a


def popt(units, order):
    # optimal: all defective first, cheapest-first within each group
    opt = sorted(units, key=lambda u: (0 if u["vuln"] else 1, u["loc"]))
    # worst: all clean first, costliest-first
    wst = sorted(units, key=lambda u: (1 if u["vuln"] else 0, -u["loc"]))
    ao, am, aw = area(units, opt), area(units, order), area(units, wst)
    return 1 - (ao - am) / (ao - aw) if ao != aw else float("nan")


CONS = lambda u: len(u["tools"])
SIZE = lambda u: u["loc"]

for label, units in [("FUNCTION level", [u for u in func.values() if u["tools"]]),
                     ("FILE level", [u for u in filu.values() if u["tools"]])]:
    rankers = {
        "CONSENSUS (n_tools)": order_by(units, CONS),
        "ManualUp   (asc size)": order_by(units, SIZE, asc=True),
        "ManualDown (desc size)": order_by(units, SIZE),
        "random": random.sample(units, len(units)),
    }
    print("=" * 88)
    print(f"{label}: {len(units)} units, {sum(u['loc'] for u in units):,} LOC, "
          f"{sum(1 for u in units if u['vuln'])} vulnerable "
          f"({100*sum(1 for u in units if u['vuln'])/len(units):.2f}%)")
    print("=" * 88)
    print(f"  {'ranker':<24}{'PofB@5':>8}{'@10':>7}{'@20':>7}{'@50':>7}"
          f"{'Popt':>8}{'IFA':>7}{'PMI@20':>9}")
    for nm, od in rankers.items():
        print(f"  {nm:<24}{pofb(units,od,.05):>8.3f}{pofb(units,od,.10):>7.3f}"
              f"{pofb(units,od,.20):>7.3f}{pofb(units,od,.50):>7.3f}"
              f"{popt(units,od):>8.3f}{ifa(od):>7}{pmi(units,od):>9.3f}")

    def boot(s1, s2, metric, n=300):
        """metric(units, order) -> value; bootstrap P(delta <= 0)."""
        d0 = metric(units, order_by(units, s1[0], s1[1])) - metric(units, order_by(units, s2[0], s2[1]))
        le = 0
        for _ in range(n):
            samp = [random.choice(units) for _ in units]
            d = metric(samp, order_by(samp, s1[0], s1[1])) - metric(samp, order_by(samp, s2[0], s2[1]))
            if d <= 0:
                le += 1
        return d0, le / n

    print()
    for mname, m in [("PofB@20", lambda u, o: pofb(u, o, .20)),
                     ("Popt", popt),
                     ("PMI@20 (lower=better)", lambda u, o: -pmi(u, o))]:
        d, pv = boot((CONS, False), (SIZE, True), m)
        verdict = ("consensus BETTER, significant" if d > 0 and pv < 0.05
                   else "consensus better, n.s." if d > 0
                   else "consensus WORSE, significant" if pv > 0.95
                   else "consensus worse, n.s.")
        print(f"  consensus vs ManualUp on {mname:<24} delta {d:+.3f}  p={pv:.3f}  {verdict}")
    # IFA compared directly (lower is better, integer)
    print(f"  consensus vs ManualUp on IFA (lower=better)     "
          f"{ifa(rankers['CONSENSUS (n_tools)'])} vs {ifa(rankers['ManualUp   (asc size)'])}")
    print()
