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
# AMENDED 2026-07-26 alongside option (a). The warning used to assert the count
# "will be ZERO for that reason alone"; once suffix linkage rescues the pair
# that is false, so the text now says linkage reconciled it AND that the
# configuration is still worth fixing. A warning that contradicts the merge
# count printed beside it is its own honesty failure.
check(any("still worth fixing" in w for w in mism.get("path_warnings", [])),
      "warning is amended when linkage rescues the pair, not left contradictory")
check(not any("ZERO for that reason alone" in w for w in mism.get("path_warnings", [])),
      "the now-false 'will be ZERO' claim is removed when linkage succeeded")
# SUPERSEDED 2026-07-26. This previously asserted "no suffix matching is
# attempted (that is option (a), not built)". Option (a) IS now built, behind
# the cardinality-1 guard, so the expectation INVERTS: these two paths are
# suffix-related and unique on both sides, so they SHOULD now merge. The
# warning above is still emitted, and that is deliberate — the operator is told
# the roots differ even when linkage rescues the merge, because the underlying
# configuration is still worth fixing.
check(max(f["n_tools"] for f in mism["ranked"]) == 2,
      "option (a) IS built: unique suffix-related paths now merge")
check(mism["suffix_linkage"]["merges_using_suffix_match"] == 1,
      "and the rescue is attributed to suffix linkage, not to plain agreement")
check(bool(mism.get("path_warnings")),
      "the root-mismatch warning is STILL emitted even when linkage succeeds")

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

# ── 13. POINT-IN-RANGE containment (Direction B) ────────────────────────────
def res_range(rid, uri, start, end, msg=""):
    r = res(rid, uri, start, msg)
    r["locations"][0]["physicalLocation"]["region"]["endLine"] = end
    return r

# THE COMMON CASE, tested first so the asymmetry is not mistaken for design:
# when NEITHER tool emits endLine there is no range, so containment adds
# NOTHING. On OWASP, SpotBugs emitted a range on 0 of 3,268 class-resolved
# findings — every gain came from semgrep's ranges. This is the default.
noranges = ingest(sarif("ToolA", [res("CWE-89", "src/A.java", 10, "sqli CWE-89")]),
                  sarif("ToolB", [res("CWE-89", "src/A.java", 14, "sqli CWE-89")]))
check(max(f["n_tools"] for f in noranges["ranked"]) == 1,
      "NEITHER tool emits endLine -> containment adds nothing (the common case)")

# One side declares a range that contains the other's point -> merge.
contained = ingest(sarif("ToolA", [res_range("CWE-89", "src/A.java", 10, 20, "sqli CWE-89")]),
                   sarif("ToolB", [res("CWE-89", "src/A.java", 14, "sqli CWE-89")]))
check(max(f["n_tools"] for f in contained["ranked"]) == 2,
      "point inside a declared range merges")
check("range-containment" in contained.get("findings_by_merge_rule", {}),
      "the merge is REPORTED as range-containment, not exact-line",
      str(contained.get("findings_by_merge_rule")))

# Exact-line merges must still be labelled as such, so the two populations
# stay separable for future measurement.
ex = ingest(sarif("ToolA", [res("CWE-89", "src/A.java", 10, "sqli CWE-89")]),
            sarif("ToolB", [res("CWE-89", "src/A.java", 10, "sqli CWE-89")]))
check(ex.get("findings_by_merge_rule", {}).get("exact-line") == 1
      and "range-containment" not in ex.get("findings_by_merge_rule", {}),
      "exact-line merges are labelled separately", str(ex.get("findings_by_merge_rule")))

# SPAN CAP: a range wider than the cap is a tolerance window with extra steps.
wide = ingest(sarif("ToolA", [res_range("CWE-89", "src/A.java", 10, 400, "sqli CWE-89")]),
              sarif("ToolB", [res("CWE-89", "src/A.java", 300, "sqli CWE-89")]))
check(max(f["n_tools"] for f in wide["ranked"]) == 1,
      f"a range wider than the cap ({audit._RANGE_SPAN_CAP}) does NOT merge")
edge = ingest(sarif("ToolA", [res_range("CWE-89", "src/A.java", 10,
                                        10 + audit._RANGE_SPAN_CAP, "sqli CWE-89")]),
              sarif("ToolB", [res("CWE-89", "src/A.java", 15, "sqli CWE-89")]))
check(max(f["n_tools"] for f in edge["ranked"]) == 2, "a range AT the cap still merges")

# CONTAINMENT RELAXES LOCATION ONLY — the class test is untouched.
diffcls = ingest(sarif("ToolA", [res_range("CWE-89", "src/A.java", 10, 20, "sqli CWE-89")]),
                 sarif("ToolB", [res("CWE-79", "src/A.java", 14, "xss CWE-79")]))
check(max(f["n_tools"] for f in diffcls["ranked"]) == 1,
      "containment does NOT relax the same-class requirement")

# Same engine must still not self-merge via a range.
sameeng = ingest(sarif("SpotBugs", [res_range("CWE-89", "src/A.java", 10, 20, "sqli CWE-89")]),
                 sarif("FindBugs", [res("CWE-89", "src/A.java", 14, "sqli CWE-89")]))
check(max(f["n_tools"] for f in sameeng["ranked"]) == 1,
      "containment does NOT bypass the engine-lineage guard")

# Exact-line and containment populations must stay SEPARABLE: a merge that
# would have happened on the exact line is never labelled range-containment.
both = ingest(sarif("ToolA", [res_range("CWE-89", "src/A.java", 10, 20, "sqli CWE-89")]),
              sarif("ToolB", [res("CWE-89", "src/A.java", 10, "sqli CWE-89")]))
check(both.get("findings_by_merge_rule", {}).get("exact-line") == 1
      and "range-containment" not in both.get("findings_by_merge_rule", {}),
      "same-line inside a range is EXACT-LINE, not containment",
      str(both.get("findings_by_merge_rule")))

# UNIT CONSISTENCY. Three counts, three units; a future change must not let
# them silently desynchronize. This is the invariant that would have caught
# "351 vs 427" being read as a shortfall.
for _lbl, _agg in [("range case", contained), ("exact case", ex),
                   ("no-range case", noranges), ("real fixtures",
                                                 audit.ingest_sarif([FF, CC]))]:
    _e = sum((_agg.get("cross_tool_edges_by_rule") or {}).values())
    _m = _agg.get("cross_tool_merged_findings", 0)
    _a = _agg.get("cross_tool_absorbed_records", 0)
    check(_e >= _m and _a >= _m,
          f"unit invariant holds ({_lbl}): edges>=merged, absorbed>=merged",
          f"edges={_e} merged={_m} absorbed={_a}")

# ── 14. Determinism and order-independence ──────────────────────────────────
a1 = audit.ingest_sarif([FF, CC])
a2 = audit.ingest_sarif([CC, FF])
strip = lambda a: [(r["score"], r["uri"], r["line"], r["ruleId"], r["n_tools"])
                   for r in a["ranked"]]
check(strip(a1) == strip(a2), "ranking is input-order independent")
check(strip(audit.ingest_sarif([FF, CC])) == strip(a1), "ranking is deterministic across runs")

# ── 0h: gated per-run size-correlation disclosure ────────────────────────────
# The gate exists because on real runs n_tools is overwhelmingly 1 (zlib
# {1: 601}, Struts all 1). A Spearman there is undefined or unstable, and a
# bare coefficient would hide that. These guard: concentrated -> NOT APPLICABLE,
# genuine spread + size correlation -> warns, uncorrelated -> silent, and the
# existing fixtures do not start warning.
print("\n0h size-correlation disclosure (gated):")


def _mkres(uri, line, rule="R1"):
    return {"ruleId": rule, "message": {"text": "x"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": uri},
                "region": {"startLine": line}}}]}


def _ranked(pairs):
    """pairs: list of (uri, line, [tools]) -> a minimal `ranked` shape."""
    return [{"uri": u, "line": ln, "tools": ts, "n_tools": len(ts),
             "level": "warning", "noisy_loc": False} for u, ln, ts in pairs]


def _sizes(pairs):
    """Real file lengths, injected. The check REFUSES to infer size from SARIF
    alone, so tests must supply measurements exactly as a real run reads them
    off disk."""
    return {u: ln for u, ln, _ in pairs}


# CASE 1 — concentrated n_tools (the real-world common case): NOT APPLICABLE.
conc = _ranked([(f"src/f{i}.c", 10 + i * 7, ["Flawfinder"]) for i in range(40)])
r1 = audit.size_correlation_disclosure(conc)
check(r1["applicable"] is False, "concentrated n_tools -> NOT APPLICABLE",
      r1.get("reason", "")[:60])
check("spearman_rho" not in r1, "no coefficient reported when not applicable")
check(r1.get("disclosure_only") is True, "declared disclosure-only (never filters)")

# CASE 2 — genuine spread AND size correlation: warns.
# big files get more tools, small files one — the confound the check is for.
corr = []
for i in range(40):
    big = i >= 25
    corr.append((f"src/g{i}.c", 400 + i * 20 if big else 5 + i,
                 ["Flawfinder", "Cppcheck", "Semgrep"] if big else ["Flawfinder"]))
r2 = audit.size_correlation_disclosure(_ranked(corr), _sizes(corr))
check(r2["applicable"] is True, "genuine spread -> check applies",
      f"n={r2.get('n_units')}, non-modal={r2.get('non_modal_units')}")
check(r2.get("size_correlated") is True, "size-correlated run WARNS",
      f"rho={r2.get('spearman_rho')}, p={r2.get('permutation_p')}")
check(r2.get("bootstrap_ci_95") is not None, "reports a bootstrap CI, not a bare point estimate")
check(r2.get("permutation_p") is not None, "reports a permutation p, not an asymptotic one")

# CASE 3 — genuine spread, NO size relationship: applies but stays silent.
# multi-tool files are interleaved across the size range.
unc = []
for i in range(40):
    multi = (i % 3 == 0)
    unc.append((f"src/h{i}.c", 20 + i * 13,
                ["Flawfinder", "Cppcheck"] if multi else ["Flawfinder"]))
r3 = audit.size_correlation_disclosure(_ranked(unc), _sizes(unc))
check(r3["applicable"] is True, "uncorrelated run: check still applies")
check(r3.get("size_correlated") is False, "uncorrelated run does NOT warn",
      f"rho={r3.get('spearman_rho')}, p={r3.get('permutation_p')}")

# CASE 4 — the gate boundary is the MEASURED one, not a round number.
_below = _ranked(
    [(f"src/i{i}.c", 500 + i * 10, ["Flawfinder", "Cppcheck"])
     for i in range(audit.MIN_NONMODAL_UNITS - 1)] +
    [(f"src/j{i}.c", 5 + i, ["Flawfinder"]) for i in range(40)])
r4 = audit.size_correlation_disclosure(_below, {r["uri"]: r["line"] for r in _below})
check(r4["applicable"] is False,
      f"just below m*={audit.MIN_NONMODAL_UNITS} non-modal -> NOT APPLICABLE")
_at = _ranked(
    [(f"src/i{i}.c", 500 + i * 10, ["Flawfinder", "Cppcheck"])
     for i in range(audit.MIN_NONMODAL_UNITS)] +
    [(f"src/j{i}.c", 5 + i, ["Flawfinder"]) for i in range(40)])
check(audit.size_correlation_disclosure(
          _at, {r["uri"]: r["line"] for r in _at})["applicable"] is True,
      f"at m*={audit.MIN_NONMODAL_UNITS} non-modal -> applies")

# CASE 5 — the CIRCULAR proxy is REFUSED, not merely labelled.
# Measured on real zlib: 2-tool files carry a median 16 findings vs 2 for
# 1-tool files, so max(startLine) rises with n_tools by sampling alone (median
# 58 -> 457). Using it would manufacture the correlation being tested for, in
# the positive direction. With no readable file sizes the answer must be
# NOT APPLICABLE, never an inferred coefficient.
r5 = audit.size_correlation_disclosure(_ranked(corr))     # no sizes supplied
check(r5["applicable"] is False,
      "no readable file sizes -> NOT APPLICABLE (refuses the circular proxy)")
check("manufacture" in (r5.get("reason") or ""),
      "refusal names the circularity as the reason")
check("spearman_rho" not in r5, "no coefficient inferred from SARIF alone")

# CASE 6 — the existing real fixtures must NOT start warning.
_agg = audit.ingest_sarif([FF, CC])
_sc = _agg.get("size_correlation")
check(_sc is not None, "size_correlation present in ingest output (JSON surface)")
check(not _sc.get("size_correlated"), "existing fixtures do not start warning",
      f"applicable={_sc.get('applicable')}")

# CASE 7 — determinism: same input, same interval.
check(audit.size_correlation_disclosure(_ranked(corr), _sizes(corr)) == r2,
      "disclosure is deterministic across runs (seeded bootstrap)")

# ── 0c(a): deterministic suffix linkage behind a cardinality-1 guard ─────────
# Record-linkage framing: basename is the BLOCKING KEY, "exactly one path per
# side" is the CARDINALITY-1 CONSTRAINT. Deterministic by choice — high
# precision, low recall — because a false merge inflates n_tools while a missed
# merge only costs a merge.
print("\n0c(a) cross-tool path suffix linkage (guarded):")


def _sfx(tool, uri, rule="CWE-89", line=7):
    return sarif(tool, [{"ruleId": rule, "message": {"text": "sql injection"},
                         "locations": [{"physicalLocation": {
                             "artifactLocation": {"uri": uri},
                             "region": {"startLine": line}}}]}])


def _ingest(a, b):
    d = tempfile.mkdtemp()
    pa, pb = os.path.join(d, "a.sarif"), os.path.join(d, "b.sarif")
    json.dump(a, open(pa, "w")); json.dump(b, open(pb, "w"))
    return audit.ingest_sarif([pa, pb])

# THE CASE THE FEATURE EXISTS FOR: package-relative vs scan-root-relative.
r = _ingest(_sfx("SpotBugs", "org/x/Foo.java"),
            _sfx("Semgrep", "proj/src/main/java/org/x/Foo.java"))
check(r["cross_tool_merged_findings"] == 1, "suffix-related paths now merge",
      f"merges={r['cross_tool_merged_findings']}")
check(r["suffix_linkage"]["merges_using_suffix_match"] == 1,
      "suffix-assisted merge is reported as its OWN layer, not folded in")
check(r["suffix_linkage"]["active"] is True, "linkage disclosed as active")

# THE GUARD: same basename, several paths per side -> AMBIGUOUS -> NO MERGE.
amb_a = sarif("SpotBugs", [
    {"ruleId": "CWE-89", "message": {"text": "sql"},
     "locations": [{"physicalLocation": {
         "artifactLocation": {"uri": "a/util/Config.java"},
         "region": {"startLine": 7}}}]},
    {"ruleId": "CWE-89", "message": {"text": "sql"},
     "locations": [{"physicalLocation": {
         "artifactLocation": {"uri": "b/util/Config.java"},
         "region": {"startLine": 7}}}]}])
amb_b = _sfx("Semgrep", "proj/src/main/java/util/Config.java")
ra = _ingest(amb_a, amb_b)
check(ra["cross_tool_merged_findings"] == 0,
      "two files sharing a basename in different directories do NOT merge",
      f"merges={ra['cross_tool_merged_findings']}")
check(ra["suffix_linkage"]["candidate_pairs_refused_ambiguous"] >= 1,
      "the ambiguous case is DISCLOSED, not silently dropped")
check(any("Config.java" in e for e in ra["suffix_linkage"]["ambiguous_examples"]),
      "the refused filename is named in the disclosure")

# SEGMENT ALIGNMENT: a suffix must align on separators, not on characters.
rs = _ingest(_sfx("SpotBugs", "x/MyFoo.java"),
             _sfx("Semgrep", "proj/src/Foo.java"))
check(rs["cross_tool_merged_findings"] == 0,
      "substring-but-not-segment-aligned paths do NOT merge (MyFoo vs Foo)")

# NON-REGRESSION: already-aligned paths are untouched and linkage stays off.
rq = _ingest(_sfx("SpotBugs", "org/x/Foo.java"), _sfx("Semgrep", "org/x/Foo.java"))
check(rq["cross_tool_merged_findings"] == 1, "identical paths still merge")
check(rq["suffix_linkage"]["active"] is False,
      "linkage stays INACTIVE when paths already agree")
_base = audit.ingest_sarif([FF, CC])
check((_base.get("suffix_linkage") or {}).get("active") is False,
      "existing fixtures do not activate suffix linkage")

# THE RECORDED COST: deterministic linkage is low-recall BY DESIGN.
check("LOW-RECALL" in _base["suffix_linkage"]["known_cost"],
      "the known cost (missed real matches) is stated in the output itself")

print()
if _fail:
    print(f"FAILED ({len(_fail)}): " + "; ".join(_fail))
    sys.exit(1)
print("all checks passed")
