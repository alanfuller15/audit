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
- Consensus RE-RANKING at FILE level: [externally-verified] (2026-07-11). Real
  Lipp C/C++ CVE data, 9 projects, 2,559 files, 5 diverse SASTs, real
  CVE-to-function ground truth. ROC-AUC 0.755 vs 0.596 best single tool vs 0.501
  random; PofB@20% = 0.655; vulnerable-rate monotonic in agreement (1 tool 0.9%
  -> 4 tools 11.6%). Corroborated by an independent study on the same data shape
  (arXiv:2407.12241, ~17pp lift from tool combination). Leak sanity check passed
  (no metric >0.85). Supersedes the older "[self-tested] ranking" row.

Tested and REJECTED (do not re-attempt as pending work):
- Tool-quality WEIGHTING layer. Tested on real data and it does NOT beat plain
  tool-counting: tier-weighting ~even with flat consensus, and a separate
  large-scale test (NASCAR, 1.08M Java warnings) found the locational-history
  feature inert (PR-AUC 0.049 vs 0.035 random). Independently corroborated by
  Kang et al. (hand-crafted features "inadequate" after a data-leak fix). Fine
  per-tool weights do not transfer across projects; only a coarse tier prior
  does. CONCLUSION: the tool's value is the SIMPLE consensus signal. This was
  formerly PENDING item 2(b); it is closed by evidence, not deferred.
- FUNCTION-level ranking. Out of scope: 0.9% base rate too sparse (consensus
  ROC-AUC 0.628, IFA 130). The proven value is FILE-level triage only.

## 6.1 STRUCTURAL DEFECT FOUND 2026-07-26 — the headline signal is inert in the
##     shipped product. [self-tested], deductive from the code, verified on real
##     scanner output. Full scoping: docs/SCOPE_shipped_consensus_defect.md

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
## 7. PENDING WORK (REORDERED 2026-07-26 by a structural finding — read §6.1)

THE FINDING THAT REORDERED THIS: the shipped flawfinder+cppcheck pair CANNOT
produce n_tools>1 on any input. flawfinder emits `fingerprints` on every result
so `_result_key` returns `fp:…`; cppcheck emits none so it returns `rk:…`; the
two can never collide. The headline consensus signal is structurally inert in
the shipped product. Full scoping: docs/SCOPE_shipped_consensus_defect.md.

0. [Mac, small — HIGHEST PRIORITY, LIVE IN SHIPPED CODE] Engine-lineage guard.
   PROMOTED 2026-07-26 from item 6b. This is the ONLY defect found in this
   session that INFLATES n_tools. By the asymmetric-error-cost rule that makes
   it the most serious thing outstanding: every other defect costs recall;
   this one CORRUPTS THE HEADLINE SIGNAL that every published number rests on.

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

1. [decision — BLOCKED on 3c] README honesty. Scoped
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
   BLOCKED ON ITEM 3c — DO NOT RE-OPEN WITHOUT THE LIPP ARTIFACT.
   This decision has now been held THREE times, and each prior attempt to settle
   it was overturned by evidence arriving afterwards:
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

3c. [Mac — GATING DEPENDENCY, blocks item 1] RE-EARN the Lipp numbers under
   current code. Requires re-obtaining the Lipp artifact (Zenodo DOI
   10.5281/zenodo.6515687; not on this machine — searched 2026-07-26).
   (a) The 1,318 dedup cross-check. The item-2 cross-tool key, _norm_uri
       normalization and +8 map entries can only ADD merges, so
       "22,403 -> 21,061 dedup, 1,318 overlaps exact" may no longer reproduce.
   (b) THE LARGER ONE — ROC-AUC 0.755 IS UNANCHORED. It was produced by ranking
       the Lipp envelope with PRE-FIX code. The fix changes n_tools; n_tools
       feeds the score (consensus = 1.6 * n_tools); and 0.755 WAS a ranking by
       agreeing-tool count. The fix therefore changes the quantity the number
       measured, over that same input. 0.755 is a property of RETIRED code — it
       described a path that could not merge, not the one that can.
       DO NOT assert it is "probably better" post-fix. That is plausible and
       unmeasured, and this project does not make unmeasured assertions.
       Until re-earned, 0.755 MUST NOT be quoted as a property of the shipped
       tool — not in the README, not anywhere.
   TENSION TO EXPECT, both true at once: the fix moves shipped toward validated
   in MECHANISM and away from it in OUTPUT. The change justified by a
   measurement invalidated that measurement. VALIDATION.md BOUND 2 anticipated
   the transfer question but not this self-invalidation. Resolve by
   re-measuring, NOT by discarding whichever framing is inconvenient.

3d. [trivial] TEST_DIR misses sibling names. `contrib/testzlib/testzlib.c` is
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
