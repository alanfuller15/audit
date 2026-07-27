#!/usr/bin/env python3
"""CORPUS ARM of the pre-registered rule-provenance measurement.
docs/SPEC_rule_provenance_measurement.md, RQ1 and RQ2 (declaration rate and
agreement attribution) on corpora already on disk. NO network. NO registry arm.

INSTRUMENT NOTE — this reads NATIVE semgrep JSON, not SARIF. SARIF DROPS
`source-rule-url`: verified 0 occurrences in owasp/sg_java2.sarif versus its
presence in owasp/sg_native.json. A SARIF-based version of this measurement
would return a guaranteed false zero.

EVERY derived fraction here is a LOWER BOUND. Nothing requires a tool to
declare that a rule was ported. A low number is consistent with genuine
independence OR with undeclared porting, and the measurement cannot tell them
apart. Pre-registered: a low number is UNINFORMATIVE, not clearance.
"""
import json, os, re, sys
from collections import defaultdict, Counter

import _corpus  # noqa: E402
OLD = _corpus.corpus_root()

# provenance-bearing metadata fields, in priority order
PROV_FIELDS = ["source-rule-url"]

# map a provenance URL to the upstream TOOL it names
UPSTREAM = [
    (r"find-sec-bugs\.github\.io", "FindSecBugs"),
    (r"spotbugs\.readthedocs|spotbugs\.github", "SpotBugs"),
    (r"pmd\.github\.io|pmd\.sourceforge", "PMD"),
    (r"checkstyle\.(org|sourceforge)", "Checkstyle"),
    (r"eslint\.org", "ESLint"),
    (r"rubocop", "RuboCop"),
    (r"bandit\.readthedocs", "Bandit"),
    (r"gosec|securego", "gosec"),
    (r"brakemanscanner", "Brakeman"),
    (r"cwe\.mitre\.org|owasp\.org", "__taxonomy__"),  # NOT a tool
]


def upstream_of(url):
    for pat, name in UPSTREAM:
        if re.search(pat, url, re.I):
            return name
    return "__other__"


def load_native(path):
    d = json.load(open(path))
    return d.get("results", [])


def rule_table(results):
    """check_id -> metadata, for rules that FIRED (one row per distinct rule)."""
    t = {}
    for r in results:
        cid = r.get("check_id")
        md = (r.get("extra") or {}).get("metadata") or {}
        if cid and cid not in t:
            t[cid] = md
    return t


def prov_of(md):
    for f in PROV_FIELDS:
        v = md.get(f)
        if v:
            return (v if isinstance(v, str) else
                    (v[0] if isinstance(v, list) and v else None))
    return None


def bar(n, d):
    return f"{n:5}/{d:<5} = {100*n/d:5.1f}%" if d else f"{n:5}/{d:<5} =   n/a"


print("=" * 78)
print("RULE-PROVENANCE MEASUREMENT — CORPUS ARM (RQ1, RQ2)")
print("all derived fractions below are LOWER BOUNDS; see header")
print("=" * 78)

RUNS = [
    ("OWASP Benchmark v1.2 (Java, synthetic)",
     f"{OLD}/owasp/sg_native.json",
     ["SpotBugs", "FindSecBugs"]),          # other tools present in this run
    ("zlib 1.3.1 (C, real)",
     f"{OLD}/lib/zs_native.json",
     ["Flawfinder", "Cppcheck"]),
]

allrules = {}
for label, path, others in RUNS:
    if not os.path.exists(path):
        print(f"\n{label}: NATIVE JSON ABSENT — cannot measure. SKIPPED.")
        continue
    res = load_native(path)
    rt = rule_table(res)
    allrules.update(rt)

    fired = len(rt)
    declared = {c: prov_of(m) for c, m in rt.items()}
    with_prov = {c: u for c, u in declared.items() if u}
    # findings-level
    per_rule = Counter(r.get("check_id") for r in res)
    find_total = sum(per_rule.values())
    find_prov = sum(per_rule[c] for c in with_prov)

    print(f"\n{'='*78}\n{label}\n  other tools in this run: {', '.join(others)}\n{'='*78}")
    print(f"  RQ1a  rules that FIRED                        : {fired}")
    print(f"  RQ1b  ...declaring provenance (LOWER BOUND)   : {bar(len(with_prov), fired)}")
    print(f"  RQ1c  FINDINGS from declaring rules (LOWER BD): {bar(find_prov, find_total)}")

    ups = Counter(upstream_of(u) for u in with_prov.values())
    print(f"\n  upstream named by those rules:")
    for name, n in ups.most_common():
        tag = ""
        if name == "__taxonomy__":
            tag = "   <- taxonomy ref, NOT a tool: excluded from RQ2"
        elif name == "__other__":
            tag = "   <- unrecognised host; inspect before counting"
        print(f"    {name:<16} {n:3} rule(s){tag}")

    # RQ2 precondition: does the named upstream correspond to a tool in THIS run?
    inrun = {c: upstream_of(u) for c, u in with_prov.items()
             if upstream_of(u) in others}
    print(f"\n  RQ2 precondition — declaring rules whose NAMED UPSTREAM is also")
    print(f"  a tool present in this same run: {bar(len(inrun), fired)}")
    if inrun:
        fi = sum(per_rule[c] for c in inrun)
        print(f"    findings from those rules: {bar(fi, find_total)}")
        for c, u in sorted(inrun.items()):
            print(f"      {per_rule[c]:5} findings  {c}")
            print(f"                       <- {with_prov[c]}")
    else:
        print("    NONE. No rule in this run declares an ancestor that is also")
        print("    one of the other tools scanned, so cross-tool agreement here")
        print("    CANNOT be rule-and-ancestor by DECLARED provenance.")

print(f"\n{'='*78}")
print("CORPORA THAT CANNOT BE MEASURED")
print("=" * 78)
print("""  Apache Struts (Java, REAL code) — only SARIF is on disk (struts/sg.sarif,
  sg_raw.sarif); no native semgrep JSON was captured. SARIF drops
  source-rule-url, so provenance is UNREADABLE for that run from local data.

  THIS IS THE CONSEQUENTIAL GAP: Struts is the project's only REAL-CODE Java
  corpus and the site of the single real-code cross-tool agreement ever
  observed (the ServletRedirectResult near-miss, HANDOFF 0e). Its rule can be
  resolved only by JOINING against rule metadata captured in another run.""")

# join attempt for the Struts rule of interest
tgt = [c for c in allrules if "unvalidated-redirect" in c or "redirect" in c.lower()]
if tgt:
    print("\n  JOIN against rule metadata captured in the OWASP run:")
    for c in sorted(tgt):
        p = prov_of(allrules[c])
        print(f"    {c}")
        print(f"      declared provenance: {p or 'NONE DECLARED'}")
    print("""    Rule metadata is a property of the RULE, not of the run, so this join
    is valid for any rule appearing in both. It does NOT recover provenance
    for Struts rules absent from the OWASP run.""")
else:
    print("\n  The Struts near-miss rule does not appear in any measured run;")
    print("  no join is possible from local data.")
