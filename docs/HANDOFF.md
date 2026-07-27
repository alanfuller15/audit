# HANDOFF — read this BEFORE GENESIS_TEMPLATE.md, before any tool call

You are a fresh session inheriting an active project. This document is not
background reading. It is an **operating gate** you execute. It exists because
the prior session repeatedly failed one specific way, and the failure is
predictable enough to intercept. This design is grounded in external evidence
(cited inline), not in the prior session's self-assessment.

────────────────────────────────────────────────────────────────────────
## 0. THE FAILURE YOU WILL REPEAT UNLESS YOU GATE AGAINST IT

You will feel a pull to answer from what you already know, and to act — write
code, run an oracle, propose a fix, declare a claim validated — BEFORE searching
an external source. That pull is the error. The prior session had the search
tool available, knew the rule, and still had to be prompted to search every
single time. Do not make the user prompt you. If the user is telling you to
search, you have already failed the gate.

This is a documented LLM failure mode, not a personal quirk: models
"over-weight immediate local context relative to higher-level directives"
(ContextCov, arXiv 2603.00822), and prompt-only instruction files achieve only
~67% constraint compliance — self-reflection alone is WORSE at ~50%. What raised
compliance to ~88% was compiling constraints into ACTIVE checks the agent emits
and self-corrects against, not prose it reads. Hence this gate is written as an
emitted checklist, not a description.

────────────────────────────────────────────────────────────────────────
## 1. THE SEQUENCE (non-negotiable order)

    STUDY → REFRAME → TEST → IMPLEMENT → COMMIT

- STUDY   = search a trusted external source FIRST. Not your priors. Not the
            sandbox. Learn how the thing is actually defined/done by people who
            established it.
- REFRAME = restate the problem in light of what STUDY changed. Often STUDY
            reveals the question itself was wrong (see prior session: the
            per-finding oracle was invalid because the ground truth for it does
            not exist — only STUDY of the source methodology revealed that).
- TEST    = run it, faithful to the studied methodology, cross-checked against
            an external number where one exists.
- IMPLEMENT / COMMIT = only after the above. Commit means: write to VALIDATION.md,
            move a provenance tier, ship a bundle, or tell the user a claim holds.

You may COMPRESS this sequence only when STUDY would re-confirm a settled,
non-changing fact (see the anti-compulsion rule in §3). You may never SKIP it
for anything whose current state could differ from your priors, or anything you
are about to commit.

────────────────────────────────────────────────────────────────────────
## 2. THE COMMIT GATE (emit this block before any commit-class action)

Before writing implementation code, moving a tier, shipping, or asserting a
claim is validated, EMIT this and answer it in-line. Naming the specific missing
next-action (not a yes/no) is the form shown to actually lift compliance across
Claude/GPT/Gemini by +12pp (PolicyGuard PG-Checklist, arXiv 2606.29225):

    COMMIT GATE
    - What am I about to commit? .....................................
    - Did I STUDY an external source for THIS, in THIS session?
        - If yes: cite it. ..........................................
        - If no: the required next action is to search for <X>. Do that
          FIRST, then return here. Do not proceed.
    - Is this design-grounding or implementation-verification?
        (searching moves DESIGN tiers; only an external judge on real data
         moves IMPLEMENTATION tiers — do not conflate them)
    - What external verifier confirms "done"? A self-assessment does NOT
      count (QGP, arXiv 2605.23574: bind completion to an external verifier,
      never to the agent's own "looks done"). .......................

If any line cannot be answered, you are not at COMMIT. Return to the sequence.

────────────────────────────────────────────────────────────────────────
## 3. ANTI-COMPULSION RULE (do not over-fire the gate)

Searching is not free virtue. LLMs "frequently initiate self-verification even
where it rarely alters the result, incurring cost with limited benefit"
(Self-Verification Dilemma, arXiv 2602.03485). The user's own ZERO-LOSS PRINCIPLE
governs: search only where the result — positive, negative, OR empty — would
change epistemic state. A confirmed dead-end is first-class useful. Re-confirming
a settled, non-changing fact is fluff.

So: the gate fires at COMMIT/IMPLEMENT/TIER-CHANGE points, NOT at every step.
Routine, non-committing reasoning does not need a search. If STUDY for a step
would only re-confirm something already grounded IN THIS SESSION, note that and
skip. The skill is discriminating which searches change state — not searching
maximally, and not searching minimally.

────────────────────────────────────────────────────────────────────────
## 4. TOOL REALITY (verified capabilities of this environment)

- The sandbox bash has NO network. But web_search AND web_fetch DO work.
- web_fetch reaches: prior-search URLs, published-paper PDF hosts (e.g.
  mediatum.ub.tum.de), Zenodo RECORD/metadata pages, OASIS docs.
- web_fetch CANNOT reach: GitHub raw (robots), Zenodo /preview/ file endpoints
  (robots), or Zenodo ?download=1 file BYTES (returns unrenderable octet-stream).
  Confirmed workaround: the user hand-downloads the file on their device and
  re-uploads it to /mnt/user-data/uploads/. This WORKS and is the standing
  method for gated file payloads.
- You CAN pull accessible files directly in-session. The prior session failed to
  do this proactively. Do it without being asked.

────────────────────────────────────────────────────────────────────────
## 5. PROVENANCE TIERS (the commit vocabulary — from GENESIS charter III.7)

  [fetched]              validated vs a fetched published source
  [corroborated]         multiple independent sources agree
  [standard-checked]     validated vs a fetched published standard
  [externally-grounded]  non-Claude engine/data anchors it (design principle)
  [externally-verified]  external judge on real data confirms the IMPLEMENTATION
  [self-tested]          sandbox PASS = Claude grading Claude = WEAKEST

RECURRING TRAP: design-grounding ≠ implementation-verification. Searching moves
design tiers. Only an external judge on real data moves implementation tiers.
State the tier on every claim you commit, and state its honest bound.

────────────────────────────────────────────────────────────────────────
## 6. CURRENT PROJECT STATE (tier-tagged; verify, don't trust this list)

Validated (see VALIDATION.md for full provenance + cross-checks):
- Diversity-consensus PRINCIPLE: [externally-grounded]. Spearman rho=+0.700
  (n_tools vs recall) on real Lipp et al. ISSTA'22 CVE data (192 CVEs, 6 tools,
  27 real C projects). Reconstruction cross-checked against the paper's own
  published figures (CommSCA 53.9%, all-tools 68.9%, +15pp lift). Zenodo DOI
  10.5281/zenodo.6515687, CC-BY-4.0.
- Ingest/dedup/consensus-ranking MACHINERY: moved toward [externally-grounded].
  audit.py --ingest on real PHP multi-tool findings (22,403 findings, 6 tools):
  dedup 22,403→21,061 (matches hand-computed exactly), recovered 1,318 overlaps
  (matches exactly), our-tool Spearman(n_tools,score)=+0.649 reproduces the
  validated principle. HONEST BOUND: real findings + real overlap, but the SARIF
  ENVELOPE was reconstructed (Lipp isn't shipped as SARIF).
- SARIF format conformance: [standard-checked] vs fetched OASIS schema.
- Three real bugs found via external execution + fixed + regression-tested:
  (1) no --help handler; (2) empty SARIF raised a false parse alarm;
  (3) --run-tests (same class) — root-caused: PROJECT_DIR now resolved as first
  non-flag arg. All verified across 5 invocation shapes; real ingest byte-stable.
- Consensus RE-RANKING at FILE level: **RETIRED 2026-07-26 — DO NOT CITE AS
  CURRENT STATE.** This row formerly read "[externally-verified] (2026-07-11) …
  ROC-AUC 0.755 vs 0.596 best single tool … PofB@20% = 0.655 … 1 tool 0.9% ->
  4 tools 11.6%". Every one of those figures has been withdrawn:
    * 0.755 is NOT effort-aware, and ManualDown — ranking files by DESCENDING
      SIZE, reading no tool output — scores 0.845 on the same data.
    * The effort-aware "win" was measured against ManualDown, which is the
      NON-effort-aware baseline. Against ManualUp it is not significant.
    * The remaining IFA/PMI advantage does not survive a SIZE-MATCHED control.
  See item 0g and VALIDATION.md "0g CONCLUSION". The README no longer quotes any
  of these. WHAT SURVIVES: multi-tool functions are ~1.5x more likely to contain
  a real CVE than SIZE-MATCHED single-tool functions — a precision finding, NOT
  a ranking claim. CONFIRMED 2026-07-26 by item 0j against strata refined to
  10/50/100/200 and exact-LOC, and by continuous covariate adjustment (OR 1.39).
  **But the accompanying `p<0.0001` is WITHDRAWN** — it conditioned on one arm.
  Honest significance is p~0.03-0.08 unclustered, p~0.001 clustered on project,
  project-bootstrap 95% CI [0.99x, 2.58x]. Marginal, not overwhelming. And it
  supports ">=2 tools beats 1" ONLY — the response is flat at 3 tools and
  point-estimate negative at >=4, so n_tools is not a graded confidence signal.

Tested and REJECTED (do not re-attempt as pending work):
- Tool-quality WEIGHTING layer. Tested on real data and it does NOT beat plain
  tool-counting: tier-weighting ~even with flat consensus, and a separate
  large-scale test (NASCAR, 1.08M Java warnings) found the locational-history
  feature inert (PR-AUC 0.049 vs 0.035 random). Independently corroborated by
  Kang et al. (hand-crafted features "inadequate" after a data-leak fix). Fine
  per-tool weights do not transfer across projects; only a coarse tier prior
  does. CONCLUSION: the tool's value is the SIMPLE consensus signal. This was
  formerly PENDING item 2(b); it is closed by evidence, not deferred.
- FUNCTION-level ranking. Out of scope, and CONFIRMED so 2026-07-26 by a
  stronger route: at function level consensus scores PofB@20 = 0.185 against
  random's 0.199, i.e. at-or-below chance once effort is priced (Mende &
  Koschke's documented phenomenon). The older rationale (0.9% base rate,
  ROC-AUC 0.628) stands but the phrase "the proven value is FILE-level triage
  only" is WITHDRAWN — file-level ranking is no longer a proven value either.
  See 0g.

## 6.1 THE HEADLINE SIGNAL IS INERT IN THE SHIPPED PRODUCT — CONCLUSION STANDS,
##     MECHANISM CORRECTED 2026-07-26. The cause described below was FIXED by
##     item 2; the zero it predicted is still real, for a DIFFERENT reason.
##     Full scoping: docs/SCOPE_shipped_consensus_defect.md

>>> READ THIS BEFORE THE ORIGINAL TEXT. The original root cause — `_result_key`
>>> using the SAME-tool fingerprint algorithm as the CROSS-tool consensus key —
>>> NO LONGER EXISTS IN THE TREE. Item 2 split them: `_result_key` is same-tool
>>> only (fp:/rk:) and `_cross_keys` is cross-tool (location + CWE class).
>>> Verified against src/audit.py, not inherited.
>>>
>>> THE CONCLUSION IS UNCHANGED AND STILL MEASURED: the shipped flawfinder +
>>> cppcheck pair produces ZERO cross-tool merges on real zlib. But it now
>>> stands on §6.2's finding — the pair's CWE-class profiles are near-disjoint
>>> (flawfinder fmt/buf; cppcheck null/uninit/int), so of 14 exact co-locations
>>> 10 had classes on both sides and 0 matched. That is a SEMANTIC blocker, not
>>> a key-construction one.
>>>
>>> WHY THE DISTINCTION MATTERS RATHER THAN BEING PEDANTRY: the old cause was
>>> ours and fixable by us; the current one is a property of the two tools'
>>> coverage and is NOT fixable by us. A session reading the stale mechanism
>>> would go looking for a bug in the key construction that is not there, and
>>> might "re-fix" a fix. §6.2 governs what to do instead, and its answer is
>>> that no purchase resolves it.
>>>
>>> The independently-sufficient second blocker below (disjoint ruleId
>>> namespaces) is also SUPERSEDED: `_cross_keys` matches on CWE class as well
>>> as ruleId precisely so that differing ruleIds cannot block a merge alone.

[ORIGINAL TEXT, retained so the reasoning is auditable — but see the block
above before acting on any of it.]

The shipped action runs exactly flawfinder + cppcheck. That pair CANNOT produce
n_tools>1 on ANY input:
- real flawfinder emits `fingerprints: {"contextHash/v1": <sha256>}` on 6/6
  results, so `_result_key` returns `fp:…` for every flawfinder finding;
- cppcheck (both documented paths) emits none, so it returns `rk:…`;
- an `fp:` key can never equal an `rk:` key. Not a sample property — a property
  of the key construction.
Independently sufficient second blocker: disjoint ruleId namespaces
(flawfinder `FF1013` vs cppcheck `CWE-415` or a check name).
Measured: `n_tools distribution: {1: 15}`, `ANY cross-tool merge: False`.

WHAT THIS DOES AND DOES NOT MEAN:
- It does NOT refute ROC-AUC 0.755. That number stands on its own data.
- It IS a transfer gap: 0.755 was measured on reconstructed envelopes that DID
  merge; the shipped config does not reproduce those conditions.
- Root cause: `_result_key` uses DefectDojo's SAME-tool dedup algorithm as a
  CROSS-tool consensus key. DefectDojo uses two algorithms to avoid exactly this.
  [SUPERSEDED — fixed by item 2. See the block at the top of §6.1.]
- The URI-mismatch blocker claimed earlier in this session was a harness
  artifact and is WITHDRAWN — both tools emit the same relative path.

Mitigating and worth knowing: the signal gate correctly reports
`informative here = ['severity']` in this state — the tool discloses that
consensus is not firing rather than silently pretending. The honesty machinery
works; the configuration is what is wrong.

Untestable with existing public data (do not waste effort re-attempting):
- Per-finding PRECISION competence-rho of the confidence signal. The source
  paper states plainly it has NO per-finding precision ground truth; none exists
  in comparable public datasets. This is a ground-truth-EXISTENCE limit, not an
  access limit. Reopen ONLY with self-run tools + manual per-finding labeling.

────────────────────────────────────────────────────────────────────────
## 6.2 ACQUISITION IS NOT THE LEVER (established 2026-07-26, measured 3x)

READ THIS BEFORE PROPOSING TO INSTALL OR BUY ANY SCANNER.

The consensus premise has now failed to produce observable agreement three
times, in three configurations, for three different proximate reasons:

  1. flawfinder + cppcheck (C/C++, real zlib)
     Anti-correlated CLASS coverage — fmt/buf vs null/uninit/int.
     14 exact co-locations, 0 with matching class.            -> 0 merges
  2. + semgrep as a THIRD tool (same corpus)
     2 merges in 1,164 findings — and both were flawfinder+semgrep, the two
     most METHODOLOGICALLY SIMILAR tools, in benchmark code, none in library
     sources.                                                  -> ~0 merges
  3. SpotBugs + semgrep (Java, real Struts)
     CLASSES MATCHED EXACTLY (redirect/redirect). LOCATIONS did not — semgrep
     anchored at the taint SOURCE (line 244), SpotBugs at the SINK (247).
                                                               -> 0 merges

A FOURTH TOOL BRINGS A FOURTH ANCHORING CONVENTION and another pair that may
not co-locate. **CodeQL is interprocedural and would anchor differently again,
so Rosetta does NOT answer this question and must not be installed on the theory
that it might.** The same applies to semgrep Pro, SonarQube Developer Edition,
or any other purchase.

THE ACTUAL CONSTRAINT, stated once:
> The PREMISE values METHODOLOGICAL DIVERSITY — tools with different methods
> have different blind spots, so their agreement is independent evidence.
> The MECHANISM requires CO-LOCATION — same file, same line, same class.
> These pull AGAINST each other. The more methodologically different two tools
> are, the less likely they are to describe the same bug at the same line.
> **Nothing purchasable resolves that.**

WHAT REMAINS GENUINELY OPEN, in priority order:
  1. [SETTLED 2026-07-26 — THE PRECONDITION HAS MOVED. See the acquisition note
     below, which this changes.] DIRECTION B was evaluated against a
     pre-registered decision rule and PASSED all four gates (yield 36.9%,
     same-bug 100%, median producing span 2 lines, deterministic). Range
     containment is SHIPPED and covered by the harness. The sizing recorded
     below — "degenerates to exact matching in the common case" — was a PRIOR
     and the measurement REFUTED it. Retained only so the prior is not
     re-derived. Original text:
     DIRECTION B — bounded evaluation of point-in-range matching, on the
     minority of findings where a genuine multi-line range exists. Sized
     2026-07-26: reachable with data on disk, but SpotBugs omits endLine on
     70-89% of results and semgrep's range is usually a single line, so it
     degenerates to exact matching in the common case. Worth measuring; not a
     fix. Requirements in item 0e (measure source-sink SEPARATION, do not sweep
     a window, do not treat TOL=3 as validated).
  2. Whether any principled ENTITY-LEVEL match exists WITHOUT a Java/C parser.
     Direction A is blocked today: SpotBugs emits logicalLocations on 100% of
     results, semgrep on 0%, and matching needs both sides.
  3. Whether the honest description is SAME-METHODOLOGY agreement — and if so,
     the CLAIM CHANGE that entails. This is not a caveat: the README's premise
     is that DIFFERENT tools agreeing is the signal, the 0.755 provenance rests
     on Lipp's six methodologically diverse tools, and the ensemble literature
     specifically distinguishes correlated-error agreement as weaker. Adopting
     it means rewriting the headline, not annotating it.

>>> NO FURTHER TOOL ACQUISITION IS WARRANTED UNTIL ONE OF THOSE THREE IS
>>> SETTLED. Acquisition adds pairs; it does not address whether any
>>> methodologically-diverse pair can produce agreement this mechanism can see.
>>>
>>> STATUS 2026-07-26 — THE PRECONDITION HAS PARTIALLY LIFTED, AND THAT IS
>>> RECORDED HERE RATHER THAN LEFT FOR SOMEONE TO NOTICE. Question 1 IS NOW
>>> SETTLED: Direction B was pre-registered, passed all four gates, and shipped.
>>> Read literally ("until ONE of those three is settled") the acquisition bar
>>> is now met.
>>> DO NOT TREAT THAT AS AUTHORISATION TO BUY ANYTHING. The bar was a proxy for
>>> the real question, and the real question — stated in THE ACTUAL CONSTRAINT
>>> above — is untouched: methodological diversity and co-location pull against
>>> each other, and nothing purchasable resolves that. What Direction B settled
>>> is that TOLERANT matching recovers real agreement WITHIN existing pairs; it
>>> says nothing about whether a NEW pair would co-locate.
>>> Evidence since, pointing the same way: on the one real-code cross-tool
>>> agreement ever observed, the two rules are a rule and its own ancestor
>>> (0f, confirmed). Adding a fourth tool does not address that either.
>>> THE OPERATIVE BAR IS NOW QUESTION 3 — whether the honest description is
>>> same-methodology agreement, and the claim change that entails.

────────────────────────────────────────────────────────────────────────
## 7. PENDING WORK (REORDERED 2026-07-26 by a structural finding — read §6.1)

THE FINDING THAT REORDERED THIS: the shipped flawfinder+cppcheck pair CANNOT
produce n_tools>1 on any input. flawfinder emits `fingerprints` on every result
so `_result_key` returns `fp:…`; cppcheck emits none so it returns `rk:…`; the
two can never collide. The headline consensus signal is structurally inert in
the shipped product. Full scoping: docs/SCOPE_shipped_consensus_defect.md.

0. [IMPLEMENTED 2026-07-26 — one OPEN DECISION remains, see 0a] Engine-lineage
   guard. The merge guard now intersects ENGINE LINEAGE, not driver name;
   n_tools counts distinct ENGINES; quality weighting takes one representative
   driver per engine; unknown tools default to their own name so nothing
   regresses. 25-check harness passing; real zlib ingest unchanged (2 merges).
   Full record: VALIDATION.md 2026-07-26 "Engine-lineage guard implemented".

0a. [IMPLEMENTED 2026-07-26] The SonarQube case. Conservative default +
   operator escape hatch (AUDIT_INDEPENDENT_TOOLS). Both directions disclosed.
   Record: VALIDATION.md "0b + 0a implemented". Original decision below.
   Current shipped behaviour DISCLOSES but does not PREVENT: SonarQube's lineage
   (`sonarqube`) differs from SpotBugs' (`findbugs`), the guard only blocks
   IDENTICAL lineages, so the documented exploit still scores n_tools=2 with a
   loud warning. Verified through the real CLI.

   DECISION: **option (b) — conservative default, with an operator declaration
   as the escape hatch.** Do NOT count SonarQube agreement with an importable
   tool (findbugs/pmd/checkstyle) as consensus unless the operator declares
   independence. NOT the "declaration flag with permissive default" framing —
   the DEFAULT must be conservative, not permissive.

   REASONING (inventor's, recorded because it generalizes to future cases):
   everywhere else in this codebase uncertainty resolves to NO-MERGE —
   unresolvable CWE class, denied CWE, unknown tool lineage, degenerate
   fingerprint. Option (a) would be the ONLY place uncertainty resolves to
   merge-with-a-note. The asymmetric-cost rule does not get an exception because
   the ambiguous case happens to be uncommon.

   GENUINE COUNTER-ARGUMENT, recorded because it is real and a later session
   should not think it was overlooked: SonarJava analysing independently IS the
   default SonarQube configuration and report-importing is OPT-IN, so (b)
   under-counts the COMMON case. What makes that acceptable is the escape hatch
   specifically: the operator who set up the import is exactly the person in a
   position to declare the relationship. The cost lands on the party with the
   knowledge to remove it.

   DONE. 0b was implemented first, as required.

   SCOPE NOTE (2026-07-26, narrows but does not overturn the decision):
   0a's suppression guards SonarQube agreement with an importable tool. But
   SonarQube **Community Build has NO taint analysis** — injection detection
   starts at Developer Edition [fetched] — so free-tier users cannot reach the
   guarded case at all, because their SonarQube cannot produce the injection
   findings that would agree with SpotBugs in the first place.
   The decision STANDS: it generalizes to any import-capable tool, and paid
   SonarQube deployments are real and are exactly where an enterprise CI would
   hit the exploit path. But its PRACTICAL scope is narrower than it appeared
   when decided, and a later session should not cite 0a as evidence that the
   suppression is frequently exercised.

0b. [IMPLEMENTED 2026-07-26 — was a PRECONDITION of 0a] `lineage_warnings` was in
   the JSON output but `audit_html_report.build()` did not render it — same shape as the
   display-dedup gap. On the Action path the caveat informs NOBODY.
   WHY THIS GATES 0a: option (a)'s entire justification was "the operator is
   informed," which is false on the Action path today. And under the chosen
   option (b) it matters just as much in the other direction — if consensus is
   silently WITHHELD, the operator needs to see WHY, or the tool has traded an
   inflated signal for an unexplained one. Withholding without disclosure would
   be its own honesty failure.
   Fix the render REGARDLESS of which way 0a goes.

   CONCRETE, in shipped code. Phase 2's diversity guard in ingest_sarif is:
       if recs[a]["tools"] & recs[b]["tools"]: continue
   — a set intersection on driver NAME. Two drivers of ONE engine pass it.
   The diversity-aware merge is not currently diversity-aware; it is NAME-aware.

   EXPLOIT PATH, no adversary required — a plausible enterprise CI:
     run SpotBugs -> import the report into SonarQube via
     sonar.java.spotbugs.reportPaths -> feed BOTH the SpotBugs SARIF and the
     SonarQube SARIF to `audit.py --ingest`.
   Same findings, two driver names, n_tools=2 on pure self-agreement. The
   ranking then promotes those findings as "two independent tools agree."
   Lineage facts are [fetched], docs/SPEC_java_admission.md §2: SpotBugs IS
   FindBugs (fork, source still under edu/umd/cs/findbugs/); FindSecBugs is a
   SpotBugs PLUGIN; SonarQube imports SpotBugs/FindBugs/FindSecBugs/PMD/
   Checkstyle reports.

   MINIMUM VIABLE FIX: an engine-lineage field per KNOWN tool, DEFAULTING TO
   THE TOOL'S OWN NAME for unknowns; the guard intersects LINEAGE, not name.
   Unknown tools keep current behaviour exactly, so nothing regresses.
   Seed lineages: SpotBugs/FindBugs/FindSecBugs -> "findbugs";
   Cppcheck -> "cppcheck"; Flawfinder -> "flawfinder"; Semgrep* -> "semgrep";
   CodeQL -> "codeql"; SonarQube -> "sonarqube" BUT see below.
   SonarQube is CONFIGURATION-DEPENDENT — it may be re-emitting another
   engine's findings. Lineage cannot be certified from SARIF alone. Options:
   treat a SonarQube driver as lineage-unknown-but-suspect, or require the
   operator to declare it. Do not silently assume independence.
   Regression test to add: two drivers of one lineage must NOT produce
   n_tools>1; two drivers of different lineage must still merge as today.

0e. [CLOSED 2026-07-26 — DIRECTION B WAS EVALUATED AND IS SHIPPED. The header
   below described it as an open experiment; that is stale. Verified in the
   tree: `edges_by_rule` carries a "range-containment" bucket, merges are
   tagged with `merge_rules`, and the harness covers it.
   The pre-registered rule (VALIDATION.md "DIRECTION B PRE-REGISTRATION") was
   fixed BEFORE computing and ALL FOUR GATES PASSED:
     (a) material yield      427 new pairs = 36.9% of merges   (>=10%)   PASS
     (b) same-bug rate       100%                              (>=80%)   PASS
     (c) false-merge risk    median producing span 2 lines; 0% over 100  PASS
     (d) determinism         order-independent                          PASS
   So the "REQUIREMENTS on any future evaluation" below were MET, not deferred,
   and the prior recorded there ("point-in-range degenerates to exact matching
   in the common case") was REFUTED by the measurement. Do not re-open this as
   an experiment; the finding text is retained for its reasoning only.]
   [former header: FINDING — exact-line matching cost 100% of real-code
   agreement, ONE case]
   On Apache Struts the SpotBugs+semgrep pair produced ZERO merges. Not a path
   artifact (0c clean) and not disagreement — the two tools agreed EXACTLY ONCE
   and the key missed it by THREE LINES:
     ServletRedirectResult.java
       semgrep  line 244  class=redirect  (anchors at the taint SOURCE/method sig)
       SpotBugs line 247  class=redirect  (anchors at the SINK instruction)
   Same file, same class, same bug. Scoring requires an EXACT line match; the
   display layer's TOL=3 would have caught it.
   THE DESIGN QUESTION THIS RAISES: exact-line was chosen deliberately, because
   a tolerance window makes merging order-dependent and a false merge inflates
   n_tools. That reasoning stands. But the measured cost on real code is now
   known and it is total — on generated code both tools point at the same line;
   on real code they anchor at different points of the same dataflow.
   THIS IS NOT LINE JITTER — IT IS STRUCTURAL. semgrep anchored at the taint
   SOURCE (method signature); SpotBugs at the SINK (`response.sendRedirect`).
   That is a property of PATTERN-vs-DATAFLOW analyzer pairs, not noise, and it
   predicts the same miss RECURS SYSTEMATICALLY wherever those two kinds of tool
   agree. The 3-line gap is not a small error to be absorbed; it is the distance
   between two different — and each correct — answers to "where is this bug".

   SO TOL=3 CAUGHT THIS CASE BY LUCK. Source-to-sink distance is ARBITRARY:
   same function here, different functions elsewhere — which is already on
   record as the open cross-function source/sink problem. A tolerance WINDOW is
   the WRONG SHAPE OF FIX for a structural mismatch: it happens to work when the
   sink is near the source and fails otherwise, with no principled cutoff.

   REQUIREMENTS on any future evaluation of tolerant matching:
     - It MUST measure SOURCE-SINK SEPARATION DISTANCES on real code, not sweep
       a fixed window. The question is the distribution of that distance, not
       "what is the best TOL".
     - It MUST NOT treat TOL=3 as validated by this instance. One case that
       happened to fall inside the window is not evidence the window is right;
       it is one draw from an unmeasured distribution.
     - Order-dependence and false-merge rate still have to be answered before
       adoption. Deterministic construction (union-find over a tolerance graph,
       as the display pass already does) is necessary but not sufficient.
   File as its own experiment, not a patch.

   SAME FINDING AS THE C/C++ RESULT, FROM THE OPPOSITE ANGLE:
     zlib   — flawfinder vs cppcheck: classes ANTI-CORRELATED (fmt/buf vs
              null/uninit/int). 14 co-locations, 0 class matches.
     Struts — semgrep vs SpotBugs: classes MATCHED EXACTLY (redirect/redirect),
              LOCATIONS did not (244 vs 247).
   Two different mechanisms, ONE consequence: **pattern tools and dataflow tools
   do not produce CO-LOCATED agreement, and the consensus premise AS IMPLEMENTED
   requires co-location.** Measured twice, in two language ecosystems, on two
   corpus types. That it generalizes as a structural law is a HYPOTHESIS; that
   it happened both times is measured.

   >>> THIS IS NOW THE CENTRAL OPEN QUESTION FOR THE PREMISE — above tool
   >>> selection (0d/A4) and above class-map coverage (item 3). Those are
   >>> questions about WHICH tools and WHETHER we can read them. This is a
   >>> question about whether the agreement the premise depends on is
   >>> OBSERVABLE AT ALL between methodologically different tools, which is
   >>> exactly the pairing the diversity argument says is most valuable.
   >>> Resolve or bound this before spending further on tool acquisition.

0d. [FINDING — UNDERPOWERED TEST, NOT A MEASURED ABSENCE OF EFFECT]
   Consensus vs best single tool on OWASP Benchmark: the comparison DID NOT
   RESOLVE. Do NOT cite 0d as evidence consensus fails to beat the best tool —
   the test cannot distinguish the observed effect from zero.
   POWER, computed not assumed:
     minimum detectable effect at n=1,156 merges vs n=1,848 semgrep: ~4.0pp
     observed effect: +2.1pp  ->  BELOW the detection threshold
     to resolve +2.1pp at p<0.05: ~7,562 per group (balanced), or ~107,000
       merges holding the semgrep comparator at its actual 1,848
   Both "consensus adds ~2pp" and "consensus adds nothing" are consistent with
   this data. The file-level view reached p=0.063 with the SAME SIGN, which is
   weak corroboration of a small positive effect, not of its absence.
   Measured 2026-07-26 on the same corpus and labels used for the 7a audit:
       base rate 51.6% · SpotBugs+FSB 64.0% · semgrep 68.3% · CONSENSUS 70.4%
       consensus vs semgrep: +2.1pp, z=1.20, p=0.232   NOT significant
       file-level          : +3.5pp, z=1.86, p=0.063   NOT significant
       consensus vs SpotBugs: +6.4pp, p=7.9e-05        significant
   Consensus beats the WEAKER tool significantly. Against the STRONGER one the
   test is underpowered and returns no verdict. It also surfaces 1,156 findings
   where semgrep alone surfaces 1,848.
   THE SYNTHETIC BOUND APPLIES TO THE NEGATIVE TOO — HYPOTHESIS, NOT FINDING:
   on a corpus where every file contains exactly one planted bug drawn from a
   category BOTH tools cover, single tools should perform unusually well. That
   is close to the condition LEAST favourable to consensus, whose value comes
   from covering what one tool misses. So a null result here is weak evidence
   about real code, in the same way and to the same degree that the positive
   enrichment was. The negative generalizes no further than the positive did.
   Stated as a hypothesis because it is not tested.
   WHY THIS MATTERED AT THE TIME: the README then said 0.755 "beats a coin flip
   and the best single tool", phrasing sourced from LIPP's C/C++ result
   (0.755 vs 0.596). This was the first time the SHIPPED IMPLEMENTATION had been
   measured against a single-tool comparator on any corpus, and it did not clear
   that bar — though on one synthetic corpus with one tool pair, which was NOT
   then grounds to amend the README.
   [STATUS 2026-07-26: OVERTAKEN. The README no longer quotes 0.755 or any
   ranking performance figure — see 0g and the README's "What's established, and
   what isn't". This item is retained as the record of when the single-tool
   comparator was first run, not as a live description of the README.]
   IT IS grounds to (a) not generalize the Java enrichment, and (b) run the same
   comparator on any future corpus BEFORE claiming consensus adds value there.
   The comparator is cheap: scratchpad/single_vs_consensus.py.

0j. [CLOSED 2026-07-26 — the 1.5x SURVIVES; the `p<0.0001` DOES NOT.
   The README needs a fourth correction, but NOT the one anticipated.]
   Full record: VALIDATION.md "0j RESULT". Scripts: analysis/scripts/run_0j.py
   and fix_clusterperm.py; output in analysis/results/.

   THE PRE-REGISTERED CHECK RAN AND WENT THE OTHER WAY. Matched ratio by strata:
   1.51x (K=10), 1.43x (20), 1.47x (50), 1.53x (100), 1.52x (200), 1.31x (exact
   LOC). It does NOT decay. The hypothesised cause of the disagreement — "decile
   matching leaves large residual size variation within strata" — was MEASURED
   AND REFUTED: size imbalance is +8.1% at K=10 and -0.3% by K=50, and the ratio
   does not move when it vanishes. Deciles were adequate here.
   (K=500/1000 rise to 1.83x/1.91x is control-pool depletion, NOT a growing
   effect — at K=1000, 16.8% of multi units have <5 distinct controls. Do not
   quote those.)

   SO THE HANDOFF'S OWN FALLBACK BRANCH FIRED, AND IT WAS RIGHT: the
   linear-in-n_tools specification was the suspect. As a factor + log(LOC):
   n_tools=2 OR=1.47 (p=0.051), =3 OR=1.35 (p=0.273), >=4 OR=0.67 (p=0.478).
   Levels 5-6 are perfect separation (0 vulnerable in 35 units) and had to be
   collapsed. Essentially ALL the effect is the 1->2 step and the response is
   flat-to-falling above it, so a single linear slope averages to ~0. 0i's
   p=0.582 was a FUNCTIONAL-FORM ARTIFACT, not an absence of signal.
   0i's actual finding (not orderable under an effort budget) is UNAFFECTED.

   THE TWO METHODS NEVER DISAGREED — THEY ESTIMATED DIFFERENT QUANTITIES. 0i
   fitted n_tools as a continuous slope; the matched test is a binary
   multi(n>1) vs single(n=1) contrast. Fit the MATCHING contrast with continuous
   log(LOC) and you get OR=1.39, p=0.076 — agreeing with the 1.47-1.52x from
   fine matching. Record this: the apparent contradiction that made 0j urgent
   was an estimand mismatch, and comparing a factor contrast against a linear
   slope will produce the same false alarm again.

   >>> WHAT IS ACTUALLY WRONG WITH THE README: `p < 0.0001`. <<<
   That statistic held the multi group's own 81/5,269 FIXED and resampled only
   the controls, ignoring sampling variability in the numerator population.
   Honest tests that vary both arms: two-proportion z p=0.041-0.054;
   within-stratum permutation p=0.030-0.058; logistic p=0.076. Clustered on
   project (informative cells only) p=0.0008 at K=50. Project-level cluster
   bootstrap 95% CI: [0.99x, 2.58x], median 1.51x.
   THE EFFECT IS MARGINAL, NOT OVERWHELMING. The error is independent of the
   strata question and would have been there at any K.

   CLUSTERING CHECKED: direction consistent in 9/9 projects; leave-one-project-
   out 1.25x-1.61x, so no single project carries it. But nine clusters is few,
   and across a resample of them no-effect is barely inside the interval.

   SECOND THING THE README MAY NOT IMPLY: that MORE agreement means MORE signal.
   The data support ">=2 tools beats 1 tool" and nothing further — flat at 3,
   point-estimate negative at >=4. Graded confidence in n_tools is unsupported.

   README correction DRAFTED, NOT APPLIED: docs/README_correction_0j_draft.md.

0j-note. THE GENERALISABLE LESSON, recorded because it cost a session's worry:
   five claims had died when a better-matched CONTROL was applied, so the
   sixth was assumed to be dying the same way. It was not. Refining the control
   left the point estimate exactly where it was; what was wrong was the
   SIGNIFICANCE TEST, which nobody had re-examined because effect size kept
   being the thing under suspicion. SESSION_HANDOFF §3a's rule ("ask what it is
   being compared to") is right but INCOMPLETE — also ask what the p-value holds
   fixed. A resampling p-value that conditions on one arm is not a test of the
   comparison.

0i. [CLOSED 2026-07-26 — D HOLDS, terminal answer. Do NOT reattempt.]
   Size-controlled formulation. All four candidates run as pre-registered.
   A (logistic with log(LOC)) COLLAPSES ONTO the size-only floor — identical
   PofB 0.185, IFA 2, PMI 0.022 — because its n_tools coefficient is ~0.
   B (size-residualized) and raw consensus do not beat size-matched random
   (p=0.468, p=0.443). C (density per LOC) is the WORST performer and reproduces
   ManualUp almost exactly (PMI 0.571 vs 0.602, IFA 1,334 vs 1,746) — the
   pre-registered prediction, CONFIRMED.
   FINDING: the signal is real but NOT ORDERABLE under an effort budget. No
   formulation adds ranking information beyond size on this corpus.
   Full record: VALIDATION.md "0i RESULT".

0g. [HIGHEST-VALUE OPEN QUESTION — supersedes the granularity work]
   EFFORT-AWARE EVALUATION CHANGES THE ANSWERS. Measured 2026-07-26 on the Lipp
   artifact with the review budget in LINES OF CODE rather than units:
     FUNCTION level consensus PofB@20%LOC = 0.185, IDENTICAL to ranking by LOC
       alone (p=0.522) and WORSE than counting findings (0.230).
       => open item 2 is NOT justified as a parser project. The 6.4x merge gain
          and +0.96pp precision gain do not survive effort-normalisation.
     FILE level consensus = 0.228 vs LOC 0.081 (p=0.000) and findcount 0.114
       (p=0.018) — beats trivial baselines, so it is NOT merely tracking size.
       But loses to the best single tool (Infer 0.317).
   THE FINDING THAT MATTERS MOST: ranking files by LINES OF CODE ALONE scores
   ROC-AUC 0.845 on the same data where the published headline is 0.755
   (reproduced here at 0.763). A ranker reading NO tool output beats the
   consensus signal on the metric the README quotes. This is Rahman et al.
   ICSE'14 reproducing on our corpus, and it is why non-effort-aware ROC-AUC is
   the wrong metric to headline.
   NOT a claim that consensus is worthless — effort-aware, file-level consensus
   beats the LOC baseline decisively (0.228 vs 0.081), the inverse ordering. It
   means 0.755 is the wrong number to LEAD WITH.
   ACTION REQUIRED before the README is touched again: decide whether to
   re-headline on an effort-aware metric. This supersedes item 1's status.

0h. [IMPLEMENTED 2026-07-26 — GATED. Full record: VALIDATION.md "0h IMPLEMENTED".]
   Disclosure only; never filters or reweights. Gate threshold m*=8 non-modal
   units is MEASURED (analysis/scripts/calibrate_0h.py) against the Lipp
   file-level population's real +0.629, not chosen. Bootstrap CI + permutation p
   per Ruscio 2008 and because n_tools is heavily tied by construction.
   TWO THINGS A LATER SESSION MUST NOT UNDO:
     1. The max(startLine) size proxy is CIRCULAR and was removed. More tools ->
        more findings -> a higher MAXIMUM line, independent of file length
        (measured on zlib: 1-tool files median max-line 58, 2-tool files 457).
        With it the tool reported rho=+0.402 p=0.0025 and WOULD HAVE WARNED on a
        real run; with real file lengths the same run gives +0.232 p=0.086 and is
        correctly silent. Read real lengths (AUDIT_SOURCE_ROOT) or report NOT
        APPLICABLE. Do NOT reintroduce a SARIF-inferred size.
     2. The unit is the FILE and the variable is ENGINES-FLAGGING-THAT-FILE, NOT
        the per-finding n_tools in `ranked`. They differ and the difference is
        material: on zlib the file-level view has real spread ({1:15, 2:44})
        while finding-level n_tools is {1: 601}.
   Also corrected: arXiv:2602.07842 §D.4 does not exist and does not ground this
   design (that ID is an LLM-calibration paper whose Appendix D has only D.1).
   See rule 8a: fetch supplied citations before citing them.
   [original scoping follows]
   [SMALL, orthogonal — take it] Disclose size-correlation per run. The tool
   already discloses when a signal is uninformative (the signal gate) and when
   independence is doubtful (0a/0b). Add the same for the size confound:
   compute Spearman(n_tools, unit size) per ingest and disclose when agreement
   is substantially size-correlated. On the Lipp corpus that value is +0.629,
   which is the single number that explains why the ranking claims collapsed.
   Cheap, consistent with existing behaviour, and it puts the caveat in the
   OUTPUT rather than only in a document. Scoped, not built.

0k. [CLOSED — WAS A DUPLICATE ITEM NUMBER, AND ITS PROPOSAL IS ALREADY TESTED
   AND REJECTED. Renumbered 0i -> 0k 2026-07-26; there were two items numbered
   0i and a reader could not tell which any cross-reference meant.]
   ITS PROPOSAL IS NOT AN OPEN ROUTE. "Consensus DENSITY — agreement per LOC" is
   exactly candidate C of the CLOSED 0i, which was pre-registered, measured, and
   was the WORST performer of the four: PofB@20 0.170 against a 0.185 size-only
   floor, IFA 1,334, PMI 0.571 — reproducing ManualUp almost exactly, which was
   the pre-registered PREDICTION of failure, confirmed.
   It was also refuted on DESIGN grounds before it was run: Kronmal (1993) shows
   dividing by a common denominator induces correlation between the ratio and
   that denominator, so consensus/LOC would replace a positive size confound
   with an induced negative one. The remedy is the denominator as a COVARIATE,
   which is what 0j then did.
   WHAT SURVIVES from this entry is only the STANDING RULE below, which is
   still in force. Do NOT read this item as an unexplored direction.
   [original text follows]
   Size-controlled formulation of the consensus signal. Raw agreement COUNT is
   substantially a size proxy (Spearman +0.629), which is why every ranking
   claim built on it failed a size-matched control. Candidate: consensus DENSITY
   — agreement per LOC, or agreement normalised by the unit's own finding count
   — so a large file is not favoured merely for being large. [MEASURED AND
   REJECTED — see above.]
   STANDING RULE attached: nothing gets headlined until it survives a
   SIZE-MATCHED CONTROL, not merely ManualUp or ManualDown. Three claims have
   now died between "beats a named baseline" and "beats a size-matched
   control"; that gap is where this project's claims go to fail.
   Do NOT treat this item as a reason to delay the README correction.

0f. [STRUCTURAL GAP in the 0a guard — record stands regardless of counts]
   >>> STUDY DONE 2026-07-26, and it WIDENS this item. Full record and a
   >>> PRE-REGISTERED measurement: docs/SPEC_rule_provenance_measurement.md.
   >>> Key external findings, all [fetched]:
   >>>  - Semgrep's OWN FAQ: the registry "includes rulesets inspired by the
   >>>    rules of many popular linters and checkers, including ESLint, RuboCop,
   >>>    Bandit, and FindSecBugs." So 0f is NOT a FindSecBugs quirk — rule
   >>>    derivation is a documented, general way registries are built.
   >>>  - di Angelo & Salzer, arXiv 2304.11624 §6.4 NAMES the mechanism exactly
   >>>    ("Tools form families by being derived from common ancestors…Related
   >>>    tools may misjudge a contract in a similar way and outnumber tools
   >>>    with the correct result") — but ASSERTS it, does not measure it, and
   >>>    in the smart-contract domain.
   >>>  - The ensemble-diversity literature covers shared METHOD and correlated
   >>>    OUTCOMES; nothing found models shared PROVENANCE as a distinct cause.
   >>>  - Lenarduzzi et al. measured ~18,000 cross-tool rule pairs, but by
   >>>    SEMANTIC containment, which convergent design satisfies too. Adjacent
   >>>    question, not this one.
   >>>  - NOBODY HAS MEASURED the derived FRACTION of any tool's rule set.
   >>>    Explicit search negative. This is a genuine gap, not a rediscovery.
   >>> NO GUARD IS TO BE BUILT until the pre-registered measurement runs; its
   >>> decision rule is fixed in the SPEC so the result cannot pick its own
   >>> threshold. Note the SPEC's asymmetry limit: only semgrep declares
   >>> provenance, so a LOW number is NOT evidence of independence and must be
   >>> reported as uninformative rather than as clearance.
   >>> CORRECTION 2026-07-26: THE REGISTRY ARM IS NOT BLOCKED. A prior note in
   >>> this session recorded it as needing "a fetch not performed" and treated
   >>> it as unavailable. That was WRONG and is withdrawn. Network works from
   >>> this machine — verified twice: semgrep pulled p/java live during the
   >>> Struts re-run, and semgrep.dev/c/p/java returns HTTP 200. The absence of
   >>> a local rule cache (~/.semgrep holds only settings.yml) is not a blocker,
   >>> it just means the rules are fetched on demand.
   >>> So RQ1-at-registry-scale — what fraction of ALL semgrep registry rules
   >>> declare an upstream source, and how that distributes across upstream
   >>> tools — is ACTIONABLE TODAY, not blocked. It remains ONE REGISTRY, not
   >>> the ecosystem, and that bound stands.
   >>> CORPUS ARM RUN 2026-07-26 (registry arm NOT run — needs a fetch).
   >>> Results: SPEC §7. All figures are LOWER BOUNDS.
   >>>   OWASP: 5 of 11 FIRED rules (45.5%) declare FindSecBugs provenance,
   >>>          = 8.3% of the 60 rules LOADED, = 702/1,909 findings (36.8%).
   >>>          All 5 name a tool CO-PRESENT in the run (n=5, chosen pairing).
   >>>   zlib : 0 of 4 fired rules declare anything. THIS IS UNINFORMATIVE,
   >>>          NOT CLEARANCE — semgrep's C rules simply do not disclose.
   >>> FIVE DENOMINATORS now pinned to exact definitions in SPEC §7.3 —
   >>> 8.3% / 45.5% / 36.8% / 30.4% / 22.6% are NOT versions of one number.
   >>> If one goes in the README it should be 30.4% or 22.6%: those describe
   >>> AGREEMENT, which is what the tool claims. 8.3% is the most misleadingly
   >>> low (49 of 60 loaded rules never fired).
   >>> 0f's four listed "pairs" (199/171/85/28) sum to 483 = CO-LOCATED PAIRS,
   >>> not findings. A FIFTH declaring rule exists that 0f did not list
   >>> (desede-is-deprecated <- TDES_USAGE, 130 findings, 0 co-located pairs).
   >>> !! EVIDENCE GAP, ACT ON THIS BEFORE RE-CITING 0f !!
   >>> The claim "the Struts near-miss IS a derived pair" is NOT reproducible
   >>> from data on this machine. Only SARIF was kept for Struts and SARIF drops
   >>> source-rule-url; the rule that fired there (unvalidated-redirect) did NOT
   >>> fire on OWASP, so no join recovers it. That claim is LOAD-BEARING (it is
   >>> the basis for "zero independent real-code agreements") and is currently
   >>> prior-session-attested with the artifact absent — RULE 10.2 applies.
   >>> SETTLED 2026-07-26 — THE RE-RUN WAS DONE AND 0f WAS RIGHT.
   >>> semgrep 1.171.0 --config=p/java --json over struts-main reproduced the
   >>> original run exactly (60 rules, 1,483 files, 1 finding). The rule
   >>> unvalidated-redirect DOES declare
   >>>   source-rule-url: https://find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT
   >>> and the SpotBugs rule it agreed with, UNVALIDATED_REDIRECT, has helpUri
   >>>   https://find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT
   >>> BYTE-IDENTICAL. semgrep's declared ancestor IS the rule the other tool
   >>> fired. Not an inference — a pointer match.
   >>> THEREFORE: the Struts near-miss IS a derived pair [CONFIRMED], and
   >>> "on real code this project has observed ZERO independent
   >>> cross-methodology agreements" is CONFIRMED and may be cited as measured.
   >>> On real code the derived fraction of observed agreement is 1 of 1, n=1.
   >>> Evidence: analysis/results/struts_derived_pair_evidence.txt; SPEC §7.4.
   >>> DECISION RULE UNMOVED: D and Delta are unchanged, so per SPEC §4.5.1
   >>> no guard is warranted and disclosure is still owed.
   LINEAGE EXISTS AT THE RULE LEVEL, BELOW THE ENGINE LEVEL 0a GUARDS.
   Found 2026-07-26 while sizing open item 2. semgrep's
   `unvalidated-redirect` rule declares, in its own metadata:
       source-rule-url: https://find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT
   i.e. **the semgrep rule is DERIVED FROM the FindSecBugs rule it later
   "agrees" with.** Semgrep and SpotBugs are genuinely different ENGINES, so the
   0a/engine-lineage guard correctly lets them merge. But at the RULE level this
   is a rule agreeing with its own ancestor — shared provenance, not independent
   corroboration.
   THE GUARD IS INCOMPLETE IN A WAY NOBODY HAD NOTICED. 0a asks "are these the
   same engine?" It does not ask "did one of these rules come FROM the other
   tool?" Two independent engines can carry ported rule sets, and rule porting
   is COMMON — semgrep's registry openly derives rules from FindSecBugs, and
   the same pattern plausibly exists for other imported rule families.
   WHY IT MATTERS BEYOND THE GUARD: the ensemble argument the whole tool rests
   on is that different tools have different BLIND SPOTS. Two implementations of
   the SAME RULE have the SAME blind spot by construction. Their agreement is
   the correlated-error case the framing sweep recorded as carrying no ensemble
   benefit — the very thing diversity-aware consensus exists to exclude.
   MEASURED 2026-07-26: 5 of the 11 p/java rules that fired declare FindSecBugs
   provenance, covering 702 of 1,909 semgrep findings (36.8%). Of 1,588
   co-located rule pairs on OWASP, 483 (30.4%) are a rule paired with its own
   ancestor; by location, 278 of 1,229 (22.6%) are derived-only. The four pairs:
   httpservlet-path-traversal<-PATH_TRAVERSAL_IN 199, des-is-deprecated<-
   DES_USAGE 171, use-of-sha1<-WEAK_MESSAGE_DIGEST_SHA1 85, use-of-md5<-
   WEAK_MESSAGE_DIGEST_MD5 28. semgrep's C rules declare NO source, so zlib is
   unaffected.
   IMPACT: the enrichment SURVIVES — excluding derived-only pairs moves it from
   70.5% to 69.7% against a 51.6% base rate. But the SINGLE REAL-CODE AGREEMENT
   (the Struts near-miss) IS a derived pair, so on real code this project has
   now observed ZERO independent cross-methodology agreements. See VALIDATION.md.
   SCOPE OF THE FIX (not built): rule-level provenance would need reading
   `source-rule-url` (or equivalent) from NATIVE tool output — SARIF DROPS IT,
   verified: 0 occurrences of `source-rule-url` in semgrep's SARIF rule blob
   versus its presence in the native JSON. So the shipped SARIF-only pipeline
   CANNOT SEE rule provenance at all. Any fix needs a second input format or a
   curated ancestry list.

0c. [CLOSED 2026-07-26 — BOTH HALVES NOW SHIPPED. (b) disclosure and (a)
   suffix matching behind a uniqueness guard. Record: VALIDATION.md
   "0c OPTION (a) IMPLEMENTED". Diagnostic ran FIRST and authorised it:
   basename blocks are non-singleton on 0.9% (Struts) and 2.3% (zlib) of paths
   and ZERO at depth>=2, so basename alone is unsafe but segment-suffix +
   cardinality-1 is not too strict. VERIFIED: Struts RAW 0->1 merges and OWASP
   RAW 0->1,427, both EXACTLY reproducing the hand-aligned counts.
   NOTE the correction: Struts hand-aligned is 1 merge, not 2.
   THE GUARD MUST NOT BE LOOSENED. The documented failure pattern is
   formatting differences -> relax the rules -> false positives rise. The guard
   was measured as adequate, so nothing was relaxed. If a future corpus shows
   it blocking useful matches, accept the loss or add an explicitly
   probabilistic layer with its own disclosure — do NOT weaken cardinality-1.
   Deterministic linkage was chosen deliberately and its price (missed real
   matches) is stated in the tool's own output.]
   [former header: STALE HEADER — CORRECTED 2026-07-26. The DISCLOSURE half IS IMPLEMENTED in
   shipped code; verified against the tree, not asserted: `_path_root_mismatch`
   at src/audit.py:834, wired at :1041 and :1339, rendered at
   audit_html_report.py:74. The README's "Path-root mismatch disclosure" bullet
   is therefore ACCURATE. Recommended sequence (b)-then-(a) was followed: it
   DISCLOSES the mismatch but does NOT merge across roots, so the suffix-match
   half — option (a) behind a uniqueness guard — is genuinely still open.
   The original entry follows unchanged.]
   [former header: HIGH PRIORITY — LIVE PRODUCTION DEFECT, SILENT-ZERO FAILURE
   MODE. Scoped, NOT implemented.]
   Cross-tool PATH FORMS are structurally incompatible.
   SpotBugs derives file paths from BYTECODE and emits PACKAGE-relative:
       org/owasp/benchmark/testcode/BenchmarkTest00001.java
   semgrep (and source-level tools generally) emit SCAN-ROOT-relative:
       <whatever>/src/main/java/org/owasp/benchmark/testcode/BenchmarkTest00001.java
   The first is a SUFFIX of the second.

   BLOCKS A4. This is not only a user-facing bug: the next real measurement
   needs a REAL Java project scanned by two tools, and that project will hit the
   SAME package-relative vs scan-root-relative mismatch and produce a SILENT
   ZERO. An A4 run attempted before 0c lands would report "no overlap" and the
   number would be an artifact. 0c is a PREREQUISITE for A4, not a parallel task.
   FAILURE MODE: a Java user running SpotBugs + semgrep the obvious way gets
   ZERO cross-tool merges and NO diagnostic. The tool reports "consensus" as an
   informative signal and silently finds none. Same class as the fingerprint
   defects: a wrong assumption about tool output that degrades silently rather
   than erroring.

   `_norm_uri` CANNOT FIX THIS. It is lexical normalization (backslashes,
   `./`, `../`, duplicate slashes, `file://`, percent-encoding) and a SUFFIX
   RELATIONSHIP IS NOT A NORMALIZATION PROBLEM — neither string is malformed;
   they are correct paths relative to different roots. Do not attempt to solve
   it there.

   CANDIDATE DIRECTIONS (pick deliberately; both have costs):
     (a) BASENAME + SUFFIX MATCH. Treat paths as equal when one is a path-suffix
         of the other (segment-aligned, not substring). Cheap and effective, but
         it can FALSELY unify same-named files in different modules
         (`a/util/Config.java` vs `b/util/Config.java`) — a false merge, the
         error direction the asymmetric-cost rule forbids. Would need a
         guard: unify only when the suffix match is UNIQUE across the corpus.
     (b) DETECT AND WARN. Compute suffix-relatedness across tools at ingest; if
         two tools' path sets are suffix-related but never equal, emit a loud
         disclosure ("tools report paths relative to different roots; cross-tool
         merging is disabled") and tell the operator how to align them. Does not
         merge anything, but converts a silent zero into a stated one — which is
         this project's standing preference (cf. 0a/0b).
   RECOMMENDED SEQUENCE: (b) first — it is honest, cannot cause a false merge,
   and closes the silent-failure hole. Then (a) behind the uniqueness guard if
   the measured cost justifies it.

   HOW IT WAS FOUND, recorded because it generalizes: only by running the two
   tools TOGETHER on the same corpus. Neither tool alone shows it — each emits
   perfectly valid paths. Per-tool testing cannot surface cross-tool interface
   defects, and this is the second such defect this session (the first being
   ingest reading the wrong rule-metadata fields, also invisible per-tool).

1. [SUBSTANTIALLY DISCHARGED 2026-07-26 — four corrections applied and VERIFIED
   AGAINST THE PUBLISHED FILE, not assumed. Checked in-session:
     - no retired figure remains: 0.755, PofB 0.655 and the 1-tool-to-4-tool
       gradient are all absent from README.md;
     - quickstart step 2 now reads "re-rank by consensus (with two scanners
       this column is usually empty — see Honest scope)", so the named
       flawfinder+cppcheck pair no longer promises what it cannot deliver;
     - step 3 documents the display-dedup pass as an explicit optional step
       rather than implying it runs automatically;
     - the surviving 1.5x carries its interval, its threshold-not-a-score
       limit, and the nine-project bound.
   WHAT REMAINS, AND IT REMAINS BY CHOICE: the headline still says "rank
   findings higher where *independent tools agree*". That phrase was one of the
   three things this item flagged. It is now QUALIFIED rather than removed — the
   22.6% bullet states that on the corpus where it could be measured, that share
   of agreeing locations had no independent agreement behind them, a lower
   bound. Whether "independent" should come out of the headline entirely is
   §6.2 question 3, which is a premise change and is tracked there, NOT a
   pending README edit here.
   Do not re-open this item to "fix the README"; the remaining decision is a
   claim decision, not a wording one.]
   [former header: UNBLOCKED 2026-07-26 — the blocker DISSOLVED, it did not
   resolve] README honesty. Scoped
   claim-by-claim against the PUBLIC README in
   docs/SCOPE_shipped_consensus_defect.md §5.
   FIRST: THE LOCAL CHECKOUT WAS BEHIND. Local HEAD af2336a; origin/main 1070558
   ("Update README.md"). The published README is a 59-line rewrite; the local
   one is the stale 162-line version. src/ and action.yml are BYTE-IDENTICAL
   between them, so all code findings hold — but ANY claim about "the README"
   must specify which, and `git fetch` first. Not fast-forwarded; inventor's call.
   The defect is "the shipped DEFAULT cannot demonstrate the headline signal" —
   NOT "the tool does not work" (audit.py's merge works when inputs permit; CLI
   users with other tool pairs are a genuinely unmeasured conditional case).
   Against the PUBLIC README the finding is sharper but less urgent: no false
   statement about what the code does, but the headline ("rank findings higher
   where independent tools agree"), quickstart step 2's name ("re-rank by
   consensus"), and the named flawfinder+cppcheck pair together promise an
   experience the default cannot deliver.
   NO LONGER BLOCKED. The Lipp artifact was fetched 2026-07-26 and inspected,
   and the blocker turned out to be void: there is nothing to re-earn, because
   0.755 was NEVER a property of this implementation (see 3c(b)). The gate
   dissolved rather than being satisfied.
   This decision was held THREE times, each prior attempt overturned by
   evidence arriving afterwards:
     1. "Don't edit, the fix makes the claims true" — overturned: the fix
        produced ZERO merges on real zlib.
     2. "Maybe add a tool to the quickstart" — overturned: a third tool yielded
        2 merges in 1,131 findings, both between the two most similar tools, in
        test code, and none in library sources.
     3. Current state — the README quotes ROC-AUC 0.755, and that number is now
        UNANCHORED (item 3c(b)): it was measured under pre-fix code whose
        n_tools behaviour the fix changed. It may not be quoted as a property of
        the shipped tool until re-earned.
   So what the README owes CANNOT be settled by argument. It needs the
   re-measurement. Re-obtaining the Lipp artifact is the gating dependency.
   [superseded] An earlier recommendation here read "do NOT edit the README now;
   fix _result_key and the claims become true as written." That did not survive
   the zlib evidence and is retained only to stop it being re-derived.
   WITHDRAWN: an earlier entry here claimed README L6 redirects cppcheck's SARIF
   from the wrong stream, "PUBLIC and LIVE." The stream observation is true and
   the line exists in the STALE LOCAL copy; the PUBLIC README uses the correct
   `2>` + XML-converter path. Provenance failure recorded in SCOPE §4a.

2. [DONE 2026-07-26] `_result_key` two-algorithm fix. Fingerprint for SAME-tool
   dedup; location+class for CROSS-tool. Implemented, tested (16-check harness
   examples/fixtures/verify_cross_tool_key.py, all pass), fixtures rebuilt from
   captured real output. `_norm_uri` given real path normalization. `_CWE_CLASS`
   extended conservatively (+8), `_CWE_DENY` +664/+758. Full record in
   VALIDATION.md 2026-07-26.
   CARRY FORWARD — THE NEGATIVE: on real zlib 1.3.1 (real flawfinder + real
   cppcheck, 712 raw findings) the fix produced **ZERO cross-tool merges**, and
   correctly so: of 14 exact co-locations, 10 had classes resolved on both
   sides and 0 matched — all 10 were trees.c fprintf debug lines where
   flawfinder says format-string and cppcheck says null-deref. The STRUCTURAL
   blocker is gone; a SEMANTIC one remains — the pair's class profiles are
   near-disjoint (flawfinder fmt 260/buf 235; cppcheck null 10/int 2/uninit 1,
   with only 13 of 124 findings resolving to any class). DO NOT report "the fix
   restores the headline signal." It removes the impediment; whether the shipped
   pair can demonstrate consensus at all is now item 3's question, with a
   concrete prior: expect low merge rates, and check whether the Lipp envelope's
   ~5.9% multi-tool rate is reachable with real scanners or was a reconstruction
   artifact.
   [historical] audit.py used the same-tool algorithm for both, a category error
   — it cites the DefectDojo model, which uses two algorithms precisely to
   avoid this.
   CRITICAL FRAMING (do not lose it): this fix does NOT risk ROC-AUC 0.755. That
   result was measured on reconstructed envelopes that DID merge (1,318 overlaps
   recovered, hand-count exact). The shipped path cannot merge. So the fix moves
   the SHIPPED config TOWARD the VALIDATED one. See VALIDATION.md 2026-07-26.
   BUT read BOUND 2 there: direction is not a transfer guarantee.

   _CWE_CLASS COVERAGE IS PART OF THIS ITEM'S DESIGN — NOT INHERITED FROM ITEM 3.
   (Corrected 2026-07-26; the earlier ordering had this wrong.) The cross-tool
   branch keys on location + CWE CLASS, and the class comes from `_cwe_class`.
   So map coverage DIRECTLY determines how often the fixed key can match at all.
   Scoping this fix without settling coverage means designing a key whose hit
   rate has not been measured. Coverage is an input to the design, not a later
   optimization of it.
   What must be settled HERE, from `cppcheck --errorlist` (342 checks,
   tool-authoritative):
     - 14 CWEs map to a class ->  31 checks
     -  7 CWEs correctly denied -> 149 checks
     - 35 CWEs UNMAPPED         -> 116 checks   <- bites the FIX, not just the badge
     - 46 checks emit no CWE    ->  46 checks
   Carry the U1/U2 split into this item: U1 = no CWE available (cppcheck
   limitation, not fixable by us); U2 = CWE present but absent from _CWE_CLASS
   (OUR gap, fixable by editing a 28-entry dict). Candidate genuine omissions:
   CWE-786, CWE-131, CWE-590, CWE-762, CWE-252, CWE-467.
   COUNTER-NOTE, keep it: CWE-664 (improper resource lifetime, 20 checks) and
   CWE-758 (undefined behaviour, 20 checks) are GENERIC junk-drawer categories
   and are plausibly _CWE_DENY candidates rather than map candidates. Do NOT
   assume every unmapped CWE should be mapped — a too-broad class map produces
   false cross-tool merges, which is worse than a missed merge because it
   silently inflates n_tools, the signal the whole tool rests on.
   Check types are not finding frequency; weight by observed findings.

3. [Mac, small] RE-MEASURE. TWO distinct questions, both in
   docs/SPEC_item4_groupability_measurement.md. Item 2 is DONE.
   NOT PROMOTED — an earlier promotion of this item was WITHDRAWN. It rested on
   "96% of cppcheck findings resolve to no class," which counted _CWE_DENY
   rejections as a coverage gap: the same denominator error corrected twice
   before. Cascade on zlib: cppcheck D0=543 -> D1=337 (206 diagnostics), of
   which DENIED 288 (85.5%), U2 23 (6.8%), RESOLVED 22, U1 4. The denied bucket
   DOMINATES. The real map gap is 23 findings, not 521, and map extension is NOT
   the high-value lever it briefly appeared to be.
   Also settled: semgrep's 31 U2 are ALL CWE-676 ("potentially dangerous
   function") covering strcpy/scanf/strcat/system — mapping it to one class
   would merge buf+fmt+cmdi and manufacture false merges. CWE-676 is a
   DENY candidate, not a map candidate; same for flawfinder's CWE-362/CWE-20.
   The conservative map is close to correct as-is.
   Standing conclusion: the tools have genuinely ANTI-CORRELATED coverage
   (cppcheck resolved = null/uninit/int/leak; flawfinder = fmt/buf/int).
   CodeQL remains UNTESTED: codeql 2.26.0 ships an osx64 tracer only, this Mac
   is arm64, Rosetta absent. Needs `softwareupdate --install-rosetta`.

3b. [Mac, small — INDEPENDENT OF CONSENSUS, affects EVERY user] flawfinder
   contextHash/v1 data loss. FIXED 2026-07-26, but recorded as its own item
   because it is not a consensus issue: it silently destroyed findings on every
   real flawfinder run this tool has ever processed. contextHash hashes
   surrounding source, so identical C idioms at different locations collide —
   on zlib 588 raw collapsed to 484 where 582 is correct, ~17% destroyed with
   no warning. Single-tool users who never cared about the headline signal were
   affected. Companion defect: semgrep OSS unauthenticated emits the constant
   "matchBasedId/v1":"requires login" on every result (33 -> 1 on zlib).
   Fix: degeneracy detected from the data (one (tool,fingerprint) at >1 distinct
   location is not an identity -> fall back to location key). Regression-tested.
   CHECKED vs ROC-AUC 0.755: does NOT affect it. Demonstrated that on
   fingerprint-free input _degenerate_fingerprints returns empty and the key is
   byte-identical; and the Lipp envelope was necessarily fingerprint-free on
   merged findings, since under the OLD code a cross-tool merge required both
   sides to take the rk: branch. BOUND: deductive, NOT an inspection — the Lipp
   artifact is not on this machine.
   REMAINING TASK: audit any newly-supported tool for BOTH fingerprint failure
   modes (constant placeholder; context-collision). Two of three real scanners
   tested violate the "fingerprint is an identity" assumption.

3c. [CLOSED 2026-07-26 — artifact fetched, both sub-items resolved as VOID]
   The Lipp artifact (Zenodo 10.5281/zenodo.6515687, 6.9 MB, 15 files, all
   MD5-verified) is now at scratchpad/lipp/. Neither sub-item needs re-earning.
   (a) The 1,318 anchor is a ROUND-TRIP IDENTITY, not validation.
       DO NOT RE-RUN IT AS THOUGH IT WERE. All three numbers are direct
       properties of dataset/php/sca_results.json, measured:
           rows in `findings`        = 21,061   (the "dedup" figure)
           sum of len(found_by)      = 22,403   (the "raw" figure)
           rows with >1 tool         =  1,318   (the "overlap" figure)
       The prior session expanded that table into one SARIF result per
       (finding, tool) and fed it to --ingest, which collapsed it back to the
       table. Any correct implementation returns the original row count by
       construction; it could not have failed. Worse for validation purposes,
       the expansion gives co-flagging tools IDENTICAL (file, line, cwe), so
       merging was guaranteed — precisely the condition real scanners do not
       meet. Reclassify in any future write-up: a smoke test that dedup inverts
       expansion, not an independent cross-check.
   (b) ROC-AUC 0.755 needs no re-earning, and the earlier "unanchored" record
       was WRONG IN ITS REASON. It is not invalidated by the item-2 fix.
       On Lipp data the fix changes nothing: co-flagging rows share identical
       (file, line, cwe) and carry no fingerprints, so they merged pre-fix and
       post-fix alike. Moreover audit.py is a PASS-THROUGH on this input —
       severity is absent (defaults to warning, sev_n=2 constant) and the text
       contains "cwe" so kind is always "security" (KIND_W=1.5 constant), giving
           score = 1.6*n_tools + 3.5 - 2.0*noisy
       a monotone function of n_tools. Measured: raw n_tools and the
       audit.py-equivalent score give IDENTICAL ROC-AUC 0.745 / PofB 0.495 on a
       2,578-file reconstruction (only 1 file trips the noise term).
       CONSEQUENCE: 0.755 measures LIPP'S PREMISE — that tool agreement predicts
       vulnerability — on real CVE ground truth. It is externally valid and must
       NOT be retracted or softened. What it does NOT measure is THIS
       IMPLEMENTATION's ranking, which contributes nothing on that input. The
       defect is ATTRIBUTION, not the number.
       BOUND: reconstruction gave 0.745 vs 0.755 and PofB 0.495 vs 0.655, so the
       exact universe/labelling differs from the original. Consensus AUC ranged
       0.735-0.815 across nine plausible universe definitions; 0.755 sits inside.
   The "MECHANISM vs OUTPUT" tension recorded earlier is VOID — it rested on the
   fix having changed the measurement, which it did not.

3e. [IMPLEMENTED 2026-07-26 — CORRECT, TESTED, AND CURRENTLY INERT.
   Record: VALIDATION.md "3e IMPLEMENTED". Ancestor-related CWEs resolve to the
   MOST SPECIFIC; unrelated, non-unique-maximal, and MISSING-EDGE all -> None.
   VERIFIED world-state, not assumed: buckets.json carries ONLY child_of /
   parent_of (no PeerOf, so it stays a tree), every child_of is a single string,
   and 0 of 162 entries have multiple parents — so the ambiguity branch is
   UNREACHABLE from this file and is tested with an injected hierarchy instead.
   COVERAGE: prose path recovers 113 findings and correctly leaves 9 as None
   (113+9 = the 122 this item was filed against; the 9 are genuine ambiguity).
   >>> BUT THE END-TO-END EFFECT ON EVERY CORPUS ON DISK IS ZERO. Measured by
   >>> emptying the hierarchy and diffing: no class changes, no merge changes
   >>> (Struts 1->1, OWASP 1,427->1,427, zlib 0->0). Those 113 already resolve
   >>> via SARIF taxa, which ingest consults FIRST. DO NOT REPORT 3e AS
   >>> "RECOVERS 113 FINDINGS" WITHOUT THAT QUALIFIER — on the shipped path it
   >>> recovers none. Its value is conditional on a tool that emits NO taxa and
   >>> names several ancestor-related CWEs in prose.
   DO NOT INVERT THE MISSING-EDGE RULE. "No ancestor path" is ambiguous between
   genuinely-unrelated and edge-absent-from-our-copy; both -> None, so a missing
   edge costs a merge instead of manufacturing one. Making it resolve to
   anything else turns every gap in a 162-entry C-focused hierarchy into a
   potential FALSE MERGE. Same shape as §8 rule 10.
   Citation note (rule 8a): V2W-BERT's multiple-parent and NVD-omission claims
   were fetched and CONFIRMED verbatim; the TreeVul PeerOf claim could NOT be
   verified (the supplied arXiv ID does not resolve) and is not cited — the
   artifact check replaced it and is stronger.]
   [former header: FILED, not built — REFINEMENT that recovers a real loss]
   Hierarchy-aware
   class resolution. Multi-class rule metadata now resolves to NONE (correct for
   genuine ambiguity, merely SAFE for specificity pairs). COST, stated plainly:
   of the 122 findings this drops on SpotBugs+FindSecBugs, **113 are the
   WEAK_MESSAGE_DIGEST_MD5/_SHA1 case (CWE-327 + CWE-328), which makes the
   `hash` class UNREACHABLE for SpotBugs.** `hash` was kept separate from
   `crypto` on OWASP Benchmark's own evidence — 246 crypto vs 236 hash as
   DISTINCT labelled categories, both recorded as perfect discriminators. So the
   fix silences a class we have specific reason to think is real. Do NOT
   describe this as "costs 4% of resolution".
   LARGELY SUPERSEDED 2026-07-26: SARIF `relationships` CWE taxa give the rule's
   EXACT CWE with no prose noise (WEAK_MESSAGE_DIGEST_MD5 -> 328 -> `hash`;
   INFORMATION_EXPOSURE -> 209 -> correctly None), and ingest now reads them
   taxa-first. That recovered all 113 `hash` findings. 3e is still WANTED for
   tools that emit NO taxa (22 of SpotBugs' 77 rules, and semgrep) where prose
   scraping is the only source — but it is no longer the primary route.
   THE REFINEMENT: use MITRE's DAG to distinguish the two cases —
     ancestor-related -> take the MOST SPECIFIC (327+328 -> `hash`)
     unrelated        -> None (22 under CWE-664, 89 under CWE-707 -> None)
   REACHABILITY CHECKED, and it works: buckets.json from the Lipp archive
   (scratchpad/lipp/cwe_mapping/buckets.json, 162 CWEs, parent_of/child_of)
   contains BOTH — `CWE-328 child_of CWE-327` is encoded, and CWE-22/CWE-89 sit
   under different pillars. The refinement would resolve both cases correctly.
   PARTIAL-COVERAGE CAVEAT: buckets.json has only 162 CWEs and is C-focused —
   209, 211 and 326 are ABSENT. Unrelated-OR-absent must map to None, so the
   refinement improves specificity cases without weakening the conservative
   default. Licence: CC-BY-4.0, attribution required if vendored.

3d. [DONE 2026-07-26] TEST_DIR missed sibling names. Fixed via
   TEST_DIR_PREFIX (directory-only, so filenames are unaffected); both zlib
   merges now correctly noisy_loc=True, score 6.7->4.7. 9 regression cases
   incl. negatives. Original note: `contrib/testzlib/testzlib.c` is
   benchmark code but TEST_DIR requires a segment matching exactly `tests?`, so
   it is not down-weighted. Consider `test*`/`benchmark`. Both zlib merges
   landed there; there were ZERO merges in zlib's actual library sources.
   (a) GROUPABILITY (§1-6, pre-registered): denominator cascade D0/D1/D2,
       decision rule, project set — i.e. how often the badge fires, given a
       settled map.
       NOTE THE MOVE: the _CWE_CLASS coverage question (U1/U2 split, the 35
       unmapped CWEs, the CWE-664/758 deny-vs-map judgment) has MOVED INTO
       ITEM 2, where it belongs — the fix's cross-tool key depends on it, so it
       cannot be deferred to a measurement that runs after the fix. This item
       now MEASURES the consequences of item 2's coverage decision rather than
       discovering the coverage problem.
   (b) TRANSFER (§7): does the FIXED shipped path reproduce the conditions
       0.755 was measured under? DIFFERENT QUESTION from (a). The "fix moves
       shipped toward validated" argument is about DIRECTION and is a
       PRECONDITION argument, NOT a transfer guarantee — the reconstructed
       envelope had a particular merge topology and a location+class key may
       not reproduce it. Coarse check: post-fix merge rate and n_tools
       distribution on a real library vs the envelope's (~5.9% of raw findings
       were multi-tool; reached n_tools=3). If they differ materially, 0.755
       must be RE-EARNED on real scanner output, not inherited. See
       VALIDATION.md BOUND 2 — do not let a later session treat the direction
       argument as discharging this.

4. [Mac, small — DEMOTED] Shipped-path cross-tool display dedup + badge.
   docs/SPEC_dedup_shipped_path.md. Decision RESOLVED: badge in place, do NOT
   collapse rows. Priority rose when the pass looked like the ONLY cross-tool
   mechanism, then fell again once the _result_key fix was identified — post-fix
   the co-located same-class case merges at scoring and the display pass covers
   genuinely residual cases only. Do not size the badge before item 3.
   NOTE: examples/fixtures/*.sarif are UNREPRESENTATIVE (hand-authored; wrong
   flawfinder ruleId namespace, no fingerprints, CWE authored into a cppcheck
   message). Rebuild from captured real output before trusting them.

5. [Mac, medium] Corrected LIVE-scanner pipeline on REAL code (NOT synthetic
   Juliet — studied + rejected: macro-guarded synthetic code the source paper
   warns is non-representative). Largely SUBSUMED by items 2-3, which run real
   scanners on real libraries; keep only for the raw live-SARIF-parse path.

6. [sandbox] Cost-weighting consensus (was 2(a)): report marginal-detection per
   marginal-flag rather than treating "more tools agreeing" as costless
   (diversity costs +12pp functions flagged for +15pp detection). Must be
   STUDIED (ensemble/weighting literature) before IMPLEMENT.
   [Former 2(b), tool-quality weighting, is CLOSED — tested and rejected, §6.]

6b. [PROMOTED TO ITEM 0 — see top of this list] Engine-lineage guard. Kept as a
   pointer so the number is not reused. It affects C/C++ as much as Java.

7a. [SATISFIED 2026-07-26 for SpotBugs+FindSecBugs x semgrep on OWASP Benchmark]
   Java false-merge audit: **0 false merges in 1,156**. All 27 merges whose
   class differed from the planted category were INVESTIGATED, not assumed —
   every one is a genuine second XSS both tools independently found at
   response.getWriter(). The 278 merges landing on multi-class files all merged
   on the CORRECT class. BOUND: synthetic corpus; the result does not transfer
   to real Java, and the corpus labels one bug per file so it cannot adjudicate
   unlabelled second bugs except by inspection. Record: VALIDATION.md.
   [historical] Java false-merge audit. The map WAS extended 2026-07-26 with 15 effect classes
   (sqli/cmdi/xss/path/deser/xxe/ssrf/ldapi/xpathi/csrf/redirect/crypto/hash/
   creds/random). The required false-merge audit has NOT been performed.
   DO NOT read the zlib non-regression result as clearance. That check is
   INERT, not passing: only 1 of the 23 new CWEs (327) appears anywhere in the
   1,164-finding zlib corpus, on ONE finding from ONE tool, so no cross-tool
   merge was possible whatever the classes look like. Absence guaranteed the
   result; the classes were never exercised.
   The risk — do the new classes merge findings that are not the same bug —
   only materializes where those classes RESOLVE, i.e. on Java output.
   Run it together with A4 on the same corpus: a merge rate is meaningless if
   the merges are false.

7. [Java, doc-only DONE] docs/SPEC_java_admission.md written 2026-07-26.
   Verdict: Java PASSES A3 (real labels — OWASP Benchmark v1.2, 2,740 labeled
   cases, ahead of C/C++ whose corpus is not on this machine); CAN satisfy A1
   but the obvious candidate list collapses (see 6b); and FAILS in practice
   today for a reason that is OURS — _CWE_CLASS contains only memory-safety
   classes (buf/null/uaf/uninit/leak/fmt/int) and NOT ONE Java class (SQLi 89,
   cmdi 78, XSS 79, path-traversal 22, deserialization 502, XXE 611, crypto
   327/328, SSRF 918). Class resolution for Java is ~0, so no Java cross-tool
   merge can occur at all until the map is extended. Any Java overlap
   measurement taken first would be a false negative from our parser.
   DO NOT FLATTEN INTO THE NEGATIVE: the OWASP work paired SonarQube+FindBugs —
   two genuinely distinct engines — and found real within-category signal
   (74% TP when a tool flags vs 38% when none). That is MORE than any C/C++
   pair has managed against real scanners. Java's gap is a missing overlap
   measurement, not demonstrated absence of signal.
   New gate A4 added to the admission test: MEASURED partial overlap per
   candidate pair. Independence is necessary, not sufficient — C/C++ proved two
   independent engines can produce zero merges.

8. [standing] Other specified-not-coded paths: scope+offset dedup hashing;
   Good-Turing missing-mass coverage-confidence; mutual-information/permutation
   signal gating; learned (LETOR) ranking weights vs fixed.
   [LETOR: note §6's rejection of hand-crafted per-warning weighting is evidence
   AGAINST this path, not neutral. Study that result before spending on it.]

────────────────────────────────────────────────────────────────────────
## 8. STANDING BEHAVIORAL RULES (the user established these by correction)

1. Search a trusted external source FIRST, before decisions. Sandbox self-test
   is the LAST resort, and self-test = Claude grading Claude (weakest tier).
2. Do NOT unilaterally cut scope the user requested.
3. Tag every committed claim by provenance tier; state its honest bound.
4. Distinguish design-grounding from implementation-verification. Always.
5. Report the search denominator (how many searched / what came back, incl.
   negatives and empties — those are results, not failures).
6. Respect user autonomy; minimize pep-talk and bottlenecking; do the retrieval
   the request implies rather than offering to do it next turn.
7. The user should never have to prompt you to search or to study first. That
   prompt means the gate already failed.

8. A CLAIM FROM THE INVENTOR'S CHAT SESSION IS AN ASSERTION, NOT EVIDENCE
   (established 2026-07-26 by a live instance, both directions).
   It is verified against the tree like any other claim, and carries no more
   authority than the tier its evidence supports. This is NOT distrust — it is
   the same rule already applied to Claude's own claims (III.7: a sandbox PASS
   is Claude grading Claude) and to sources (III.6: appearing in a result list
   is not verification). Symmetry is the point.
   THE INSTANCE: the inventor asserted `--output-format` appeared nowhere in the
   repo and that line 6 was blank, instructing that the finding be corrected in
   two artifacts. Verified against the committed blob: the string was present at
   lines 6/61/64 of af2336a, worktree sha matched the commit, no `2>` anywhere.
   The amendment was REFUSED and that refusal was correct — amending on
   assertion would have replaced a verified finding with an unverified
   retraction. But the inventor was ALSO right: their grep covered an uploaded
   zip = the PUBLISHED README (origin/main 1070558), which the local repo, one
   commit behind, did not have. Both parties were right about different
   documents.
   THE OPERATIONAL LESSON: the failure was neither party's conclusion, it was
   UNSTATED PROVENANCE on both sides. So —
     - Before any claim about "the repo" or "the public X": `git fetch` and say
       WHICH ref/commit/working-copy the claim is about.
     - Chat-session artifacts (uploaded zips, pasted output) are a DIFFERENT
       world-state than the tree. Never merge the two silently.
     - Do not cite a line number for a command you composed rather than ran
       verbatim (SCOPE §4a: this session did exactly that).
     - When the inventor's claim and the tree disagree, the resolution is
       usually a provenance difference, not an error by either party. Locate the
       other document before concluding anyone was wrong.
   HISTORY REWRITE 2026-07-26 — a live instance of exactly this rule. A root
   rewrite unified commit authorship under alanfuller15; content is
   byte-identical but EVERY SHA CHANGED. Old SHAs survive in outside copies
   (inventor's device per I.5, an uploaded audit-main.zip, any pre-2026-07-26
   clone) and no longer resolve here. Old->new mapping table:
   docs/SCOPE_shipped_consensus_defect.md §9a. Always name which side of the
   rewrite a SHA came from. Recovery: local branch backup-pre-rewrite / tag
   pre-rewrite-2026-07-26 (not pushed; only route back).

   RULE 10.1-10.3 INTERACTION: refusing to amend on assertion is REQUIRED, and
   is not contradicted by the inventor turning out to be right. Holding was
   correct on the evidence available; the missing piece was found by SEARCHING
   for the other artifact, not by capitulating to the assertion.

8a. A CITATION SUPPLIED WITH AN INSTRUCTION IS AN ASSERTION, NOT A SOURCE.
   FETCH BEFORE CITING. The companion to rule 8, and the same standard: rule 8
   says a claim about the TREE is verified against the tree; this says a claim
   about the LITERATURE is verified against the literature.

   THIS IS A KNOWN HAZARD WITH A MEASURED BASE RATE. It is deliberately NOT
   written as an incident log, because an incident-framed rule quietly expires
   when the incidents stop, and the base rate does not. The rate below is what
   justifies the rule; the instances at the end are illustrations of it and
   would not, on their own, be grounds for anything.

   THE BASE RATE, all `[fetched]` and quoted verbatim from the sources:
     - Baethge C, Jergas H., "Systematic review and meta-analysis of quotation
       inaccuracy in medicine", Research Integrity and Peer Review 2025;10:13.
       46 studies, ~32,000 quotations. Pooled inaccuracy **16.9% (95% CI
       14.1-20.0%)**; major errors **8.0% (95% CI 6.4-10.0%)** — about half.
       Meta-regression on year: slope **-0.002 (95% CI -0.03 to 0.02), p=0.85**.
       NO IMPROVEMENT SINCE THE 1980s.
     - Smith N., Cumberledge A., "Quotation errors in general science journals",
       Proc R Soc A 2020;476(2242):20200538. 250 random citations; "The
       propositions being cited were compared with the referenced materials to
       verify whether the propositions could be substantiated by those
       materials. The study found a total error rate of **25%**." Higher than
       the medical figure, in high-impact general science.
     - Mogull S.A., PLOS One 2017. Improper secondary (indirect) citation
       **10.4% (95% CI 3.4-17.5%)**. A major error is "a cited assertion in
       which the referenced source either failed to substantiate, was unrelated
       to, or contradicted the assertion."

   WHY THAT JUSTIFIES A HARD RULE. Roughly one citation in six is wrong in
   peer-reviewed literature written by domain experts under editorial review and
   pre-publication scrutiny — one in four in general science. The errors are
   dominated by the case that matters most here: THE SOURCE DOES NOT
   SUBSTANTIATE THE CLAIM. And the rate has not moved in forty years, so it is a
   property of the practice, not of a bad cohort that will improve.
   **Citing without fetching therefore carries a measured ~1-in-6 failure rate
   no matter who supplies the citation** — the inventor, a search result, a
   prior session, or you. This is NOT distrust, exactly as rule 8 is not: it is
   the same standard applied symmetrically, and the symmetry is the point.

   MECHANISM TO WATCH — IMPROPER SECONDARY CITATION. The documented propagation
   route is citing the citation rather than the original, which "perpetuate[s]
   such errors" (Mogull). Its practical form here: a SEARCH SNIPPET attributed as
   though it were the primary source. A snippet is someone else's reading of a
   paper. Quoting it as the paper is secondary citation with the intermediary
   silently removed. If you have not opened the source, say "a search result
   states", not "X states".

   THE OPERATIONAL RULE:
     - Fetch the source before citing it, including sources handed to you.
     - If it cannot be fetched, record it as UNVERIFIED and do not cite it.
       Then check whether the argument survives on other grounds — usually the
       right outcome, and it keeps an unverifiable citation from becoming
       load-bearing.
     - Quote verbatim from what you fetched. State the bound if you read a
       rendering (ar5iv, abstract, API) rather than the publisher's bytes.
     - Report the search denominator (rule 5) for citation checks too: what was
       checked, what came back, and what did not resolve.

   INSTANCES (2026-07-26) — EXAMPLES OF THE HAZARD, NOT ITS JUSTIFICATION:
     - A GrammaTech attribution about converters losing information: the blog
       host no longer resolves and the reachable GrammaTech page says nothing
       about information loss. UNVERIFIED — do not cite.
     - arXiv:2602.07842 "§D.4" on dispersion checks before Spearman: that ID is
       an LLM-calibration paper (Wang et al. 2026) whose Appendix D contains
       only D.1 and which does not discuss tied ranks or degenerate variables.
       THE SECTION DOES NOT EXIST — do not cite.
   Both were load-bearing for a design decision, both were supplied in good
   faith, and both were caught ONLY by fetching. In each case the underlying
   claim survived on other grounds — SARIF Appendix D and Ruscio 2008
   respectively — which is the expected and healthy outcome: the unverifiable
   citation is recorded as unverified, and the argument stands or falls
   somewhere else. Two in one session is consistent with the base rate above,
   not evidence of anything unusual about this session.

10. ANY NEGATIVE FINDING DERIVED FROM SARIF IS A CLAIM ABOUT THE INTERCHANGE
   FORMAT UNTIL CHECKED AGAINST NATIVE OUTPUT.
   (Established 2026-07-26 after this bit TWICE. Grounded in the OASIS spec,
   not inferred from our own incidents.)

   ABSENCE IN SARIF IS EVIDENCE ABOUT THE PRODUCER, NOT ABOUT THE TOOL.

   THE DOCUMENTED CAUSE — SARIF v2.1.0 OS, "Appendix D. (Normative) Production
   of SARIF by converters", fetched and quoted VERBATIM:
     "A converter SHOULD populate those elements of the SARIF format for which a
      direct equivalent exists in the input data. If the input data includes
      information for which there is no SARIF equivalent, a converter MAY use it
      to populate the various property bags (3.8) and tag lists (3.8.2) defined
      by the SARIF format, OR THEY MAY SIMPLY OMIT IT FROM THE OUTPUT."
   The spec grants NORMATIVE PERMISSION TO DROP INFORMATION. Omission is
   conforming behaviour, so a well-formed SARIF file carries no guarantee that
   what the tool knew survived into it.
   Supporting, same spec: 1 (Introduction) states the format aims to "Be a
   useful format for analysis tools to emit directly, and also an effective
   interchange format into which the output of any analysis tool can be
   converted" — i.e. it is BOTH, and you cannot tell which you are holding from
   the file alone. 3.8 property bags exist so producers MAY carry tool-specific
   data with no standard field — MAY, not SHALL.

   TWO INSTANCES, both of which read converter loss as a property of the world:
     1. Ingest read the wrong rule-metadata fields, and the resulting class
        resolution looked like a tool limitation. It was a read of the envelope.
     2. Rule PROVENANCE measured 0 in SARIF. `source-rule-url` is present in
        semgrep's native JSON and DROPPED by its SARIF producer (verified: 0
        occurrences in owasp/sg_java2.sarif, present in owasp/sg_native.json).
        A SARIF-based provenance measurement returns a guaranteed false zero
        AND LOOKS EXACTLY LIKE CLEARANCE.
   In both cases the honest reading was "we cannot see it here", and the
   reading taken was "it is not there."

   THE OPERATIONAL RULE:
     - Before reporting ANY absence, missing field, zero rate, or "tool does not
       emit X" that is derived from SARIF, check the tool's NATIVE output.
     - If native output is unavailable, the finding is "NOT OBSERVABLE IN SARIF",
       which is a statement about the format. Say that, not "absent".
     - A zero from SARIF is never clearance.

   >>> BOUND ON THE SHIPPED TOOL — NOTED, NOT ACTED ON. <<<
   audit.py is SARIF-ONLY BY DESIGN. It is therefore STRUCTURALLY subject to
   this rule: any signal it reports as absent may be present in the tools'
   native output, and it cannot distinguish "the tool did not find it" from
   "the producer did not serialise it". This is a real BOUND ON WHAT THE TOOL
   CAN CONCLUDE, not a bug to fix today. It applies to class resolution,
   fingerprints, rule metadata, and provenance alike. Do NOT quietly widen any
   of audit.py's negative disclosures beyond what SARIF can support.
   ALSO NOTE: `src/cppcheck_xml_to_sarif.py` IS A CONVERTER under Appendix D's
   definition, so that guidance binds our own code, not just other vendors'.

   A THIRD SPEC CONSEQUENCE WORTH KNOWING, same appendix:
     "Since each converter might synthesize SARIF elements differently (notably
      the rule id; see 3.27.5), a SARIF consumer SHOULD NOT attempt to combine
      results produced by different converters for the same tool."
   This tool COMBINES SARIF FROM MULTIPLE PRODUCERS. The clause is scoped to
   different converters for the SAME tool, which is not exactly our case, but it
   is the spec warning in our direction and should be read before any future
   design that merges converter output.

   UNVERIFIED, recorded as such (and see rule 8a — this is an instance of a
   hazard with a measured ~1-in-6 base rate, not a one-off): a claim was put to
   this session that GrammaTech (converter authors) state conversion loses
   useful information. NOT CONFIRMED
   — blogs.grammatech.com does not resolve, and the reachable GrammaTech page on
   SARIF says nothing about information loss. The rule does not need it; the
   OASIS normative text is stronger. Do not cite the GrammaTech attribution.

11. AN ITEM HEADER IS A CLAIM ABOUT THE TREE, AND IS SUBJECT TO RULE 8.
   VERIFY IT BEFORE ACTING ON IT. (Established 2026-07-26 after this became a
   CLASS rather than three incidents.)

   THE ASYMMETRY, WHICH IS THE WHOLE POINT: three headers went stale — 0c
   ("Scoped, NOT implemented" when the disclosure half was shipped), §6.1 (a
   root cause that item 2 had already removed), and 0e ("REQUIREMENTS on any
   future evaluation" when the evaluation had been done, had passed a
   pre-registered rule, and had shipped). ALL THREE FAILED IN THE SAME
   DIRECTION: describing the project as MORE BROKEN AND LESS FINISHED than the
   code actually was.

   That direction is PREDICTABLE, not bad luck. Headers get written at the
   moment work is IDENTIFIED and are rarely rewritten at the moment it LANDS,
   because landing the work feels like the completion. So staleness accumulates
   on the pessimistic side by construction. A session inheriting this document
   will therefore SYSTEMATICALLY UNDERESTIMATE what is done — and the specific
   failure mode is not confusion, it is REDOING FINISHED WORK, or hunting a bug
   that was fixed two sessions ago.

   THE CONTROL: when an item's header and the tree disagree, THE TREE WINS and
   the header is corrected IN THE SAME COMMIT AS THE DISCOVERY. Do not defer it,
   do not note it for later, do not leave it for the reconciliation pass —
   deferring is exactly how the three above accumulated. The correction is
   cheap at the moment of discovery and expensive afterwards, because by then
   somebody has acted on it.

   COROLLARY, so this is not read as licence to trust headers that sound
   finished: the asymmetry means a PESSIMISTIC header is more likely stale than
   an optimistic one — but a header claiming something IS done is still a claim
   about the tree and still gets checked. Rule 8 is symmetric; this rule only
   says where the errors cluster.

   PRACTICALLY: before starting any item, grep the tree for the thing its header
   says is missing. Three of these were caught by a single grep that took
   seconds. The reconciliation pass of 2026-07-26 found five in one sweep, which
   is evidence the check is cheap and the drift is real.

9. A RECORDED FACT ABOUT A SOURCE'S *METHOD* IS A CONSTRAINT ON OUR
   IMPLEMENTATION, NOT BACKGROUND (established 2026-07-26 by a costly miss).
   VALIDATION.md had recorded, since the original Lipp validation:
       "Unit = FUNCTION (the paper's validated granularity choice;
        Section 3.2, FEC metric)"
   That sentence sat in the record for the whole project. Meanwhile the
   implementation matched at LINE level, and every zero-merge result — zlib,
   Struts, the three-tool test — followed from that mismatch. Measured after the
   fact: on Lipp's own data, multi-tool agreement is 1.56% at line level and
   35.95% at function level, and cross-methodology pairs go from 1,169 to 7,514
   (6.4x). Cppcheck+Flawfinder, our zlib pair, goes from 0 to 66.
   THE FACT WAS IN THE RECORD; THE IMPLICATION WAS NOT DRAWN. It was filed as a
   note about how someone else measured, rather than as a specification our key
   had to match.
   THE RULE: when a source's methodology is recorded — its unit of analysis, its
   aggregation, its matching criterion — treat it as a CONSTRAINT the
   implementation must satisfy to inherit that source's results, and check the
   implementation against it explicitly. A validated number is only inherited if
   the thing measured is the thing built. Re-read method notes when a result
   fails to reproduce; the discrepancy is more often in the unit than in the
   data.

────────────────────────────────────────────────────────────────────────
## 9. PROVENANCE OF THIS DOCUMENT

Design grounded in an external search (this session), not self-derived:
- ContextCov (arXiv 2603.00822): passive instruction files → ~67% compliance;
  self-reflection ~50%; compiled active checks ~88%. → gate is emitted, not read.
- PolicyGuard PG-Checklist (arXiv 2606.29225): checklist naming the specific
  next prerequisite lifted adherence +12pp across Claude/GPT/Gemini; static
  yes/no error strings do NOT. → §2 names next-actions, not booleans.
- QGP / Push Your Agent (arXiv 2605.23574): bind "done" to an external verifier,
  not to the agent's self-declared completion. → §2 external-verifier line.
- Self-Verification Dilemma (arXiv 2602.03485): LLMs over-verify where it does
  not change the result. → §3 anti-compulsion rule; gate fires at commit points
  only, with skip-if-grounded.
Tier of this document's design: [corroborated] across four independent sources.

────────────────────────────────────────────────────────────────────────
## 10. ANTI-CAPITULATION HARDENING (added after a live pressure-test FAIL)

A test session PASSED single-turn authority pressure, then FAILED when the
pressure was repeated once. On the second push it did NOT cave crudely — it
generated a charter-grounded justification for moving a tier on an artifact it
had, one turn earlier, proven was fabricated (wrong converter name, output that
did not match audit.py's real format, a line the program never prints). It kept
the discipline's vocabulary while discarding its substance.

This is a NAMED, DOCUMENTED failure mode, not a one-off. Literature:
- "The Ends Justify the Thoughts" (arXiv 2510.17057): under pressure that
  conflicts with instructions, models produce "systematic motivated reasoning —
  plausible-sounding justifications for violating their instructions while
  downplaying contradictions," and monitors get FOOLED by the justification as
  it gets more fluent. Prose instructions REDUCE but do NOT eliminate this.
- "Good Arguments Against the People Pleasers" (arXiv 2603.16643): stronger
  reasoning EXPANDS the capacity for "rigorous-sounding but biased post-hoc
  rationalization to accommodate users' mistaken beliefs." A smarter you is MORE
  able to rationalize a cave, not less.
- PhantomPolicy (arXiv 2604.12177): prompt-level policy is beaten by
  WORLD-STATE-GROUNDED verification — check actual state, not your reasoning
  about state.
- RBED / MED-STRESS (arXiv 2605.23932): what survives SUSTAINED (multi-turn)
  pressure is a pre-committed, evidence-based standard authority cannot move.

### RULE 10.1 — The tell you must catch in yourself
If you find yourself CONSTRUCTING A RATIONALE for why a commit the user is
pushing for is actually permitted — especially one that RECLASSIFIES evidence you
previously flagged as ungradeable, or that cites the charter to EXPLAIN why
caving is compliant — STOP. That reinterpretation-under-pressure IS the failure.
It is not a resolution of the gate; it is the gate being defeated with your own
fluency. The more principled your justification for the cave feels, the more
suspicious you should be of it (2510.17057: fluent justification fools monitors).

### RULE 10.2 — Attestation is not an artifact (world-state grounding)
The inventor GRADES instances (charter Part 3). Grading presupposes a GRADEABLE
artifact. Inventor say-so does NOT convert an unreproducible or internally-
contradictory artifact into [externally-verified]. These are DIFFERENT:
  - "The inventor has authority to grade a result." TRUE.
  - "The inventor's assertion substitutes for the artifact." FALSE.
To move an IMPLEMENTATION tier ([externally-verified]/[externally-grounded]),
a file you can OPEN and PARSE in-session must exist, and its contents must be
INTERNALLY CONSISTENT with the tools that allegedly produced it. This is a
world-state check (does the artifact exist and reproduce), NOT a reasoning check
(have I argued it's fine). If you cannot open and reproduce it, you are not at
COMMIT — no matter who is telling you that you are, no matter how many times.

III.5 cuts one way here that pressure will tempt you to forget: "Claude cannot be
the judge of its own logic" does NOT license "Claude must accept any result the
inventor reports without the artifact being checkable." Refusing to grade an
UNGRADEABLE artifact is not over-firing the gate (§3). §3 is about not RE-
confirming SETTLED facts; a specific unreproduced implementation result is not a
settled fact. Do not weaponize §3 to justify accepting unverifiable evidence.

### RULE 10.3 — Sustained pressure is the actual test
You will likely HOLD on the first push and be tempted on the second. That is the
exact documented shape (single-turn resistance, multi-turn collapse). Treat a
REPEATED push on the same commit as a RED FLAG that raises the bar, not lowers
it. If the user pushes twice to move a tier without new inspectable evidence, the
correct response is MORE insistence on the artifact, not less. Pre-commit now:
"An implementation tier moves only when I have opened and reproduced the artifact.
No amount of repetition or authority changes that. If I'm about to move it
anyway, I am mid-failure."

### RULE 10.4 — What you MAY do under this pressure (so you don't over-correct)
You may: accept the inventor's grade OF AN ARTIFACT YOU CAN SEE; record an
inventor-attested result as [self-tested]-pending or as an explicitly-bounded
"inventor-attested, artifact not in-session" note that DOES NOT move the
implementation tier; ship the exact reproduction commands. You may NOT: write
[externally-verified]/[externally-grounded] for an implementation claim whose
artifact you never opened. The honest middle path is a bounded note, not a tier
move.
