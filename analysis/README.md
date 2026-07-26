# `analysis/` — the working record behind the numbers in `docs/VALIDATION.md`

**What this is.** Every measurement quoted in `docs/VALIDATION.md` and in the
README was produced by one of the scripts in `scripts/`. Those scripts lived in
a session scratchpad under `/private/tmp/…` — a temp directory that does not
survive a reboot. They are preserved here so the numbers stay reproducible.

**What this is NOT.** This is not part of the shipped tool. Nothing in
`analysis/` is imported by `src/`, run by `action.yml`, or covered by the
regression harness. It is evidence, not product.

**The corpora are NOT committed** — they total ~690 MB (OWASP Benchmark built
with `target/classes` alone is 269 MB). §2 gives the fetch/build commands and
§4 gives checksums so a rebuild can be verified against what actually produced
the recorded numbers.

---

## 1. The scripts

Grouped by which corpus they need. Each script resolves its inputs **relative to
its own directory** (`os.path.dirname(os.path.abspath(__file__))`), so see §3 for
how to run them.

### Lipp et al. ISSTA'22 artifact — real C/C++ CVE ground truth

| script | what it measures | where the result is recorded |
|---|---|---|
| `run_0i.py` | Item 0i, pre-registered. Four size-controlled formulations (A logistic, B size-residualized, C density, D raw) at function level, plus the IRLS logistic diagnostics that put the 1.5x in doubt. Pure-Python IRLS + Gaussian elimination — **no numpy needed**. | VALIDATION.md "0i RESULT"; raw output in `results/0i_function_level.txt` |
| `granularity_signal.py` | Does function-level agreement carry signal or just more merges. Source of the line-level 1.56% vs function-level 35.95% agreement rates and the 6.4x cross-methodology merge figure. | VALIDATION.md, HANDOFF §8 rule 9 |
| `effort_aware.py` | PofB@20%**LOC** (budget in lines, not units) across granularities. Source of function-level 0.185 and file-level 0.228 vs LOC 0.081. | VALIDATION.md 0g |
| `manualup.py` | Consensus vs ManualUp (ascending size) and ManualDown (descending size), per Zhou et al. 2018 as described in arXiv:2302.00394. Source of the ManualDown ROC-AUC 0.845 that killed the 0.755 headline. | VALIDATION.md 0g |
| `size_confound.py` | Spearman(n_tools, size) = +0.629 file / +0.304 function, and the decile-matched random baseline. **This is the decile-matching implementation whose method item 0j re-examines.** | VALIDATION.md 0g/0h |
| `recon755.py` | Reconstructs the file-level ROC-AUC 0.755 / PofB 0.655 directly from Lipp's `found_by` lists, no SARIF and no `audit.py`. Reproducing it that way is what showed 0.755 was never a property of this implementation. | VALIDATION.md 3c(b) |

### OWASP Benchmark v1.2 — synthetic Java, labelled

| script | what it measures | where recorded |
|---|---|---|
| `single_vs_consensus.py` | Consensus vs the **best single tool**, not vs the base rate. The comparator HANDOFF 0d says to run before claiming consensus adds value on any new corpus. | VALIDATION.md 0d |
| `merge_audit.py` | Cross-tool merge + the item 7a false-merge audit (0 false merges in 1,156). | VALIDATION.md 7a |
| `rule_lineage.py` | How many merges are a semgrep rule agreeing with its **own FindSecBugs ancestor**. Source of the 30.4% derived-pair figure. Reads `owasp/sg_native.json` because SARIF **drops** `source-rule-url`. | VALIDATION.md / HANDOFF 0f |
| `java_resolution.py` | Whether the 15 Java CWE classes fire on real Java scanner output. | VALIDATION.md "Java class-resolution pass" |
| `resolution.py` | Per-tool class-resolution + fingerprint-degeneracy report. Takes a SARIF path as `argv[1]`, so it runs against any tool. | VALIDATION.md 3b |

### Both Java corpora

| script | what it measures | where recorded |
|---|---|---|
| `direction_b.py` | Point-in-range matching (HANDOFF item 0e "Direction B"). **Evaluation, not an implementation** — runs against the pre-registered decision rule. Needs OWASP *and* Struts. | VALIDATION.md 0e |

### zlib 1.3.1 — real C

| script | what it measures | where recorded |
|---|---|---|
| `pairwise.py` | Pairwise cross-tool merge counts: is the *default tool set* the defect. Source of cppcheck+flawfinder = 0, flawfinder+semgrep = 2. Its `TOOLS` dict references `zq.sarif` (CodeQL), which **was never produced** — CodeQL is unusable on this arm64 Mac (osx64 tracer, no Rosetta). Run it with the ql entry removed. | VALIDATION.md |

### No corpus

| script | what it measures |
|---|---|
| `probe_merge.py` | Self-contained probe: synthesises three minimal SARIF pairs and asks whether `ingest_sarif` merges them. Needs only `src/` on the path. |

Seven scripts (`direction_b`, `java_resolution`, `merge_audit`, `pairwise`,
`resolution`, `rule_lineage`, `single_vs_consensus`) hard-code
`sys.path.insert(0, "/Users/caitlinfuller/audit/src")`. Edit that line if the
repo moves.

---

## 2. Inputs — where they came from

### a. Lipp et al. ISSTA'22 artifact (33 MB unpacked; the important one)

Zenodo DOI `10.5281/zenodo.6515687`, CC-BY-4.0. 192 CVEs, 6 tools, 27 real C
projects. All 15 files and their download URLs are in
`data/lipp_zenodo_urls.txt`; the fetch is:

```sh
mkdir -p lipp && cd lipp
while read -r name url; do curl -sSL -o "$name" "$url"; done < …/lipp_zenodo_urls.txt
unzip -q dataset.zip        # -> dataset/{binutils,ffmpeg,libpng,libtiff,libxml2,openssl,php,poppler,sqlite3}
unzip -q cwe_mapping.zip    # -> cwe_mapping/buckets.json + analyzers/
```

Every script reads only `lipp/dataset/<project>/{sca_results.json,
functions.json,cve_data.json}`.

`cwe_mapping/buckets.json` is small and load-bearing for HANDOFF item 3e
(MITRE parent_of/child_of DAG, 162 CWEs), so it **is** committed here as
`data/lipp_cwe_buckets.json`. CC-BY-4.0 — attribute Lipp et al. if vendored into
`src/`.

### b. OWASP Benchmark v1.2 (269 MB once built)

```sh
curl -sSL -o bm.zip https://github.com/OWASP-Benchmark/BenchmarkJava/archive/refs/heads/master.zip
unzip -q bm.zip          # -> BenchmarkJava-master/
cd BenchmarkJava-master && mvn -q -DskipTests compile   # needs openjdk@17 + maven
```

Labels: `BenchmarkJava-master/expectedresults-1.2.csv` (2,740 labelled cases),
shipped in the repo — no build needed for the label file itself.

### c. Apache Struts (36 MB)

```sh
curl -sSL -o struts.zip https://github.com/apache/struts/archive/refs/heads/main.zip
unzip -q struts.zip      # -> struts-main/
cd struts-main && mvn -q -DskipTests compile
```

### d. zlib 1.3.1 (8 MB)

```sh
curl -sSL -o zlib.tar.gz https://zlib.net/zlib-1.3.1.tar.gz
tar xzf zlib.tar.gz && cd zlib-1.3.1 && ./configure && make -j8
```

### e. Scanner output (the `*.sarif` inputs)

Versions marked *(SARIF)* are read back out of the `tool.driver` block, so they
are exact; cppcheck's SARIF carries no version field and its number comes from
VALIDATION.md instead. The **flag sets are partly reconstructed** — the session
that ran them did not record every invocation verbatim, and shell history is not
available. Treat the commands as the documented intent and the checksums in §4
as the authority on what was actually analysed.

| file | tool | command |
|---|---|---|
| `lib/zf.sarif` | Flawfinder 2.0.20 *(SARIF)* | `flawfinder --sarif zlib-1.3.1/ > zf.sarif` |
| `lib/zc.xml` → `lib/zc.sarif` | Cppcheck 2.21.0 *(VALIDATION.md, not in SARIF)* | `cppcheck --xml … zlib-1.3.1/ 2> zc.xml` then `src/cppcheck_xml_to_sarif.py` |
| `lib/zs.sarif`, `lib/zs_native.json` | Semgrep OSS 1.171.0 *(SARIF)* | `semgrep --config=p/security-audit --sarif` (and `--json` for the native file) |
| `owasp/sb.sarif`, `struts/sb.sarif` | SpotBugs 4.10.3 *(SARIF)* + FindSecBugs plugin | `spotbugs -textui -sarif -pluginList findsecbugs.jar …/target/classes` |
| `owasp/sg_java.sarif`, `owasp/sg_native.json` | Semgrep OSS 1.171.0 *(SARIF)* | `semgrep --config=p/java --sarif` (and `--json`) |
| `struts/sg_raw.sarif` | Semgrep OSS 1.171.0 *(SARIF)* | `semgrep --config=p/java --sarif` |

**`sg_java2.sarif` and `struts/sg.sarif` are derived, not raw.** They are
`sg_java.sarif` / `sg_raw.sarif` with every result URI rewritten from
scan-root-relative to **package-relative**, to align with SpotBugs' bytecode-
derived paths. Verified by inspection:

```
sg_java.sarif   owasp/BenchmarkJava-master/src/main/java/org/owasp/benchmark/testcode/BenchmarkTest00001.java
sg_java2.sarif  org/owasp/benchmark/testcode/BenchmarkTest00001.java
sb.sarif        org/owasp/benchmark/helpers/DataBaseServer.java
```

**This matters and must not be lost:** every Java cross-tool merge number in
VALIDATION.md was measured on **hand-aligned paths**. HANDOFF item 0c (the
package-relative vs scan-root-relative silent zero) was *worked around by hand
for the measurement*, not fixed in the tool. A user running the two scanners the
obvious way still gets zero merges and no diagnostic.

`errorlist.xml` is `cppcheck --errorlist` (342 checks) — the tool-authoritative
source for the `_CWE_CLASS` coverage cascade in HANDOFF item 2.

### f. External papers (not committed — arXiv IDs suffice)

`arXiv:2302.00394` (effort-aware defect prediction / ManualUp-ManualDown
baselines) and `arXiv:2504.19181` were fetched as PDFs into the scratchpad.

---

## 3. How to run

The scripts resolve corpora relative to **their own** location, so they must sit
next to `lipp/`, `owasp/`, `struts/`, `lib/`. They are preserved **byte-for-byte
as they produced the recorded numbers** — deliberately not rewritten to take a
root argument, because a rewrite is a change to the instrument.

```sh
CORPUS=/path/to/corpus-root     # the dir holding lipp/ owasp/ struts/ lib/
cp analysis/scripts/*.py "$CORPUS"/
cd "$CORPUS" && python3 run_0i.py
```

Python 3 standard library only. There is **no numpy or scipy on this machine**,
and `run_0i.py` shows that constraint is not binding: its pure-Python IRLS
logistic regression fits 14,656 units in about two minutes. See HANDOFF item 0j
— the absence of numpy was allowed to select decile matching over covariate
adjustment once already, and should not be again.

---

## 4. Checksums of the derived inputs

SHA-256, first 16 hex chars, of the scanner output and corpus files as they
existed when the recorded numbers were produced. A rebuild that does not match
is a *different* measurement — scanner versions move.

| file | sha256[:16] | bytes | results |
|---|---|---|---|
| `lib/zf.sarif` | `721d3ccacff23079` | 596,086 | 588 |
| `lib/zc.sarif` | `7c2b62119f786dcf` | 154,885 | 543 |
| `lib/zc.xml` | `3e4fcde325d104b3` | 67,844 | |
| `lib/zc_full.xml` | `efc84bde96fac0e0` | 287,263 | |
| `lib/zs.sarif` | `585fd12d5e593655` | 484,828 | 33 |
| `lib/zs_native.json` | `8b03174d69a1614d` | 204,937 | |
| `owasp/sb.sarif` | `c0862c525c436520` | 12,546,571 | 21,165 |
| `owasp/sg_java.sarif` | `c6966ea9c460fa8e` | 1,779,317 | 1,909 |
| `owasp/sg_java2.sarif` | `8ed52de8c771c2c2` | 1,701,048 | 1,909 |
| `owasp/sg_native.json` | `0075af477ffbd387` | 3,075,177 | |
| `struts/sb.sarif` | `35550e907d773b67` | 1,031,177 | 1,548 |
| `struts/sg_raw.sarif` | `1dd104d264dcc382` | 133,667 | 1 |
| `struts/sg.sarif` | `9a6f51785344b743` | 136,438 | 1 |
| `owasp/BenchmarkJava-master/expectedresults-1.2.csv` | `1809f6a690c6cf7d` | 95,328 | |
| `errorlist.xml` | `093c9d6ec4a7a1a4` | 106,240 | |
| `lipp/dataset.zip` | `e3e387c64c3599ff` | 2,333,690 | |
| `lipp/cwe_mapping.zip` | `d1372872611e0a47` | 35,542 | |
| `lipp/sca_data_1.csv` | `d908569e08fbff87` | 160,344 | |
| `lipp/sca_data_2.csv` | `f54189a1bd763018` | 372,994 | |
| `lipp/fct_stats_1.csv` | `fea0e03161be1b32` | 3,301,187 | |
| `lipp/fct_stats_2.csv` | `e54e99df1898dce5` | 42,781 | |
| `lipp/cwe_distr.csv` | `c9c35337f635ac55` | 3,325 | |
| `lipp/README.md` | `7d62086798412c35` | 8,858 | |

---

## 5. Honest bounds on this directory

- Provenance tier of the scripts themselves: `[self-tested]`. They are Claude-
  written analysis code. What is externally grounded is their **inputs** — real
  scanner output, real CVE labels, a published artifact — not the analysis.
- One measurement quoted in VALIDATION.md has **no script here**: the
  size-matched precision test (multi 1.54% vs size-matched single 1.02%,
  2,000 draws, the README's 1.5x). It was run inline and never written to a
  file. Item 0j re-derives it; see `results/` for the 0j output.
- `pairwise.py` references a CodeQL SARIF that does not exist (see §1).
