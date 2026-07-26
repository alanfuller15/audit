# Spec — Java admission: what must be true before the consensus premise is claimed for Java

Status: **scoping document only.** No implementation, no tier movement. Written
2026-07-26 (HANDOFF item J).

Java is NOT unexplored territory for this project. Prior work exists and is the
starting point, not something to re-derive: the 2026-07-08 OWASP Benchmark
section of VALIDATION.md, and the NASCAR result. Both are summarized in §3.

---

## 1. The admission test

A language may not have the consensus premise claimed for it until all of the
following hold. These are gates, not a scorecard — failing one is disqualifying
for the CLAIM, though not for shipping the tool as a ranker.

**A1 — At least three scanners with genuinely disjoint miss-sets.**
Not three *products*. Three *engines*. A wrapper, fork, plugin, or report
importer does not add an independent vote; it re-casts an existing one. Shared
lineage must be checked, not assumed (§2 shows why: the first candidate checked
turned out to be the tool this project has already tested).

**A2 — Usable SARIF from each**, containing at minimum a location and something
from which a vulnerability class can be resolved (ruleId, message, or rule
metadata — the ingest reads all three).

**A3 — A corpus with real labels.** Human-labeled ground truth, not synthetic
seeding whose construction defeats the signal being measured (the OWASP lesson,
§3).

**A4 — MEASURED PARTIAL OVERLAP between candidate pairs.**
Added 2026-07-26 on C/C++ evidence, and it is the gate the others miss.
Independence is necessary but NOT sufficient: two engines can be so
methodologically different that they never agree at all. Consensus requires
tools different enough that agreement is independent evidence, yet similar
enough that they can agree. See VALIDATION.md, "The overlap constraint."

A4 cannot be satisfied by argument. It requires a **measured cross-tool merge
rate on real code** for each candidate pair. An engine-count is not evidence
of overlap.

---

## 2. Does Java clear it? Candidate set and independence

Candidates: SpotBugs, semgrep, CodeQL, SonarQube (as named), plus PMD and
Error Prone, checked because they are the obvious additions.

### Lineage findings — `[fetched]`

| tool | engine basis | independent? |
|---|---|---|
| **SpotBugs** | fork of FindBugs; source still under `edu/umd/cs/findbugs/`, e.g. `FindBugs2.java` | **NO — it IS FindBugs**, continued |
| **FindSecBugs** | a **SpotBugs plugin** (adds ~128 security detectors on top of SpotBugs' patterns) | **NO — same engine as SpotBugs** |
| **SonarQube / SonarJava** | own analyzer, BUT documented to import SpotBugs, FindSecBugs, FindBugs, PMD and Checkstyle reports via `sonar.java.spotbugs.reportPaths`, `sonar.java.pmd.reportPaths`, `sonar.java.checkstyle.reportPaths` | **CONFIGURATION-DEPENDENT** |
| **PMD** | own JavaCC-based parser; rules over its own AST, with a DFA layer for control/data-flow rules | yes |
| **Error Prone** | javac plugin; uses `com.sun.*` APIs, reusing the compiler's AST and symbol table, interleaved in one pass | yes (but coupled to javac; needs compilation) |
| **semgrep** | tree-sitter parse → generic AST; taint tracking. **Community Edition is INTRAPROCEDURAL ONLY**; cross-file/cross-function requires Pro | yes |
| **CodeQL** | custom per-language extractor into a queryable database; optimized for depth and multi-step interprocedural patterns | yes |

### Three consequences

**(a) The admission test fired on its first check — that is the test working.**
SpotBugs is not a new independent tool for this project. It is FindBugs, the
tool already tested in the OWASP work, under a new name. Any "SpotBugs +
FindBugs" or "SpotBugs + FindSecBugs" pairing is ONE engine counted twice, and
would have inflated `n_tools` with self-agreement. Our diversity-aware
consensus counts distinct *tool names*, so it would not have caught this — the
SARIF driver names differ.

**→ Requirement: the supported-tool registry must record ENGINE LINEAGE, not
just tool name.** Two drivers sharing an engine must not both contribute to
`n_tools`. This is a real gap in the current implementation, applying to C/C++
equally (noted, not fixed here).

**(b) SonarQube's independence is a property of the DEPLOYMENT, not the tool.**
A SonarQube instance configured with `sonar.java.spotbugs.reportPaths` is
re-emitting SpotBugs findings under the Sonar name. Consensus between that
instance and SpotBugs is circular. Independence therefore cannot be certified
from the tool list alone; it depends on scanner configuration, which the
consuming project controls and we cannot see from SARIF.

**→ Requirement: the admission test must inspect configuration, or the pairing
must be declared unverifiable.**

**(c) semgrep CE vs CodeQL is the pattern-vs-dataflow pairing again**, which is
the exact shape that produced zero merges in C/C++ (§4).

### Verdict on A1
**Conditionally.** Genuinely distinct engines exist: SpotBugs/FindBugs, PMD,
Error Prone, semgrep, CodeQL, SonarJava-proper. Three or more is achievable.
But the naive candidate list collapses on inspection, and SonarQube may
silently duplicate another member. A1 is satisfiable, not satisfied.

### Verdict on A4
**Unknown, and it is the binding gate.** No merge rate has been measured for
any Java pair. Until it is, Java's admission is undetermined regardless of how
the engine count comes out.

---

## 3. What the existing OWASP work establishes — and what it does not

Source: VALIDATION.md, 2026-07-08. Do not re-derive.

### Establishes
- **Real labeled Java ground truth exists and was used**: OWASP Benchmark v1.2,
  2,740 human-labeled cases (1,415 real vulns, 1,325 planted false positives),
  with real SonarQube and FindBugs findings joined to the answer key. `[fetched]`.
  **A3 is already satisfied for Java** — better than for C/C++, where the
  equivalent (Lipp) is currently not even on the machine.
- **Real within-category signal**: holding category constant, tool-flagging
  correlates with truth — **74% TP when a tool flags vs 38% when none do**. A
  tool's flag is a perfect discriminator in some categories (crypto, hash:
  100% TPR / 0% FPR) and pure noise in others (cmdi, ldapi: flags everything).
- **The right signal is per-tool-per-rule reliability**, not category severity
  (matches FAULTBENCH). Not yet built.

### Does NOT establish — and the confound must be stated
- **The category-ranking negative is CONFOUNDED, not clean.** Global pooling by
  category-severity did worse than random on SonarQube (16 TPs in top-25 vs ~20)
  and no better than random on FindBugs. But OWASP Benchmark is *documented as
  engineered to defeat exactly that*: it plants plausible fakes in the scary
  categories specifically to punish shortcut learning, and its own scoring
  averages per-category on purpose. So the negative does not cleanly indict our
  ranking — **and equally, dodging a flawed test is not passing one.** Both
  halves must travel together.
- **Consensus was NEVER testable on that data.** SonarQube and FindBugs flagged
  the same case **zero** times, a CWE-normalization artifact of the scorecards.
  The headline signal had nothing to fire on. **So OWASP does not test A4
  either** — it is silent on overlap, not evidence of it.
- **NASCAR (1.08M Java warnings)** found the locational-history feature inert
  (PR-AUC 0.049 vs 0.035 random), corroborated by Kang et al. finding
  hand-crafted features "inadequate" after a data-leak fix. This is evidence
  against elaborate per-warning weighting for Java, consistent with the C/C++
  finding that simple consensus beat tool-quality weighting.

### The point that must NOT be flattened into the negative
The OWASP work paired **SonarQube + FindBugs — two genuinely distinct engines —
and found real within-category signal on real labels (74% vs 38%).** That is
*more* than the C/C++ pair has ever managed against real scanners, where
flawfinder + cppcheck produced zero merges and zero measurable agreement.

Java's evidence base is in some respects STRONGER than C/C++'s, not weaker.
The honest summary is not "Java is unproven and probably won't work." It is:
Java has real labels and a real correlation result, and lacks an overlap
measurement — while C/C++ has an overlap measurement that came back empty.

---

## 4. The C/C++ prior — what it predicts for Java

Carried in as a prior because it predicts the failure mode, `[self-tested]`
analysis over `[externally-grounded]` data (real scanners, real zlib):

> flawfinder (pattern-matching on dangerous function names) and cppcheck
> (dataflow) produced **ZERO** cross-tool merges on real code. Not weak
> agreement — none. Of 43 co-locations, 11 had a class resolved on both sides
> and 0 matched. Adding semgrep yielded 2 merges in 1,131 findings, and both
> were flawfinder+semgrep — two pattern-matchers agreeing a `printf` is a
> `printf` — in test code, none in library sources.

**Prediction for Java: semgrep CE vs CodeQL should behave the same way.**
semgrep CE is intraprocedural; CodeQL is built for multi-step interprocedural
patterns. That is the same pattern-vs-dataflow axis, and the same anti-correlated
coverage should follow. Expect low or zero overlap for that specific pair.

Corollary: the pairs most likely to satisfy A4 are those on the SAME side of the
axis — and those are precisely the pairs whose agreement carries least
independent signal. This is the overlap constraint biting from both ends, and it
is the central open risk to the premise, in any language.

**This is a prediction, not a result.** It must be measured, not assumed. It is
recorded here so that a measurement confirming it is not mistaken for a surprise,
and so that a measurement refuting it is recognized as important.

---

## 5. What the fixed `_result_key` changes for Java specifically

The two-algorithm fix (VALIDATION.md 2026-07-26) matters MORE for Java than for
C/C++, for one reason and with one new risk.

**The fp:/rk: collision would have bitten harder here.** The pre-fix key used a
tool's own fingerprint as cross-tool identity, so any fingerprint-emitting tool
could never merge with a fingerprint-free one. Java-ecosystem tools emit
fingerprints more consistently than the C/C++ pair did — CodeQL emits
`partialFingerprints`, semgrep emits `fingerprints`, and SonarQube-family SARIF
generally carries stable issue identity. Pre-fix, a Java tool set would likely
have produced `n_tools == 1` universally, exactly as the shipped C/C++ pair did,
and for the same reason.

**`[unverified]` — this expectation is from tool documentation and general
knowledge, NOT measured.** No Java SARIF has been ingested by this project since
the fix. Verifying which Java tools emit which fingerprint fields, and whether
any are degenerate, is a prerequisite (below).

**The new risk: degenerate fingerprints.** Two of the three real scanners tested
in C/C++ violated the "a fingerprint is an identity" assumption — semgrep OSS
unauthenticated emits a constant `"matchBasedId/v1": "requires login"`, and
flawfinder's `contextHash/v1` collides on repeated code. semgrep is a Java
candidate too, so the constant-placeholder failure carries over directly.

**→ Requirement: every Java candidate must be audited for BOTH fingerprint
failure modes before its findings are trusted** — constant placeholder, and
context-collision. The degeneracy check now catches both automatically, but the
audit tells us whether a tool's fingerprints are usable at all.

---

## 6. CWE class-map coverage — the map is C/C++-shaped and will not serve Java

This is the most concrete blocker, and it is larger than the independence
question.

`_CWE_CLASS` currently resolves seven classes:
`buf`, `null`, `uaf`, `uninit`, `leak`, `fmt`, `int`.

Every one is a **memory-safety** class. Java's finding profile is:

| Java finding class | typical CWE | in our map? |
|---|---|---|
| SQL injection | 89 | no |
| Command injection | 78 | no |
| XSS | 79 | no |
| Path traversal | 22 | no |
| Deserialization | 502 | no |
| XXE | 611 | no |
| LDAP / XPath injection | 90 / 643 | no |
| Weak crypto / hash | 327 / 328 | no |
| SSRF | 918 | no |

**Not one Java vulnerability class is representable in the current map.**
Class resolution for Java findings would be approximately **zero** — worse than
cppcheck's on C, where at least `null`/`uninit`/`int`/`leak` resolved. Since the
cross-tool key requires a resolvable class on BOTH sides, **no Java cross-tool
merge can occur at all until the map is extended.**

Any Java overlap measurement taken before extending the map would produce a
false negative caused by our parser — the same failure already caught once this
session, when result-only class scanning resolved 0 of 33 semgrep findings.

### The tension with the C/C++ conclusion — resolved, and NOT by the obvious rule

The C/C++ session concluded "the conservative map is close to correct as-is"
and that CWE-676 is a deny candidate. Java needs the OPPOSITE: substantial map
extension, or class resolution stays at zero and A4 can never be measured.
Whether those conflict was CHECKED rather than assumed.

**First hypothesis, REFUTED.** The obvious rule is MITRE's own abstraction
level: map Base/Variant entries, deny Class/Pillar. MITRE does say Base is the
preferred mapping level and that overly abstract Class/Pillar entries are less
useful (`[fetched]`). But checking the actual entries kills the rule:

| CWE | abstraction | MITRE mapping usage | our experience |
|---|---|---|---|
| **676** use of potentially dangerous function | **Base** | **Allowed** | **DANGEROUS for us** — spans buf, fmt, cmdi |
| **119** improper restriction within buffer bounds | **Class** | **Discouraged** | **SAFE for us** — already mapped to `buf` |

Both are backwards from the rule. So abstraction level does NOT predict
false-merge risk, and MITRE's mapping guidance answers a different question
(what to file a CVE against) than ours (when do two tools mean the same thing).

**The criterion that actually holds: CLASS-COHERENCE of the consequence set.**

> Map a CWE if everything it covers lands in ONE class of our taxonomy.
> Deny it if it spans several.

This explains every case:
- **119** is abstract, but all its descendants (120, 125, 787, …) are buffer
  issues → coherent → safe to map to `buf`.
- **676** is specific-sounding, but it is a *mechanism* ("you called a dangerous
  function"), and the mechanism's consequences differ per function: `strcpy`→buf,
  `scanf`→buf/fmt, `system`→command injection → incoherent → deny.
- **664, 758, 20, 74, 707** span essentially everything → deny.

The distinction is **effect vs mechanism**, not general vs specific. A
mechanism category collects weaknesses that share a cause but differ in
consequence, and consequence is what our classes encode.

**Applying it to Java — the tension dissolves, and the reasoning is why.**
Java's candidate CWEs are effect categories that each name one sink:

| CWE | consequence set | coherent? |
|---|---|---|
| 89 SQL injection | SQL query manipulation | yes — spans nothing |
| 79 XSS | script execution in a page | yes |
| 502 deserialization | object-graph attack | yes |
| 611 XXE | XML entity resolution | yes |
| 918 SSRF | server-side request | yes |
| 22 path traversal | filesystem path escape | yes |

Each names a specific sink with a single consequence. **CWE-89 spans nothing**,
exactly as hypothesized — and now with a stated reason rather than an
impression. So Java map extension carries **lower** false-merge risk than the
C/C++ experience suggests, and the two conclusions do not conflict: C/C++'s
problem CWEs were mechanism categories, and Java's candidates are not.

**The trap that DOES carry over** is Java's own mechanism/parent categories —
CWE-20 (improper input validation), CWE-74 (injection, generic), CWE-707. Those
are deny candidates in Java for precisely the reason 676 is in C/C++. Extending
the map is safe for the specific sinks; it is not a licence to add parents.

CAVEAT, stated because this is a design argument and not a measurement: the
coherence criterion is reasoned from CWE definitions and two fetched entries,
not from observed merge behaviour on Java data. It predicts lower false-merge
risk; it does not demonstrate it. The first Java map extension should still be
followed by a false-merge audit on real output.

### Extending it for Java — the constraint still applies
The asymmetric-error-cost rule holds: a false merge inflates `n_tools`, which
every published number rests on; a missed merge only costs recall. So each Java
class must be added on the same conservative basis, and the C/C++ session
already showed how easily this goes wrong — CWE-676 ("use of a potentially
dangerous function") spans `strcpy`, `scanf`, `strcat` and `system`, so mapping
it to one class would merge buffer, format-string and command-injection
findings. **Java's broad parent CWEs pose the same trap** (e.g. CWE-20 improper
input validation, CWE-74 injection-generic, CWE-707): they are deny candidates,
not map candidates.

The OWASP within-category result offers a principled starting order: crypto and
hash were **perfect discriminators** (100% TPR / 0% FPR), while cmdi and ldapi
were **pure noise**. Classes where a tool's flag is highly discriminating are
the ones where cross-tool agreement is most likely to mean something. Start
there; treat the noisy categories with suspicion.

---

## 7. What would move Java from unproven to validated, and at what tier

Ordered; each depends on the previous.

| # | evidence | tier it would reach |
|---|---|---|
| 1 | Extend `_CWE_CLASS` with Java classes, conservatively, deny-listing broad parents | `[self-tested]` — a code change, no claim |
| 2 | Audit each candidate's SARIF for fingerprint fields and degeneracy | `[self-tested]`, but on real tool output |
| 3 | Establish engine lineage per candidate; record it in the registry; inspect any SonarQube deployment's import configuration | `[fetched]` for lineage; the registry change is `[self-tested]` |
| 4 | **Measure the cross-tool merge rate for each candidate pair on a real Java codebase** (A4) | `[externally-grounded]` — real tools, real code, non-Claude input |
| 5 | If a pair clears A4: re-run the OWASP within-category analysis using CONSENSUS rather than single-tool flagging, and compare against the 74%/38% single-tool baseline | `[standard-checked]` — real labels, our harness |
| 6 | Independent judge on the ranked output over real labeled Java data | `[externally-verified]` — the only step that moves an implementation tier |

**Nothing short of step 4 permits any claim about Java consensus**, and step 4
is currently unstarted. Steps 1–3 are prerequisites that produce no claim by
themselves.

---

## 8. Honest summary

- Java **passes A3 today** (real labels exist and have been used) — ahead of
  C/C++, whose corpus is not currently in hand.
- Java **can satisfy A1**, but the obvious candidate list does not: SpotBugs is
  FindBugs, FindSecBugs is a SpotBugs plugin, and SonarQube may be re-emitting
  either. Engine lineage must be recorded, and the tool does not currently
  track it — a real gap that affects C/C++ too.
- Java **fails A2/A4 in practice today** for a reason that is ours, not the
  tools': the CWE class map contains no Java class, so cross-tool merging is
  structurally impossible before it is extended.
- The C/C++ prior predicts the pattern-vs-dataflow pairing will not overlap.
  That prediction is unmeasured and must not be treated as a result.
- The strongest thing in Java's favour is not speculative: **two genuinely
  distinct engines produced a real 74% vs 38% correlation on real labels.** No
  C/C++ pair has matched that against real scanners. Java's problem is a missing
  overlap measurement, not a demonstrated absence of signal.

No tier claimed for Java in this document. `[fetched]` applies to the lineage
and engine-basis findings in §2 only.

## Sources (§2 lineage, `[fetched]`)
- SpotBugs — <https://github.com/spotbugs/spotbugs> and `spotbugs/src/main/java/edu/umd/cs/findbugs/FindBugs2.java>`
- Find Security Bugs — <https://github.com/find-sec-bugs/find-sec-bugs>, <https://owasp.org/www-project-find-security-bugs/>
- SonarQube external analyzer reports — <https://docs.sonarsource.com/sonarqube-server/2025.4/analyzing-source-code/importing-external-issues/external-analyzer-reports>
- Error Prone installation/architecture — <https://errorprone.info/docs/installation>
- PMD — <https://pmd.github.io/>
- Semgrep dataflow engine (CE intraprocedural) — <https://semgrep.dev/docs/writing-rules/data-flow/data-flow-overview/>
- Semgrep vs CodeQL engine comparison — <https://konvu.com/compare/semgrep-vs-codeql>
