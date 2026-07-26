#!/usr/bin/env python3
"""
audit.py — Layer 1 mechanical sweep for the GENESIS audit plug-in.

Runs ENTIRELY in the sandbox. Walks a project directory and extracts cheap,
high-signal facts WITHOUT the model reading the source — so a 40k-line project
costs the model ~nothing (it sees this inventory, not the code). This is the
lookup.py trick applied to codebases: breadth is paid in sandbox compute, not
context. The model then deep-reads (Layer 2) only what this flags as risky.

Language-agnostic: high-signal facts (tests exist/pass, secrets, TODOs, churn,
untested files, dependency staleness signals) are universal. A small command
table handles per-stack test/build invocation.

Output: JSON inventory + a risk-ranked file list. Presence, not truth — it
reports what is mechanically detectable; subtle logic/architecture bugs need
Layer 2's deep-read of the flagged slice.

Usage:
  python3 audit.py PROJECT_DIR [--json out.json] [--sarif out.sarif] [--run-tests]
  python3 audit.py --ingest a.sarif [b.sarif ...] [--json out.json] [--sarif out.sarif]
  DEFAULT = inspection only (walk/read/regex, ZERO code execution).
  --run-tests = ALSO execute the project's test command (runs author-chosen code; opt-in).
"""
import sys, os, re, json, subprocess, posixpath, urllib.parse

# Tool-quality weighting for the ingest consensus term (restricted-2b).
# Graceful degradation (charter F-EXT8): if the module is absent, fall back to
# the flat consensus baseline exactly — never stall, never fake it.
try:
    from tool_quality_weighting import resolve_weighting, weighted_consensus_term
    _QUALITY_WEIGHTING = True
except Exception:
    _QUALITY_WEIGHTING = False

SECRET = re.compile(r"(sk_live_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
# Only count a "secret" hit if it's NOT inside a regex literal or a scanner's pattern list.
# A live secret is a concrete value; a scanner/linter holds the PATTERN (brackets, quantifiers,
# re.compile, raw-string). This prevents flagging security tools for containing the patterns
# they hunt (the FieldLab false-positive: audit.py flagged a secret-scanner as a leak).
REGEX_CTX = re.compile(r"(re\.compile|r['\"]|\[0-9|\[A-Z|\{[0-9]|\\d|\\w|# ?(?:pattern|regex|api keys?:))", re.I)

def secret_hits(line):
    """Count live-secret hits, excluding pattern/regex context."""
    if REGEX_CTX.search(line):
        return 0  # this is a pattern definition, not a live secret
    # require a concrete instance: AKIA + 16 REAL alnum (not a bracketed class)
    return len([m for m in SECRET.finditer(line)
                if "[" not in m.group(0) and "{" not in m.group(0)])
TODO = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
RUN_TESTS = False  # test execution is OPT-IN (--run-tests); safe default = inspection only
CODE_EXT = {".py",".js",".ts",".jsx",".tsx",".mjs",".cjs",".go",".rs",".java",".rb",".c",".cpp",".h",".cs",".php"}

# --- Test-file identification (multi-convention) ---------------------------
# A file is a TEST if its name matches any common convention OR it lives under a
# recognized test directory. Covers: test_x.py / x_test.py (py, go), x.test.js /
# x.spec.ts (js/ts), and tests|test|__tests__|spec dirs (any stack).
TEST_NAME = re.compile(r"(^test_|_test$|_spec$|\.test$|\.spec$|^test$|^spec$)", re.I)
TEST_DIR = re.compile(r"(^|/)(tests?|__tests__|spec|specs)(/|$)", re.I)
# Sibling directory names that are test/benchmark harnesses but do not match the
# exact-word list above. Found 2026-07-26: zlib's contrib/testzlib/ is benchmark
# code, and BOTH cross-tool merges on that corpus landed there while the finding
# was scored as ordinary library code.
# DELIBERATELY DIRECTORY-ONLY (requires a trailing '/'): a *file* named
# testzlib.c is left to TEST_NAME, so widening here cannot start flagging
# production sources whose filename happens to start with "test".
# Calibrated against zlib's real tree — contrib/{blast,puff,minizip,untgz} are
# genuine utilities and must NOT match; only contrib/testzlib does.
TEST_DIR_PREFIX = re.compile(r"(^|/)(test[\w.-]*|bench|benchmarks?)/", re.I)
# --- Fixture / test-data exclusion ----------------------------------------
# Files under these dirs are INPUTS to tests, not application code and not tests.
# They must not inflate the "untested" count (the detect-secrets false-positive:
# test_data/*.py flagged as untested application code).
FIXTURE_DIR = re.compile(r"(^|/)(test_data|testdata|fixtures?|__mocks__|__fixtures__|mocks|test/data|tests/data|golden|snapshots?)(/|$)", re.I)
# --- Packaging / distribution artifacts -----------------------------------
# Files under packaging dirs (Homebrew formulae, debian/, rpm specs, etc.) are
# distribution metadata, not application code — they must not be counted as
# untested source (ripgrep: pkg/brew/ripgrep-bin.rb, a Homebrew formula, was
# miscounted as an untested .rb code file and dragged a stray "ruby" language
# into the root subtree).
PACKAGING_DIR = re.compile(r"(^|/)(pkg|packaging|debian|rpm|\.homebrew|homebrew|snap|flatpak|dist-packaging|contrib/packaging)(/|$)", re.I)
def is_packaging(rel):
    return bool(PACKAGING_DIR.search(rel))
# --- Reference-based coverage ---------------------------------------------
# A module is COVERED if any test file imports or names its stem. Catches
# integration-style suites (requests: tests/test_requests.py exercises sessions,
# models, auth by import, not by paired filename).
IMPORTish = re.compile(r"\b(import|from|require|use|include)\b", re.I)
# --- Subprocess / E2E test-style detection --------------------------------
# A suite that spawns the built app as a child process (CLI E2E) exercises code
# that neither import-reference nor paired-name matching can see. Real coverage
# tools (coverage.py patch=subprocess, tarpaulin --follow-exec, cypress plugin)
# solve this ONLY by execution-time instrumentation — it is not statically
# resolvable. So we don't try to resolve it; we DETECT the style and DOWNGRADE
# the confidence of coverage verdicts for the whole suite, rather than assert
# tested/untested the tool can't back up. (create-polyglot: execa-driven suite
# made both "tested" and "untested" flags unreliable in both directions.)
SUBPROC_TEST = re.compile(
    r"(execa|child_process|\bspawn\b|\bexecSync\b|\bexec\(|subprocess\.(run|Popen|call|check_output)"
    r"|Command::cargo_bin|assert_cmd|\bpexpect\b|\bsh\.|CliRunner|testscript|os/exec|exec\.Command"
    r"|std::process::Command|Command::new|process::Command)",  # Rust std-lib idiom (ripgrep gap)
    re.I)
# --- Inline / in-file tests -----------------------------------------------
# Some languages co-locate unit tests IN the source file (Rust `#[cfg(test)]`
# mod tests, `#[test]` fns; Python `if __name__ == "__main__"` self-tests /
# doctests; Go `func Example...`). The file-level "code XOR test" model can't see
# these, so a fully self-tested file reads as "untested" (ripgrep: 46% of
# untested flags were inline-tested false positives). Detect them by CONTENT.
INLINE_TEST = re.compile(
    r"(#\[cfg\(test\)\]|#\[test\]|#\[tokio::test\]"          # Rust
    r"|\bmod\s+tests?\b"                                       # Rust test module
    r"|>>>\s"                                                  # Python doctest
    r"|\bfunc\s+Example\w*\s*\("                               # Go example tests
    r"|\bfunc\s+Test\w*\s*\(\s*\w+\s+\*testing\.T)",           # Go in-file tests
    re.I)

STACK = {  # per-stack test command lookup — ORDER MATTERS: specific before generic
    "package.json": ("npm test", "js/ts"),
    "pyproject.toml": ("pytest", "python"),
    "requirements.txt": ("pytest", "python"),
    "setup.py": ("pytest", "python"),      # setuptools idiom (detect-secrets false-neg)
    "setup.cfg": ("pytest", "python"),
    "tox.ini": ("pytest", "python"),
    "go.mod": ("go test ./...", "go"),
    "Cargo.toml": ("cargo test", "rust"),
    "pom.xml": ("mvn test", "java"),
    "build.gradle": ("gradle test", "java"),
    "Gemfile": ("bundle exec rspec", "ruby"),
    "composer.json": ("phpunit", "php"),
}
# Extension -> language, so each file is graded against ITS OWN language (SARIF
# sourceLanguage model), not the repo's single detected stack.
EXT_LANG = {
    ".py": "python",
    ".js": "js/ts", ".jsx": "js/ts", ".ts": "js/ts", ".tsx": "js/ts", ".mjs": "js/ts", ".cjs": "js/ts",
    ".go": "go", ".rs": "rust",
    ".java": "java", ".rb": "ruby", ".php": "php",
    ".c": "c/cpp", ".cpp": "c/cpp", ".h": "c/cpp", ".cs": "c#",
}
def file_lang(rel):
    return EXT_LANG.get(os.path.splitext(rel)[1], "unknown")

def relposix(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")

def is_fixture(rel):
    return bool(FIXTURE_DIR.search(rel))

def is_test_file(rel):
    base = os.path.splitext(os.path.basename(rel))[0]
    return bool(TEST_NAME.search(base) or TEST_DIR.search(rel)
                or TEST_DIR_PREFIX.search(rel))

def find_markers(root, all_files):
    """Recursively locate every stack-marker file in the tree (not just root).
    Returns a list of (posix_dir, marker_name, language, test_cmd), where dir is
    the subtree the marker governs. This is presence detection (Renovate/
    Dependabot model): it reports WHERE markers are; boundary judgment is Layer 2's.
    """
    found = []
    for f in all_files:
        name = os.path.basename(f)
        if name in STACK:
            cmd, lang = STACK[name]
            d = relposix(os.path.dirname(f), root)  # "." for root
            found.append((d, name, lang, cmd))
    return found

def nearest_subtree(rel, marker_dirs):
    """Assign a file to the deepest marker dir that is an ancestor of it.
    marker_dirs: list of posix dirs (already sorted longest-first for us to pick
    the most specific). Returns the subtree dir, or None if no marker governs it.
    This is an INFERRED boundary (nearest-marker-wins) — tagged as inferred in
    output, confirmed by Layer 2, never asserted as structural truth."""
    parts = rel
    for d in marker_dirs:  # caller passes longest-first
        if d == ".":
            continue
        if parts == d or parts.startswith(d + "/"):
            return d
    return None

def walk(root):
    files = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in {".git","node_modules","venv",".venv","__pycache__","dist","build","target"}]
        for f in fn:
            files.append(os.path.join(dp, f))
    return files

def analyze(root):
    files = walk(root)
    code = [f for f in files
            if os.path.splitext(f)[1] in CODE_EXT
            and not is_packaging(relposix(f, root))]  # drop packaging metadata

    # Classify every code file: fixture / test / application-code.
    # PRECEDENCE: fixture is checked BEFORE test, because fixture dirs often live
    # under a test tree (test/fixtures/, __tests__/__fixtures__/) and would
    # otherwise be mis-classed as tests (verified: test/fixtures/*.js bug).
    rels = {f: relposix(f, root) for f in code}
    fixtures = [f for f in code if is_fixture(rels[f])]
    _fixset = set(fixtures)
    tests = [f for f in code if f not in _fixset and is_test_file(rels[f])]
    app_code = [f for f in code if f not in _fixset and f not in set(tests)]

    # Paired-name stems (both directions: test_x / x_test / x.test / x.spec).
    test_stems = set()
    for t in tests:
        b = os.path.splitext(os.path.basename(t))[0]
        b = re.sub(r"(^test[_.]|[_.]test$|[_.]spec$|^spec[_.])", "", b, flags=re.I)
        if b:
            test_stems.add(b.lower())

    # Reference-based coverage: collect the import/reference surface of all test
    # files ONCE (the extra read-pass). A module is covered if its stem appears
    # as an actual IMPORT TARGET in a test file — not merely as a word on a line
    # that happens to contain "import" (that over-credits common stems like
    # config/utils mentioned in comments; verified false-covered in regression).
    # SAME pass also detects subprocess/E2E test style (see SUBPROC_TEST).
    # Two-stage detection to handle SHARED HARNESSES: a suite often puts the
    # actual Command::spawn in ONE helper (e.g. tests/util.rs) that the other
    # test files pull in via `mod util` / `include!` / `use`. The spawn appears
    # in one file but the whole suite is subprocess-driven. Stage 1: find files
    # that spawn directly. Stage 2: credit files that reference a spawning
    # helper by its module stem. (ripgrep: 7 test files drive the binary through
    # tests/util.rs but only util.rs matched directly → confidence wrongly normal.)
    test_import_lines = []
    subproc_direct = []      # test files that spawn a child process directly
    test_txt = {}            # rels[t] -> text, for stage 2
    for t in tests:
        try:
            txt = open(t, errors="replace").read()
        except Exception:
            continue
        test_txt[rels[t]] = txt
        if SUBPROC_TEST.search(txt):
            subproc_direct.append(rels[t])
        for ln in txt.splitlines():
            if IMPORTish.search(ln):
                test_import_lines.append(ln)
    # Stage 2: harness fan-in. Stems of the directly-spawning test helpers.
    harness_stems = {os.path.splitext(os.path.basename(p))[0].lower() for p in subproc_direct}
    subproc_tests = list(subproc_direct)
    if harness_stems:
        harness_ref = re.compile(
            r"\b(?:mod|use|include!?|require|import|from)\b[^\n]*\b(" +
            "|".join(re.escape(s) for s in harness_stems) + r")\b", re.I)
        for rp, txt in test_txt.items():
            if rp not in subproc_tests and harness_ref.search(txt):
                subproc_tests.append(rp)  # transitively subprocess-driven
    # Coverage confidence is LOW when the suite is meaningfully subprocess-driven:
    # static matching can't see what a spawned CLI exercises (both false-tested
    # via name coincidence and false-untested via indirect exercise occur).
    subproc_ratio = len(subproc_tests) / max(1, len(tests))
    coverage_confidence = "low" if subproc_ratio >= 0.25 else "normal"

    def _imports_stem(stem):
        # stem must appear in import position across any test file's import lines.
        # Covers: `import stem`, `from stem import`, `from x import stem`,
        # `import x.stem`, `require('stem')`, `require("…/stem")`.
        pats = [
            r"\bimport\s+(?:[\w.]+\s*,\s*)*[\w.]*\b" + re.escape(stem) + r"\b",  # import ... stem
            r"\bfrom\s+[\w.]*\b" + re.escape(stem) + r"\b\s+import\b",           # from ...stem import
            r"\bfrom\s+[\w.]+\s+import\s+(?:[\w]+\s*,\s*)*" + re.escape(stem) + r"\b",  # from x import stem
            r"\brequire\(\s*['\"][^'\"]*\b" + re.escape(stem) + r"\b",           # require('…stem…')
            r"\b(?:import|from)\s+['\"][^'\"]*\b" + re.escape(stem) + r"\b",     # es6 import '…/stem'
        ]
        rx = re.compile("|".join(pats), re.I)
        return any(rx.search(ln) for ln in test_import_lines)

    def covered(f):
        stem = os.path.splitext(os.path.basename(rels[f]))[0].lower()
        if not stem or stem in ("__init__", "__main__"):
            return True  # package markers: not independently testable
        if stem in test_stems or any(stem in ts for ts in test_stems):
            return True  # paired-name match
        return _imports_stem(stem)  # reference-based (import-position only)

    # --- Recursive stack detection (SARIF run-level facts) ------------------
    # Find every marker anywhere in the tree, not just at root. This fixes the
    # monorepo 4-markers-present / 0-detected miss.
    markers = find_markers(root, files)
    marker_dirs_longest_first = sorted({m[0] for m in markers}, key=len, reverse=True)
    langs_present = sorted({m[2] for m in markers})
    # Root-governing marker (if any) drives the whole-repo test_command, for the
    # single-stack (non-monorepo) case. Prefer a marker at "." else the shallowest.
    root_marker = None
    for d, name, lang, cmd in sorted(markers, key=lambda m: len(m[0])):
        root_marker = (d, name, lang, cmd)
        if d == ".":
            break

    secrets, todos, untested, per_file = [], 0, [], []
    inline_tested = []  # files that test themselves in-file (Rust cfg(test), etc.)
    for f in code:
        try:
            txt = open(f, errors="replace").read()
        except Exception:
            continue
        loc = txt.count("\n") + 1
        s = sum(secret_hits(ln) for ln in txt.splitlines())
        t = len(TODO.findall(txt))
        todos += t
        rel = rels[f]
        is_test = f in tests
        is_fix = f in fixtures
        # A file with its own inline test block (Rust #[cfg(test)], Go Example/
        # Test funcs, Python doctests) is self-covered — the file-level model
        # otherwise can't see it and false-flags it "untested".
        has_inline = bool(INLINE_TEST.search(txt)) and not is_test
        if has_inline:
            inline_tested.append(rel)
        # fixtures and tests are never "untested application code"
        has_test = is_test or is_fix or has_inline or covered(f)
        if s: secrets.append((f, s))
        if not has_test: untested.append(f)
        # risk score: untested + secrets + todos + size, weighted.
        # fixtures get no untested penalty (they're inputs, not code-under-test).
        risk = (0 if has_test else 3) + s*5 + t + (1 if loc > 200 else 0)
        per_file.append({"file": rel, "loc": loc, "has_test": has_test,
                         "is_fixture": is_fix, "secrets": s, "todos": t, "risk": risk,
                         "inline_tested": has_inline,
                         # SARIF sourceLanguage: grade each file by its own language
                         "language": file_lang(rel),
                         # SARIF logical location: inferred subtree (nearest marker).
                         # None = governed by repo root / no marker. INFERRED, not truth.
                         "subtree": nearest_subtree(rel, marker_dirs_longest_first)})

    # --- Stack + test status (multi-marker aware) --------------------------
    # Presence of multiple markers is reported honestly, but "monorepo" is a
    # SUBSTANCE judgment, not a marker count: a lone package.json governing a
    # thin wrapper (e.g. a Tauri shell over a Python app) is a peripheral
    # component, not a co-equal subtree. We call it a monorepo only when >=2
    # subtrees each hold a meaningful share of the code (>=20% each; see below).
    # (Matches the web-validated "colocation != monorepo" caveat: report
    # presence; let substance + Layer 2 decide structure.)
    lang_counts = {}
    for p in per_file:
        lang_counts[p["language"]] = lang_counts.get(p["language"], 0) + 1
    total_code = max(1, len(per_file))
    # SUBSTANCE by PROPORTION: a real monorepo has multiple components each
    # holding a meaningful share. An absolute-count floor (e.g. ">=10 files")
    # wrongly promotes a 23-file frontend inside a 453-file Python app. Require
    # >=20% share to count a language as a co-equal subtree; below that it is a
    # peripheral component (thin wrapper, embedded UI, build tooling).
    substantial_langs = [L for L, n in lang_counts.items()
                         if L != "unknown" and n / total_code >= 0.20]
    is_monorepo = len(markers) >= 2 and len(substantial_langs) >= 2

    if not markers:
        stack, test_cmd = "unknown", None
    elif is_monorepo:
        stack = " + ".join(sorted(substantial_langs)) + f"  (monorepo: {len(markers)} markers, {len(set(m[0] for m in markers))} subtrees)"
        test_cmd = None  # no single repo-wide command; test per-subtree
    else:
        # single-stack (possibly with thin peripheral components): use the
        # dominant language's root marker for the repo-wide command, and note
        # any minor markers as peripheral rather than co-equal subtrees.
        _dom = max(lang_counts, key=lambda L: (L != "unknown", lang_counts[L]))
        _cmd = next((cmd for d, name, lang, cmd in markers if lang == _dom), None)
        _peris = sorted({m[2] for m in markers} - {_dom} - {"unknown"})
        stack = _dom + (f"  (+ peripheral: {', '.join(_peris)})" if _peris else "")
        test_cmd = _cmd

    test_status = "not-run (use --run-tests to execute; SAFE DEFAULT is no execution)"
    if RUN_TESTS and markers:
        # SECURITY: executing a test command runs project-author-chosen code
        # (package.json scripts, conftest.py import-time code, build scripts).
        # Only with explicit --run-tests. shell=False + arg list, no shell injection.
        # In a monorepo we run EACH subtree's command in its own cwd.
        results = []
        run_targets = ([(root, test_cmd)] if not is_monorepo and test_cmd
                       else [(os.path.join(root, d) if d != "." else root, cmd)
                             for d, _, _, cmd in markers])
        for cwd, cmd in run_targets:
            try:
                r = subprocess.run(cmd.split(), cwd=cwd, capture_output=True,
                                   timeout=60, text=True)
                results.append(f"{relposix(cwd, root)}:{'PASS' if r.returncode==0 else f'FAIL(rc={r.returncode})'}")
            except FileNotFoundError:
                results.append(f"{relposix(cwd, root)}:not-run(runner '{cmd.split()[0]}' absent)")
            except subprocess.TimeoutExpired:
                results.append(f"{relposix(cwd, root)}:timeout")
            except Exception as e:
                results.append(f"{relposix(cwd, root)}:error:{e}")
        test_status = " | ".join(results)

    per_file.sort(key=lambda x: -x["risk"])
    # Per-subtree rollup (SARIF logical-location grouping) — INFERRED boundaries.
    subtrees = {}
    for p in per_file:
        key = p["subtree"] or "(root/none)"
        st = subtrees.setdefault(key, {"languages": set(), "code": 0, "untested": 0})
        st["languages"].add(p["language"])
        if not (p["is_fixture"] or p["has_test"] is True and p["file"] in {rels[t] for t in tests}):
            st["code"] += 1
        if p["file"] in [rels[f] for f in untested]:
            st["untested"] += 1
    subtree_report = {k: {"languages": sorted(v["languages"]),
                          "files": v["code"], "untested": v["untested"]}
                      for k, v in sorted(subtrees.items())}

    return {
        "root": root, "stack": stack, "test_command": test_cmd, "test_status": test_status,
        "is_monorepo": is_monorepo,
        "languages_present": langs_present,
        "coverage_confidence": coverage_confidence,
        "subprocess_driven_tests": subproc_tests,
        "inline_tested_files": inline_tested,
        "markers": [{"dir": d, "marker": name, "language": lang} for d, name, lang, _ in markers],
        "subtrees_inferred": subtree_report,
        "counts": {"code_files": len(code), "test_files": len(tests),
                   "fixture_files": len(fixtures),
                   "untested_files": len(untested), "total_secrets": sum(s for _,s in secrets),
                   "total_todos": todos, "total_loc": sum(p["loc"] for p in per_file)},
        "secrets_found": [rels[f] for f,_ in secrets],
        "untested_files": [rels[f] for f in untested],
        "risk_ranked": per_file,
    }

def to_sarif(inv, tool_version="5.1"):
    """Emit SARIF 2.1.0 at the spec's 'minimal recommended with source
    information' tier — the subset GitHub code scanning and VS Code actually
    consume. Design choices are externally grounded (OASIS 2.1.0 + GitHub docs):
      - stable ruleId per finding class (fingerprint stability across runs)
      - relative artifactLocation.uri, no leading '/', no '..' (errata #480/#460)
      - region always carries startLine (errata #462: region SHALL have a start)
      - our triage edge (risk rank, confidence, provenance) rides in the result
        `properties` bag — the spec's sanctioned extension point — so consumers
        that don't understand it ignore it, and ours can use it.
    This is a REPORTING format for findings the scanner already made; it invents
    no new analysis and asserts nothing the inventory didn't already say.
    """
    # Rule catalog: one stable rule per finding class the scanner produces.
    RULES = {
        "untested": ("No test relationship detected",
                     "No inline, paired-name, or import-reference test was found for this file. "
                     "A Layer-2 triage signal (presence, not truth) — not a verdict that the code is unexercised.",
                     "warning"),
        "secret": ("Possible secret in source",
                   "A line matched a secret-like pattern. Verify whether this is a real credential or a "
                   "planted test/fixture value before acting.",
                   "error"),
        "todo": ("TODO/FIXME marker",
                 "A TODO/FIXME/HACK/XXX marker is present. Informational; indicates known-incomplete work.",
                 "note"),
        "coverage-confidence": ("Low coverage confidence (subprocess/E2E suite)",
                 "The test suite drives the app as a subprocess, so static coverage matching is unreliable "
                 "in both directions. Coverage flags in this run are indicative, not verdicts.",
                 "note"),
    }
    def clean_uri(rel):
        # relative, forward-slash, no leading slash, no ".." (SARIF errata #480/#460)
        u = rel.replace(os.sep, "/").lstrip("/")
        return u
    rules, rule_index = [], {}
    for rid, (name, desc, level) in RULES.items():
        rule_index[rid] = len(rules)
        rules.append({
            "id": rid,
            "name": name,
            "shortDescription": {"text": name},
            "fullDescription": {"text": desc},
            "defaultConfiguration": {"level": level},
        })
    results = []
    def add(rid, rel, line, msg, props):
        r = {
            "ruleId": rid,
            "ruleIndex": rule_index[rid],
            "level": RULES[rid][2],
            "message": {"text": msg},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": clean_uri(rel)},
                    "region": {"startLine": max(1, line)},  # region SHALL have a start
                }
            }],
            # Stable dedup key: ruleId + path (consistent across runs → stable alert).
            "partialFingerprints": {"auditPluginV1": f"{rid}:{clean_uri(rel)}"},
            "properties": props,
        }
        results.append(r)
    # Map inventory findings → results. Deterministic order (sorted) so run-to-run
    # diffs are clean (SARIF Appendix F: deterministic output).
    byfile = {p["file"]: p for p in inv["risk_ranked"]}
    for rel in sorted(byfile):
        p = byfile[rel]
        base_props = {"riskRank": p["risk"], "language": p["language"],
                      "subtree": p.get("subtree") or "(root)",
                      "coverageConfidence": inv.get("coverage_confidence", "normal")}
        if not p["has_test"] and not p["is_fixture"]:
            add("untested", rel, 1,
                f"No test relationship detected for {rel} (risk rank {p['risk']}). "
                f"Layer-2 triage signal, not a verdict.", dict(base_props))
        if p["secrets"]:
            props = dict(base_props); props["secretHits"] = p["secrets"]
            props["inFixtureDir"] = p.get("is_fixture", False)
            add("secret", rel, 1,
                f"{p['secrets']} secret-like pattern(s) in {rel}. Verify real vs. planted before acting.",
                props)
        if p["todos"]:
            props = dict(base_props); props["todoCount"] = p["todos"]
            add("todo", rel, 1, f"{p['todos']} TODO/FIXME marker(s) in {rel}.", props)
    # One run-level coverage-confidence result (not file-specific) when low.
    if inv.get("coverage_confidence") == "low":
        subs = inv.get("subprocess_driven_tests", [])
        anchor = sorted(subs)[0] if subs else sorted(byfile)[0] if byfile else "."
        add("coverage-confidence", anchor, 1,
            f"{len(subs)} test file(s) drive the app as a subprocess; coverage flags are indicative, not verdicts.",
            {"subprocessDrivenTests": len(subs)})
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "GENESIS-audit",
                "version": tool_version,
                "informationUri": "https://example.invalid/genesis-audit",
                "rules": rules,
            }},
            "results": results,
            "columnKind": "unicodeCodePoints",
        }],
    }

def _norm_uri(u):
    """Normalize a SARIF artifact URI for CROSS-TOOL comparison.

    Different scanners emit the same file differently: 'src/x.c', './src/x.c',
    'a/../src/x.c', 'src//x.c', 'file:///abs/src/x.c', backslashes on Windows.
    The old implementation only handled backslashes and a leading '/', so
    './src/x.c' and 'src/x.c' were DIFFERENT keys — a silent cross-tool
    merge-blocker. Cross-tool matching needs real path normalization.

    Deliberately NOT resolved against the filesystem: ingest must work on SARIF
    produced elsewhere (CI, another machine), where the paths may not exist
    locally. This is pure lexical normalization.
    """
    if not isinstance(u, str) or not u:
        return ""
    s = u.replace("\\", "/")
    if s.lower().startswith("file://"):          # file:///abs/path -> /abs/path
        s = s[7:]
        if len(s) > 2 and s[0] == "/" and s[2] == ":":   # file:///C:/x -> C:/x
            s = s[1:]
    try:
        s = urllib.parse.unquote(s)              # %20 -> space
    except Exception:
        pass
    s = posixpath.normpath(s)                    # collapses ./ , // , and a/../b
    # normpath leaves leading '../' alone (correct — can't resolve above root).
    s = s.lstrip("/")
    if s in (".", ""):
        return ""
    return s

# ── CWE class map (cross-tool consensus) ────────────────────────────────────
# A CWE-class match is what lets two DIFFERENT tools agree on the same finding
# when their ruleIds disagree. Coverage of this map therefore sets the ceiling
# on how often the cross-tool key can match at all.
#
# ASYMMETRIC ERROR COST — the reason this map is extended conservatively:
# a FALSE merge inflates n_tools, the signal every published number rests on
# (ROC-AUC 0.755 et al). A MISSED merge only costs recall. These are not
# symmetric, so an unmapped CWE (-> no merge) is the safe default and mapping
# is the change that needs justification.
_CWE_CLASS = {
    # buffer
    119: "buf", 120: "buf", 121: "buf", 122: "buf", 125: "buf", 126: "buf",
    127: "buf", 787: "buf", 788: "buf", 805: "buf",
    131: "buf",   # added: incorrect calculation of buffer size
    786: "buf",   # added: access of memory location before start of buffer
    # null deref
    476: "null",
    # use-after-free / free-correctness
    415: "uaf", 416: "uaf", 825: "uaf",
    590: "uaf",   # added: free of memory not on the heap
    762: "uaf",   # added: mismatched memory management routines
    # uninitialized
    457: "uninit", 456: "uninit", 824: "uninit", 908: "uninit", 665: "uninit",
    # resource leak
    401: "leak", 404: "leak", 772: "leak", 775: "leak",
    771: "leak",  # added: missing reference to active allocated resource
    # format string
    134: "fmt",
    # integer
    190: "int", 191: "int", 369: "int",
    128: "int",   # added: wrap-around error
    195: "int",   # added: signed-to-unsigned conversion error
    197: "int",   # added: numeric truncation error

    # ── Java / web classes (added 2026-07-26; see docs/SPEC_java_admission.md) ──
    # Every entry below is an EFFECT category naming ONE sink, so its consequence
    # set is class-coherent. That is the criterion (VALIDATION.md, "Map/deny
    # criterion"), NOT CWE abstraction level — CWE-676 is Base and mapping-Allowed
    # yet spans buf/fmt/cmdi, while CWE-119 is Class and mapping-Discouraged yet
    # is coherent. Effect vs mechanism, not general vs specific.
    89: "sqli", 564: "sqli",              # SQL injection (564 = Hibernate variant)
    78: "cmdi",                            # OS command injection
    79: "xss", 80: "xss", 83: "xss",       # cross-site scripting (+ variants)
    22: "path", 23: "path", 36: "path",    # path traversal (+ variants)
    502: "deser",                          # deserialization of untrusted data
    611: "xxe",                            # XML external entity
    918: "ssrf",                           # server-side request forgery
    90: "ldapi",                           # LDAP injection
    643: "xpathi",                         # XPath injection
    352: "csrf",                           # cross-site request forgery
    601: "redirect",                       # open redirect
    327: "crypto", 326: "crypto",          # broken/weak cryptographic algorithm
    328: "hash",                           # weak hash — kept SEPARATE from crypto:
    #   the OWASP Benchmark analysis treated crypto and hash as distinct
    #   categories and both were perfect discriminators (100% TPR / 0% FPR).
    #   Merging them would be the only unforced widening here, so it is not done.
    798: "creds", 259: "creds",            # hardcoded credentials / password
    330: "random", 338: "random",          # weak / cryptographically-poor PRNG
}
# Junk-drawer / too-generic CWEs. Matching on these would merge unrelated
# findings that happen to share a vague parent category.
_CWE_DENY = {
    398, 561, 563, 570, 571, 682, 704,
    664,  # improper control of a resource through its lifetime (20 checks)
    758,  # reliance on undefined/unspecified behaviour (20 checks)
    # Java/web MECHANISM and parent categories. Same trap as CWE-676: they
    # collect weaknesses that share a CAUSE but differ in CONSEQUENCE, and
    # consequence is what these classes encode. CWE-74 is the direct analogue —
    # it is the parent of 77/78/79/89/90/643, so it spans sqli, cmdi, xss,
    # ldapi and xpathi at once. Mapping it would merge them all.
    20,   # improper input validation (Class — spans essentially everything)
    74,   # injection, generic (spans sqli/cmdi/xss/ldapi/xpathi)
    77,   # command injection, generic parent of 78
    93, 116,  # CRLF / improper encoding-or-escaping, generic
    200,  # exposure of sensitive information (Class — very broad)
    693, 707, 710,  # Pillars
    676,  # use of a potentially dangerous function — the original instance:
    #     strcpy->buf, scanf->fmt, system->cmdi. Confirmed on real semgrep
    #     output (31 of 33 zlib findings were CWE-676).
}
# DELIBERATELY LEFT UNMAPPED (no merge) pending frequency evidence — each would
# need its own class, and a class with one member can never produce a merge:
#   252 unchecked return value · 467 sizeof on pointer · 362 race condition
#   833 deadlock · 686 wrong argument type
# Adding a class is only useful once >=2 tools are observed emitting it.
# Measure first: docs/SPEC_item4_groupability_measurement.md.

_CWE_RE = re.compile(r"cwe[-_/:=\"'\s]{0,4}(\d+)", re.I)

def _class_from_cwes(cwes):
    """Resolve a class from an explicit list of CWE numbers (SARIF taxa).
    Same conservative rule as the text path: >1 distinct class -> None."""
    found = []
    for n in cwes:
        if n in _CWE_DENY:
            continue
        c = _CWE_CLASS.get(n)
        if c and c not in found:
            found.append(c)
    return found[0] if len(found) == 1 else None

def _cwe_class_of(rule_id, message, uri=""):
    """Resolve a coarse vulnerability class from CWE numbers appearing in the
    ruleId / message / uri (or rule metadata, when the caller passes it).

    Returns None when nothing maps, AND when the text implies MORE THAN ONE
    class. None never merges, which is the conservative default this pipeline
    applies to every other uncertainty (unresolvable class, denied CWE, unknown
    lineage, degenerate fingerprint, inexact line).

    WHY NOT FIRST-MATCH-WINS (the previous behaviour): text order carries no
    semantic meaning, so the first mapped CWE in a blob is an arbitrary winner.
    Measured on real SpotBugs+FindSecBugs output, that mis-classified 122
    findings in two DIFFERENT ways:

      * GENUINE AMBIGUITY — INFORMATION_EXPOSURE_THROUGH_AN_ERROR_MESSAGE lists
        CWE-22, 89, 209, 211. It is a rule about error-message exposure; 22 and
        89 are incidental prose. First-match returned `path`. None is the RIGHT
        answer here.
      * SPECIFICITY, NOT AMBIGUITY — WEAK_MESSAGE_DIGEST_MD5/_SHA1 list CWE-327
        and CWE-328. Both tags are CORRECT; 328 (weak hash) is a child of 327
        (broken crypto) and is the more precise one. First-match returned
        `crypto`, shadowing `hash`. None is the SAFE answer here, not the right
        one — resolving it properly needs hierarchy awareness (see
        HANDOFF item 3e).

    Collapsing both to None is deliberate: it is correct for the first and
    merely lossy for the second, and a lossy miss costs recall while a wrong
    class can cause a FALSE MERGE, which inflates n_tools.
    """
    found = []
    for m in _CWE_RE.finditer(f"{rule_id} {message} {uri}"):
        try:
            n = int(m.group(1))
        except (TypeError, ValueError):
            continue
        if n in _CWE_DENY:
            continue
        cls = _CWE_CLASS.get(n)
        if cls and cls not in found:
            found.append(cls)
    return found[0] if len(found) == 1 else None

# ── ENGINE LINEAGE (diversity-aware consensus must be ENGINE-aware) ─────────
# Consensus counts agreement across DIFFERENT tools. "Different" must mean a
# different ANALYSIS ENGINE, not a different product name. Several widely-used
# tools are forks, plugins, or re-exporters of another tool: counting them
# separately turns SELF-agreement into apparent consensus and INFLATES n_tools —
# the one error direction the asymmetric-cost rule forbids, since n_tools is the
# signal every published number rests on.
#
# Lineage facts are [fetched] (docs/SPEC_java_admission.md §2):
#   - SpotBugs IS FindBugs: a fork, source still under edu/umd/cs/findbugs/.
#   - Find Security Bugs is a SpotBugs PLUGIN, not a separate analyzer.
#   - SonarQube can IMPORT SpotBugs/FindBugs/FindSecBugs/PMD/Checkstyle reports
#     (sonar.java.*.reportPaths), so its independence depends on DEPLOYMENT
#     CONFIGURATION and cannot be certified from SARIF. Handled by disclosure
#     below, not by silently assuming independence.
#
# UNKNOWN TOOLS DEFAULT TO THEIR OWN NAME, so anything not listed here behaves
# exactly as before this registry existed. Nothing regresses.
_TOOL_LINEAGE = {
    "spotbugs": "findbugs",
    "findbugs": "findbugs",
    "find security bugs": "findbugs",
    "findsecbugs": "findbugs",
    "cppcheck": "cppcheck",
    "flawfinder": "flawfinder",
    "semgrep": "semgrep",
    "semgrep oss": "semgrep",
    "semgrep ce": "semgrep",
    "codeql": "codeql",
    "pmd": "pmd",
    "checkstyle": "checkstyle",
    "error prone": "errorprone",
    "errorprone": "errorprone",
    "sonarqube": "sonarqube",
    "sonarjava": "sonarqube",
    "sonarcloud": "sonarqube",
}
# Lineages a SonarQube deployment may be RE-EMITTING rather than independently
# finding (sonar.java.*.reportPaths). Co-occurrence is never silently trusted.
_SONAR_IMPORTABLE = {"findbugs", "pmd", "checkstyle"}

# ── Ambiguous-independence policy (decision 0a, 2026-07-26) ─────────────────
# When SonarQube co-occurs with a tool it can IMPORT, we cannot tell from SARIF
# whether it analysed independently or re-emitted that tool's findings. The
# DEFAULT IS CONSERVATIVE: such a pair does not count as consensus.
#
# WHY conservative rather than disclose-and-count: everywhere else in this
# codebase uncertainty resolves to NO-MERGE — unresolvable CWE class, denied
# CWE, unknown lineage, degenerate fingerprint, inexact line. Counting here
# would be the only place uncertainty resolved to merge-with-a-note, and the
# asymmetric-cost rule (a false merge inflates n_tools, which every published
# number rests on; a missed merge only costs recall) does not get an exception
# because the ambiguous case happens to be uncommon.
#
# KNOWN COST, accepted: SonarJava analysing independently IS SonarQube's default
# configuration and report-importing is OPT-IN, so this under-counts the COMMON
# case. The escape hatch is what makes that acceptable — the operator who
# configured the import is exactly the person able to declare the relationship,
# so the cost falls on the party holding the knowledge to remove it.
#
# ESCAPE HATCH: declare independence explicitly.
#   AUDIT_INDEPENDENT_TOOLS="SonarQube"            (comma-separated driver names)
# Declaring a tool asserts it analysed independently of everything else in the
# ingest. It is the operator's assertion, and it is DISCLOSED in the output so
# the assertion travels with the result rather than silently changing it.
def _declared_independent():
    raw = os.environ.get("AUDIT_INDEPENDENT_TOOLS", "")
    return {t.strip().lower() for t in raw.split(",") if t.strip()}

def _suppressed_pairs(tools, declared):
    """(lineage_a, lineage_b) pairs whose agreement must NOT count as consensus.

    Currently only the SonarQube-import ambiguity. Returned as a set of frozen
    pairs so the merge guard can consult it cheaply.
    """
    lin = {t: _lineage_of(t) for t in tools}
    present = set(lin.values())
    pairs = set()
    if "sonarqube" in present:
        sonar_drivers = [t for t, l in lin.items() if l == "sonarqube"]
        if not all(d.strip().lower() in declared for d in sonar_drivers):
            for other in (_SONAR_IMPORTABLE & present):
                pairs.add(frozenset(("sonarqube", other)))
    return pairs

def _lineage_of(tool):
    """Analysis-engine lineage for a SARIF driver name. Unknown -> its own name."""
    t = (tool or "").strip().lower()
    if t in _TOOL_LINEAGE:
        return _TOOL_LINEAGE[t]
    # Tolerate version/edition suffixes ("Semgrep OSS 1.2", "CodeQL CLI").
    for known, lineage in sorted(_TOOL_LINEAGE.items(), key=lambda kv: -len(kv[0])):
        if t.startswith(known):
            return lineage
    return t or "unknown-tool"

def _lineage_warnings(tools, declared=frozenset()):
    """Independence caveats we can detect from the driver names alone."""
    out = []
    lin = {t: _lineage_of(t) for t in tools}
    # Two drivers, one engine: now prevented from inflating n_tools, but the
    # operator should know their "two tools" are one.
    byl = {}
    for t, l in lin.items():
        byl.setdefault(l, []).append(t)
    for l, ts in sorted(byl.items()):
        if len(ts) > 1:
            out.append(f"{', '.join(sorted(ts))} share one analysis engine "
                       f"({l}); counted ONCE for consensus, not {len(ts)} times.")
    # SonarQube may be re-emitting a co-present tool's findings.
    if "sonarqube" in byl:
        overlap = sorted(_SONAR_IMPORTABLE & set(byl))
        sonar_drivers = byl["sonarqube"]
        if overlap and all(d.strip().lower() in declared for d in sonar_drivers):
            out.append(
                "SonarQube agreement with " + ", ".join(overlap) + " IS being counted "
                "as consensus because independence was DECLARED by the operator "
                "(AUDIT_INDEPENDENT_TOOLS). This is an operator assertion, not "
                "something the tool verified — SARIF cannot show whether SonarQube "
                "analysed independently or re-emitted an imported report.")
        elif overlap:
            out.append(
                "SonarQube is present alongside " + ", ".join(overlap) +
                ". SonarQube can IMPORT those tools' reports (sonar.java.*.reportPaths), "
                "so its findings may not be independent. Independence cannot be "
                "determined from SARIF, so agreement between them is NOT counted as "
                "consensus. If this deployment analyses independently, declare it: "
                "AUDIT_INDEPENDENT_TOOLS=\"" + ",".join(sorted(sonar_drivers)) + "\"")
    return out

def _path_root_mismatch(tool_paths):
    """Detect tools that report the SAME files relative to DIFFERENT roots.

    SpotBugs derives paths from bytecode and emits package-relative
    (`org/owasp/benchmark/X.java`); source-level tools emit scan-root-relative
    (`.../src/main/java/org/owasp/benchmark/X.java`). One is a SUFFIX of the
    other, so the paths never compare equal and cross-tool merging silently
    yields ZERO with no diagnostic — the same silent-degradation class as the
    fingerprint defects.

    `_norm_uri` cannot fix this: it is lexical normalization, and a suffix
    relationship is not a malformed path. This function does NOT attempt to
    reconcile them either — deliberately. Suffix matching can falsely unify
    same-named files in different modules (`a/util/Config.java` vs
    `b/util/Config.java`), which is a FALSE MERGE, the error direction the
    asymmetric-cost rule forbids. Detect and disclose; do not silently guess.

    `tool_paths` maps tool name -> set of normalized uris.
    Returns a list of warning strings.
    """
    out = []
    tools = sorted(t for t, p in tool_paths.items() if p)
    for i in range(len(tools)):
        for j in range(i + 1, len(tools)):
            a, b = tools[i], tools[j]
            pa, pb = tool_paths[a], tool_paths[b]
            if pa & pb:
                continue                      # they already agree somewhere
            base_a = {p.rsplit("/", 1)[-1] for p in pa}
            base_b = {p.rsplit("/", 1)[-1] for p in pb}
            shared = base_a & base_b
            if not shared:
                continue                      # genuinely different files
            # Same filenames, zero identical paths -> different roots.
            suffix = any(x.endswith("/" + y) or y.endswith("/" + x)
                         for x in list(pa)[:400] for y in list(pb)[:400])
            out.append(
                f"{a} and {b} report the SAME {len(shared)} filename(s) but ZERO "
                f"identical paths"
                + (" (one tool's paths are a SUFFIX of the other's)" if suffix else "")
                + f". They are reporting paths relative to DIFFERENT ROOTS, so "
                f"cross-tool merging between them CANNOT MATCH and any consensus "
                f"count involving this pair will be ZERO for that reason alone — "
                f"NOT because the tools disagree. Common cause: a bytecode-based "
                f"analyzer (e.g. SpotBugs) emits package-relative paths while a "
                f"source-based one emits scan-root-relative paths. FIX: run the "
                f"source-based tool from the directory that makes its paths match "
                f"(e.g. `src/main/java`), or post-process one tool's SARIF.")
    return out

def _fingerprint_value(res):
    """The tool's own stable identity for a result, or None."""
    for field in ("partialFingerprints", "fingerprints"):
        d = res.get(field) or {}
        if d:
            return sorted(f"{k}={v}" for k, v in d.items())[0]
    return None

def _degenerate_fingerprints(items):
    """Fingerprints that are NOT identities and must not be used as dedup keys.

    A fingerprint is supposed to identify ONE finding. Some tools emit a
    constant placeholder instead: semgrep OSS, run unauthenticated, sets
    `"matchBasedId/v1": "requires login"` on EVERY result. Trusting that as an
    identity collapses every finding from that tool into one — on real zlib it
    destroyed 32 of 33 findings silently.

    Detected from the data rather than by pattern-matching known strings: if one
    (tool, fingerprint) pair appears at more than one distinct location, it is
    not identifying anything and we fall back to the location key. Deterministic
    — depends only on input content.

    `items` is an iterable of (tool, fingerprint_value, uri, line).
    """
    seen = {}
    for tool, fpv, uri, line in items:
        if fpv is None:
            continue
        seen.setdefault((tool, fpv), set()).add((uri, line))
    return {k for k, locs in seen.items() if len(locs) > 1}

def _result_key(res, tool=None, degenerate=frozenset()):
    """SAME-TOOL dedup key. Prefers the tool's own fingerprint — that is exactly
    what fingerprints are for, and within one tool it is the most reliable
    identity available. Falls back to ruleId + normalized location.

    NOT a cross-tool key. See _cross_keys(): a fingerprint is tool-private, so
    using it to decide cross-tool agreement makes agreement impossible between
    any tool that emits fingerprints and any tool that does not. That was the
    structural defect recorded in docs/SCOPE_shipped_consensus_defect.md — real
    flawfinder emits fingerprints on every result and cppcheck emits none, so
    n_tools could never exceed 1 in the shipped action. DefectDojo, which this
    model cites, uses TWO algorithms precisely to avoid that.
    """
    fpv = _fingerprint_value(res)
    if fpv is not None and (tool, fpv) not in degenerate:
        return "fp:" + fpv
    rid = res.get("ruleId", "?")
    loc = (((res.get("locations") or [{}])[0].get("physicalLocation") or {}))
    uri = _norm_uri((loc.get("artifactLocation") or {}).get("uri", ""))
    line = (loc.get("region") or {}).get("startLine", "")
    return f"rk:{rid}|{uri}|{line}"

def _cross_keys(rec):
    """CROSS-TOOL consensus keys for a same-tool-deduped record. Two records from
    DIFFERENT tools that share any of these keys describe the same finding.

    Never derived from a tool's own fingerprint (see _result_key).

    Two independent grounds for agreement, both requiring identical normalized
    location:
      cls| — same CWE class. The DefectDojo cross-tool algorithm, and the case
             the fix exists for: different tools name the same bug differently
             (flawfinder 'FF1001', cppcheck 'CWE-120') but agree on the class.
      rid| — literally the same ruleId. Preserves the pre-fix behaviour for
             fingerprint-free tool pairs, so this change cannot REGRESS a merge
             that already worked.

    Line is matched EXACTLY, not within a tolerance. Conservative on purpose:
    a tolerance window makes merging depend on which findings are compared
    first, and a false merge inflates n_tools. Near-miss line offsets remain the
    display layer's job (audit_dedup_display.py, TOL=3), where the consequence
    is a cosmetic grouping rather than a corrupted signal.
    """
    uri, line = rec["uri"], rec["line"]
    keys = [f"rid|{uri}|{line}|{rec['ruleId']}"]
    # RULE METADATA IS PART OF THE SEARCH SPACE. Several tools put their CWE
    # mapping ONLY in the driver's rule definitions, never in the result:
    # semgrep uses rule.properties.tags (["CWE-415: Double Free", ...]) and
    # emits no CWE in the result at all. Scanning result-only text resolved
    # 0 of 33 semgrep findings on real code — a false negative produced by our
    # parser, not by the tools disagreeing. ingest_sarif already collects this
    # as rec["rulemeta"]; it just was not being consulted.
    # Structured CWE taxa first (authoritative); prose only as fallback.
    cls = _class_from_cwes(rec.get("taxa_cwes") or []) \
        or _cwe_class_of(rec["ruleId"], rec["message"], uri) \
        or _cwe_class_of(rec["ruleId"], rec.get("rulemeta") or "", "")
    if cls:
        keys.append(f"cls|{uri}|{line}|{cls}")
    rec["cwe_class"] = cls
    return keys

def ingest_sarif(paths):
    """DETERMINISTIC backbone (no LLM, no network). Parse >=1 SARIF files from any
    producer, normalize, dedup by fingerprint/location, and rank by the four
    signals the empirical literature validated (FAULTBENCH/CASTLE/ensemble
    studies): (1) LOCATION noise-proneness, (2) PERSISTENCE across tools/runs,
    (3) DIVERSITY-AWARE CONSENSUS (agreement counts only across DIFFERENT tools;
    redundant same-tool overlap does not inflate it), (4) rule KIND prior.
    Ranks REVIEW-WORTHINESS (worth a human's first look), NOT exploitability
    (which needs external threat feeds we deliberately don't fake).
    Output is reproducible: identical inputs -> byte-identical ranking."""
    SEV = {"error": 3, "warning": 2, "note": 1, "none": 0}
    docs = []
    for p in paths:
        try:
            raw = open(p, errors="replace").read()
            if not raw.strip():
                # Empty or whitespace-only file: a scanner that found nothing may
                # still emit an empty file. This is NOT a malformed-input error;
                # treat it as an empty result set so it doesn't raise a false alarm.
                docs.append((p, {"_empty": True}))
                continue
            docs.append((p, json.loads(raw)))
        except Exception as e:
            docs.append((p, {"_parse_error": str(e)}))

    # Collect every result, tagged with which tool/run produced it.
    findings = {}   # dedup_key -> aggregate record
    tools_seen = set()
    parse_errors = []
    empty_inputs = []
    # PRE-SCAN: find fingerprints that are not identities (constant placeholders
    # emitted on every result). Must happen before keying — see
    # _degenerate_fingerprints for why trusting them destroys findings.
    _fp_scan = []
    for _p, _d in docs:
        if "_empty" in _d or "_parse_error" in _d:
            continue
        for _run in (_d.get("runs") or []):
            _tool = (((_run.get("tool") or {}).get("driver") or {})).get("name", "unknown-tool")
            for _res in (_run.get("results") or []):
                _loc = (((_res.get("locations") or [{}])[0].get("physicalLocation") or {}))
                _fp_scan.append((
                    _tool, _fingerprint_value(_res),
                    _norm_uri((_loc.get("artifactLocation") or {}).get("uri", "")),
                    (_loc.get("region") or {}).get("startLine", 1)))
    degenerate_fps = _degenerate_fingerprints(_fp_scan)
    # Per-tool path sets, for the different-roots check (item 0c).
    _tool_paths = {}
    for _t, _f, _u, _l in _fp_scan:
        if _u:
            _tool_paths.setdefault(_t, set()).add(_u)
    path_warnings = _path_root_mismatch(_tool_paths)

    for path, doc in docs:
        if "_empty" in doc:
            empty_inputs.append(path)
            continue
        if "_parse_error" in doc:
            parse_errors.append({"file": path, "error": doc["_parse_error"]})
            continue
        for run in (doc.get("runs") or []):
            driver = ((run.get("tool") or {}).get("driver") or {})
            tool = driver.get("name", "unknown-tool")
            tools_seen.add(tool)
            # rule metadata for kind inference
            # Rule metadata, used for CWE-class resolution. TWO sources, in
            # priority order:
            #   1. relationships -> CWE taxa. The STRUCTURED, canonical SARIF
            #      mechanism: target.id is the CWE number and toolComponent.name
            #      is "CWE". Authoritative and free of prose noise.
            #   2. free text (id/name/descriptions/tags), scanned only when no
            #      taxon is declared.
            # Why taxa first, measured on real SpotBugs+FindSecBugs output:
            # prose listed CWE-327 AND CWE-328 for WEAK_MESSAGE_DIGEST_MD5, so
            # scraping had to give up (ambiguous), while the taxon says exactly
            # 328 -> `hash`, the correct and more specific answer. Likewise
            # INFORMATION_EXPOSURE prose mentions 22/89 incidentally while its
            # taxon is 209 -> correctly unmapped. Structured beats scraped.
            rulemeta, ruletaxa = {}, {}
            for r in (driver.get("rules") or []):
                rid = r.get("id")
                if not rid:
                    continue
                cwes = []
                for rel in (r.get("relationships") or []):
                    tgt = rel.get("target") or {}
                    comp = (tgt.get("toolComponent") or {}).get("name") or ""
                    if comp.upper() == "CWE":
                        tid = str(tgt.get("id") or "").strip()
                        m = re.search(r"(\d+)", tid)
                        if m:
                            cwes.append(int(m.group(1)))
                if cwes:
                    ruletaxa[rid] = cwes
                rulemeta[rid] = " ".join(str(x) for x in [
                    rid, (r.get("name") or ""),
                    ((r.get("shortDescription") or {}).get("text") or ""),
                    ((r.get("fullDescription") or {}).get("text") or ""),
                    " ".join(str(t) for t in (((r.get("properties") or {}).get("tags")) or []))]).lower()
            for res in (run.get("results") or []):
                # PHASE 1 — SAME-TOOL dedup. Scoped by tool so one tool's
                # fingerprint can never collide with another tool's key.
                key = (tool, _result_key(res, tool, degenerate_fps))
                loc = (((res.get("locations") or [{}])[0].get("physicalLocation") or {}))
                uri = _norm_uri((loc.get("artifactLocation") or {}).get("uri", ""))
                line = (loc.get("region") or {}).get("startLine", 1)
                rid = res.get("ruleId", "?")
                lvl = (res.get("level") or "warning").lower()
                msg = ((res.get("message") or {}).get("text") or "")
                rec = findings.get(key)
                if rec is None:
                    rec = {"key": key, "ruleId": rid, "uri": uri, "line": line,
                           "message": msg, "level": lvl, "tools": set(),
                           "levels": set(), "rulemeta": "", "all_rule_ids": set(),
                           "all_msgs": {}, "taxa_cwes": []}
                    findings[key] = rec
                rec["tools"].add(tool)
                rec["levels"].add(lvl)
                rec["all_rule_ids"].add(rid)
                rec["all_msgs"][rid] = msg
                if SEV.get(lvl, 1) > SEV.get(rec["level"], 1):
                    rec["level"] = lvl  # keep the most severe claim across tools
                if rid in rulemeta and not rec["rulemeta"]:
                    rec["rulemeta"] = rulemeta[rid]
                if rid in ruletaxa and not rec.get("taxa_cwes"):
                    rec["taxa_cwes"] = ruletaxa[rid]

    # ── PHASE 2 — CROSS-TOOL consensus merge ────────────────────────────────
    # Union same-tool-deduped records that DIFFERENT tools agree on, keyed by
    # normalized location + CWE class (or identical ruleId). This is the second
    # of DefectDojo's two algorithms; phase 1 was the first. Using phase 1's
    # fingerprint key for this purpose is what made n_tools>1 impossible in the
    # shipped scanner pair (docs/SCOPE_shipped_consensus_defect.md).
    same_tool_count = len(findings)
    order = sorted(findings.keys())            # deterministic, input-order-independent
    recs = [findings[k] for k in order]

    def _lineages(rec):
        return {_lineage_of(t) for t in rec["tools"]}

    # Decision 0a: pairs whose independence cannot be established do not count
    # as consensus. Conservative by default; operator-declarable.
    declared_independent = _declared_independent()
    suppressed = _suppressed_pairs(tools_seen, declared_independent)
    parent = list(range(len(recs)))

    def _find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)   # lowest index wins -> deterministic

    by_key = {}
    for i, rec in enumerate(recs):
        for ck in _cross_keys(rec):
            by_key.setdefault(ck, []).append(i)
    for ck in sorted(by_key):
        idxs = by_key[ck]
        for a, b in zip(idxs, idxs[1:]):
            # DIVERSITY-AWARE: only merge across DIFFERENT ENGINES. Two findings
            # from the same tool at one location are that tool's business and
            # were already handled in phase 1; merging them here would let a
            # single tool inflate its own consensus.
            # Compared by ENGINE LINEAGE, not driver name — SpotBugs and FindBugs
            # are one engine under two names, and merging them would manufacture
            # consensus out of self-agreement. See _TOOL_LINEAGE.
            la, lb = _lineages(recs[a]), _lineages(recs[b])
            if la & lb:
                continue
            # Decision 0a: uncertainty resolves to NO-MERGE, as it does
            # everywhere else in this pipeline. A SonarQube deployment may be
            # re-emitting a co-present tool's report; SARIF cannot tell us.
            if suppressed and any(frozenset((x, y)) in suppressed
                                  for x in la for y in lb):
                continue
            _union(a, b)

    groups = {}
    for i in range(len(recs)):
        groups.setdefault(_find(i), []).append(i)
    merged = {}
    for root in sorted(groups):
        members = [recs[i] for i in groups[root]]
        base = members[0]                       # lowest index — deterministic
        for m in members[1:]:
            base["tools"] |= m["tools"]
            base["levels"] |= m["levels"]
            base["all_rule_ids"] |= m["all_rule_ids"]
            base["all_msgs"].update(m["all_msgs"])
            if SEV.get(m["level"], 1) > SEV.get(base["level"], 1):
                base["level"] = m["level"]      # most severe claim across tools
            if m["rulemeta"] and not base["rulemeta"]:
                base["rulemeta"] = m["rulemeta"]
            if m.get("taxa_cwes") and not base.get("taxa_cwes"):
                base["taxa_cwes"] = m["taxa_cwes"]
        merged[base["key"]] = base
    findings = merged

    # Deterministic identity: regardless of input order, a merged finding adopts
    # the lexicographically-smallest ruleId among agreeing tools (and its message).
    # This makes the whole ranking order-independent.
    for rec in findings.values():
        canon = sorted(rec["all_rule_ids"])[0]
        rec["ruleId"] = canon
        rec["message"] = rec["all_msgs"].get(canon, rec["message"])

    # Signal computation.
    def kind_of(rec):
        t = (rec["rulemeta"] + " " + rec["ruleId"] + " " + rec["message"]).lower()
        if any(w in t for w in ("inject", "xss", "csrf", "secret", "credential", "crypto",
                                 "auth", "ssrf", "path-travers", "deserial", "cwe", "security", "vuln")):
            return "security"
        if any(w in t for w in ("null", "leak", "overflow", "race", "use-after", "bounds",
                                 "uninitial", "resource", "deadlock", "bug")):
            return "bug"
        return "style"
    KIND_W = {"security": 1.5, "bug": 0.8, "style": 0.0}

    # Resolve tool-quality weighting ONCE per ingest. qmult is a per-tool
    # multiplier that is INGEST-INVARIANT (a tool's weight depends only on its
    # own known quality, never on what else is in the ingest). ground_truth is
    # None in the normal production path (-> PRIOR or MIXED disclosure); a labeled
    # benchmark passing a detection matrix would trigger MEASURED. If the module
    # is absent, qmult is identity -> flat baseline preserved exactly.
    if _QUALITY_WEIGHTING:
        qmode, qmult = resolve_weighting(sorted(tools_seen), ground_truth=None)
    else:
        qmode, qmult = {"mode": "INACTIVE (module absent)", "disclosure":
                        "Quality-weighting module not present; flat consensus baseline.",
                        "per_tool_multiplier": {}}, (lambda t: 1.0)

    for rec in findings.values():
        # DIVERSITY-AWARE: distinct ENGINES, not distinct driver names. A record
        # can acquire two same-lineage drivers transitively (A/engine1 merges
        # with B/engine2, which merges with C/engine1), so this is counted here
        # as well as guarded at merge time.
        rec["lineages"] = sorted({_lineage_of(t) for t in rec["tools"]})
        rec["n_tools"] = len(rec["lineages"])
        # One representative driver per engine, so quality-weighting also counts
        # each engine once rather than once per name.
        _byl = {}
        for _t in sorted(rec["tools"]):
            _byl.setdefault(_lineage_of(_t), _t)
        rec["consensus_tools"] = set(_byl.values())
        rec["sev_n"] = SEV.get(rec["level"], 1)
        rec["noisy_loc"] = bool(FIXTURE_DIR.search(rec["uri"]) or is_packaging(rec["uri"])
                                or TEST_DIR.search(rec["uri"])
                                or TEST_DIR_PREFIX.search(rec["uri"]))
        rec["kind"] = kind_of(rec)
        # consensus term: quality-weighted across the tools agreeing ON THIS
        # finding (was: flat 1.6 * n_tools). weighted_consensus_term reduces to
        # 1.6 * n_tools exactly when every multiplier is 1.0.
        if _QUALITY_WEIGHTING:
            consensus = weighted_consensus_term(rec["consensus_tools"], qmult)
        else:
            consensus = 1.6 * rec["n_tools"]
        # review-worthiness score (validated signal combination; NOT exploitability)
        rec["score"] = round(
            consensus                       # diversity-aware, quality-weighted consensus
            + 1.0 * rec["sev_n"]            # severity (their claim, preserved)
            + KIND_W[rec["kind"]]           # rule kind prior
            - (2.0 if rec["noisy_loc"] else 0.0),  # location noise penalty (top signal)
            3)

    # Deterministic order: score desc, then stable tie-breakers.
    ranked = sorted(findings.values(),
                    key=lambda r: (-r["score"], r["uri"], str(r["line"]), r["ruleId"]))
    total_raw = sum(len((d.get("runs") or [{}])[0].get("results", []))
                    if ("_parse_error" not in d and "_empty" not in d) else 0
                    for _, d in docs)
    return {
        "inputs": [p for p, _ in docs],
        "parse_errors": parse_errors,
        "empty_inputs": empty_inputs,
        "tools": sorted(tools_seen),
        # Engine lineage per driver, plus any independence caveats we can detect
        # from the names alone. Consensus counts ENGINES, not product names.
        "tool_lineages": {t: _lineage_of(t) for t in sorted(tools_seen)},
        "distinct_engines": len({_lineage_of(t) for t in tools_seen}),
        "lineage_warnings": _lineage_warnings(tools_seen, declared_independent),
        # Cross-tool path-root mismatch: a zero merge count caused by paths,
        # not by tool disagreement. Kept separate so it is never read as a
        # consensus result.
        "path_warnings": path_warnings,
        "declared_independent": sorted(declared_independent),
        "raw_result_count": total_raw,
        # Two-stage dedup is now visible, so a reader can tell which stage did
        # the work: same-tool (fingerprint) vs cross-tool (location + CWE class).
        "same_tool_deduplicated_count": same_tool_count,
        "cross_tool_merges": same_tool_count - len(findings),
        "deduplicated_count": len(findings),
        "ranking_basis": "review-worthiness (location + diversity-aware consensus + "
                         "severity + kind). NOT exploitability — no external threat feeds.",
        "quality_weighting": qmode,
        "ranked": [{"rank": i + 1, "score": r["score"], "ruleId": r["ruleId"],
                    "uri": r["uri"], "line": r["line"], "level": r["level"],
                    "tools": sorted(r["tools"]), "n_tools": r["n_tools"],
                    "kind": r["kind"], "noisy_loc": r["noisy_loc"],
                    # the CWE class actually used for cross-tool matching —
                    # exposed so audits read what ingest used, not a recompute
                    "cwe_class": r.get("cwe_class"),
                    "message": r["message"]} for i, r in enumerate(ranked)],
    }

def ingest_to_sarif(agg, tool_version="6.0"):
    """Re-emit the deduplicated, re-ranked findings as valid SARIF 2.1.0, so the
    re-ranked view is itself consumable by any SARIF reader. Rank + score + the
    review-worthiness signals ride in each result's properties bag (spec's
    sanctioned extension point). Deterministic, ordered by rank."""
    results = []
    for r in agg["ranked"]:
        uri = r["uri"] or "unknown"
        results.append({
            "ruleId": r["ruleId"] or "unknown",
            "level": r["level"] if r["level"] in ("error", "warning", "note", "none") else "warning",
            "message": {"text": r["message"] or f"{r['ruleId']} at {uri}"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": uri.lstrip("/")},
                "region": {"startLine": r["line"] if isinstance(r["line"], int) and r["line"] >= 1 else 1},
            }}],
            "partialFingerprints": {"ingestKey": r["ruleId"] + ":" + (uri.lstrip("/"))},
            "properties": {"reviewRank": r["rank"], "reviewScore": r["score"],
                           "agreeingTools": r["tools"], "toolCount": r["n_tools"],
                           "kind": r["kind"], "noisyLocation": r["noisy_loc"],
                           "rankingBasis": "review-worthiness, not exploitability"},
        })
    rule_ids = sorted({(r["ruleId"] or "unknown") for r in agg["ranked"]})
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "GENESIS-audit-ingest",
                "version": tool_version,
                "informationUri": "https://example.invalid/genesis-audit",
                "rules": [{"id": rid,
                           "shortDescription": {"text": f"Ingested rule {rid}, re-ranked by review-worthiness"}}
                          for rid in rule_ids],
            }},
            "results": results,
            "columnKind": "unicodeCodePoints",
        }],
    }

def signal_informativeness(ranked):
    """EVIDENCE-DRIVEN signal gate (NOT benchmark detection). For THIS input,
    report which ranking signals actually have discriminating information —
    based purely on structural facts about the findings, never on 'is this a
    known benchmark'. A signal with no variety in the input carries no
    information and is honestly down-weighted AND disclosed. Works on any input.
    Origin: measured on OWASP Benchmark, where all findings share one clean
    location, tools don't overlap, and severity doesn't vary — so location,
    consensus, and severity signals are ALL uninformative, and the tool should
    say so rather than rank confidently on noise."""
    n = len(ranked)
    locs = {r["uri"] for r in ranked}
    noisy_variety = any(r["noisy_loc"] for r in ranked) and any(not r["noisy_loc"] for r in ranked)
    max_tools = max((r["n_tools"] for r in ranked), default=1)
    sevs = {r["level"] for r in ranked}
    location_ok = len(locs) > 1 and noisy_variety
    consensus_ok = max_tools >= 2
    severity_ok = len(sevs) > 1
    informative = [s for s, ok in (("location", location_ok), ("consensus", consensus_ok),
                                    ("severity", severity_ok)) if ok]
    uninformative = [s for s in ("location", "consensus", "severity")
                     if s not in informative]
    # honest confidence: how much of the ranking rests on real signal
    confidence = ("high" if len(informative) >= 2 else
                  "low" if len(informative) == 0 else "medium")
    return {"distinct_locations": len(locs), "location_variety": noisy_variety,
            "max_tools_agreeing": max_tools, "distinct_severities": len(sevs),
            "informative_signals": informative, "uninformative_signals": uninformative,
            "ranking_confidence": confidence}

def main():
    global RUN_TESTS
    RUN_TESTS = "--run-tests" in sys.argv
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__); return 0

    # --ingest: DETERMINISTIC re-rank of existing SARIF file(s). Distinct entry
    # path (consumes SARIF, does not scan a directory). LLM triage (AUDIT.md
    # protocol) layers ON TOP of this reproducible output; this core stands alone.
    if "--ingest" in sys.argv:
        i = sys.argv.index("--ingest")
        # collect input paths until the NEXT flag (don't swallow --json/--sarif values)
        paths = []
        for a in sys.argv[i+1:]:
            if a.startswith("--"):
                break
            paths.append(a)
        if not paths:
            print("usage: audit.py --ingest a.sarif [b.sarif ...] [--sarif out.sarif] [--json out.json]")
            return 1
        agg = ingest_sarif(paths)
        agg["signal_assessment"] = signal_informativeness(agg["ranked"])
        if "--json" in sys.argv:
            json.dump(agg, open(sys.argv[sys.argv.index("--json")+1], "w"), indent=2)
        if "--sarif" in sys.argv:
            json.dump(ingest_to_sarif(agg), open(sys.argv[sys.argv.index("--sarif")+1], "w"), indent=2)
        print(f"SARIF INGEST — deterministic re-rank")
        print(f"  inputs: {', '.join(agg['inputs'])}")
        if agg["parse_errors"]:
            for pe in agg["parse_errors"]:
                print(f"  ⚠ parse error in {pe['file']}: {pe['error']}")
        if agg.get("empty_inputs"):
            for ei in agg["empty_inputs"]:
                print(f"  · {ei}: empty (no findings) — skipped")
        print(f"  tools: {', '.join(agg['tools']) or '(none)'}")
        if agg.get("distinct_engines", 0) and agg["distinct_engines"] != len(agg["tools"]):
            print(f"  distinct ANALYSIS ENGINES: {agg['distinct_engines']} "
                  f"(consensus counts engines, not product names)")
        for w in agg.get("path_warnings", []):
            print(f"  ⚠ PATH MISMATCH: {w}")
        for w in agg.get("lineage_warnings", []):
            print(f"  ⚠ independence: {w}")
        print(f"  {agg['raw_result_count']} raw results → {agg['deduplicated_count']} unique after dedup")
        sa = agg["signal_assessment"]
        print(f"  signal check: informative here = {sa['informative_signals'] or 'NONE'}; "
              f"ranking confidence = {sa['ranking_confidence']}")
        if sa["ranking_confidence"] == "low":
            print(f"    ⚠ this input lacks location variety, tool overlap, and severity spread —")
            print(f"      ranking signals have little to work with; treat order as low-confidence.")
        print(f"  ranking: {agg['ranking_basis']}")
        qw = agg.get("quality_weighting")
        if qw:
            print(f"  quality-weighting [{qw.get('mode','?')}]: {qw.get('disclosure','')}")
        print(f"\n  TOP FINDINGS BY REVIEW-WORTHINESS (deterministic; LLM triage would annotate on top):")
        for r in agg["ranked"][:12]:
            tools = "+".join(r["tools"])
            flags = []
            if r["n_tools"] > 1: flags.append(f"{r['n_tools']}tools")
            if r["noisy_loc"]: flags.append("noisy-loc")
            flags.append(r["kind"])
            print(f"    #{r['rank']:<2} score={r['score']:<5} {r['ruleId']:22.22s} {r['uri']}:{r['line']}  [{tools}] {' '.join(flags)}")
        if len(agg["ranked"]) > 12:
            print(f"    … {len(agg['ranked'])-12} more (full list in --json / --sarif output)")
        return 0

    # PROJECT_DIR is the first positional (non-flag) argument. Resolving it this
    # way — rather than assuming sys.argv[1] — means modifier flags like
    # --run-tests can appear in any position without being mistaken for a path.
    root = None
    skip_next = False
    for a in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if a in ("--json", "--sarif"):   # these take a value; skip the value too
            skip_next = True
            continue
        if a.startswith("--"):
            continue
        root = a
        break
    if root is None:
        print(__doc__)
        print("error: no PROJECT_DIR given. Provide a directory to scan, or use --ingest for SARIF files.")
        return 1
    if not os.path.isdir(root):
        print(f"not a directory: {root}"); return 1
    inv = analyze(root)
    if "--json" in sys.argv:
        json.dump(inv, open(sys.argv[sys.argv.index("--json")+1], "w"), indent=2)
    if "--sarif" in sys.argv:
        out = sys.argv[sys.argv.index("--sarif")+1]
        json.dump(to_sarif(inv), open(out, "w"), indent=2)
    c = inv["counts"]
    print(f"AUDIT LAYER 1 — mechanical sweep of {root}")
    print(f"  stack: {inv['stack']}  |  tests: {inv['test_status']}")
    if inv["is_monorepo"]:
        print(f"  MONOREPO — markers found (presence, Layer 2 confirms boundaries):")
        for m in inv["markers"]:
            print(f"    {m['dir']:30s} {m['marker']:18s} → {m['language']}")
        print(f"  per-subtree (inferred by nearest marker):")
        for st, info in inv["subtrees_inferred"].items():
            print(f"    {st:30s} {'+'.join(info['languages']):15s} {info['files']} files, {info['untested']} untested")
    print(f"  {c['code_files']} code files, {c['total_loc']} LOC, {c['test_files']} test files, {c['fixture_files']} fixture files")
    print(f"  FLAGS: {c['total_secrets']} secret(s), {c['untested_files']} untested file(s), {c['total_todos']} TODO/FIXME")
    if inv.get("coverage_confidence") == "low":
        n = len(inv.get("subprocess_driven_tests", []))
        print(f"  ⚠ COVERAGE CONFIDENCE: LOW — {n} test file(s) spawn the app as a subprocess (E2E/CLI style).")
        print(f"    Static matching can't see what a spawned process exercises, so 'tested'/'untested'")
        print(f"    flags are unreliable IN BOTH DIRECTIONS here. Treat coverage as indicative only;")
        print(f"    run with --run-tests + a coverage tool to get real per-file coverage.")
    if inv["secrets_found"]:
        print(f"  SECRETS IN SOURCE (highest priority): {', '.join(inv['secrets_found'])}")
        _fixhits = [p['file'] for p in inv['risk_ranked'] if p['secrets'] and p.get('is_fixture')]
        if _fixhits:
            print(f"    note: {len(_fixhits)} of these are in fixture/test-data dirs "
                  f"(likely planted test values — Layer 2 confirm): {', '.join(_fixhits)}")
    print(f"\n  RISK-RANKED (Layer 2 deep-reads the top of this list, not the whole repo):")
    for p in inv["risk_ranked"][:10]:
        tag = "no-test " if not p["has_test"] else ""
        sec = f"{p['secrets']}secret " if p["secrets"] else ""
        st = f"[{p['subtree']}] " if p.get("subtree") else ""
        print(f"    risk={p['risk']:2d}  {p['file']:34s} {st}{p['language']:7s} {tag}{sec}{p['todos']}todo {p['loc']}loc")
    return 0

if __name__ == "__main__":
    sys.exit(main())
