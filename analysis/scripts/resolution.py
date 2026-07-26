#!/usr/bin/env python3
"""Per-tool class-resolution + fingerprint-degeneracy report on OWASP Benchmark.
Usage: resolution.py <tool.sarif> [label]
Deliberately per-tool: a merge rate is uninterpretable if one tool's resolution
is broken, so each tool gets a clean picture before any merge is computed."""
import json, os, sys, csv
from collections import Counter
sys.path.insert(0, "/Users/caitlinfuller/audit/src")
from audit import (_cwe_class_of, _fingerprint_value, _degenerate_fingerprints,
                   _norm_uri)

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "owasp", "BenchmarkJava-master", "expectedresults-1.2.csv")
NEW_JAVA = {"sqli", "cmdi", "xss", "path", "deser", "xxe", "ssrf", "ldapi",
            "xpathi", "csrf", "redirect", "crypto", "hash", "creds", "random"}
CAT2CLS = {"sqli": "sqli", "cmdi": "cmdi", "xss": "xss", "pathtraver": "path",
           "ldapi": "ldapi", "xpathi": "xpathi", "crypto": "crypto",
           "hash": "hash", "weakrand": "random", "trustbound": None,
           "securecookie": None}

sarif, label = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
key = {}
for r in csv.DictReader(open(KEY)):
    key[r["# test name"].strip()] = (r[" category"].strip(), int(r[" cwe"]),
                                     r[" real vulnerability"].strip().lower() == "true")

doc = json.load(open(sarif))
allres, rules_by_tool = [], {}
for run in doc.get("runs", []):
    tool = ((run.get("tool") or {}).get("driver") or {}).get("name", "?")
    rules_by_tool[tool] = {
        rr.get("id"): " ".join(str(x) for x in [
            rr.get("id", ""), rr.get("name", ""),
            (rr.get("shortDescription") or {}).get("text", ""),
            (rr.get("fullDescription") or {}).get("text", ""),
            " ".join((rr.get("properties") or {}).get("tags") or [])])
        for rr in (run["tool"]["driver"].get("rules") or [])}
    for r in run.get("results", []):
        allres.append((tool, r))

print(f"=== {label} ===")
print(f"driver(s): {', '.join(rules_by_tool)}   findings: {len(allres)}   "
      f"rules declared: {sum(len(v) for v in rules_by_tool.values())}\n")

# ---- fingerprint degeneracy, BOTH modes -----------------------------------
scan, withfp = [], 0
for tool, r in allres:
    fpv = _fingerprint_value(r)
    if fpv is not None:
        withfp += 1
    loc = ((r.get("locations") or [{}])[0].get("physicalLocation") or {})
    scan.append((tool, fpv,
                 _norm_uri((loc.get("artifactLocation") or {}).get("uri", "")),
                 (loc.get("region") or {}).get("startLine", 1)))
degen = _degenerate_fingerprints(scan)
vals = Counter(f for _, f, _, _ in scan if f is not None)
print("FINGERPRINTS")
print(f"  results carrying a fingerprint : {withfp} / {len(allres)}")
if withfp:
    print(f"  distinct fingerprint values    : {len(vals)}")
    top, topn = vals.most_common(1)[0]
    print(f"  most common value repeats      : {topn}x  {top[:60]}")
    print(f"  DEGENERATE (tool,fp) pairs     : {len(degen)}"
          f"   <- fall back to location key")
    if len(vals) == 1 and withfp > 1:
        print("  !! CONSTANT PLACEHOLDER mode — one value for every result")
    elif degen:
        print("  !! CONTEXT-COLLISION mode — a value repeats across locations")
    else:
        print("  clean: every fingerprint identifies one location")
else:
    print("  none emitted -> location key used throughout (no degeneracy risk)")
print()

# ---- class resolution ------------------------------------------------------
via_text = via_meta = unres = 0
by_class = Counter(); unres_rules = Counter(); per_case = {}
for tool, r in allres:
    rid = r.get("ruleId", "")
    msg = (r.get("message") or {}).get("text", "")
    loc = ((r.get("locations") or [{}])[0].get("physicalLocation") or {})
    uri = (loc.get("artifactLocation") or {}).get("uri", "")
    base = os.path.splitext(os.path.basename(uri))[0]
    ct = _cwe_class_of(rid, msg, uri)
    cm = _cwe_class_of(rid, rules_by_tool.get(tool, {}).get(rid, ""), "")
    cls = ct or cm
    if ct: via_text += 1
    elif cm: via_meta += 1
    else:
        unres += 1; unres_rules[rid] += 1
    if cls:
        by_class[cls] += 1
        if base in key:
            per_case.setdefault(base, set()).add(cls)

tot = len(allres)
print("RESOLUTION")
print(f"  resolved            : {via_text+via_meta} / {tot} "
      f"({100*(via_text+via_meta)/tot:.0f}%)" if tot else "  no findings")
print(f"    via RESULT TEXT   : {via_text}")
print(f"    via RULE METADATA : {via_meta}")
print(f"  unresolved          : {unres}")
print()
print("CLASS DISTRIBUTION")
for c, n in by_class.most_common():
    print(f"  {c:<10} {n:5}  {'NEW java class' if c in NEW_JAVA else 'pre-existing'}")
fired = sorted(c for c in NEW_JAVA if by_class.get(c))
print(f"\n  new classes firing ({len(fired)}/15): {', '.join(fired) or '(none)'}")
print(f"  silent: {', '.join(sorted(NEW_JAVA - set(fired)))}")
print()

print("AGAINST THE ANSWER KEY")
agree = dis = nocls = 0
mismatch = Counter()
for base, classes in per_case.items():
    cat, cwe, real = key[base]
    want = CAT2CLS.get(cat)
    if want is None: nocls += 1; continue
    if want in classes: agree += 1
    else:
        dis += 1; mismatch[(cat, tuple(sorted(classes)))] += 1
print(f"  labelled cases with a resolved class : {len(per_case)}")
print(f"    planted class PRESENT              : {agree}")
print(f"    planted class ABSENT (mismatch)    : {dis}")
print(f"    category has no class in our map   : {nocls}")
if mismatch:
    print("  mismatches (planted -> resolved):")
    for (cat, cls), n in mismatch.most_common(8):
        print(f"    {cat:<14} -> {', '.join(cls):<24} {n}")
multi = {b: c for b, c in per_case.items() if len(c) > 1}
print(f"  multi-class cases (merge-risk sites)  : {len(multi)}")
for combo, n in Counter(tuple(sorted(c)) for c in multi.values()).most_common(6):
    print(f"    {' + '.join(combo):<28} {n}")
if unres_rules:
    print("\nTOP UNRESOLVED RULES")
    for rn, n in unres_rules.most_common(6):
        print(f"  {str(rn)[:58]:<58} {n}")
