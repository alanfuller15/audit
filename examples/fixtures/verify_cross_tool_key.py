#!/usr/bin/env python3
"""verify_cross_tool_key.py — regression harness for the _result_key
two-algorithm split (HANDOFF §7 item 2).

Guards the fix recorded in docs/SCOPE_shipped_consensus_defect.md: before it,
`_result_key` used a tool's own fingerprint as the CROSS-tool identity, so the
shipped flawfinder+cppcheck pair could never produce n_tools>1 on any input.

Runs with no scanners installed and no network — the SARIF fixtures beside this
file are CAPTURED real output (see regen_fixtures.sh).

    python3 examples/fixtures/verify_cross_tool_key.py
"""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import audit  # noqa: E402

FF = os.path.join(HERE, "flawfinder_min.sarif")
CC = os.path.join(HERE, "cppcheck_min.sarif")

_fail = []


def check(ok, label, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not ok:
        _fail.append(label)


def sarif(tool, results):
    return {"version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": tool}}, "results": results}]}


def res(rid, uri, line, msg="", fingerprint=None):
    r = {"ruleId": rid, "level": "warning", "message": {"text": msg},
         "locations": [{"physicalLocation": {
             "artifactLocation": {"uri": uri}, "region": {"startLine": line}}}]}
    if fingerprint:
        r["fingerprints"] = {"contextHash/v1": fingerprint}
    return r


def ingest(*docs):
    """Write docs to temp SARIF files and ingest, returning the aggregate."""
    tmp = tempfile.mkdtemp()
    paths = []
    for i, d in enumerate(docs):
        p = os.path.join(tmp, f"t{i}.sarif")
        json.dump(d, open(p, "w"))
        paths.append(p)
    return audit.ingest_sarif(paths)


print("verify_cross_tool_key — two-algorithm dedup key\n")

# ── 1. THE FIX: real captured output from the shipped tool pair now merges ──
agg = audit.ingest_sarif([FF, CC])
merged = [f for f in agg["ranked"] if f["n_tools"] > 1]
check(len(merged) == 1, "1 cross-tool merge on REAL captured fixtures",
      f"{len(merged)} merged; n_tools max={max(f['n_tools'] for f in agg['ranked'])}")
if merged:
    m = merged[0]
    check(sorted(m["tools"]) == ["Cppcheck", "Flawfinder"] and m["line"] == 15,
          "merged finding is the genuine overlap",
          f"{m['uri']}:{m['line']} tools={sorted(m['tools'])}")

# The two sides had DIFFERENT ruleIds and one carried fingerprints — the exact
# combination that was structurally unmergeable before the fix.
ff_raw = json.load(open(FF))["runs"][0]["results"]
check(all(r.get("fingerprints") for r in ff_raw),
      "fixture flawfinder side really does emit fingerprints",
      f"{sum(1 for r in ff_raw if r.get('fingerprints'))}/{len(ff_raw)}")

# ── 2. SAME-TOOL dedup must not regress ─────────────────────────────────────
dup = res("CWE-476", "src/a.c", 10, "null deref", fingerprint="samehash")
agg = ingest(sarif("ToolA", [dup, json.loads(json.dumps(dup))]))
check(agg["deduplicated_count"] == 1 and agg["ranked"][0]["n_tools"] == 1,
      "same-tool duplicate collapses, n_tools stays 1",
      f"{agg['deduplicated_count']} finding(s), n_tools={agg['ranked'][0]['n_tools']}")

# Same tool, same location, same class, DIFFERENT rules must NOT merge into
# self-agreement — that would let one tool inflate its own consensus.
agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null deref"),
                             res("CWE-825", "src/a.c", 10, "stale pointer")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 1,
      "same-tool findings never inflate n_tools",
      f"n_tools max={max(f['n_tools'] for f in agg['ranked'])}")

# ── 3. Fingerprints must no longer block CROSS-tool agreement ───────────────
agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null", fingerprint="aaa")]),
             sarif("ToolB", [res("nullDeref", "src/a.c", 10, "null deref CWE-476")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 2,
      "fingerprint on one side no longer blocks cross-tool merge")

# ── 4. Path normalization (the _norm_uri fix) ───────────────────────────────
for a, b, label in [("src/a.c", "./src/a.c", "./ prefix"),
                    ("src/a.c", "x/../src/a.c", "../ segment"),
                    ("src/a.c", "src//a.c", "double slash")]:
    agg = ingest(sarif("ToolA", [res("CWE-476", a, 10, "null")]),
                 sarif("ToolB", [res("CWE-476", b, 10, "null")]))
    check(max(f["n_tools"] for f in agg["ranked"]) == 2,
          f"path forms unify: {label}", f"{a} vs {b}")

# ── 5. CONSERVATISM: false merges are worse than missed ones ────────────────
agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null")]),
             sarif("ToolB", [res("CWE-120", "src/a.c", 10, "overflow")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 1,
      "different CWE classes at one location do NOT merge")

agg = ingest(sarif("ToolA", [res("CWE-476", "src/a.c", 10, "null")]),
             sarif("ToolB", [res("CWE-476", "src/a.c", 11, "null")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 1,
      "off-by-one lines do NOT merge at the scoring layer (TOL is display-only)")

for denied in ("CWE-398", "CWE-664", "CWE-758"):
    agg = ingest(sarif("ToolA", [res(denied, "src/a.c", 10, "generic")]),
                 sarif("ToolB", [res(denied + "x", "src/a.c", 10, "generic " + denied)]))
    check(max(f["n_tools"] for f in agg["ranked"]) == 1,
          f"junk-drawer {denied} does not merge")

# ── 6. DEGENERATE FINGERPRINTS must not destroy findings ────────────────────
# Real defect found on zlib: semgrep OSS run unauthenticated emits a CONSTANT
# "matchBasedId/v1": "requires login" on every result. Trusting it as an
# identity collapsed 33 findings into 1. flawfinder's contextHash/v1 hashes
# surrounding code, so identical C idioms in different places also collided —
# 588 raw findings were collapsing to 484 instead of 582.
CONST = "requires login"
agg = ingest(sarif("Placeholder", [
    res("R1", "src/a.c", 10, "x", fingerprint=CONST),
    res("R2", "src/b.c", 20, "y", fingerprint=CONST),
    res("R3", "src/c.c", 30, "z", fingerprint=CONST)]))
check(agg["deduplicated_count"] == 3,
      "constant placeholder fingerprint does NOT collapse distinct findings",
      f"{agg['deduplicated_count']}/3 survived")

# A genuine per-finding fingerprint must still dedup normally.
agg = ingest(sarif("Good", [res("R1", "src/a.c", 10, "x", fingerprint="uniq-1"),
                            res("R1", "src/a.c", 10, "x", fingerprint="uniq-1"),
                            res("R2", "src/b.c", 20, "y", fingerprint="uniq-2")]))
check(agg["deduplicated_count"] == 2,
      "genuine per-finding fingerprints still dedup", f"{agg['deduplicated_count']}/2")

# ── 7. Rule METADATA is searched for CWE, not just the result ───────────────
# semgrep puts its CWE only in rule.properties.tags (["CWE-415: Double Free"]);
# scanning result text alone resolved 0 of 33 findings — a false negative from
# our parser rather than from the tools disagreeing.
meta_doc = {"version": "2.1.0", "runs": [{
    "tool": {"driver": {"name": "MetaTool", "rules": [
        {"id": "some.rule.id", "properties": {"tags": ["CWE-476: NULL Pointer Dereference"]}}]}},
    "results": [res("some.rule.id", "src/a.c", 10, "no cwe in this message")]}]}
agg = ingest(meta_doc, sarif("Other", [res("nullDeref", "src/a.c", 10, "null deref CWE-476")]))
check(max(f["n_tools"] for f in agg["ranked"]) == 2,
      "CWE found in rule metadata enables cross-tool merge")

# ── 8. ENGINE LINEAGE: two names for one engine must not fake consensus ─────
# The exploit needs no adversary: run SpotBugs, import the report into SonarQube
# via sonar.java.spotbugs.reportPaths, feed BOTH SARIFs to --ingest. Same
# findings, two driver names. Pre-fix that scored n_tools=2 on self-agreement.
same_engine = ingest(
    sarif("SpotBugs", [res("CWE-476", "src/a.c", 10, "null deref")]),
    sarif("FindBugs", [res("nullDeref", "src/a.c", 10, "null deref CWE-476")]))
check(max(f["n_tools"] for f in same_engine["ranked"]) == 1,
      "SpotBugs + FindBugs (one engine) do NOT inflate n_tools",
      f"n_tools max={max(f['n_tools'] for f in same_engine['ranked'])}")

plugin = ingest(
    sarif("SpotBugs", [res("CWE-476", "src/a.c", 10, "null deref")]),
    sarif("Find Security Bugs", [res("nullDeref", "src/a.c", 10, "null deref CWE-476")]))
check(max(f["n_tools"] for f in plugin["ranked"]) == 1,
      "SpotBugs + its FindSecBugs PLUGIN do NOT inflate n_tools")

# Genuinely different engines must still merge exactly as before.
diff_engine = ingest(
    sarif("Cppcheck", [res("CWE-476", "src/a.c", 10, "null deref")]),
    sarif("Flawfinder", [res("FF9", "src/a.c", 10, "null deref CWE-476")]))
check(max(f["n_tools"] for f in diff_engine["ranked"]) == 2,
      "different engines still merge (no regression)")

# Unknown tools default to their own name -> behave exactly as before.
unknown = ingest(sarif("MyCustomScanner", [res("CWE-476", "src/a.c", 10, "null")]),
                 sarif("OtherScanner", [res("CWE-476", "src/a.c", 10, "null")]))
check(max(f["n_tools"] for f in unknown["ranked"]) == 2,
      "unknown tools keep prior behaviour (default lineage = own name)")

# Transitive case: A/engine1 merges with B/engine2 merges with C/engine1.
# The chain can put two same-engine drivers in ONE record, so n_tools must be
# counted by engine, not just guarded at merge time.
trans = ingest(sarif("SpotBugs", [res("CWE-476", "src/a.c", 10, "null deref")]),
               sarif("Cppcheck", [res("CWE-476", "src/a.c", 10, "null deref")]),
               sarif("FindBugs", [res("CWE-476", "src/a.c", 10, "null deref")]))
top = max(f["n_tools"] for f in trans["ranked"])
check(top == 2, "transitive chain counts ENGINES not names", f"n_tools={top} (expect 2, not 3)")

# The independence caveat must be disclosed, not silently assumed.
sonar = ingest(sarif("SonarQube", [res("CWE-476", "src/a.c", 10, "null")]),
               sarif("SpotBugs", [res("CWE-476", "src/b.c", 20, "null")]))
check(any("SonarQube" in w and "import" in w.lower() for w in sonar.get("lineage_warnings", [])),
      "SonarQube + an importable tool triggers an independence disclosure",
      f"{len(sonar.get('lineage_warnings', []))} warning(s)")

# ── 9. Decision 0a: ambiguous independence resolves to NO-MERGE by default ──
# SonarQube can import SpotBugs/PMD/Checkstyle reports, so SARIF cannot show
# whether it analysed independently. Uncertainty resolves the same way it does
# everywhere else in this pipeline: no merge.
_saved = os.environ.pop("AUDIT_INDEPENDENT_TOOLS", None)
amb = ingest(sarif("SonarQube", [res("java:S1", "src/A.java", 5, "null CWE-476")]),
             sarif("SpotBugs", [res("NP_NULL", "src/A.java", 5, "null CWE-476")]))
check(max(f["n_tools"] for f in amb["ranked"]) == 1,
      "SonarQube + importable tool does NOT count as consensus by default",
      f"n_tools max={max(f['n_tools'] for f in amb['ranked'])}")
check(any("NOT counted as consensus" in w for w in amb.get("lineage_warnings", [])),
      "suppression is DISCLOSED, not silent")
check(any("AUDIT_INDEPENDENT_TOOLS" in w for w in amb.get("lineage_warnings", [])),
      "the disclosure names the escape hatch")

# SonarQube alongside a tool it CANNOT import is unaffected.
unrelated = ingest(sarif("SonarQube", [res("java:S1", "src/A.java", 5, "null CWE-476")]),
                   sarif("CodeQL", [res("java/npe", "src/A.java", 5, "null CWE-476")]))
check(max(f["n_tools"] for f in unrelated["ranked"]) == 2,
      "SonarQube + a non-importable tool still merges (no over-blocking)")

# Escape hatch: the operator declares independence.
os.environ["AUDIT_INDEPENDENT_TOOLS"] = "SonarQube"
declared = ingest(sarif("SonarQube", [res("java:S1", "src/A.java", 5, "null CWE-476")]),
                  sarif("SpotBugs", [res("NP_NULL", "src/A.java", 5, "null CWE-476")]))
check(max(f["n_tools"] for f in declared["ranked"]) == 2,
      "operator declaration re-enables the merge")
check(any("DECLARED by the operator" in w for w in declared.get("lineage_warnings", [])),
      "the declaration itself is disclosed as an operator assertion")
if _saved is None:
    os.environ.pop("AUDIT_INDEPENDENT_TOOLS", None)
else:
    os.environ["AUDIT_INDEPENDENT_TOOLS"] = _saved

# ── 10. Test-directory heuristic (item 3d) ──────────────────────────────────
# zlib's contrib/testzlib/ is benchmark code but TEST_DIR required a segment
# matching exactly `tests?`, so BOTH cross-tool merges on that corpus were
# scored as ordinary library code. Widened to directory-prefix matching.
# The negatives matter as much as the positives: this must not start
# down-weighting production sources.
for path, want, why in [
        ("zlib-1.3.1/contrib/testzlib/testzlib.c", True, "the reported case"),
        ("proj/testsuite/foo.c", True, "test-prefixed dir"),
        ("proj/benchmark/foo.c", True, "benchmark dir"),
        ("zlib-1.3.1/contrib/blast/blast.c", False, "real utility, must not match"),
        ("zlib-1.3.1/contrib/minizip/miniunz.c", False, "real utility, must not match"),
        ("zlib-1.3.1/deflate.c", False, "library source"),
        ("src/tester.c", False, "FILE not dir — must not match"),
        ("src/latest/foo.c", False, "substring 'test', not a prefix"),
        ("src/contest/foo.c", False, "substring 'test', not a prefix")]:
    check(audit.is_test_file(path) == want, f"test-dir heuristic: {why}", path)

# ── 11. Multi-class metadata resolves to NONE (found on real SpotBugs output) ─
# Text order carries no semantic meaning, so first-mapped-CWE-wins picked an
# arbitrary winner. Two real FindSecBugs rules exposed it, in different ways.
from audit import _cwe_class_of  # noqa: E402

# (a) GENUINE AMBIGUITY: rule is about error-message exposure; 22/89 are
#     incidental prose. None is the RIGHT answer.
check(_cwe_class_of("INFORMATION_EXPOSURE_THROUGH_AN_ERROR_MESSAGE",
                    "CWE-22 CWE-89 CWE-209 CWE-211 error message exposure", "") is None,
      "ambiguous multi-class metadata resolves to None (was: 'path')")

# (b) SPECIFICITY, not ambiguity: CWE-328 is a CHILD of CWE-327, both correct.
#     None is the SAFE answer, not the right one — see HANDOFF 3e.
check(_cwe_class_of("WEAK_MESSAGE_DIGEST_MD5", "CWE-327 CWE-328 weak digest", "") is None,
      "specificity pair 327/328 resolves to None (was: 'crypto', shadowing 'hash')")

# Single-class metadata must still resolve — the fix must not break the 97%.
check(_cwe_class_of("SQL_INJECTION_JDBC", "CWE-89 sql injection", "") == "sqli",
      "single-class metadata still resolves")
check(_cwe_class_of("XSS_SERVLET", "CWE-79 potential XSS", "") == "xss",
      "single-class metadata still resolves (xss)")
# Repeats of the SAME class are not ambiguity.
check(_cwe_class_of("R", "CWE-22 and also CWE-23 and CWE-36 path traversal", "") == "path",
      "several CWEs mapping to ONE class still resolve")
# A denied CWE alongside a mapped one is not ambiguity — denied ones are skipped.
check(_cwe_class_of("R", "CWE-398 CWE-89 injection", "") == "sqli",
      "denied CWE alongside a mapped one does not block resolution")

# ── 12. PATH-ROOT MISMATCH must be DETECTED and DISCLOSED (item 0c) ─────────
# SpotBugs derives paths from bytecode (package-relative); source tools emit
# scan-root-relative. One is a suffix of the other, so merging silently yields
# ZERO. Detect and warn — deliberately NOT suffix-matching, which could falsely
# unify same-named files across modules.
pkg_rel = sarif("SpotBugs", [res("CWE-89", "org/acme/Login.java", 42, "sqli CWE-89")])
root_rel = sarif("Semgrep OSS", [res("sqli.rule", "src/main/java/org/acme/Login.java", 42,
                                     "sql injection CWE-89")])
mism = ingest(pkg_rel, root_rel)
check(bool(mism.get("path_warnings")),
      "different path ROOTS are detected and warned",
      f"{len(mism.get('path_warnings', []))} warning(s)")
check(any("DIFFERENT ROOTS" in w for w in mism.get("path_warnings", [])),
      "the warning names the cause")
check(any("ZERO for that reason alone" in w for w in mism.get("path_warnings", [])),
      "the warning says a zero count is NOT tool disagreement")
check(max(f["n_tools"] for f in mism["ranked"]) == 1,
      "no suffix matching is attempted (that is option (a), not built)")

# Matched paths must stay silent AND still merge.
matched = ingest(sarif("SpotBugs", [res("CWE-89", "org/acme/Login.java", 42, "sqli CWE-89")]),
                 sarif("Semgrep OSS", [res("sqli.rule", "org/acme/Login.java", 42,
                                           "sql injection CWE-89")]))
check(not matched.get("path_warnings"), "matched paths produce NO path warning")
check(max(f["n_tools"] for f in matched["ranked"]) == 2,
      "matched paths still merge (no regression)")

# Genuinely different files must not warn — no shared basenames.
diff = ingest(sarif("ToolA", [res("CWE-89", "src/a/One.java", 5, "sqli CWE-89")]),
              sarif("ToolB", [res("CWE-89", "src/b/Two.java", 9, "sqli CWE-89")]))
check(not diff.get("path_warnings"),
      "disjoint filenames do not warn (not a root mismatch)")

# Real captured C/C++ fixtures must stay silent.
check(not audit.ingest_sarif([FF, CC]).get("path_warnings"),
      "real cppcheck+flawfinder fixtures stay silent")

# ── 13. Determinism and order-independence ──────────────────────────────────
a1 = audit.ingest_sarif([FF, CC])
a2 = audit.ingest_sarif([CC, FF])
strip = lambda a: [(r["score"], r["uri"], r["line"], r["ruleId"], r["n_tools"])
                   for r in a["ranked"]]
check(strip(a1) == strip(a2), "ranking is input-order independent")
check(strip(audit.ingest_sarif([FF, CC])) == strip(a1), "ranking is deterministic across runs")

print()
if _fail:
    print(f"FAILED ({len(_fail)}): " + "; ".join(_fail))
    sys.exit(1)
print("all checks passed")
