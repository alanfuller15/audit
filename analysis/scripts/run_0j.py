#!/usr/bin/env python3
"""0j: does the README's 1.5x survive a FINER size control than deciles?

Pre-registered in HANDOFF 0j / SESSION_HANDOFF_2026-07-26 §1:
  re-run the size-matched precision test at 10 / 50 / 200 strata.
  If the effect DECAYS as strata refine, the 1.5x does not survive.
  If it HOLDS at 200, suspect the logistic's linear-in-n_tools spec instead.

STUDY grounding (fetched this session):
  Brenner H, Blettner M. "Controlling for continuous confounders in
  epidemiologic research." Epidemiology 1997;8(4):429-34. PMID 9209859.
  "inclusion of the confounder as a single linear term often provides
   satisfactory control for confounding even in situations in which the model
   assumptions are clearly violated. In contrast, categorization of the
   confounder may often lead to serious residual confounding if the number of
   categories is small."
  => the continuous-covariate logistic is the REFERENCE; decile matching is
     the SUSPECT. Not the other way round.

Unit construction is copied verbatim from run_0i.py so the two are comparable.
Pure Python - no numpy/scipy on this machine, and per SESSION_HANDOFF §3b that
constraint must NOT be allowed to select the statistical method again.
"""
import json, os, math, random, statistics as st
from collections import defaultdict
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus  # noqa: E402  (path resolution only)

random.seed(31)
HERE = _corpus.corpus_root()
B = os.path.join(HERE, "lipp", "dataset")

# ---------------- unit construction (identical to run_0i.py) ----------------
U = []
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
    idx = {}
    for f in fnl:
        loc = max(1, f.get("LOC") or (f["line_range"][1] - f["line_range"][0] + 1))
        rec = {"loc": loc, "tools": set(), "vuln": (f["file"], f["name"]) in vf,
               "proj": p}
        idx[(f["file"], f["name"])] = rec
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
    for x in fi:
        for lo, hi, nm in byfile.get(x["file"], []):
            if lo <= x["line"] <= hi:
                idx[(x["file"], nm)]["tools"].update(x["found_by"]); break
    U += [r for r in idx.values() if r["tools"]]

for u in U:
    u["n"] = len(u["tools"])
    u["lg"] = math.log(u["loc"])
    u["multi"] = 1 if u["n"] > 1 else 0

MULTI = [u for u in U if u["multi"]]
SINGLE = [u for u in U if not u["multi"]]
pm = sum(u["vuln"] for u in MULTI) / len(MULTI)
ps = sum(u["vuln"] for u in SINGLE) / len(SINGLE)

print("=" * 78)
print("0j - DOES THE 1.5x SURVIVE A FINER SIZE CONTROL?")
print("=" * 78)
print(f"\nfunction-level units {len(U):,}   vulnerable {sum(u['vuln'] for u in U)} "
      f"({100*sum(u['vuln'] for u in U)/len(U):.2f}%)")
print(f"  MULTI-tool (n>1)  {len(MULTI):6,}   vulnerable {sum(u['vuln'] for u in MULTI):3}  "
      f"= {100*pm:.2f}%   mean LOC {st.mean([u['loc'] for u in MULTI]):7.1f}  "
      f"median {st.median([u['loc'] for u in MULTI]):5.0f}")
print(f"  SINGLE-tool (n=1) {len(SINGLE):6,}   vulnerable {sum(u['vuln'] for u in SINGLE):3}  "
      f"= {100*ps:.2f}%   mean LOC {st.mean([u['loc'] for u in SINGLE]):7.1f}  "
      f"median {st.median([u['loc'] for u in SINGLE]):5.0f}")
print(f"\n  UNCONTROLLED ratio = {pm/ps:.2f}x   "
      f"(README names this as 2.7x and attributes ~40% of it to size)")

# ---------------- stratified matching, K strata ----------------
def strata_assign(units, K):
    """Quantile strata on LOC over the POOLED unit set (multi + single)."""
    byloc = sorted(units, key=lambda u: u["loc"])
    n = len(byloc)
    return {id(u): min(K - 1, (i * K) // n) for i, u in enumerate(byloc)}


DEPTH = {}


def matched_test(K, draws=2000, label=None):
    sid = strata_assign(U, K)
    pools = defaultdict(list)
    for u in SINGLE:
        pools[sid[id(u)]].append(u)
    # how many multi units have ANY single-tool control in their stratum
    want = defaultdict(int)
    matchable = 0
    for u in MULTI:
        s = sid[id(u)]
        if pools[s]:
            want[s] += 1
            matchable += 1
    dropped = len(MULTI) - matchable
    # the multi rate must be recomputed over the MATCHABLE subset only,
    # otherwise the comparison is against a different numerator population
    mm = [u for u in MULTI if pools[sid[id(u)]]]
    pm_m = sum(u["vuln"] for u in mm) / len(mm) if mm else float("nan")

    rates, mlocs = [], []
    for _ in range(draws):
        pick = []
        for s, k in want.items():
            pool = pools[s]
            pick += (random.sample(pool, k) if k <= len(pool)
                     else [random.choice(pool) for _ in range(k)])
        rates.append(sum(u["vuln"] for u in pick) / len(pick))
        mlocs.append(st.mean([u["loc"] for u in pick]))
    m, sd = st.mean(rates), st.pstdev(rates)
    # NOTE: this p-value conditions on the multi group's own 81/5,269 as FIXED
    # and resamples only the controls. It therefore ignores sampling variability
    # in the numerator population. It is the statistic the original decile test
    # reported as "p<0.0001"; TEST 1b replaces it with a test that does not
    # make that assumption.
    pv = sum(1 for x in rates if x >= pm_m) / len(rates)

    # control-pool depletion: at fine K the same few singles get reused, which
    # shrinks effective n and can move the ratio for reasons unrelated to size
    avail = [len(pools[sid[id(u)]]) for u in mm]
    DEPTH[K] = (st.median(avail), sum(1 for a in avail if a < 5) / len(avail))

    # residual within-stratum size variation - the MECHANISM under test
    spreads = []
    for s in set(sid.values()):
        ls = sorted(u["loc"] for u in U if sid[id(u)] == s)
        if len(ls) > 1 and ls[0] > 0:
            spreads.append(ls[-1] / ls[0])
    med_spread = st.median(spreads) if spreads else float("nan")

    lbl = label or f"K={K}"
    print(f"  {lbl:<10}{100*pm_m:8.2f}%{100*m:12.2f}% +/-{100*sd:.2f}"
          f"{pm_m/m if m else float('nan'):9.2f}x{pv:11.4f}"
          f"{st.mean([u['loc'] for u in mm]):9.0f}{st.mean(mlocs):9.0f}"
          f"{med_spread:11.1f}x{dropped:8}")
    return pm_m / m if m else float("nan"), pv


print("\n" + "=" * 78)
print("TEST 1 - MATCHED PRECISION AS STRATA REFINE (2,000 draws each)")
print("=" * 78)
print(f"  {'strata':<10}{'multi':>8}{'matched single':>15}{'ratio':>11}"
      f"{'P(ctl>=multi)':>13}{'mLOC-m':>9}{'mLOC-c':>9}{'strat.spread':>13}{'dropped':>8}")
ratios = {}
for K in (10, 20, 50, 100, 200, 500, 1000):
    ratios[K] = matched_test(K)

# exact-LOC matching: the limit of refinement
print("\n  --- limiting case: EXACT LOC matching (stratum = one distinct LOC value) ---")
bloc = defaultdict(list)
for u in SINGLE:
    bloc[u["loc"]].append(u)
mm = [u for u in MULTI if bloc[u["loc"]]]
pm_e = sum(u["vuln"] for u in mm) / len(mm)
rates = []
for _ in range(2000):
    pick = [random.choice(bloc[u["loc"]]) for u in mm]
    rates.append(sum(x["vuln"] for x in pick) / len(pick))
me, sde = st.mean(rates), st.pstdev(rates)
pve = sum(1 for x in rates if x >= pm_e) / len(rates)
print(f"  {'exact':<10}{100*pm_e:8.2f}%{100*me:12.2f}% +/-{100*sde:.2f}"
      f"{pm_e/me if me else float('nan'):9.2f}x{pve:11.4f}"
      f"{st.mean([u['loc'] for u in mm]):9.0f}{st.mean([u['loc'] for u in mm]):9.0f}"
      f"{1.0:11.1f}x{len(MULTI)-len(mm):8}")


print("\n  control-pool depth (why the ratio RISES at very fine K):")
print(f"  {'strata':<10}{'median singles available per multi unit':>42}{'  % with <5':>12}")
for K in sorted(DEPTH):
    med, frac = DEPTH[K]
    print(f"  {'K='+str(K):<10}{med:>42.0f}{100*frac:>11.1f}%")


# ---------------- TEST 1b: a significance test that is not conditional ------
print("\n" + "=" * 78)
print("TEST 1b - IS 'p<0.0001' REAL? Two tests of the SAME matched contrast")
print("=" * 78)
print("""  The p-value above holds the multi group's 81/5,269 FIXED and resamples only
  the controls. Both groups are random samples, so that understates the
  uncertainty. Two honest alternatives:""")


def two_prop_z(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return float("nan"), float("nan")
    z = (p1 - p2) / se
    return z, 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


for K in (10, 50, 200):
    sid = strata_assign(U, K)
    pools = defaultdict(list)
    for u in SINGLE:
        pools[sid[id(u)]].append(u)
    mm = [u for u in MULTI if pools[sid[id(u)]]]
    xm = sum(u["vuln"] for u in mm)
    # (a) two-proportion z on one matched draw, averaged over draws
    zs, ps_ = [], []
    for _ in range(400):
        pick = []
        for u in mm:
            pick.append(random.choice(pools[sid[id(u)]]))
        z, pv = two_prop_z(xm, len(mm), sum(x["vuln"] for x in pick), len(pick))
        zs.append(z); ps_.append(pv)
    # (b) within-stratum label permutation: under H0 the multi/single label is
    #     exchangeable within a size stratum. This is the correct null and it
    #     varies BOTH groups.
    bys = defaultdict(list)
    for u in U:
        bys[sid[id(u)]].append(u)
    obs = pm - ps
    ge = 0
    PERM = 2000
    for _ in range(PERM):
        d_num_m = d_den_m = d_num_s = d_den_s = 0
        for s, grp in bys.items():
            nm_ = sum(u["multi"] for u in grp)
            if nm_ == 0 or nm_ == len(grp):
                continue
            lab = [1] * nm_ + [0] * (len(grp) - nm_)
            random.shuffle(lab)
            for u, L in zip(grp, lab):
                if L:
                    d_den_m += 1; d_num_m += u["vuln"]
                else:
                    d_den_s += 1; d_num_s += u["vuln"]
        if d_den_m and d_den_s and (d_num_m / d_den_m - d_num_s / d_den_s) >= obs:
            ge += 1
    print(f"\n  K={K}")
    print(f"    (a) two-proportion z, both groups random : z={st.mean(zs):+.2f}  "
          f"p={st.mean(ps_):.4f}")
    print(f"    (b) within-stratum label permutation     : "
          f"p={ge/PERM:.4f}  ({ge}/{PERM} permutations >= observed)")


# ---------------- logistic: the reference control ----------------
def solve(A, b):
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-12:
            return None
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def logistic(X, y, iters=30):
    k = len(X[0]); beta = [0.0] * k
    for _ in range(iters):
        H = [[0.0] * k for _ in range(k)]; g = [0.0] * k
        for xi, yi in zip(X, y):
            z = max(-30, min(30, sum(b * v for b, v in zip(beta, xi))))
            pr = 1 / (1 + math.exp(-z)); w = pr * (1 - pr)
            for a in range(k):
                g[a] += (yi - pr) * xi[a]
                for c in range(k):
                    H[a][c] += w * xi[a] * xi[c]
        step = solve(H, g)
        if step is None:
            break
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < 1e-9:
            break
    H = [[0.0] * k for _ in range(k)]
    for xi in X:
        z = max(-30, min(30, sum(b * v for b, v in zip(beta, xi))))
        pr = 1 / (1 + math.exp(-z)); w = pr * (1 - pr)
        for a in range(k):
            for c in range(k):
                H[a][c] += w * xi[a] * xi[c]
    se = []
    for i in range(k):
        e = [1.0 if j == i else 0.0 for j in range(k)]
        col = solve(H, e)
        se.append(math.sqrt(col[i]) if col and col[i] > 0 else float("nan"))
    return beta, se


def zp(b, s):
    if s != s or s == 0:
        return float("nan"), float("nan")
    z = b / s
    return z, 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def report(name, X, labels, y):
    beta, se = logistic(X, y)
    print(f"\n  {name}")
    for nm, b, s in zip(labels, beta, se):
        z, pv = zp(b, s)
        star = "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else ""
        orr = f"  OR={math.exp(b):6.2f}" if nm != "int" else ""
        print(f"    {nm:<14} b={b:+8.4f}  se={s:7.4f}  z={z:+6.2f}  p={pv:.3g} {star}{orr}")
    return beta


y = [u["vuln"] * 1 for u in U]
print("\n" + "=" * 78)
print("TEST 2 - THE SAME CONTRAST UNDER CONTINUOUS COVARIATE ADJUSTMENT")
print("        (Brenner & Blettner's recommended control; the REFERENCE)")
print("=" * 78)
report("multi alone (= the uncontrolled 2.7x)",
       [[1.0, u["multi"]] for u in U], ["int", "multi(n>1)"], y)
report("multi + log(LOC)   <-- DIRECT ANALOGUE OF THE MATCHED TEST",
       [[1.0, u["multi"], u["lg"]] for u in U], ["int", "multi(n>1)", "log(LOC)"], y)
report("multi + log(LOC) + log(LOC)^2",
       [[1.0, u["multi"], u["lg"], u["lg"]**2] for u in U],
       ["int", "multi(n>1)", "log(LOC)", "log(LOC)^2"], y)

print("\n" + "=" * 78)
print("TEST 3 - IS n_tools NON-LINEAR IN LOG-ODDS? (the fallback the handoff")
print("        says to check IF the matched effect had held at 200 strata)")
print("=" * 78)
lv = sorted({u["n"] for u in U})
print(f"  n_tools levels present: {lv}")
for k in lv:
    g = [u for u in U if u["n"] == k]
    print(f"    n_tools={k}: {len(g):6,} units, {sum(u['vuln'] for u in g):3} vulnerable "
          f"({100*sum(u['vuln'] for u in g)/len(g):5.2f}%), mean LOC {st.mean([u['loc'] for u in g]):7.1f}")
print("""
  n_tools=5 and n_tools=6 contain ZERO vulnerable units (31 and 4 units), which
  is perfect separation - the full 6-level factor has a singular Hessian and no
  standard errors exist. Levels are collapsed to 1 / 2 / 3 / >=4 so the model is
  estimable. Collapsing is forced by the data, not chosen to help the result.""")


def lvl(u):
    return min(u["n"], 4)


dm = [2, 3, 4]
report("n_tools as FACTOR (1 / 2 / 3 / >=4) + log(LOC), reference n_tools=1",
       [[1.0] + [1.0 if lvl(u) == k else 0.0 for k in dm] + [u["lg"]] for u in U],
       ["int"] + [(f"n_tools={k}" if k < 4 else "n_tools>=4") for k in dm]
       + ["log(LOC)"], y)
print("""
  READ THIS AGAINST 0i's LINEAR TERM. 0i fitted n_tools as a single linear
  slope and got b=+0.057, p=0.582. The factor model shows why that is the wrong
  specification: essentially all of the effect is the 1 -> 2 step, and the
  response is FLAT or falling above 2. A linear slope averages a real first step
  against a flat tail and returns ~0. The null 0i reported is an artifact of the
  functional form, not an absence of signal.""")

print("\n" + "=" * 78)
print("TEST 4 - WHY THE TWO METHODS CAN DISAGREE: residual size imbalance")
print("=" * 78)
for K in (10, 50, 200):
    sid = strata_assign(U, K)
    pools = defaultdict(list)
    for u in SINGLE:
        pools[sid[id(u)]].append(u)
    ml, cl = [], []
    for u in MULTI:
        if pools[sid[id(u)]]:
            ml.append(u["loc"])
            cl.append(st.mean([x["loc"] for x in pools[sid[id(u)]]]))
    print(f"  K={K:<5} mean LOC  multi {st.mean(ml):8.1f}   "
          f"stratum-mean of available controls {st.mean(cl):8.1f}   "
          f"imbalance {st.mean(ml)-st.mean(cl):+8.1f} LOC "
          f"({100*(st.mean(ml)/st.mean(cl)-1):+.1f}%)")
print("\n  (a positive imbalance means the matched control is SMALLER than the")
print("   multi-tool unit it is standing in for, so size favours multi and the")
print("   matched ratio is inflated by exactly that much.)")


# ---------------- TEST 5: is it one project? clustering ----------------
print("\n" + "=" * 78)
print("TEST 5 - CLUSTERING. 14,656 units come from 9 projects and vulnerable")
print("        functions cluster by project and by CVE. Unit-independence is an")
print("        assumption both tests above make, and p is already near 0.05.")
print("=" * 78)

K = 50
sid = strata_assign(U, K)
pools_all = defaultdict(list)
for u in SINGLE:
    pools_all[sid[id(u)]].append(u)

projs = sorted({u["proj"] for u in U})
print(f"\n  {'project':<12}{'units':>8}{'multi':>8}{'m.vuln':>8}{'m.rate':>9}"
      f"{'single':>8}{'s.vuln':>8}{'s.rate':>9}{'raw ratio':>11}")
for p in projs:
    g = [u for u in U if u["proj"] == p]
    gm = [u for u in g if u["multi"]]; gs = [u for u in g if not u["multi"]]
    rm = sum(u["vuln"] for u in gm) / len(gm) if gm else float("nan")
    rs = sum(u["vuln"] for u in gs) / len(gs) if gs else float("nan")
    rr = (rm / rs) if rs else float("inf")
    print(f"  {p:<12}{len(g):>8,}{len(gm):>8,}{sum(u['vuln'] for u in gm):>8}"
          f"{100*rm:>8.2f}%{len(gs):>8,}{sum(u['vuln'] for u in gs):>8}"
          f"{100*rs:>8.2f}%{rr:>10.2f}x")

print("\n  LEAVE-ONE-PROJECT-OUT, K=50 matched ratio (does one project carry it?):")
for p in [None] + projs:
    sub = [u for u in U if u["proj"] != p] if p else U
    subm = [u for u in sub if u["multi"]]
    pl = defaultdict(list)
    for u in sub:
        if not u["multi"]:
            pl[sid[id(u)]].append(u)
    mm = [u for u in subm if pl[sid[id(u)]]]
    if not mm:
        continue
    rm = sum(u["vuln"] for u in mm) / len(mm)
    rs = []
    for _ in range(400):
        pick = [random.choice(pl[sid[id(u)]]) for u in mm]
        rs.append(sum(x["vuln"] for x in pick) / len(pick))
    mrs = st.mean(rs)
    lbl = "ALL PROJECTS" if p is None else f"drop {p}"
    flag = ""
    if p is not None:
        pass
    print(f"    {lbl:<20} multi {100*rm:5.2f}%  matched single {100*mrs:5.2f}%  "
          f"ratio {rm/mrs if mrs else float('nan'):5.2f}x   (n_multi={len(mm):,})")

print("\n  CLUSTER PERMUTATION - permute the multi/single label within")
print("  (project x size stratum) cells, so the null respects project structure:")
bys = defaultdict(list)
for u in U:
    bys[(u["proj"], sid[id(u)])].append(u)
obs = pm - ps
ge = 0
PERM = 2000
for _ in range(PERM):
    nm_t = ns_t = vm_t = vs_t = 0
    for cell in bys.values():
        k = sum(u["multi"] for u in cell)
        if k == 0 or k == len(cell):
            # cell is pure: it contributes to whichever arm it is, unpermuted
            if k:
                nm_t += len(cell); vm_t += sum(u["vuln"] for u in cell)
            else:
                ns_t += len(cell); vs_t += sum(u["vuln"] for u in cell)
            continue
        lab = [1] * k + [0] * (len(cell) - k)
        random.shuffle(lab)
        for u, L in zip(cell, lab):
            if L:
                nm_t += 1; vm_t += u["vuln"]
            else:
                ns_t += 1; vs_t += u["vuln"]
    if nm_t and ns_t and (vm_t / nm_t - vs_t / ns_t) >= obs:
        ge += 1
print(f"    p = {ge/PERM:.4f}   ({ge}/{PERM} permutations >= observed diff of "
      f"{100*obs:.2f}pp)")

print("\n  CLUSTER BOOTSTRAP - resample the 9 PROJECTS with replacement,")
print("  recompute the K=50 matched ratio. This is the honest interval if the")
print("  project is the sampling unit rather than the function:")
boots = []
for _ in range(400):
    take = [random.choice(projs) for _ in projs]
    sub = []
    for p in take:
        sub += [u for u in U if u["proj"] == p]
    subm = [u for u in sub if u["multi"]]
    pl = defaultdict(list)
    for u in sub:
        if not u["multi"]:
            pl[sid[id(u)]].append(u)
    mm = [u for u in subm if pl[sid[id(u)]]]
    if not mm:
        continue
    rm = sum(u["vuln"] for u in mm) / len(mm)
    pick = [random.choice(pl[sid[id(u)]]) for u in mm]
    rs_ = sum(x["vuln"] for x in pick) / len(pick)
    if rs_:
        boots.append(rm / rs_)
boots.sort()
lo = boots[int(.025 * len(boots))]; hi = boots[int(.975 * len(boots))]
print(f"    matched ratio 95% CI over projects: [{lo:.2f}x, {hi:.2f}x]   "
      f"median {st.median(boots):.2f}x")
print(f"    fraction of project-bootstraps with ratio <= 1.0 (no effect): "
      f"{sum(1 for b in boots if b <= 1.0)/len(boots):.3f}")
