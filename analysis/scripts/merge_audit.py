#!/usr/bin/env python3
"""Cross-tool merge + 7a false-merge audit on OWASP Benchmark v1.2.
SpotBugs+FindSecBugs x semgrep. Labels are the point of this corpus."""
import json, os, sys, csv
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", "..", "src"))  # was hard-coded
import audit
from audit import _cwe_class_of, _norm_uri
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _corpus  # noqa: E402  (path resolution only)

HERE = _corpus.corpus_root()
SB = os.path.join(HERE, "owasp", "sb.sarif")
SG = os.path.join(HERE, "owasp", "sg_java2.sarif")
KEY = os.path.join(HERE, "owasp", "BenchmarkJava-master", "expectedresults-1.2.csv")

key = {}
for r in csv.DictReader(open(KEY)):
    key[r["# test name"].strip()] = (r[" category"].strip(), int(r[" cwe"]),
                                     r[" real vulnerability"].strip().lower() == "true")
CAT2CLS = {"sqli": "sqli", "cmdi": "cmdi", "xss": "xss", "pathtraver": "path",
           "ldapi": "ldapi", "xpathi": "xpathi", "crypto": "crypto",
           "hash": "hash", "weakrand": "random", "trustbound": None,
           "securecookie": None}

agg = audit.ingest_sarif([SB, SG])
ranked = agg["ranked"]
merged = [f for f in ranked if f["n_tools"] > 1]

print("=== CROSS-TOOL MERGES: SpotBugs+FindSecBugs x semgrep ===")
print(f"  tools            : {agg['tools']}")
print(f"  raw findings     : {agg['raw_result_count']}")
print(f"  same-tool dedup  : {agg['same_tool_deduplicated_count']}")
print(f"  cross-tool merges: {agg['cross_tool_merges']}")
print(f"  final findings   : {agg['deduplicated_count']}")
rate = 100.0 * agg["cross_tool_merges"] / max(1, agg["same_tool_deduplicated_count"])
print(f"  merge rate       : {rate:.2f}% of same-tool-deduped findings")
print(f"  n_tools distrib  : {dict(sorted(Counter(f['n_tools'] for f in ranked).items()))}")
print()

if not merged:
    print("  no merges — nothing to audit")
    sys.exit(0)

def testname(uri):
    b = os.path.splitext(os.path.basename(uri))[0]
    return b if b in key else None

print("=== WHICH CLASSES DO MERGES LAND IN ===")
mc = Counter()
for f in merged:
    cls = f.get("cwe_class") or "?"
    mc[cls] += 1
for c, n in mc.most_common():
    print(f"  {c:<10} {n}")
print()

print("=== MERGES vs THE ANSWER KEY (the point of this corpus) ===")
onvuln = onfp = unlabelled = 0
for f in merged:
    t = testname(f["uri"])
    if t is None:
        unlabelled += 1
    elif key[t][2]:
        onvuln += 1
    else:
        onfp += 1
print(f"  on files labelled REAL VULNERABILITY : {onvuln}")
print(f"  on files labelled PLANTED FALSE POS  : {onfp}")
print(f"  on unlabelled files (helpers etc.)   : {unlabelled}")
if onvuln + onfp:
    print(f"  precision of merges vs labels        : {100.0*onvuln/(onvuln+onfp):.1f}%")
    base = sum(1 for v in key.values() if v[2]) / len(key)
    print(f"  benchmark base rate (real vulns)     : {100.0*base:.1f}%")
print()

print("=== 7a FALSE-MERGE AUDIT ===")
print("A merge is at (uri, line, class): BOTH tools flagged the same line with")
print("the same class. A FALSE merge = same location+class but different bugs.")
print()
same_cat = diff_cat = nocat = 0
suspects = []
for f in merged:
    t = testname(f["uri"])
    cls = f.get("cwe_class")
    if t is None:
        nocat += 1
        continue
    cat, cwe, real = key[t]
    want = CAT2CLS.get(cat)
    if want is None:
        nocat += 1
    elif cls == want:
        same_cat += 1
    else:
        diff_cat += 1
        suspects.append((f, cat, cls))
print(f"  merged class MATCHES the file's planted category : {same_cat}")
print(f"  merged class DIFFERS from planted category       : {diff_cat}")
print(f"  file unlabelled / category has no class          : {nocat}")
print()
if suspects:
    print("  merges whose class differs from the planted category:")
    for f, cat, cls in suspects[:15]:
        print(f"    {os.path.basename(f['uri']):<26}:{f['line']:<5} planted={cat:<12} merged_class={cls}")
    print()
    print("  NOTE: differing != false. The tools may both have found a genuine")
    print("  SECOND issue in the file; the key labels one planted bug per file.")
print()

print("=== PREDICTED FALSE-MERGE SITES (the 56 multi-class files) ===")
multi = {}
for path, lbl in ((SB, "sb"), (SG, "sg")):
    d = json.load(open(path))
    for run in d["runs"]:
        rules = {rr.get("id"): " ".join(str(x) for x in [
            rr.get("id", ""), rr.get("name", ""),
            (rr.get("shortDescription") or {}).get("text", ""),
            (rr.get("fullDescription") or {}).get("text", ""),
            " ".join((rr.get("properties") or {}).get("tags") or [])])
            for rr in (run["tool"]["driver"].get("rules") or [])}
        for r in run.get("results", []):
            rid = r.get("ruleId", "")
            loc = ((r.get("locations") or [{}])[0].get("physicalLocation") or {})
            uri = _norm_uri((loc.get("artifactLocation") or {}).get("uri", ""))
            t = testname(uri)
            if not t:
                continue
            c = (_cwe_class_of(rid, (r.get("message") or {}).get("text", ""), uri)
                 or _cwe_class_of(rid, rules.get(rid, ""), ""))
            if c:
                multi.setdefault(t, set()).add(c)
mset = {t: c for t, c in multi.items() if len(c) > 1}
print(f"  files where either tool resolved >1 class: {len(mset)}")
for combo, n in Counter(tuple(sorted(c)) for c in mset.values()).most_common(6):
    print(f"    {' + '.join(combo):<26} {n}")
merged_in_multi = [f for f in merged if testname(f["uri"]) in mset]
print(f"  merges landing on those files            : {len(merged_in_multi)}")
for f in merged_in_multi[:10]:
    t = testname(f["uri"])
    cls = f.get("cwe_class")
    print(f"    {os.path.basename(f['uri']):<26}:{f['line']:<5} planted={key[t][0]:<12} "
          f"merged={cls:<8} classes_seen={sorted(mset[t])}")
