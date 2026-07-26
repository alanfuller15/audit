#!/usr/bin/env python3
"""semgrep-only class-resolution pass on OWASP Benchmark v1.2.
Tests whether the 15 Java classes added 2026-07-26 actually fire on real Java
scanner output, and whether resolution comes from result text or rule metadata."""
import json, os, sys, csv, re
from collections import Counter
sys.path.insert(0, "/Users/caitlinfuller/audit/src")
from audit import _cwe_class_of, _CWE_CLASS, _CWE_DENY

HERE = os.path.dirname(os.path.abspath(__file__))
SARIF = os.path.join(HERE, "owasp", "sg_java.sarif")
KEY = os.path.join(HERE, "owasp", "BenchmarkJava-master", "expectedresults-1.2.csv")

NEW_JAVA = {"sqli", "cmdi", "xss", "path", "deser", "xxe", "ssrf", "ldapi",
            "xpathi", "csrf", "redirect", "crypto", "hash", "creds", "random"}

# answer key: test name -> (category, cwe, is_real)
key = {}
for r in csv.DictReader(open(KEY)):
    key[r["# test name"].strip()] = (r[" category"].strip(), int(r[" cwe"]),
                                     r[" real vulnerability"].strip().lower() == "true")

doc = json.load(open(SARIF))
run = doc["runs"][0]
rules = {}
for rr in (run["tool"]["driver"].get("rules") or []):
    rules[rr.get("id")] = " ".join(str(x) for x in [
        rr.get("id", ""), rr.get("name", ""),
        (rr.get("shortDescription") or {}).get("text", ""),
        " ".join((rr.get("properties") or {}).get("tags") or [])])

res = run.get("results", [])
print(f"semgrep p/java on OWASP Benchmark: {len(res)} findings, {len(rules)} rules\n")

by_class = Counter()
via_text, via_meta, unresolved = 0, 0, 0
unres_rules = Counter()
per_case = {}          # test name -> set of classes semgrep resolved there
matched_cat = Counter()

for r in res:
    rid = r.get("ruleId", "")
    msg = (r.get("message") or {}).get("text", "")
    loc = r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    base = os.path.splitext(os.path.basename(loc))[0]

    c_text = _cwe_class_of(rid, msg, loc)
    c_meta = _cwe_class_of(rid, rules.get(rid, ""), "")
    cls = c_text or c_meta
    if c_text:
        via_text += 1
    elif c_meta:
        via_meta += 1
    else:
        unresolved += 1
        unres_rules[rid.rsplit(".", 1)[-1]] += 1
    if cls:
        by_class[cls] += 1
        if base in key:
            per_case.setdefault(base, set()).add(cls)

print("RESOLUTION")
print(f"  resolved to a class : {via_text + via_meta} / {len(res)} "
      f"({100*(via_text+via_meta)/len(res):.0f}%)")
print(f"    via RESULT TEXT   : {via_text}")
print(f"    via RULE METADATA : {via_meta}   <- the 2026-07-26 metadata fix")
print(f"  unresolved          : {unresolved}")
print()

print("CLASS DISTRIBUTION (semgrep-resolved)")
for c, n in by_class.most_common():
    tag = "NEW java class" if c in NEW_JAVA else "pre-existing (C/C++)"
    print(f"  {c:<10} {n:5}   {tag}")
print()

print("WHICH OF THE 15 NEW JAVA CLASSES FIRE")
fired = [c for c in sorted(NEW_JAVA) if by_class.get(c)]
silent = [c for c in sorted(NEW_JAVA) if not by_class.get(c)]
print(f"  fire   ({len(fired)}): {', '.join(fired) or '(none)'}")
print(f"  silent ({len(silent)}): {', '.join(silent) or '(none)'}")
print()

print("DOES semgrep's CLASS MATCH THE PLANTED CWE? (labelled test cases only)")
CAT2CLS = {"sqli": "sqli", "cmdi": "cmdi", "xss": "xss", "pathtraver": "path",
           "ldapi": "ldapi", "xpathi": "xpathi", "crypto": "crypto",
           "hash": "hash", "weakrand": "random", "trustbound": None,
           "securecookie": None}
agree = dis = nolabelcls = 0
disagreements = Counter()
for base, classes in per_case.items():
    cat, cwe, real = key[base]
    want = CAT2CLS.get(cat)
    if want is None:
        nolabelcls += 1
        continue
    if want in classes:
        agree += 1
    else:
        dis += 1
        disagreements[(cat, tuple(sorted(classes)))] += 1
print(f"  labelled cases with >=1 semgrep class : {len(per_case)}")
print(f"    class MATCHES the planted category  : {agree}")
print(f"    class DIFFERS from planted category : {dis}")
print(f"    category has no class in our map    : {nolabelcls}")
print()
print("  top mismatches (planted category -> classes semgrep resolved):")
for (cat, cls), n in disagreements.most_common(8):
    print(f"    {cat:<14} -> {', '.join(cls):<22} {n:5}")
print()
print("TOP UNRESOLVED semgrep RULES")
for rname, n in unres_rules.most_common(8):
    print(f"  {rname[:58]:<58} {n:5}")
