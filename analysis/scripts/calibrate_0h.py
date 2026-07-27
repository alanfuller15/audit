#!/usr/bin/env python3
"""0h CALIBRATION — derive the dispersion gate from MEASURED distributions.

The gate must not be a round number picked by taste. This measures, on real
corpora with a real size correlation, how many non-modal n_tools units a run
needs before a permutation test can detect even a STRONG size correlation.
Below that count the statistic cannot distinguish anything and must be
reported NOT APPLICABLE rather than as a coefficient.

Parent population: Lipp file-level units, which carry the measured
Spearman(n_tools, LOC) = +0.629. If the gate cannot detect a correlation that
strong, it certainly cannot detect a weaker one.

Conventions alpha=0.05 / power=0.80 are the field's standard; the THRESHOLD m*
is measured, not assumed.
"""
import json, os, math, random, statistics as st
from collections import defaultdict, Counter

random.seed(17)
import _corpus  # noqa: E402
OLD = _corpus.corpus_root()
B = os.path.join(OLD, "lipp", "dataset")


def spearman(xs, ys):
    """Tie-corrected Spearman (Pearson on midranks). Returns None if either
    variable has zero rank variance — the degenerate case the gate exists for."""
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sx = sum((a - mx) ** 2 for a in rx)
    sy = sum((b - my) ** 2 for b in ry)
    if sx <= 0 or sy <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(sx * sy)


def perm_p(xs, ys, reps=200):
    obs = spearman(xs, ys)
    if obs is None:
        return None
    ge = 0
    yy = list(ys)
    for _ in range(reps):
        random.shuffle(yy)
        r = spearman(xs, yy)
        if r is not None and abs(r) >= abs(obs):
            ge += 1
    return (ge + 1) / (reps + 1)


# ---- build Lipp FILE-level units (matches the recorded +0.629) ----
files = {}
for p in sorted(os.listdir(B)):
    d = os.path.join(B, p)
    if not os.path.isdir(d):
        continue
    fi = json.load(open(f"{d}/sca_results.json"))["findings"]
    fns = json.load(open(f"{d}/functions.json"))
    fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
    for f in fnl:
        loc = max(1, f.get("LOC") or (f["line_range"][1] - f["line_range"][0] + 1))
        e = files.setdefault((p, f["file"]), {"loc": 0, "tools": set()})
        e["loc"] += loc
    for x in fi:
        k = (p, x["file"])
        if k in files:
            files[k]["tools"].update(x["found_by"])

U = [(len(v["tools"]), v["loc"]) for v in files.values() if v["tools"]]
allrho = spearman([u[0] for u in U], [u[1] for u in U])
print(f"parent: {len(U):,} file units, Spearman(n_tools, LOC) = {allrho:+.3f}")
print(f"n_tools distribution: {dict(sorted(Counter(u[0] for u in U).items()))}\n")

MULTI = [u for u in U if u[0] > 1]
SINGLE = [u for u in U if u[0] == 1]

print("=" * 78)
print("CALIBRATION — power of a permutation test to detect this parent's")
print("correlation, as a function of NON-MODAL COUNT m (units with n_tools>1)")
print("=" * 78)
print(f"  {'m':>5}{'run size':>10}{'power(p<.05)':>14}{'median rho':>12}"
      f"{'median CI width':>17}{'gate':>10}")

RUNSIZE = 120          # a realistic per-run file count
TRIALS = 200
gate = None
rows = []
for m in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30):
    hits = 0
    rhos, widths = [], []
    for _ in range(TRIALS):
        sub = random.sample(MULTI, min(m, len(MULTI))) + \
              random.sample(SINGLE, min(RUNSIZE - m, len(SINGLE)))
        xs = [u[0] for u in sub]; ys = [u[1] for u in sub]
        r = spearman(xs, ys)
        if r is None:
            continue
        rhos.append(r)
        pv = perm_p(xs, ys, reps=120)
        if pv is not None and pv < 0.05:
            hits += 1
        # bootstrap CI (percentile), Ruscio 2008: bootstrap >= analytic on ordinal
        bs = []
        for _ in range(120):
            samp = [sub[random.randrange(len(sub))] for _ in range(len(sub))]
            rb = spearman([a for a, _ in samp], [b for _, b in samp])
            if rb is not None:
                bs.append(rb)
        if len(bs) > 20:
            bs.sort()
            widths.append(bs[int(.975 * len(bs)) - 1] - bs[int(.025 * len(bs))])
    power = hits / TRIALS
    mr = st.median(rhos) if rhos else float("nan")
    mw = st.median(widths) if widths else float("nan")
    mark = ""
    if gate is None and power >= 0.80:
        gate = m
        mark = "  <== m*"
    rows.append((m, power, mr, mw))
    print(f"  {m:>5}{RUNSIZE:>10}{power:>14.2f}{mr:>12.3f}{mw:>17.3f}{mark:>10}")

print(f"\n  m* = {gate}  (smallest non-modal count reaching 80% power against a")
print(f"  parent correlation of {allrho:+.3f} at a run size of {RUNSIZE})")

print("\n" + "=" * 78)
print("SENSITIVITY — does m* move with run size?")
print("=" * 78)
for rs in (40, 80, 120, 300):
    g = None
    for m in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30):
        if m >= rs:
            break
        hits = 0
        for _ in range(120):
            sub = random.sample(MULTI, min(m, len(MULTI))) + \
                  random.sample(SINGLE, min(rs - m, len(SINGLE)))
            xs = [u[0] for u in sub]; ys = [u[1] for u in sub]
            pv = perm_p(xs, ys, reps=100)
            if pv is not None and pv < 0.05:
                hits += 1
        if hits / 120 >= 0.80:
            g = m
            break
    print(f"  run size {rs:>4}: m* = {g}")

print("\n" + "=" * 78)
print("THE RUNS THIS PROJECT HAS ACTUALLY SEEN")
print("=" * 78)
print("""  zlib   (flawfinder+cppcheck+semgrep) : n_tools = {1: 601}   non-modal m = 0
  Struts (SpotBugs+semgrep)             : all n_tools = 1      non-modal m = 0
  Both are BELOW any m* above. Under the gate both correctly report
  NOT APPLICABLE instead of a coefficient — which is the whole point: with
  m=0 the rank variance of n_tools is exactly zero and Spearman is UNDEFINED
  (zero denominator), not merely unstable.""")
