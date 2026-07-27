#!/usr/bin/env python3
"""Direction B: point-in-range matching. EVALUATE, do not implement.
Against the pre-registered decision rule in VALIDATION.md."""
import json, os, sys, csv
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", "..", "src"))  # was hard-coded
from audit import _cwe_class_of, _norm_uri, _CWE_CLASS, _CWE_DENY
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus  # noqa: E402  (path resolution only)

HERE = _corpus.corpus_root()
KEY = os.path.join(HERE, "owasp", "BenchmarkJava-master", "expectedresults-1.2.csv")
key = {}
for r in csv.DictReader(open(KEY)):
    key[r["# test name"].strip()] = (r[" category"].strip(), int(r[" cwe"]),
                                     r[" real vulnerability"].strip().lower() == "true")
CAT2CLS = {"sqli": "sqli", "cmdi": "cmdi", "xss": "xss", "pathtraver": "path",
           "ldapi": "ldapi", "xpathi": "xpathi", "crypto": "crypto",
           "hash": "hash", "weakrand": "random"}


def load(path):
    """-> list of (tool, uri, start, end, cls, ruleId)."""
    d = json.load(open(path))
    out = []
    for run in d.get("runs", []):
        tool = ((run.get("tool") or {}).get("driver") or {}).get("name", "?")
        taxa = {}
        rules = {}
        for rr in (run["tool"]["driver"].get("rules") or []):
            rid = rr.get("id")
            cw = []
            for rel in (rr.get("relationships") or []):
                t = rel.get("target") or {}
                if ((t.get("toolComponent") or {}).get("name") or "").upper() == "CWE":
                    import re as _re
                    m = _re.search(r"(\d+)", str(t.get("id") or ""))
                    if m:
                        cw.append(int(m.group(1)))
            if cw:
                taxa[rid] = cw
            rules[rid] = " ".join(str(x) for x in [
                rid, rr.get("name", ""),
                (rr.get("shortDescription") or {}).get("text", ""),
                (rr.get("fullDescription") or {}).get("text", ""),
                " ".join((rr.get("properties") or {}).get("tags") or [])])
        for r in run.get("results", []):
            rid = r.get("ruleId", "")
            loc = ((r.get("locations") or [{}])[0].get("physicalLocation") or {})
            uri = _norm_uri((loc.get("artifactLocation") or {}).get("uri", ""))
            reg = loc.get("region") or {}
            st = reg.get("startLine")
            if st is None:
                continue
            en = reg.get("endLine") or st
            # class: taxa first, then prose (mirrors ingest)
            cls = None
            for n in taxa.get(rid, []):
                if n in _CWE_DENY:
                    continue
                c = _CWE_CLASS.get(n)
                if c:
                    cls = c if cls in (None, c) else "AMBIG"
            if cls == "AMBIG":
                cls = None
            if not cls:
                cls = (_cwe_class_of(rid, (r.get("message") or {}).get("text", ""), uri)
                       or _cwe_class_of(rid, rules.get(rid, ""), ""))
            out.append((tool, uri, st, en, cls, rid))
    return out


def evaluate(paths, label, keyed):
    recs = []
    for p in paths:
        recs += load(p)
    bytool = defaultdict(list)
    for t, u, s, e, c, r in recs:
        if c:
            bytool[t].append((u, s, e, c, r))
    tools = sorted(bytool)
    print(f"=== {label} ===")
    print(f"  tools: {tools}")
    for t in tools:
        spans = [e - s for _, s, e, _, _ in bytool[t]]
        ranged = sum(1 for x in spans if x > 0)
        print(f"    {t:<14} {len(bytool[t]):5} class-resolved, {ranged:5} with a real range "
              f"({100*ranged/max(1,len(bytool[t])):.0f}%)")
    if len(tools) < 2:
        print("  <2 tools with classes — nothing to match")
        return
    A, B = bytool[tools[0]], bytool[tools[1]]
    exact, newpairs = set(), []
    bidx = defaultdict(list)
    for u, s, e, c, r in B:
        bidx[(u, c)].append((s, e, r))
    for u, s, e, c, r in A:
        for s2, e2, r2 in bidx.get((u, c), []):
            if s == s2:
                exact.add((u, c, s, s2))
                continue
            # point-in-range, either direction
            if (s2 <= s <= e2) or (s <= s2 <= e):
                span = (e2 - s2) if (s2 <= s <= e2) else (e - s)
                newpairs.append((u, c, s, s2, span, r, r2))
    print(f"  exact-line matches (current behaviour) : {len(exact)}")
    print(f"  NEW point-in-range matches             : {len(newpairs)}")
    if exact:
        print(f"    as a fraction of existing            : {100*len(newpairs)/len(exact):.1f}%")
    if not newpairs:
        print("  -> nothing added; criteria (b) and (c) moot\n")
        return
    spans = sorted(p[4] for p in newpairs)
    med = spans[len(spans) // 2]
    over100 = sum(1 for x in spans if x > 100)
    print(f"  span of PRODUCING ranges: median {med}  mean {sum(spans)/len(spans):.1f}  "
          f"max {spans[-1]}  >100 lines: {over100} ({100*over100/len(spans):.0f}%)")
    if keyed:
        ok = bad = nokey = 0
        for u, c, s, s2, span, r, r2 in newpairs:
            t = os.path.splitext(os.path.basename(u))[0]
            if t not in key:
                nokey += 1
                continue
            want = CAT2CLS.get(key[t][0])
            if want is None:
                nokey += 1
            elif want == c:
                ok += 1
            else:
                bad += 1
        tot = ok + bad
        print(f"  same-bug by answer key: class matches planted {ok}, differs {bad}, "
              f"unlabelled {nokey}" + (f"  -> {100*ok/tot:.0f}% same-bug" if tot else ""))
    else:
        print("  no answer key — enumerating all new matches:")
        for u, c, s, s2, span, r, r2 in newpairs[:40]:
            print(f"    {os.path.basename(u):<38} {s:>5} vs {s2:<5} span={span:<4} "
                  f"class={c:<9} {r[:26]} | {r2[:26]}")
    print()


evaluate([os.path.join(HERE, "owasp", "sb.sarif"),
          os.path.join(HERE, "owasp", "sg_java2.sarif")], "OWASP Benchmark", True)
evaluate([os.path.join(HERE, "struts", "sb.sarif"),
          os.path.join(HERE, "struts", "sg.sarif")], "Apache Struts", False)
