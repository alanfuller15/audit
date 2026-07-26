#!/usr/bin/env python3
"""How many OWASP merges are a semgrep rule agreeing with its OWN ANCESTOR?
A merge between a rule and the rule it was derived from is shared provenance,
not independent corroboration."""
import json, os, re, sys, csv
from collections import Counter, defaultdict
sys.path.insert(0, "/Users/caitlinfuller/audit/src")
from audit import _norm_uri, _cwe_class_of, _CWE_CLASS, _CWE_DENY

HERE = os.path.dirname(os.path.abspath(__file__))

# --- semgrep: rule -> declared source anchor (the FindSecBugs bug pattern) ---
nat = json.load(open(os.path.join(HERE, "owasp", "sg_native.json")))
rule_src = {}
for r in nat.get("results", []):
    md = (r.get("extra") or {}).get("metadata") or {}
    src = md.get("source-rule-url") or ""
    if isinstance(src, list):
        src = " ".join(src)
    rule_src[r["check_id"]] = str(src)

def anchors(src):
    """FindSecBugs bug-pattern names named in a source-rule-url."""
    return {m.upper() for m in re.findall(r"find-sec-bugs\.github\.io/bugs\.htm#([A-Z_0-9]+)",
                                          str(src), re.I)}

# semgrep findings keyed by location
sg = defaultdict(list)
for r in nat.get("results", []):
    u = _norm_uri(r["path"])
    ln = (r.get("start") or {}).get("line")
    if ln is None:
        continue
    sg[(u, ln)].append(r["check_id"])

# --- SpotBugs findings keyed by location ---
sbd = json.load(open(os.path.join(HERE, "owasp", "sb.sarif")))
sb = defaultdict(list)
for run in sbd["runs"]:
    for r in run.get("results", []):
        loc = ((r.get("locations") or [{}])[0].get("physicalLocation") or {})
        u = _norm_uri((loc.get("artifactLocation") or {}).get("uri", ""))
        ln = (loc.get("region") or {}).get("startLine")
        if ln is None:
            continue
        sb[(u, ln)].append(r.get("ruleId", ""))

# --- co-located pairs, and whether each is rule-and-ancestor ----------------
derived = independent = 0
pairs = Counter()
for k, sgrules in sg.items():
    for sbrule in sb.get(k, []):
        for sgr in sgrules:
            a = anchors(rule_src.get(sgr, ""))
            if sbrule.upper() in a:
                derived += 1
                pairs[(sgr.split(".")[-1], sbrule)] += 1
            else:
                independent += 1
                pairs[("OTHER:" + sgr.split(".")[-1], sbrule)] += 0

tot = derived + independent
print("=== OWASP: co-located semgrep x SpotBugs rule pairs ===")
print(f"  total co-located rule pairs        : {tot}")
print(f"  RULE-AND-ITS-OWN-ANCESTOR pairs    : {derived}  ({100*derived/max(1,tot):.1f}%)")
print(f"  independent-provenance pairs       : {independent}  ({100*independent/max(1,tot):.1f}%)")
print()
print("  ancestor pairs by rule:")
for (a, b), n in pairs.most_common():
    if n:
        print(f"    {a:<34} <- derived from ->  {b:<26} {n}")

# --- how much of the *finding* population is affected ----------------------
fsb_findings = sum(1 for r in nat.get("results", []) if anchors(rule_src.get(r["check_id"], "")))
print()
print(f"  semgrep findings from FindSecBugs-derived rules: {fsb_findings} / {len(nat.get('results', []))}"
      f"  ({100*fsb_findings/max(1,len(nat.get('results',[]))):.1f}%)")
