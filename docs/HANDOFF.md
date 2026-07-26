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

1. [decision — DEMOTED, and coupled to item 2] README honesty. Scoped
   claim-by-claim against the PUBLIC README in
   docs/SCOPE_shipped_consensus_defect.md §5.
   FIRST: THE LOCAL CHECKOUT IS BEHIND. Local HEAD 729e893; origin/main c5f75d6
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
   RECOMMENDATION: do NOT edit the README now. Fix _result_key (item 2) and the
   claims become true as written. Editing first documents a limitation about to
   be removed. Revisit only if the fix is deferred.
   WITHDRAWN: an earlier entry here claimed README L6 redirects cppcheck's SARIF
   from the wrong stream, "PUBLIC and LIVE." The stream observation is true and
   the line exists in the STALE LOCAL copy; the PUBLIC README uses the correct
   `2>` + XML-converter path. Provenance failure recorded in SCOPE §4a.

2. [Mac, medium] THE REAL WORK: `_result_key` two-algorithm fix. Fingerprint for
   SAME-tool dedup; location+class for CROSS-tool. audit.py currently uses the
   same-tool algorithm for both, which is a category error — it cites the
   DefectDojo model, which uses two algorithms precisely to avoid this.
   CRITICAL FRAMING (do not lose it): this fix does NOT risk ROC-AUC 0.755. That
   result was measured on reconstructed envelopes that DID merge (1,318 overlaps
   recovered, hand-count exact). The shipped path cannot merge. So the fix moves
   the SHIPPED config TOWARD the VALIDATED one. See VALIDATION.md 2026-07-26.

3. [Mac, small] RE-MEASURE — TWO distinct questions, both in
   docs/SPEC_item4_groupability_measurement.md. RUN AFTER item 2.
   (a) GROUPABILITY (§1-6, pre-registered): denominator cascade D0/D1/D2,
       U1-vs-U2 split, decision rule, project set. Watch U2: 35 unmapped CWEs
       cover 116 cppcheck checks vs 14 mapped covering 31 — extending the
       28-entry _CWE_CLASS map may beat the badge for far less work.
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

7. [standing] Other specified-not-coded paths: scope+offset dedup hashing;
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
   lines 6/61/64 of 729e893, worktree sha matched the commit, no `2>` anywhere.
   The amendment was REFUSED and that refusal was correct — amending on
   assertion would have replaced a verified finding with an unverified
   retraction. But the inventor was ALSO right: their grep covered an uploaded
   zip = the PUBLISHED README (origin/main c5f75d6), which the local repo, one
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
