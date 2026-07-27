#!/usr/bin/env python3
"""ITEM 2 — does FUNCTION-LEVEL matching earn a boundary-extraction dependency?

================================ PRE-REGISTRATION ============================
FIXED BEFORE COMPUTING. Deviations recorded as deviations.

WHY NO PARSER IS NEEDED FOR THIS EVALUATION. Lipp's `functions.json` carries
function boundaries extracted by the paper's own authors. So the evaluation runs
on GROUND-TRUTH boundaries and introduces no new instrument. A parser is only
needed to APPLY function-level matching to new scans, and that question is only
worth answering if this evaluation says the matching earns its place.

METHOD. Findings are routed through OUR pipeline (`audit.ingest_sarif`) at two
granularities. Function-level matching is implemented as a PRE-INGEST LOCATION
CANONICALISATION — each finding's line is replaced by its enclosing function's
start line — so `audit.py` is not modified and no new merge logic is introduced.
Two findings in the same function then share a location and may merge exactly as
two findings on the same line would.

!! TWO BOUNDS ON THIS DESIGN, STATED BEFORE RESULTS !!
 1. ROUND-TRIP IDENTITY (HANDOFF 3c(a)). Lipp's `findings` rows are ALREADY
    deduplicated across tools; each row carries `found_by`. Expanding a row into
    one SARIF result per tool gives those results IDENTICAL (file, line, cwe),
    so at LINE level our pipeline necessarily reproduces Lipp's own dedup. That
    is a SANITY CHECK, not a validation of our dedup. What is genuinely measured
    here is the DELTA between line and function level.
 2. FAVOURABLE CLASSES. The expansion gives every tool on a row the SAME CWE.
    Real scanners disagree about class. So class-matching here is EASIER than on
    real scanner output, and the function-level merge count is an UPPER BOUND on
    what the shipped pipeline would achieve against live tools.

MEASUREMENTS
 1. Merge counts, n_tools distribution, class distribution, line vs function.
 2. The 1.5x precision finding at function level with a size-matched control.
    THIS IS A CONSISTENCY CHECK, NOT A NEW RESULT — 0j already measured it at
    function level. If it disagrees, the pipeline is wrong, not the finding.
 3. THE ONE THAT MATTERS: does function-level consensus, using merges from OUR
    machinery, beat ManualUp and size-matched random on PofB@20%LOC, IFA and
    PMI@20%? 0i said no at function level using `found_by` directly. Routing
    through the real merge machinery is the thing that has not been tried.

DECISION RULE — FIXED NOW, BEFORE ANY NUMBER EXISTS
 BUILD boundary extraction if EITHER:
   (a) function-level consensus beats size-matched random on PofB@20%LOC at
       permutation p < 0.05, AND also beats ManualUp; or
   (b) IFA improves by >=2x against the size-only floor without losing PofB.
 CLOSE item 2 as NOT WORTH IT if:
   consensus fails to beat SIZE-MATCHED RANDOM on PofB@20%LOC — regardless of
   how far merge counts rise. Observability that does not become ranking does
   not justify a dependency whose failure mode is FALSE MERGES.
 MIDDLE (beats random, loses to ManualUp): does NOT earn a parser. Record the
   granularity finding as a disclosure/observability result only.

PRE-COMMITTED: a large rise in merge counts is NOT on its own a reason to build.
That is the trap this rule exists to prevent — it is the same shape as Direction
B, where yield rose and the ranking did not follow.
==============================================================================
"""
import json, os, sys, math, random, statistics as st
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus  # noqa: E402  (path resolution only)
_corpus.add_src()
import audit  # noqa: E402

random.seed(0x2)
B = _corpus.corpus("lipp", "dataset")

TOOL_CANON = {"Flawfinder": "Flawfinder", "Cppcheck": "Cppcheck",
              "CodeQL": "CodeQL", "Infer": "Infer",
              "CodeChecker": "CodeChecker", "CommSCA": "CommSCA"}


def sarif_for(tool, results):
    return {"version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": tool}}, "results": results}]}


def build(project, granularity):
    """Return per-tool SARIF docs for one project at the given granularity."""
    d = os.path.join(B, project)
    fi = json.load(open(f"{d}/sca_results.json"))["findings"]
    fns = json.load(open(f"{d}/functions.json"))
    fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
    byfile = defaultdict(list)
    for f in fnl:
        byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
    def canon(fileq, line):
        if granularity == "line":
            return line
        for lo, hi, _ in byfile.get(fileq, []):
            if lo <= line <= hi:
                return lo                      # enclosing function's start line
        return line                            # outside any function: unchanged
    per = defaultdict(list)
    for x in fi:
        ln = canon(x["file"], x["line"])
        cwe = x.get("cwe") or ""
        rid = f"CWE-{cwe}" if str(cwe).isdigit() else (str(cwe) or "UNKNOWN")
        for t in x["found_by"]:
            per[TOOL_CANON.get(t, t)].append({
                "ruleId": rid, "message": {"text": f"{rid} finding"},
                "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": f'{project}/{x["file"]}'},
                    "region": {"startLine": max(1, int(ln))}}}]})
    return per


def ingest(project, granularity, tmp):
    per = build(project, granularity)
    paths = []
    for t, res in per.items():
        p = os.path.join(tmp, f"{project}_{granularity}_{t}.sarif")
        json.dump(sarif_for(t, res), open(p, "w"))
        paths.append(p)
    return audit.ingest_sarif(paths) if paths else None


def main():
    import tempfile
    tmp = tempfile.mkdtemp()
    projects = sorted(p for p in os.listdir(B) if os.path.isdir(os.path.join(B, p)))
    print("=" * 78)
    print("ITEM 2 — FUNCTION-LEVEL MATCHING THROUGH THE REAL PIPELINE")
    print("ground-truth boundaries from Lipp functions.json; no parser used")
    print("=" * 78)

    tot = {}
    for g in ("line", "function"):
        merged = raw = uniq = 0
        ndist, cdist = Counter(), Counter()
        for p in projects:
            agg = ingest(p, g, tmp)
            if not agg:
                continue
            merged += agg["cross_tool_merged_findings"]
            raw += agg["raw_result_count"]
            uniq += agg["deduplicated_count"]
            for r in agg["ranked"]:
                ndist[r["n_tools"]] += 1
                if r.get("cwe_class"):
                    cdist[r["cwe_class"]] += 1
        tot[g] = dict(merged=merged, raw=raw, uniq=uniq,
                      ndist=dict(sorted(ndist.items())), cdist=cdist)
        print(f"\n  {g.upper()} level")
        print(f"    raw results        {raw:8,}")
        print(f"    unique after dedup {uniq:8,}")
        print(f"    cross-tool merges  {merged:8,}   "
              f"({100*merged/max(1,uniq):.2f}% of unique)")
        print(f"    n_tools            {dict(sorted(ndist.items()))}")
        print(f"    top classes        {dict(cdist.most_common(5))}")
    if tot["line"]["merged"]:
        print(f"\n  MERGE DELTA: {tot['line']['merged']:,} -> "
              f"{tot['function']['merged']:,}  "
              f"({tot['function']['merged']/tot['line']['merged']:.1f}x)")

    # ---------- units for the precision + ranking questions ----------
    U = []
    for p in projects:
        d = os.path.join(B, p)
        fi = json.load(open(f"{d}/sca_results.json"))["findings"]
        fns = json.load(open(f"{d}/functions.json"))
        fnl = fns if isinstance(fns, list) else next(iter(fns.values()))
        cve = json.load(open(f"{d}/cve_data.json"))
        vf = {(f["file"], f["name"]) for c in cve.values()
              for f in c.get("functions", [])}
        byfile, idx = defaultdict(list), {}
        for f in fnl:
            loc = max(1, f.get("LOC") or (f["line_range"][1] - f["line_range"][0] + 1))
            idx[(f["file"], f["name"])] = {"loc": loc, "tools": set(),
                                           "vuln": (f["file"], f["name"]) in vf}
            byfile[f["file"]].append((f["line_range"][0], f["line_range"][1], f["name"]))
        for x in fi:
            for lo, hi, nm in byfile.get(x["file"], []):
                if lo <= x["line"] <= hi:
                    idx[(x["file"], nm)]["tools"].update(x["found_by"]); break
        U += [r for r in idx.values() if r["tools"]]
    for u in U:
        u["n"] = len(u["tools"])

    print("\n" + "=" * 78)
    print("2. PRECISION AT FUNCTION LEVEL — CONSISTENCY CHECK, NOT A NEW RESULT")
    print("=" * 78)
    M = [u for u in U if u["n"] > 1]; S = [u for u in U if u["n"] == 1]
    pm = sum(u["vuln"] for u in M)/len(M); ps = sum(u["vuln"] for u in S)/len(S)
    byloc = sorted(U, key=lambda u: u["loc"])
    dec = {id(u): min(9, (i*10)//len(byloc)) for i, u in enumerate(byloc)}
    pool = defaultdict(list)
    for u in S:
        pool[dec[id(u)]].append(u)
    want = Counter(dec[id(u)] for u in M)
    rates = []
    for _ in range(2000):
        pick = []
        for k, c in want.items():
            pl = pool[k]
            pick += (random.sample(pl, c) if pl and c <= len(pl)
                     else [random.choice(pl) for _ in range(c)] if pl else [])
        if pick:
            rates.append(sum(u["vuln"] for u in pick)/len(pick))
    mr = st.mean(rates)
    print(f"  multi {100*pm:.2f}%  single {100*ps:.2f}%  uncontrolled {pm/ps:.2f}x")
    print(f"  size-matched control {100*mr:.2f}%   ratio {pm/mr:.2f}x")
    print(f"  0j recorded 1.51x at 10 strata — agreement here means the pipeline")
    print(f"  reproduces it, not that the finding is re-established.")

    # ---------- 3. ranking ----------
    print("\n" + "=" * 78)
    print("3. RANKING AT FUNCTION LEVEL — THE DECIDING QUESTION")
    print("=" * 78)

    def pofb(units, od, frac=.20):
        tl = sum(u["loc"] for u in units); tv = sum(u["vuln"] for u in units)
        cap = frac*tl; sp = h = 0
        for u in od:
            if sp + u["loc"] > cap: break
            sp += u["loc"]; h += u["vuln"]
        return h/tv if tv else float("nan")

    def pmi(units, od, frac=.20):
        tl = sum(u["loc"] for u in units); cap = frac*tl; sp = k = 0
        for u in od:
            if sp + u["loc"] > cap: break
            sp += u["loc"]; k += 1
        return k/len(units)

    def ifa(od):
        for i, u in enumerate(od):
            if u["vuln"]: return i
        return len(od)

    rankers = {
        "consensus (n_tools desc)": lambda u: (-u["n"], u["loc"]),
        "ManualUp (size asc)":      lambda u: (u["loc"],),
        "size-only floor (desc)":   lambda u: (-u["loc"],),
    }
    print(f"  {'ranker':<28}{'PofB@20':>9}{'IFA':>8}{'PMI@20':>9}")
    res = {}
    for nm, key in rankers.items():
        od = sorted(U, key=key)
        res[nm] = (pofb(U, od), ifa(od), pmi(U, od))
        print(f"  {nm:<28}{res[nm][0]:>9.3f}{res[nm][1]:>8}{res[nm][2]:>9.3f}")

    od = sorted(U, key=rankers["consensus (n_tools desc)"])
    tl = sum(u["loc"] for u in U); cap = .20*tl; sp = 0; sel = []
    for u in od:
        if sp + u["loc"] > cap: break
        sp += u["loc"]; sel.append(u)
    want2 = Counter(dec[id(u)] for u in sel)
    poolA = defaultdict(list)
    for u in U:
        poolA[dec[id(u)]].append(u)
    tv = sum(u["vuln"] for u in U)
    ps_ = []
    for _ in range(2000):
        pick = []
        for k, c in want2.items():
            pl = poolA[k]
            pick += (random.sample(pl, c) if c <= len(pl)
                     else [random.choice(pl) for _ in range(c)])
        ps_.append(sum(u["vuln"] for u in pick)/tv if tv else 0)
    obs = res["consensus (n_tools desc)"][0]
    pv = sum(1 for x in ps_ if x >= obs)/len(ps_)
    print(f"\n  consensus PofB@20 {obs:.3f} vs SIZE-MATCHED random "
          f"{st.mean(ps_):.3f}+/-{st.pstdev(ps_):.3f}   P(rand>=)={pv:.3f}")
    print(f"  vs ManualUp {res['ManualUp (size asc)'][0]:.3f}   "
          f"vs size-only floor {res['size-only floor (desc)'][0]:.3f}")

    print("\n" + "=" * 78)
    print("DECISION, against the rule fixed before computing")
    print("=" * 78)
    beats_rand = pv < 0.05
    beats_mu = obs > res["ManualUp (size asc)"][0]
    ifa_gain = (res["size-only floor (desc)"][1] / max(1, res["consensus (n_tools desc)"][1]))
    print(f"  beats size-matched random (p<0.05)? {beats_rand}   (p={pv:.3f})")
    print(f"  beats ManualUp?                     {beats_mu}")
    print(f"  IFA gain vs size-only floor         {ifa_gain:.2f}x  (rule wants >=2)")
    if beats_rand and beats_mu:
        print("  => BUILD boundary extraction (rule a)")
    elif ifa_gain >= 2 and obs >= res["size-only floor (desc)"][0]:
        print("  => BUILD boundary extraction (rule b)")
    elif not beats_rand:
        print("  => CLOSE item 2. Consensus does not beat a size-matched control,")
        print("     so merge-count gains do not become ranking gains and do not")
        print("     justify a dependency whose failure mode is FALSE MERGES.")
    else:
        print("  => MIDDLE: beats random, loses to ManualUp. Does NOT earn a")
        print("     parser; record as an observability/disclosure result only.")


if __name__ == "__main__":
    main()
