#!/usr/bin/env python3
"""0i: the pre-registered evaluation. A, B, C, D at FUNCTION level.
Pure Python — no numpy/scipy on this machine, so IRLS logistic regression and
the linear algebra are implemented directly."""
import json, os, math, random, statistics as st
from collections import defaultdict

random.seed(31)
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lipp", "dataset")

# ---------- load function units ----------
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
        rec = {"loc": loc, "tools": set(), "vuln": (f["file"], f["name"]) in vf}
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
N = len(U)
print(f"FUNCTION-level units: {N}, vulnerable {sum(u['vuln'] for u in U)} "
      f"({100*sum(u['vuln'] for u in U)/N:.2f}%)\n")


# ---------- linear algebra ----------
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


def logistic(X, y, iters=25):
    """IRLS. X includes an intercept column. Returns (beta, se)."""
    k = len(X[0]); beta = [0.0] * k
    for _ in range(iters):
        H = [[0.0] * k for _ in range(k)]; g = [0.0] * k
        for xi, yi in zip(X, y):
            z = sum(b * v for b, v in zip(beta, xi))
            z = max(-30, min(30, z)); pr = 1 / (1 + math.exp(-z)); w = pr * (1 - pr)
            for a in range(k):
                g[a] += (yi - pr) * xi[a]
                for c in range(k):
                    H[a][c] += w * xi[a] * xi[c]
        step = solve(H, g)
        if step is None:
            break
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < 1e-8:
            break
    # standard errors from inverse Hessian
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


y = [1 if u["vuln"] else 0 for u in U]
print("=" * 78)
print("ADDITION 1 — REGRESSION DIAGNOSTICS")
print("=" * 78)
models = {
    "n_tools alone":            [[1.0, u["n"]] for u in U],
    "log(LOC) alone [FLOOR]":   [[1.0, u["lg"]] for u in U],
    "n_tools + log(LOC)":       [[1.0, u["n"], u["lg"]] for u in U],
    "n_tools + log + log^2":    [[1.0, u["n"], u["lg"], u["lg"]**2] for u in U],
}
names = {"n_tools alone": ["int", "n_tools"],
         "log(LOC) alone [FLOOR]": ["int", "log(LOC)"],
         "n_tools + log(LOC)": ["int", "n_tools", "log(LOC)"],
         "n_tools + log + log^2": ["int", "n_tools", "log(LOC)", "log(LOC)^2"]}
fits = {}
for m, X in models.items():
    beta, se = logistic(X, y)
    fits[m] = beta
    print(f"\n  {m}")
    for nm, b, s in zip(names[m], beta, se):
        z, pv = zp(b, s)
        star = "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else ""
        print(f"    {nm:<12} b={b:+8.4f}  se={s:7.4f}  z={z:+6.2f}  p={pv:.3g} {star}")

# VIF between n_tools and log(LOC)
xs = [u["n"] for u in U]; zs = [u["lg"] for u in U]
mx, mz = st.mean(xs), st.mean(zs)
r = (sum((a-mx)*(b-mz) for a, b in zip(xs, zs))
     / math.sqrt(sum((a-mx)**2 for a in xs) * sum((b-mz)**2 for b in zs)))
print(f"\n  Pearson(n_tools, log(LOC)) = {r:+.3f}   VIF = {1/(1-r*r):.2f}"
      f"   ({'tolerable' if 1/(1-r*r) < 5 else 'PROBLEM'})")

# ---------- ranking evaluation ----------
def score_A(u):
    b = fits["n_tools + log(LOC)"]
    return b[0] + b[1]*u["n"] + b[2]*u["lg"]


# B: residual of n_tools after regressing on log(LOC)  (OLS)
sxx = sum((z-mz)**2 for z in zs); sxy = sum((z-mz)*(x-mx) for z, x in zip(zs, xs))
sl = sxy/sxx; ic = mx - sl*mz
def score_B(u):
    return u["n"] - (ic + sl*u["lg"])
def score_C(u):
    return u["n"] / u["loc"]
def score_SIZE(u):
    b = fits["log(LOC) alone [FLOOR]"]
    return b[0] + b[1]*u["lg"]
def score_CONS(u):
    return u["n"]


def order(units, sc):
    return sorted(units, key=lambda u: (-sc(u), u["loc"]))


def pofb(units, od, frac=.20):
    tl = sum(u["loc"] for u in units); tv = sum(u["vuln"] for u in units)
    cap = frac*tl; sp = h = 0
    for u in od:
        if sp + u["loc"] > cap:
            break
        sp += u["loc"]; h += u["vuln"]
    return h/tv if tv else float("nan")


def pmi(units, od, frac=.20):
    tl = sum(u["loc"] for u in units); cap = frac*tl; sp = k = 0
    for u in od:
        if sp + u["loc"] > cap:
            break
        sp += u["loc"]; k += 1
    return k/len(units)


def ifa(od):
    for i, u in enumerate(od):
        if u["vuln"]:
            return i
    return len(od)


print("\n" + "=" * 78)
print("ADDITION 2 — RANKING EVALUATION (function level)")
print("=" * 78)
cands = [("A logistic n_tools+log(LOC)", score_A), ("B size-residualized", score_B),
         ("C density n_tools/LOC", score_C), ("SIZE-ONLY [FLOOR]", score_SIZE),
         ("raw consensus", score_CONS)]
print(f"  {'ranker':<30}{'PofB@20':>9}{'IFA':>8}{'PMI@20':>9}")
res = {}
for nm, sc in cands:
    od = order(U, sc)
    res[nm] = (pofb(U, od), ifa(od), pmi(U, od))
    print(f"  {nm:<30}{res[nm][0]:>9.3f}{res[nm][1]:>8}{res[nm][2]:>9.3f}")

# size-matched random: preserve each ranker's within-budget size profile
byloc = sorted(U, key=lambda u: u["loc"])
dec = {id(u): min(9, (i*10)//len(byloc)) for i, u in enumerate(byloc)}
pool = defaultdict(list)
for u in U:
    pool[dec[id(u)]].append(u)
print("\n  vs SIZE-MATCHED random (400 draws, matched on within-budget size deciles):")
for nm, sc in cands:
    od = order(U, sc)
    tl = sum(u["loc"] for u in U); cap = .20*tl; sp = 0; sel = []
    for u in od:
        if sp + u["loc"] > cap:
            break
        sp += u["loc"]; sel.append(u)
    want = defaultdict(int)
    for u in sel:
        want[dec[id(u)]] += 1
    tv = sum(u["vuln"] for u in U)
    ps, fs = [], []
    for _ in range(400):
        pick = []
        for dcl, k in want.items():
            pick += random.sample(pool[dcl], min(k, len(pool[dcl])))
        ps.append(sum(u["vuln"] for u in pick)/tv if tv else 0)
        # IFA within the selected set only (O(n)); the tail is irrelevant to it
        f = len(pick)
        for i, u in enumerate(pick):
            if u["vuln"]:
                f = i; break
        fs.append(f)
    m, sd = st.mean(ps), st.pstdev(ps)
    pv = sum(1 for x in ps if x >= res[nm][0])/len(ps)
    print(f"    {nm:<30} PofB {res[nm][0]:.3f} vs {m:.3f}+/-{sd:.3f}  "
          f"P(rand>=)={pv:.3f}  IFA {res[nm][1]} vs {st.mean(fs):.0f}"
          f"   {'BEATS' if pv < 0.05 else 'does NOT beat'}")
