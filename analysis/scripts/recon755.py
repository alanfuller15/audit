#!/usr/bin/env python3
"""Reconstruct the recorded file-level result:
   2,559 files, 3.4% vulnerable, consensus ROC-AUC 0.755, PofB@20% 0.655,
   best single tool (CommSCA) 0.596, random 0.501.
Computed DIRECTLY from Lipp's found_by lists — no SARIF, no audit.py.
If this reproduces the numbers, the result never measured audit.py."""
import json, os, itertools

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lipp", "dataset")
FIVE = {"Cppcheck", "CodeChecker", "CodeQL", "Flawfinder", "CommSCA"}   # recorded set (no Infer)


def auc(scores, labels):
    """ROC-AUC via Mann-Whitney U, ties averaged."""
    pairs = sorted(zip(scores, labels))
    n = len(pairs)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    pos = sum(1 for _, l in pairs if l)
    neg = n - pos
    if not pos or not neg:
        return float("nan")
    rsum = sum(r for r, (_, l) in zip(ranks, pairs) if l)
    return (rsum - pos * (pos + 1) / 2.0) / (pos * neg)


def pofb(scores, labels, frac=0.20):
    """Proportion of Bugs found inspecting the top `frac` of files by score."""
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    k = int(round(frac * len(scores)))
    tot = sum(labels)
    return sum(labels[i] for i in order[:k]) / tot if tot else float("nan")


def load(universe_mode, tools):
    files, vuln, flags = set(), set(), {}
    for p in sorted(os.listdir(BASE)):
        d = os.path.join(BASE, p)
        if not os.path.isdir(d):
            continue
        fns = json.load(open(f"{d}/functions.json"))
        fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
        cve = json.load(open(f"{d}/cve_data.json"))
        find = json.load(open(f"{d}/sca_results.json"))["findings"]

        # vulnerable functions -> their files
        vfn = set()
        for c in cve.values():
            for f in c.get("functions", []):
                vfn.add((f["file"], f["name"]))
        for f, n in vfn:
            vuln.add((p, f))

        if universe_mode == "functions":
            for fn in fnl:
                files.add((p, fn["file"]))
        for x in find:
            key = (p, x["file"])
            if universe_mode == "findings":
                files.add(key)
            ts = {t for t in x["found_by"] if t in tools}
            if ts:
                flags.setdefault(key, set()).update(ts)
    return files, vuln, flags


print("reconstructing the recorded file-level result\n")
for mode in ("functions", "findings"):
    files, vuln, flags = load(mode, FIVE)
    if mode == "findings":
        files |= set()          # universe already = files with findings
    fl = sorted(files)
    labels = [1 if f in vuln else 0 for f in fl]
    scores = [len(flags.get(f, ())) for f in fl]
    rate = 100.0 * sum(labels) / len(fl) if fl else 0
    print(f"universe = files appearing in {mode}.json")
    print(f"  files={len(fl)}  vulnerable={sum(labels)} ({rate:.1f}%)")
    print(f"  consensus  ROC-AUC={auc(scores, labels):.3f}  PofB@20%={pofb(scores, labels):.3f}")
    for t in sorted(FIVE):
        s1 = [1 if t in flags.get(f, ()) else 0 for f in fl]
        print(f"    single {t:<12} ROC-AUC={auc(s1, labels):.3f}")
    print()
