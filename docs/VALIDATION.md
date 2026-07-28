# VALIDATION STATUS — per GENESIS charter III.7

This file records the HONEST verification tier of each part of the tool, using
the three tiers from charter III.7. It exists because a sandbox "PASS" is Claude
grading Claude (internal consistency), NOT external truth. Read this before
trusting any "it works" claim.

## The three tiers (III.7)
- **`[self-tested]`** — ran and passed a test Claude also wrote in-sandbox.
  WEAKEST: a wrong mental model produces wrong code AND a wrong test that still
  passes. "Runs and passes my own test" — never call this "verified."
- **`[standard-checked]`** — output validated against a published reference
  artifact Claude FETCHED (real spec/schema pulled via web_fetch), not memory.
  Strongest tier reachable in-session. Authority is external; harness is Claude's.
- **`[externally-verified]`** — confirmed by a non-Claude engine/judge against
  non-Claude input. NOT reachable in-sandbox. A desktop step you or a trusted
  third party runs. Command given per artifact below.

> **[DEFINITION SUPERSEDED 2026-07-28 — the wording above predates the six-tier
> scale.]** This section records the THREE-tier framing as of v6.0 (2026-07-08).
> The current commit vocabulary is **HANDOFF §5's six tiers**, and there
> `[externally-verified]` is narrower than the line above:
> - `[externally-grounded]` — *"non-Claude engine/data anchors it (design principle)"*
> - `[externally-verified]` — *"external judge on real data confirms the IMPLEMENTATION"*
>
> "Confirmed by a non-Claude engine/judge against non-Claude input" is verbatim
> the **`[externally-grounded]`** test. Read as a definition of
> `[externally-verified]` it collapses the two tiers into one and licenses the
> stronger label on the weaker evidence — the exact direction every recorded
> failure in this project has run. **Where the two disagree, HANDOFF §5 governs.**
> Same correction applied to `docs/AUDIT.md` and `docs/GENESIS_TEMPLATE.md`;
> filed five consecutive times (steps 1–5) before being acted on. The
> `[externally-verified]` tier *assertions* elsewhere in this file are NOT
> re-audited by this note — see the scoped item in HANDOFF.

## Tier map (as of v6.0, 2026-07-08)

| Component | Tier reached | How | To reach `[externally-verified]` |
|---|---|---|---|
| SARIF output conforms to spec (scan mode `--sarif`) | `[standard-checked]` | Validated against the FETCHED official OASIS `sarif-schema-2.1.0.json` (543 constraint-checks, 0 violations on the FieldLab output) | Run `jsonschema` (full engine) against the schema; or POST to NIST SARD validator (commands below) |
| SARIF output conforms to spec (ingest mode `--ingest --sarif`) | `[standard-checked]` | Validated against fetched OASIS schema (46 checks, 0 violations) | Same as above |
| Dedup collapses same finding across tools | `[self-tested]` | Passed a 2-tool scenario Claude built (4 raw → 3 unique) | Run on REAL scanner output (e.g. semgrep + codeql on the same repo) and confirm true duplicates collapse |
| Re-ranking puts review-worthy findings first | `[self-tested]` | Passed on Claude-built synthetic findings; the RANKING SIGNALS are `[fetched]`-grounded in the literature, but the ranking being CORRECT on real data is not externally confirmed | Run against a labeled benchmark (Juliet-derived alert set) and measure true-positives-in-top-N |
| Order-independence of ranking | `[self-tested]` | Passed Claude's swap test (identical ranking regardless of input order) | Confirm on real multi-tool output |
| Determinism (byte-identical reruns) | `[self-tested]` | Passed in-sandbox | Confirm on desktop |
| Ranking SIGNAL CHOICE (location/consensus/severity/kind) | `[fetched]` (design) | Grounded in FAULTBENCH/CASTLE/ensemble labeled-benchmark studies | N/A — this is design validation, already external |
| Architecture (deterministic core + governed LLM layer) | `[fetched]` (design) | 2026 production-arch consensus + DUCTILE + SIGPLAN interleaving paper | N/A |
| LLM triage layer behaves per protocol | `[self-tested]` at best | The protocol is `[fetched]`-grounded (CoT/E&V/ZeroFalse); actual per-run behavior is non-deterministic (COBOL-study) and unaudited | Human review of real triage runs; not fully closable |

## The exact desktop commands to reach `[externally-verified]`

> **[SCOPE CORRECTION 2026-07-28.]** Under HANDOFF §5 (above), these commands do
> not all reach the same tier. Commands 1–3 put a **non-Claude engine** on the
> FORMAT-conformance claim — that is `[externally-grounded]` at least, and
> whether it reaches `[externally-verified]` depends on whether `out.sarif` came
> from a real scan or a fixture, which the command does not say. **Command 4 is
> the one aimed at the gap this file's own "Honest bottom line" names** — the
> dedup/ranking LOGIC, which no engine judges and which needs real scanner output.
> Running 1–3 and recording "`[externally-verified]`" against the ranking claim
> would be a tier move the evidence does not support.

**1. Full JSON-schema validation (mechanical, whole schema):**
```
pip install jsonschema
# save the official schema: https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json
python -c "import json,jsonschema; jsonschema.validate(json.load(open('out.sarif')), json.load(open('sarif-schema-2.1.0.json')))"
```
(This runs the COMPLETE schema engine, including $ref resolution — stronger than
the in-bundle `validation/schema_check.py`, which enforces the constraints Claude
transcribed from the fetched schema, not the whole engine.)

**2. NIST SARD validator (independent authority):**
```
curl -sSf -XPOST 'https://samate.nist.gov/SARD/sarif-validator' -F 'file=@out.sarif'
```

**3. Real render (the "use" confirmation):**
Open `out.sarif` in the VS Code SARIF Viewer extension, or upload to a GitHub
repo's Security tab, and confirm findings render.

**4. Dedup/ranking on real data:**
Run two real scanners (e.g. `semgrep --sarif`, CodeQL) on the same repo, then
`audit.py --ingest a.sarif b.sarif` and confirm duplicates collapse and the top
of the list is genuinely what you'd read first.

## Honest bottom line
Format conformance is `[standard-checked]` — genuinely validated against the real
OASIS schema, pulled into the sandbox. The dedup and ranking LOGIC is only
`[self-tested]` — it runs and passes Claude's own tests, but no non-Claude judge
has confirmed it's correct on real data. Closing that gap is a desktop step, by
design (III.5/III.7): Claude cannot be the external judge of its own logic.

## Search & source discipline (charter III.8, ratified 2026-07-08)
Every web-search-grounded claim in this project is tagged `[snippet]` (search
excerpt only) or `[fetched]` (primary source pulled and read). Source selection
follows SIFT (Hapgood 2019) over CRAAP (Blakeslee 2004): prefer
primary/standards-body/.gov/.edu/peer-reviewed; find better coverage before
concluding; report the denominator (results seen vs. read). Genuinely `[fetched]`
in this project: the OASIS SARIF schema; the CRAAP/SIFT frameworks; the secret-
detection tool literature. The rest were `[snippet]`-level and are marked so.

## Known gap: secret scanner has no entropy scoring
Our secret detection is regex-only. Mature tools (Gitleaks, TruffleHog) pair
regex with Shannon entropy (typically 3.5–4.0 bits/char) to cut false positives
— e.g. `password123` (~3.2) passes, a high-entropy token is flagged. We do not
compute entropy, so our false-positive rate on realistic strings is higher than
a mature tool's. `[corroborated]` across independent 2026 sources. This is a
stated design limit, not a defect; documented here so it is never overstated.

## Real-ground-truth validation attempt (2026-07-08): walls, pivots, and honest findings

We tried to move ranking correctness from `[self-tested]` to real external
validation. This section records what actually happened — including the walls —
because the walls are as informative as the wins (charter II.3).

### What we tested against
OWASP Benchmark v1.2: 2,740 human-labeled Java test cases (1,415 real vulns,
1,325 planted false positives), plus real findings from two tools (SonarQube,
FindBugs) — all downloaded by the inventor and joined to the OWASP answer key.
Genuine external ground truth, not Claude-generated. `[fetched]`.

### Finding 1 — our severity/category ranking FAILED its first real test.
Ranking pooled findings globally by category-severity and measured
true-positives-in-top-N. Result: WORSE than random on SonarQube (16 TPs in top-25
vs. ~20 random), no better than random on FindBugs. Honest negative result.

### Pivot — why: the benchmark is documented as hostile to category ranking.
Web search (`[fetched]`, multiple peer-reviewed sources) established OWASP
Benchmark is engineered so category is an unreliable signal — it plants plausible
fakes in the scary categories specifically to defeat "shortcut learning" (OpenAnt
2026; systematic SAST review 2025). Its own scoring AVERAGES per-category on
purpose; global pooling (what we did) is documented as misleading. So the negative
result is CONFOUNDED, not clean — but it does NOT exonerate us: dodging a flawed
test is not a passing test.

### Finding 2 — within-category analysis (category confound neutralized) found REAL signal.
Holding category constant: tool-flagging correlates strongly with truth (74% TP
when a tool flags vs. 38% when none do). A tool's flag is a PERFECT discriminator
in some categories (crypto, hash: 100% TPR / 0% FPR) and pure NOISE in others
(cmdi, ldapi: flags everything). This is real signal on real ground truth, though
still on synthetic data with documented transfer caveats.

### Finding 3 — the data points at a signal we DON'T currently compute.
The right ranking signal is not "category severity" but "how discriminating is
THIS tool in THIS context" — per-tool-per-rule reliability. This matches the
FAULTBENCH literature (location + history of past alerts = top predictors). Our
tool doesn't compute it yet. Honest gap → concrete design direction.

### Wall 1 — consensus signal untestable on this data.
SonarQube and FindBugs flagged the SAME case ZERO times (CWE-normalization
artifact of the scorecards). Our headline signal — diversity-aware consensus —
had nothing to fire on. Cannot be validated here. Needs a genuinely overlapping
tool pair, or raw SARIF from two tools on the same code.

### Wall 2 — PrimeVul (the right instrument) could not be fetched.
The realistic corrective (PrimeVul: ~7k real vulnerable + ~229k benign functions,
WITH file-path metadata our location signal needs) was identified and confirmed
real. But the data files are HuggingFace-hosted and too large / access-gated to
pull into the sandbox, and too large to reasonably hand-download. Location signal
therefore REMAINS UNTESTED. Named honestly as an open item, not closed.

### Design outcome — evidence-driven signal gating (NOT benchmark detection).
The inventor asked: can the tool selectively use only the signals that fit the
input? Yes — but the selection criterion is "does this input contain the evidence
each signal needs?" NEVER "is this a known benchmark?" (the latter is
benchmark-gaming, the exact trap the research warns against). Implemented as a
gate that, per input, reports which signals are informative (location variety?
tool overlap? severity spread?) and DOWN-WEIGHTS + DISCLOSES the ones that aren't.
On OWASP-shaped input it correctly reports "all three ranking signals
uninformative here; ranking low-confidence." This degrades nothing, works on any
input, and makes the tool self-disclosing about its own competence — which is the
charter ethos, not a benchmark hack.

### Honest tier summary after this session
- Consensus/tool-flag correlates with truth: `[standard-checked]` (real ground
  truth, synthetic-data caveat). Real signal, confirmed.
- Severity/category ranking alone: `[standard-checked]` and FOUND WANTING; the
  better signal (per-tool-per-context reliability) is not yet built.
- Location signal: still `[self-tested]` — the instrument to test it (PrimeVul)
  exists but could not be reached in-session.
- Evidence-driven signal gate: `[self-tested]` (new; runs and behaves correctly
  on shaped inputs, but "correct on real data" needs the same external tests).

## Systematic design-claim audit (2026-07-08): every load-bearing claim, re-tagged

The inventor asked to apply multi-framing external search across ALL prior
deliverables, and to close coverage gaps. HONEST SCOPE NOTE FIRST: gaps that
require a non-Claude judge on real data CANNOT be closed in-session (charter
III.7) — searching can move a claim's DESIGN from `[self-tested]` to
`[corroborated]`/`[fetched]` by grounding the principle in literature, but it
CANNOT make our specific implementation's CORRECTNESS externally verified. So
this audit closes the *grounding* gaps it can and names the rest as un-closable
here. Distinguishing "design grounded" from "implementation verified" is the
whole point.

| Claim | Design tier (after audit) | Implementation tier | External grounding found |
|---|---|---|---|
| Deterministic backbone + governed LLM layer | `[fetched]` | n/a (architecture) | 2026 production-arch consensus; DUCTILE; SIGPLAN interleaving; tool-calibration "confidence dichotomy" paper independently endorses deterministic-floor design |
| SARIF format conformance | `[standard-checked]` | `[standard-checked]` | validated vs. fetched OASIS schema (543/46 checks, 0 violations) |
| Ranking signal CHOICE (location/consensus/severity/kind) | `[fetched]` | — | FAULTBENCH/CASTLE/ensemble labeled-benchmark literature |
| Diversity-aware consensus (distinct tools only) | `[fetched]` | `[self-tested]` | CASTLE: redundant-tool overlap amplifies shared FPs |
| Dedup by fingerprint/location | `[corroborated]` | `[self-tested]` | DefectDojo mechanism; Wiz/AI-SAST dedup-then-rank is standard ASPM |
| Subprocess/E2E coverage-confidence flag | `[corroborated]` | `[self-tested]` | coverage.py + multiple 2025/26 sources: subprocess-spawned tests are a DOCUMENTED coverage blind spot |
| Monorepo/polyglot detection (colocation≠monorepo, substance-weighting) | `[corroborated]` | `[self-tested]` | monorepo.tools, Nx, + peer-reviewed Multivocal Literature Review on monorepo definitions |
| Inline-test detection (Rust cfg(test)/Go Example/py doctest) | `[self-tested]` | `[self-tested]` | language docs confirm the CONSTRUCTS exist; our detection accuracy unverified |
| Secret regex design limits (regex-only, no entropy) | `[corroborated]` | `[self-tested]` | Gitleaks/TruffleHog literature: regex+entropy is the mature standard; we lack entropy — STATED GAP |
| LLM triage protocol (CoT, verify-first, cite-or-abstain) | `[fetched]` | `[self-tested]` | ZeroFalse/E&V/IEEE CoT study |
| Evidence-driven signal gate | `[corroborated]` | `[self-tested]` | FIVE literatures: selective prediction, confidence-gating theorem, adaptive alert ranking (Heckman 2007), mutual-information/permutation testing, OOD/out-of-model-scope detection; "bouncers" paper is near-identical concept |

### Gaps that remain OPEN (un-closable in-session, by design — III.7)
Every "Implementation `[self-tested]`" above needs the same thing to close: a
non-Claude judge (real scanner output, labeled benchmark, or execution engine)
on non-Claude input. The instruments exist (Juliet/OWASP/PrimeVul) but could not
be run in-sandbox. These are honest desktop steps, listed with commands earlier
in this file. NONE are closed by this audit; all are now precisely NAMED.

### The load-bearing open gap (flagged loudly)
The evidence-driven signal gate's confidence signal is ITSELF unverified — we
never ran the "competent for gating" test (does our confidence label actually
predict ranking quality? — Spearman ρ > 0, per the robot-autonomy paper). This
is an unverified assumption inside the mechanism we built to police unverified
assumptions. Highest-priority thing to verify on real data. Not closed here.

### What the multi-framing audit DID accomplish
Moved 4 claims from `[self-tested]` design → `[corroborated]`/`[fetched]` design
(dedup, subprocess-confidence, monorepo, signal-gate) by grounding their
PRINCIPLES in external literature. Confirmed nothing we designed is idiosyncratic
— every major choice has independent literature support. But design-grounding is
not implementation-verification, and this audit changed zero implementation tiers.

## Full 5-framing literature sweep (2026-07-08): every load-bearing claim, all framings

The inventor requested the complete sweep: every load-bearing design claim audited
through 5 distinct search framings — (1) SAST/security-tooling, (2) ML/statistics,
(3) formal/theory, (4) software-engineering practice, (5) adjacent field — with
empties reported honestly as negative results. This is the exhaustive version;
future audits will target load-bearing claims only.

HONEST SCOPE CORRECTION: the working inventory initially listed 12 claims, but
"coverage-confidence (E2E)" and "subprocess/coverage-confidence" are the SAME
claim (the flag IS the mechanism). Real count: 11 distinct claims × 5 framings =
55 framing-cells. All 55 filled.

### Per-claim results (design-grounding tier after full sweep)

1. **Architecture (deterministic backbone + governed LLM)** — `[fetched]`, all 5.
   Strongest-validated decision in the tool. Formal: neuro-symbolic separation
   (deterministic engine + non-authoritative LLM explainer = 100% determinism).
   Adjacent: the MANDATED safety-critical pattern (defense guidance, aviation
   autopilot advisory-only, clinical CDSS logic-vs-governance split). "Deterministic
   shell, probabilistic core" is a named standard pattern.

2. **SARIF format conformance** — `[standard-checked]`, all 5. Validated vs the real
   OASIS schema. Both new framings SHARPEN the boundary: schema-conformance ≠
   content-correctness (ML) and = "conformance testing" not "certification" or
   "verification" (adjacent). Matches charter "tools verify presence not truth."

3. **Ranking-signal choice** — `[fetched]`, all 5. Formal: Learning-to-Rank frames
   it as feature-vector scoring; optimal combination is NP-hard (so fixed weights
   defensible). Adjacent: medical triage (ESI) uses identical weighted-signal
   ranking AND independently confirms our OWASP lesson (signals weak in isolation,
   over/under-triage common, context-dependent).

4. **Diversity-aware consensus** — `[fetched]`, all 5, EMPIRICALLY validated.
   Formal: correlated errors provide no ensemble benefit (proof); reducing
   correlation tightens error bound. SE-practice: NPM study — tool intersection
   → 97% precision, cross-methodology pairs win (disjoint miss-sets). Adjacent:
   inter-rater reliability ("reliable raters behave like independent witnesses").

5. **Dedup** — `[fetched]`, all 5. GAP surfaced + confirmed across 3 independent
   fields (SAST, record-linkage, storage): exact-fingerprint is high-precision/
   low-recall, brittle to code-shift; mature fix = scope/content-based hashing.
   Formal: set-union is commutative/associative/idempotent (proves order-independence).

6. **Coverage-confidence / subprocess detection** — `[fetched]`, all 5. Formal:
   exact coverage is UNDECIDABLE (Rice) — our humility is FORCED, not optional.
   ML: missing-mass/unseen-species gives a principled lower-bound upgrade path.
   Adjacent: professional audit "sampling risk" + "scope-limitation disclaimer."

7. **Monorepo/polyglot detection** — `[corroborated]`, all 5. Formal VINDICATES
   the heuristic: proper graph-partition detection is NP-hard + resolution-limited,
   so a lightweight heuristic is defensible (as Nx/Bazel also do). ML exposes it's
   a coarse proxy for community-detection. Adjacent (ecology) weak/analogical, noted.

8. **Inline-test detection** — `[corroborated]`, 4 of 5 (1 HONEST EMPTY). SE-practice
   strongest: #[cfg(test)]/doctests are documented conventions. Formal partial
   (conditional-compilation/DCE). Adjacent field: NO grounding found — "test-as-
   scaffolding" is metaphor only. Negative result reported, not forced.

9. **Secret regex limits (no entropy)** — `[fetched]`, all 5. Exemplary honest
   self-assessment: our disclosed "regex-only" gap is accurate and corroborated
   across 5 fields; formal (Kolmogorov: K uncomputable, random/structured
   distinction is crypto-hard) shows even the FIX (entropy) has a theoretical ceiling.

10. **LLM triage protocol** — `[fetched]`, all 5. Formal both-edged: stepwise
    soundness frameworks support verify-first, BUT faithfulness tests measure
    output self-consistency not true reasoning (validates charter's "Claude can't
    judge own logic"). Adjacent: clinical debiasing (checklists, second opinion,
    consider-opposite) = our protocol; mitigates not guarantees.

11. **Evidence-driven signal gate** — `[corroborated]`, all 5 (earlier this session).
    Selective prediction / confidence-gating / adaptive alert ranking / mutual-
    information / OOD detection. LOAD-BEARING GAP: our confidence signal is itself
    unverified (the "competent for gating" Spearman-ρ test — desktop-only).

### What the full sweep established
- Every one of the 11 load-bearing design claims is grounded across multiple
  independent literatures. NOTHING we designed is idiosyncratic — every major
  choice was independently arrived at by one or more established fields.
- 1 honest empty (inline-test / adjacent) and several weak/partial hits, all
  flagged rather than inflated.
- Recurring honest pattern: our GOALS/DESIGNS are well-grounded; our METHODS are
  frequently the lightweight-heuristic version of a rigorous (often NP-hard or
  uncomputable) ideal — which the theory itself shows is a defensible tradeoff.
- CRUCIAL: this sweep changed only DESIGN-grounding tiers. Zero IMPLEMENTATION
  tiers moved. Design-grounding ≠ implementation-verification (charter III.7).
  Every implementation claim remains `[self-tested]`, closable only by an external
  judge on real data (desktop). The sweep tells us we're building the right things;
  it does NOT tell us we built them correctly.

## External validation on real CVE data (2026-07-09): diversity-consensus principle

This is the first validation in this project's history against **real external
ground truth** (not literature, not sandbox self-test). It closes a chain that
started with the OWASP negative result and ran through the tool-overlap wall.

### Data & provenance
- Source: Lipp, Banescu, Pretschner, "An Empirical Study on the Effectiveness of
  Static C Code Analyzers for Vulnerability Detection," ISSTA'22.
  Artifact: Zenodo DOI 10.5281/zenodo.6515687 (CC-BY-4.0). Fetched via Zenodo
  (record metadata web-fetchable; data files hand-downloaded by inventor and
  re-uploaded — the confirmed workaround for robots-gated file payloads).
- Content: 6 distinct SAST tools (Flawfinder, Cppcheck, Infer, CodeChecker,
  CodeQL, CommSCA) run on 27 real C projects, 1.15M LoC, 192/193 validated CVEs
  as ground truth. Per-finding tool flags (file, line, CWE, found_by) in
  sca_results.json — the tool-OVERLAP data OWASP structurally could not provide.

### Methodology (faithful to the source paper, NOT improvised)
- Unit = FUNCTION (the paper's validated granularity choice; Section 3.2, FEC
  metric). NOT per-finding — an earlier per-finding oracle was abandoned as
  methodologically invalid (it produced a meaningless 1.2% TP rate because no
  per-finding precision ground truth exists — see "honest limits" below).
- Detection (Scenario S1-1): a CVE is detected if >=1 of its affected functions
  is marked by >=1 tool in the set, regardless of vuln class.
- FP proxy = Marked-Function Ratio (the paper's own precision surrogate, since
  per-finding precision ground truth does not exist).

### Reconstruction cross-check (why this result is trustworthy)
Our independently-built oracle reproduces the paper's published figures:
- CommSCA best single tool @ 53.9% (paper: ~53%, "misses 47%"). MATCH.
- All-6-tools recall 68.9% / 133 CVEs (paper: ~70%, 135/192). MATCH.
- Lift +15.0pp detection @ +12pp functions flagged (paper: +17pp @ +15pp). MATCH.
An independently-constructed oracle landing on externally-published numbers is
the check that distinguishes this from a sandbox result grading itself.

### Result: diversity-aware consensus — design principle CONFIRMED on real data
- **Spearman rho (n_distinct_tools vs recall) = +0.700** across all 63 combos.
- Monotonic, no reversals: k=1 22.2% -> k=2 38.2% -> k=3 49.8% -> k=4 58.3%
  -> k=5 64.4% -> k=6 68.9% mean recall.
- Combining all 6 distinct tools: +15pp CVE detection over best single tool.
- Contrast: OWASP gave rho = UNDEFINED (zero tool overlap). Right instrument -> +0.700.
- This is the exact mechanism our signal gate's diversity-aware consensus encodes
  (distinct tools have disjoint miss-sets; union across DISTINCT tools recovers
  misses). Tier for the PRINCIPLE moves to [externally-grounded].

### Honest limits (what this does NOT establish)
- Implementation NOT validated. This confirms the PRINCIPLE our gate relies on is
  true on real data; it does not verify audit.py computes consensus correctly.
  Implementation tier remains [self-tested], unchanged.
- Recall-side only. Measures detection + flagged-function FP proxy, NOT per-finding
  precision. Per the source paper's own statement, per-finding precision ground
  truth DOES NOT EXIST in this (or comparable public) datasets.
- Therefore the per-finding competence-rho of our confidence signal is
  **untestable with existing public ground truth** — reclassified from
  "untested, need data" to "requires either self-run tools with manual
  per-finding labeling, or acceptance of recall-level validation as the closest
  available." This is a ground-truth-EXISTENCE limit, not an access limit.

### Two refinements surfaced BY the data (specified, not vague)
1. **Cost-weighting the consensus signal.** Diversity buys +15pp detection at
   +12pp more functions flagged — not free. UPGRADE: the gate should expose the
   recall/flagged-ratio tradeoff (detection gained per additional function
   flagged) rather than treating "more tools agreeing" as costless. Concretely:
   report marginal-detection-per-marginal-flag when adding a tool to the set.
2. **Tool-quality weighting ("good vs bad diversity").** CommSCA alone (54%)
   beats many 3-tool open-source combos; a weak tool's agreement is worth less
   than a strong tool's. UPGRADE: weight each tool's consensus contribution by
   its standalone reliability (per-tool, ideally per-CWE-class recall), instead
   of treating tools interchangeably. Matches the ensemble-theory "good diversity
   vs bad diversity" decomposition already in the framing sweep (claim 4, F3).

## Real multi-tool ingest test + implementation fixes (2026-07-09, cont.)

After the recall-side principle validation (rho=+0.700), we ran the IMPLEMENTATION
against real multi-tool output — the test the synthetic-Juliet live-scanner run
could not provide (cppcheck found nothing on Juliet; studied + reframed: Juliet is
synthetic macro-guarded code that the source paper itself warns is non-
representative, so forcing a result there would validate nothing).

### Test: audit.py --ingest on real Lipp findings (PHP subject, richest overlap)
- Converted the real PHP sca_results.json (22,403 real findings from 6 distinct
  tools, with 1,318 genuine cross-tool overlaps) into per-tool SARIF and ran
  audit.py --ingest on all six.
- PROVENANCE NOTE: the findings (file, line, CWE, which-tools) are 100% real Lipp
  data; the SARIF *envelope* was reconstructed (Lipp is not distributed as SARIF).
  So this validates processing of real multi-tool FINDINGS with real overlap; the
  raw live-scanner-SARIF parse path is covered separately by the flawfinder run.

### Results — implementation behaves correctly on real overlap
- Dedup: 22,403 raw -> 21,061 unique. Independently MATCHES the hand-computed PHP
  distinct-finding count. Dedup arithmetic conforms to ground truth.
- Overlap recovery: tool surfaced exactly 1,318 multi-tool findings — IDENTICAL to
  the hand-computed overlap count. Not approximate; exact.
- Signal gate: correctly detected consensus as informative and raised ranking
  confidence to "high" when real overlap was present (vs "medium"/severity-only on
  the single-tool Juliet run). This consensus-active path had never been exercised
  on real input before.
- Ranking reproduces the validated principle: mean review-worthiness score rises
  monotonically with tool agreement (1 tool 5.21 -> 2 tools 6.70 -> 3 tools 8.30);
  Spearman(n_tools, our-score)=+0.649, consistent with the hand-validated recall-
  side rho=+0.700. The implementation encodes the externally-validated principle.
- Top findings are all 3-distinct-tool agreements (e.g. CWE-476 null-deref in
  phar_object.c flagged by CodeChecker+CodeQL+Cppcheck) — diversity-consensus
  mechanism working on real code.

### Tier movement
Ingest/dedup/consensus-ranking machinery moves from [self-tested] toward
[externally-grounded]: it (a) processed real external tool findings, (b) matched
an independently-computed overlap count EXACTLY (1,318=1,318), and (c) reproduced
a separately-validated principle. Three external anchors, not self-grading.
HONEST BOUND: real findings + real overlap + real principle-match; SARIF envelope
reconstructed. Live raw-SARIF parse validated separately (flawfinder, below).

### Two real implementation bugs found on real data + FIXED
Surfaced by running on the actual Mac with real scanners — exactly what external
execution exists to find. Both fixed and regression-tested (real 6-tool ingest
output verified byte-stable after fixes):
1. No --help handler: `audit.py --help` treated "--help" as a directory path
   ("not a directory: --help"). FIXED: --help/-h now prints usage, exits 0.
2. Empty SARIF raised an alarming parse error. A scanner that finds nothing may
   emit an empty file — not a malformed input. FIXED: empty/whitespace-only inputs
   report as clean "empty (no findings) — skipped"; genuinely malformed input
   STILL reports a real parse error (verified — the fix distinguishes the two,
   does not swallow real errors). Graceful-degradation design confirmed on real
   bad input throughout.

### Third bug (same class) found during fix-verification + root-caused
While regression-testing the --help fix, `audit.py --run-tests` (flag with no
directory) failed with "not a directory: --run-tests" — the SAME bug class as
--help (a flag treated as a path). Rather than patch per-flag, root-caused it:
PROJECT_DIR is now resolved as the first non-flag positional argument (skipping
--json/--sarif values), so modifier flags in any position are never mistaken for
a path, and a flag-only invocation prints usage + a clear error. Verified across
five invocation shapes (flag-only, --help, dir scan, dir+modifier, ingest) with
the real 6-tool ingest output confirmed byte-stable (21,061 dedup / 1,318 overlap
unchanged). Lesson recorded: the first two fixes patched instances; the class
needed a root fix. This is itself evidence for why external execution matters —
the flaw was invisible to prior sandbox self-testing.
UPDATE (2026-07-11) — Ranking now tested on REAL C/C++ CVE data

> **[SUPERSEDED 2026-07-26 — READ THIS BEFORE THE FIGURES BELOW.]**
> Every performance figure in this section (ROC-AUC 0.755, PofB@20% 0.655,
> 0.9%->11.6% monotonicity, and the `[externally-verified]` tier) has been
> RETIRED. They are not effort-aware, and ManualDown — ranking files by
> descending size while reading no tool output — scores 0.845 on the same data.
> The later effort-aware and size-matched controls are in "0g CONCLUSION" at the
> end of this file. This section is retained as the historical record of what
> was claimed and when, NOT as a current result. Do not cite these numbers.

The tier map above listed "Re-ranking puts review-worthy findings first" as
[self-tested] — passed only on Claude-built synthetic findings. That has now been
tested against real ground truth. Updated status:

Re-ranking (consensus) — now [externally-verified] at FILE level

Ran the consensus ranking against the Lipp dataset: 9 real C/C++ projects (binutils,
ffmpeg, libpng, libtiff, libxml2, openssl, php, poppler, sqlite3), 135 CVE-vulnerable
functions, 5 diverse SASTs (Cppcheck, CodeChecker, CodeQL, Flawfinder, CommSCA).
Ground truth = real CVE-to-function mappings, not Claude-generated.

Result (file level, 2,559 files, 3.4% vulnerable):

methodROC-AUCPR-AUCPofB@20%consensus (# agreeing tools)0.7550.0870.655best single tool (CommSCA)0.5960.0420.333random0.5010.0400.172


Consensus beats the best single tool by a real margin, and roughly doubles random.
PofB@20% = 0.655: inspecting the top 20% of files by tool-agreement catches ~65% of
vulnerable files.
Vulnerable-rate rises monotonically with agreement (1 tool 0.9% -> 4 tools 11.6%).
No metric exceeded 0.85 (leak sanity check); 0.755 is legitimately at the top of the
honest field ceiling (~0.5-0.7 leak-free).


External corroboration (not Claude): an independent empirical study on the same data
shape (arXiv:2407.12241) found combining tools detects ~17pp more vulnerabilities than
the best single tool, and that individually-weak tools find bugs others miss — matching
this tool's thesis.

Honest limits found in the same testing (stated, not hidden)


Function-level ranking does NOT work (0.9% base rate too sparse; consensus
ROC-AUC 0.628, IFA 130). The tool's proven value is FILE-level triage only.
The tool-quality WEIGHTING layer does not beat plain tool-counting. Ranking
experiments on real data showed the tier-weighting ~even with flat consensus, and a
separate large-scale test (NASCAR, 1.08M Java warnings) found the "locational-history"
feature inert (PR-AUC 0.049 vs 0.035 random). Independently corroborated: Kang et al.
found these hand-crafted features "inadequate" after fixing a data leak. Conclusion:
the tool's value is the SIMPLE consensus signal, not elaborate per-warning weighting.
Fine per-tool weights do not transfer across projects; only a coarse tier prior does.


What this changes

The core thesis — multi-tool consensus ranks real vulnerabilities better than any single
tool — is now [externally-verified] on real C/C++ CVE data at file level, not just
[self-tested]. The elaborate weighting redesign was tested and does NOT earn its place;
production should rely on the simple consensus signal. Function-level ranking remains
out of scope (too sparse to be useful).

## Narrowed bound on the cross-tool display-dedup gap (2026-07-26)

Recorded BEFORE implementing docs/SPEC_dedup_shipped_path.md, because that
spec's original framing overstated the gap and the overstatement would have
propagated into a shipped claim.

### The claim that was wrong
The spec asserted that the HTML report "renders cross-tool agreement as
unrelated single-tool findings." False in general. Corrected in the spec.

### What is actually true (verified by execution this session)
`cppcheck_xml_to_sarif.py:17` puts cppcheck's `cwe` attribute into the ruleId
(`"CWE-%s"`). `_result_key` (audit.py:521) falls back to
`rk:{ruleId}|{uri}|{startLine}` absent fingerprints. So SAME-ruleId,
same-location cross-tool agreement merges at the SCORING layer with `n_tools=2`
and ALREADY renders today — `audit_html_report.py:51-52` emits a chip per tool
plus an `N tools` consensus badge. Confirmed end-to-end; the rendered cell is
`<span class="chip">Cppcheck</span><span class="chip">flawfinder</span><span
class="consensus">2 tools</span>`.

The shipped gap is therefore NARROWER than stated: it is the same-location /
DIFFERENT-ruleId / same-CWE-class case, plus three merge-blockers where
same-ruleId agreement still fails to merge (tool emits fingerprints → `fp:`
branch is tool-specific; uri form mismatch → `_norm_uri` only handles
backslashes and a leading `/`; line offset → scoring needs an exact match).
The display pass rescues all three (verified: 1 group each), because it
compares basename + CWE-class + `TOL=3`.

### The binding constraint, and a second cause not previously anticipated
The display pass cannot group anything whose CWE-class is unresolvable on
either side. Real cppcheck 2.21.0 on `examples/sample_c/demo.c`, through the
real converter and `_cwe_class`: **1 of 9 findings groupable (11%)**. Two
distinct suppressors, roughly equal here:
1. no `cwe` attribute → check-name ruleId, and **0 of 10 raw errors carried a
   CWE number in the message text** — so the fallback is genuinely ungroupable;
2. `cwe` attribute present but the CWE is in `_CWE_DENY` — 4 of the 5 findings
   that HAD a cwe attribute were denied (398, 563, 561).

Cause (2) was not anticipated in the original concern and is as large as (1)
on this sample. Any real measurement must separate the two.

### FOLLOW-UP, same session — the correction above was itself too strong

The narrowing above is correct as a statement about `audit.py`'s CODE. It is
misleading as a statement about the SHIPPED ACTION. Both were checked; the
second check reverses the practical conclusion.

`action.yml` runs exactly two scanners: `flawfinder --sarif` and `cppcheck`
(XML→SARIF). Against real output from both, on the same relative path:

```
uri forms match: True          (my earlier mismatch was a harness artifact, not real)
n_tools distribution: {1: 15}
ANY cross-tool merge: False
```

**No flawfinder finding can EVER merge with a cppcheck finding.** This is
deductive from `_result_key`, not a property of the sample:

- Real flawfinder emits `fingerprints: {"contextHash/v1": "<sha256>"}` on
  **6 of 6** results. `_result_key` therefore returns `fp:contextHash/v1=...`
  for every flawfinder finding.
- `cppcheck_xml_to_sarif.py` emits no fingerprints, so every cppcheck finding
  gets `rk:{ruleId}|{uri}|{line}`.
- An `fp:`-prefixed key can never equal an `rk:`-prefixed key. The merge is
  impossible on any input, for this tool pair.

A second, independently sufficient blocker: the two tools' ruleId namespaces
are disjoint by construction — flawfinder emits `FF1013`, `FF1001`; cppcheck
emits `CWE-415` or a check name. They never match even without fingerprints.

### Consequence — the validated headline signal is inert in the shipped product

`n_tools` (diversity-aware consensus) is this tool's headline signal, the one
carried to `[externally-verified]` at file level (ROC-AUC 0.755)
— **[TIER RETIRED 2026-07-26; MARKER ADDED 2026-07-28. Do not read this clause
as a current tier.** The `[externally-verified]` tier on ROC-AUC 0.755 was
retired by the SUPERSEDED banner above the "UPDATE (2026-07-11)" section
earlier in this file. That banner does not cover THIS section, so the phrase
survived here unmarked. The sentence's POINT — that the headline signal is
inert in the shipped pair — stands and does not depend on the tier.]** **In the
shipped two-scanner action it can never exceed 1.** The Lipp validation ran on
a RECONSTRUCTED SARIF envelope — already flagged in this file as the honest
bound of that result — and that envelope evidently carried no fingerprints and
consistent ruleIds, conditions the real scanner pair does not satisfy.

This is a transfer gap between the validated configuration and the shipped one.
It is NOT a refutation of the ROC-AUC 0.755 result, which stands on its own
data. It means the shipped action does not currently produce the input that
result was measured on.

Implications, in order of importance:
1. `_result_key` preferring a tool's own fingerprint is a category error for a
   CROSS-tool consensus key. The DefectDojo model this cites uses TWO
   algorithms — fingerprint for SAME-tool dedup, location+class for cross-tool.
   audit.py uses the same-tool algorithm for both. Candidate real fix; it is in
   `audit.py`, which SPEC_dedup_shipped_path.md places out of scope.
2. `audit_dedup_display.py` is therefore not a narrow add-on for a
   different-ruleId corner case. It is the ONLY mechanism by which cross-tool
   agreement can surface at all in the shipped action. Its priority goes UP.
3. Item 4's measurement must target realized display groups on the real tool
   pair, not per-tool CWE-class resolution in isolation.

### Why the `_result_key` fix STRENGTHENS ROC-AUC 0.755 rather than risking it

Recorded BEFORE touching code, because it inverts the standard objection that
changing ranking behaviour invalidates a published metric. That objection does
not apply here, and the reason is worth stating plainly.

ROC-AUC 0.755 was measured on RECONSTRUCTED Lipp SARIF envelopes — envelopes in
which cross-tool merging **did** occur. This file records 1,318 multi-tool
overlaps recovered from that data, matching a hand-computed count exactly. So
the VALIDATED configuration is one where cross-tool merge works.

The SHIPPED configuration cannot merge at all (above). Therefore:

> The two-algorithm fix moves the shipped configuration TOWARD the validated
> one, not away from it.

The current shipped state is what fails to reproduce the conditions 0.755 was
measured under. Fixing `_result_key` does not put the number at risk — it is
the precondition for the number applying to the shipped product at all.

BOUND 1 — the artifact was not re-opened. This rests on this file's recorded
1,318-overlap match. The reconstructed envelope was not re-examined in the
session that made this argument. If that envelope merged for some other reason
the argument weakens, though the direction of the fix does not.

BOUND 2 — **DIRECTION IS NOT TRANSFER. Read this before leaning on the
argument above.** "The fix moves shipped TOWARD validated" is a claim about
DIRECTION, not a transfer guarantee. It does NOT establish that a fixed shipped
path reproduces the conditions 0.755 was measured under.

The reconstructed envelope had some PARTICULAR merge topology — a specific
distribution of how many findings merged, at what rate, across which tool
combinations, with whatever co-location characteristics the reconstruction
happened to produce. A location+class cross-tool key on real scanner output may
or may not reproduce that topology. Plausible ways it diverges: a different
merge rate; merges concentrated in different CWE classes; two real tools whose
co-location behaviour differs from the reconstruction's; a coarser or finer key
than the reconstruction effectively used.

So the honest statement is:

> Fixing `_result_key` is a PRECONDITION for 0.755 applying to the shipped
> product. It is not SUFFICIENT for it. Whether the number transfers is an
> open empirical question that the fix does not settle.

If post-fix merge behaviour on real scanner output turns out to differ
materially from the reconstructed envelope's, **0.755 must be re-earned on real
scanner output rather than inherited.** Do not let a later session cite the
direction argument as though it discharged that obligation. The measurement
that would settle it is specified in
`docs/SPEC_item4_groupability_measurement.md` §7.

Full claim-by-claim scoping of what is and is not false, including a second and
independent README defect (the quickstart redirects cppcheck's SARIF from the
wrong stream, silently degrading the two-scanner quickstart to a single-tool
run): `docs/SCOPE_shipped_consensus_defect.md`.

### Tier
`[self-tested]` — this is Claude's harness on Claude-built probe inputs plus one
real cppcheck run on a 25-line toy file (n=9, 3 of which are
`missingIncludeSystem` include-resolution noise). The merge-vs-no-merge
behaviour is a direct observation of the shipped code and is solid. The 11%
groupability number is a DIRECTIONAL SIGNAL ONLY, not a frequency estimate —
it does not survive contact with a real library and must not be quoted as a
rate. Measuring it properly (HANDOFF §7 item 4) is a prerequisite for deciding
how prominent the badge should be; the render must not be designed around an
assumed frequency.

## _result_key two-algorithm fix (2026-07-26) — implemented, tested, real-library result

Closes the structural defect recorded above: the shipped scanner pair could not
produce `n_tools > 1` on any input. HANDOFF §7 item 2.

### What changed (src/audit.py only; no action.yml, no README)
1. **Dedup split by purpose.** Phase 1 SAME-tool dedup keeps the fingerprint
   branch, now scoped by tool so one tool's fingerprint cannot collide with
   another's key. Phase 2 CROSS-tool consensus unions records from DIFFERENT
   tools by normalized location + CWE class (or identical ruleId, which
   preserves pre-fix behaviour so the change cannot REGRESS a working merge).
   Union-find with lowest-index-wins, so the result is order-independent.
2. **`_norm_uri` given real path normalization.** Was backslashes + leading
   slash only, so `./src/x.c` and `src/x.c` were different keys. Now handles
   `file://`, percent-encoding, `./`, `../`, and duplicate slashes. Lexical
   only — ingest must work on SARIF produced on another machine.
3. **`_CWE_CLASS` extended conservatively**, +8 entries: 131/786 (buf),
   590/762 (uaf), 771 (leak), 128/195/197 (int). Only existing classes were
   extended; no new class was created without frequency evidence, because a
   class with one member can never produce a merge. `_CWE_DENY` gains 664 and
   758 (junk-drawer, 20 checks each). 252/467/362/833/686 deliberately left
   unmapped pending measurement.
   Rationale, stated because it governs future edits: a FALSE merge inflates
   `n_tools`, the signal every published number rests on; a MISSED merge only
   costs recall. Unmapped (no merge) is the safe default.
4. Display module now imports the canonical map from audit.py with a
   standalone fallback, so the two cannot drift.

### Verification
- `examples/fixtures/verify_cross_tool_key.py` — 16 checks, all pass: merge
  occurs on real captured fixtures; same-tool dedup does not regress; same-tool
  findings never inflate `n_tools`; fingerprints no longer block cross-tool
  agreement; three path-form cases unify; different classes, off-by-one lines,
  and denied CWEs all correctly decline to merge; order-independence and
  determinism hold.
- Fixtures REBUILT from captured real output (`regen_fixtures.sh`). The prior
  hand-authored pair modelled a tool combination that does not exist. The new
  flawfinder fixture carries real `fingerprints` on 3/3 results and real
  `FF####` ruleIds — i.e. it actually exercises the defect.
- Earlier CLI fixes re-checked and intact: `--help`, empty-SARIF graceful,
  malformed-SARIF still a real error, flag-only invocation.

### Real-library result — zlib 1.3.1, and it is a NEGATIVE worth reading
Real flawfinder + real cppcheck (with `-I`), 15 C files, 9,539 lines:

```
raw findings      712
same-tool dedup   601   (111 collapsed)
cross-tool merges   0
n_tools            {1: 601}
```

**Zero cross-tool merges — and the mechanism is behaving correctly.** Diagnosis:
- 14 exact file+line co-locations between the tools
- 10 of those had a resolvable class on both sides
- **0 of those 10 had MATCHING classes**

All 10 are `fprintf` debug lines in `trees.c`. flawfinder reports a format-string
risk (`fmt`); cppcheck reports a null-deref-on-allocation-failure (`null`). Those
are different bugs that happen to share a line. Declining to merge them is right,
and a location-only key would have manufactured 10 false merges on debug code —
direct empirical support for the asymmetric-error-cost design above.

### HONEST FINDING — the structural blocker is gone, a SEMANTIC one remains
Class profiles for this tool pair are near-disjoint on real code:
- flawfinder: `fmt` 260, `buf` 235, `int` 7, unresolved 86
- cppcheck: unresolved 111, `null` 10, `int` 2, `uninit` 1

Only 13 of 124 cppcheck findings resolve to a class at all; its bulk output is
CWE-398 (68, correctly denied) and `missingIncludeSystem` (23, an analysis
diagnostic). flawfinder pattern-matches dangerous functions; cppcheck does
dataflow. They look for different things, so they rarely agree.

So the fix was necessary but is NOT sufficient for the shipped default to
demonstrate consensus. Do not report "the fix restores the headline signal" —
on one real library it produced zero merges for legitimate reasons. Whether
this generalizes is exactly item 3's transfer question (§7 of the item-4 spec),
and it now has a concrete prior: expect low merge rates for flawfinder+cppcheck
and check whether the Lipp envelope's ~5.9% multi-tool rate is reachable with
real scanners at all, or whether it was an artifact of the reconstruction.

### Tier
`[self-tested]` for the implementation — Claude's harness, Claude's assertions.
The zlib observation is stronger: non-Claude engines (real flawfinder, real
cppcheck) on non-Claude input (real zlib), so the DATA is externally grounded.
The judgment that declining those 10 merges is correct is Claude's analysis, not
an external verdict. NO implementation tier moves to `[externally-verified]`:
no external judge has confirmed the ranking is right on real data.

## The overlap constraint: consensus needs PARTIAL overlap, not maximal diversity
(2026-07-26; surfaced by the zlib negative, independent of any tool-set outcome)

The framing sweep (claim 4) already recorded one failure mode of the consensus
premise: tools with CORRELATED blind spots produce merges that carry little
signal, because agreement between near-duplicates is not independent evidence.
That is the "bad diversity" half of the ensemble decomposition.

The zlib result exposes the INVERSE failure, which was not previously named:

> Tools with ANTI-correlated coverage produce no merges at all.

flawfinder and cppcheck on zlib had 14 exact co-locations, 10 with classes
resolved on both sides, and ZERO class matches. Their profiles barely intersect
(flawfinder `fmt` 260 / `buf` 235; cppcheck `null` 10 / `int` 2 / `uninit` 1).
One pattern-matches dangerous functions; the other does dataflow. Maximally
diverse — and therefore mute.

**The premise requires an overlap sweet spot.** Consensus is only informative
when tools have DIFFERENT enough methods that agreement is independent evidence,
but SIMILAR enough coverage that they can agree at all. Both extremes break it:

| overlap | outcome |
|---|---|
| near-total (redundant tools, shared engine) | merges are plentiful but carry little signal — shared FPs amplify |
| partial | the premise works — this is the regime the Lipp validation measured |
| near-zero (anti-correlated coverage) | no merges; consensus signal is absent, not weak |

This is a real constraint on WHICH TOOL SETS the premise can hold for, and it is
not fixable by any change to the dedup key — the zlib merges were correctly
declined, since the tools genuinely disagreed about what the bug was.

Consequences to carry:
1. **Tool-set selection is a first-class design parameter**, not a packaging
   detail. "Add more diverse tools" is NOT unconditionally good advice, which is
   how the diversity literature is easy to misread.
2. **The admission criteria for any new language must test for the sweet spot**,
   not merely count tools or assert independence. Three tools that share an
   engine fail on one side; three tools with disjoint specialities fail on the
   other. See docs/SPEC_java_admission.md.
3. **The Lipp validation's 6 tools evidently sat in the partial-overlap regime**
   (1,318 real cross-tool overlaps). Whether any 2-tool subset of the shipped
   Action reaches that regime is an open question, not an assumption.

## TWO DATA-LOSS DEFECTS found while adding a third tool (2026-07-26)

Both PREDATE the two-algorithm fix — `_result_key` has always preferred a
tool's own fingerprint — and both silently DESTROYED real findings. Found only
because a third scanner was added to a real-library run; no synthetic fixture
would have surfaced either.

### Defect 1 — a constant placeholder fingerprint collapses a whole tool
semgrep OSS, run unauthenticated, emits the SAME fingerprint on every result:

```json
"fingerprints": {"matchBasedId/v1": "requires login"}
```

`_result_key` trusted it as a stable identity, so all 33 zlib findings received
one key and collapsed to **1 finding — 32 destroyed**, with no warning.

### Defect 2 — a context-hash fingerprint collides on repeated code
flawfinder's `contextHash/v1` hashes the surrounding source, so identical C
idioms at different locations hash the same. On zlib this collapsed
**588 raw findings to 484** when the correct figure is 582 — ~98 distinct
findings silently merged.

### Fix — degeneracy detected from the data, not from a string blacklist
A fingerprint is supposed to identify ONE finding. If a single
(tool, fingerprint) pair appears at more than one distinct location, it is not
identifying anything, so we fall back to the location key. Pre-scanned before
keying; deterministic, content-only. Genuine per-finding fingerprints still
dedup normally — both behaviours are regression-tested.

Result on zlib: semgrep 33->33 (was 33->1), flawfinder 588->582 (was 588->484).

### Defect 3 (same session) — CWE in rule METADATA was never read
`_cwe_class_of` scanned ruleId + message + uri only. semgrep records its CWE
ONLY in the driver's rule definitions (`properties.tags`:
`["CWE-415: Double Free", ...]`) and emits no CWE in the result at all — so
class resolution returned None for 33 of 33 semgrep findings. That would have
produced a FALSE NEGATIVE in the three-tool overlap test: an apparent
"tools don't agree" caused by our parser, not by the tools. `ingest_sarif`
already collected this as `rec["rulemeta"]`; `_cross_keys` now consults it.

### Why this matters beyond the bugs
Trusting a tool's self-reported identity is not safe by default. The DefectDojo
model says use the tool's fingerprint for same-tool dedup — correct in
principle, but it assumes the fingerprint IS an identity. Two of the three real
scanners tested violate that assumption in different ways. Any future tool
added to the supported set must be checked for both failure modes.

Tier: `[self-tested]` for the fixes (regression-tested, 19 checks). The DEFECTS
themselves are externally grounded — real semgrep and real flawfinder output on
real zlib, not constructed cases.

## Three-tool overlap test on zlib (2026-07-26) — is the default tool SET the defect?

Question: the shipped flawfinder+cppcheck pair produces no consensus. Is that a
tool-SELECTION problem fixable by adding a third scanner, or something deeper?

### Method and its bounds — READ BEFORE THE NUMBERS
- **CodeQL could NOT be run.** `codeql` 2.26.0 is installed but C/C++ database
  creation fails: the cask ships only an `osx64` tracer, this is an arm64 Mac,
  and Rosetta is absent ("Bad CPU type in executable"). Needs
  `softwareupdate --install-rosetta`. **semgrep 1.171.0 (`p/security-audit`) was
  substituted.** semgrep is NOT CodeQL; this does not test the README's claim
  that CodeQL is a validated tool for this pipeline.
- All three run from ONE root with comparable paths. A first pass was DISCARDED:
  semgrep's URIs carried a `lib/` prefix from a different working directory and
  cppcheck had scanned 18 top-level files against flawfinder's 44 recursive, so
  "0 files in common" was a harness artifact. Corrected: cppcheck 59 files,
  flawfinder 44 (all shared with cppcheck), semgrep 5 (all shared with both).
- One library. zlib 1.3.1 only.

### Result
```
single tool     cppcheck 543 raw / 520 dedup · flawfinder 588/582 · semgrep 33/33

cppcheck + flawfinder            merges = 0     (0.00%)
cppcheck + semgrep               merges = 0     (0.00%)
flawfinder + semgrep             merges = 2     (0.33%)
all three                        merges = 2     (0.18%)
```

### The two merges are the LEAST informative kind of agreement
Both are `printf` format-string flags at `contrib/testzlib/testzlib.c:169` and
`:172` — flawfinder `FF1016` and semgrep, both **pattern-matchers on dangerous
function names**, agreeing that a `printf` is a `printf`. This is the
CORRELATED-tools case the framing sweep warns about ("bad diversity"): agreement
between near-duplicate methods is not independent evidence. It is also in test
code, not library code.

Meanwhile cppcheck — the dataflow tool, the one offering genuine methodological
diversity — overlaps with NOBODY.

### The binding constraint is CLASS RESOLUTION, not tool selection
```
class profile (WITH rule metadata consulted)
  cppcheck     521 of 543 UNRESOLVED (96%) · null 14 · uninit 5 · int 2 · leak 1
  flawfinder    86 of 588 unresolved (15%) · fmt 260 · buf 235 · int 7
  semgrep       31 of  33 UNRESOLVED (94%) · fmt 2

co-location vs class agreement
  cppcheck  vs flawfinder   co-located 43   both-classed 11   MATCH 0
  cppcheck  vs semgrep      co-located  0   both-classed  0   MATCH 0
  flawfinder vs semgrep     co-located 33   both-classed  2   MATCH 2
```
cppcheck and flawfinder co-locate 43 times, but only 11 of those have a class on
both sides and none match. 96% of cppcheck's findings and 94% of semgrep's carry
no resolvable class at all — so most co-locations can never be evaluated for
agreement, whatever the tools actually think.

**This is the U1/U2 map-coverage question (HANDOFF §7 item 2) showing up as the
dominant term, exactly as predicted, and it sits UPSTREAM of tool selection.**
The "unresolved" bulk mixes correctly-denied junk (CWE-398/561/563), unmapped
CWEs (U2 — fixable), and findings with no CWE at all (U1 — not fixable by us).
Splitting those three is now the highest-value measurement available.

### Answer to the question asked
**Adding a third tool did not rescue the default set.** 2 merges in 1,131
findings (0.18%), between the two most methodologically SIMILAR tools, on test
code.
> [DENOMINATOR CORRECTED 2026-07-26. **1,131 is wrong**: it is 543 + 588, the
> TWO-tool raw count, and omits semgrep's 33 from a THREE-tool result. Derived
> from this section's own component line above — raw 543 + 588 + 33 = **1,164**,
> dedup 520 + 582 + 33 = **1,135** — and both match the four structured ingest
> records elsewhere in this file ("1,164 raw / 1,135 dedup / 2 merges").
> THE RATE IS UNAFFECTED and the correct denominator is the DEDUP one: this
> section's own table reads 0.18%, and 2/1,135 = 0.176% -> 0.18% while
> 2/1,164 = 0.172% -> 0.17%. Cross-checked on the other row, which is only
> consistent the same way: flawfinder+semgrep 2/(582+33) = 0.33%.
> So the figures were computed on dedup and only the prose denominator is
> wrong. STATE IT AS: 2 merges among 1,135 deduplicated findings (0.18%), from
> 1,164 raw. The slip propagated to HANDOFF item 2's carry-forward and to
> SPEC_java_admission §6; both are annotated. The measurements stand.] None of the three pre-registered outcomes fits cleanly: it is not "the
tool set is the defect" (the added tool barely helped), not "all pairs merge"
(one pair, barely), and not quite "deeper than tool selection" either — because
a concrete, fixable cause is now visible, and it is class-map coverage.

Do NOT conclude the consensus premise fails. Conclude that on this evidence it
cannot be evaluated for these tools until class resolution improves, and that
adding scanners is the wrong lever to pull first.

Tier: `[self-tested]` analysis over `[externally-grounded]` data — three real
scanners on real zlib. One library, and CodeQL untested. Not generalizable as
a rate.

## CORRECTION to the three-tool conclusion — the cascade reverses it (2026-07-26)

The previous section concluded "class resolution, not tool selection, is the
dominant term," from cppcheck's 521/543 unresolved. **That was the denominator
error this project has now made twice**: it counted `_CWE_DENY` rejections as a
coverage gap, i.e. charged the filter working correctly as a defect. Applying
the D0/D1/D2 cascade:

```
cppcheck        D0=543   D1(analysis-valid)=337   [206 diagnostics excluded]
  DENIED (filter working correctly)   288   85.5% of D1   CWE-398 x235, 563 x41
  U2 CWE present but UNMAPPED          23    6.8%
  RESOLVED (mapped)                    22    6.5%
  U1 no CWE emitted                     4    1.2%

semgrep         D0=D1=33
  U2 UNMAPPED                          31   93.9%   ALL CWE-676
  RESOLVED                              2    6.1%

flawfinder      D0=D1=588
  RESOLVED                            502   85.4%
  U2 UNMAPPED                          86   14.6%   CWE-362 x130, CWE-20 x40
```

**The denied bucket dominates cppcheck (85.5% of D1).** cppcheck on zlib emits
overwhelmingly style/quality findings — CWE-398 "poor code quality" 235 times —
which we reject correctly. Among genuinely triage-relevant cppcheck findings
(D1 minus denied = 49), 22 resolve, 23 are U2, 4 are U1. That is a real but
SMALL gap: 23 findings, not 521.

**So class resolution is NOT the binding constraint, and item 3's promotion on
that basis was wrong.** The original conclusion stands: the two tools have
genuinely anti-correlated coverage. cppcheck's 22 resolved findings are
null 14 / uninit 5 / int 2 / leak 1; flawfinder's 502 are fmt / buf / int. The
classes barely intersect because the tools look for different things.

### semgrep's U2 is NOT an argument for map extension
All 31 are **CWE-676, "use of a potentially dangerous function"** — semgrep's
rules for `strcpy`, `scanf`, `strcat`, `system`. flawfinder flags those same
call sites as CWE-120 (buf) and CWE-134 (fmt). Mapping 676 to any single class
would merge buffer, format-string and command-injection findings together —
manufacturing exactly the false merges the asymmetric-error-cost rule forbids.
**CWE-676 is a deny-list candidate, not a map candidate.** Same reasoning as
664/758.

Likewise flawfinder's CWE-362 (race, 130) and CWE-20 (improper input
validation, 40) are broad parents; neither is a safe map candidate without
frequency evidence that two tools use them compatibly.

Net: on this evidence, the conservative map is close to correct as-is, and map
extension is NOT the high-value lever it appeared to be an hour ago.

## Where the 2 merges actually landed — and a heuristic gap
Both merges are in `zlib-1.3.1/contrib/testzlib/testzlib.c`, a benchmark/test
harness. Checked against the tool's own noise heuristics:

```
zlib-1.3.1/contrib/testzlib/testzlib.c   FIXTURE=False  TEST=False  packaging=False
```

`TEST_DIR` requires a path segment matching exactly `tests?`; `testzlib` does
not match. So the tool does NOT down-weight these, and the 0.18% rate is not
secretly zero by the tool's own accounting.

But by human reading it is test code, and there were **zero merges anywhere in
zlib's actual library sources**. Two consequences:
1. The starker statement is true: 0 cross-tool merges in library code on zlib.
2. `TEST_DIR` misses `testzlib`-style sibling names (`testfoo/`, `benchmark/`,
   `contrib/test*/`). Minor, separate from consensus, worth a look.

## contextHash data loss vs ROC-AUC 0.755 — the check, and its bound
Question: does the flawfinder `contextHash/v1` collision (and its fix) affect
the 0.755 result?

**ARTIFACT NOT AVAILABLE.** The reconstructed Lipp SARIF is not on this machine
(searched). This was NOT settled by opening it — stating that plainly rather
than asserting a check that did not happen (Rule 10.2).

What IS verifiable in-session, and is decisive for the degeneracy fix:
- `_fingerprint_value` returns None for a fingerprint-free result;
  `_degenerate_fingerprints` returns the empty set for a fingerprint-free
  corpus; `_result_key` then returns the identical `rk:` key with or without the
  degeneracy argument. **On fingerprint-free input the degeneracy fix cannot
  change any key.** Demonstrated.
- The Lipp envelope was necessarily fingerprint-free on merged findings: under
  the OLD code a cross-tool merge required BOTH sides to take the `rk:` branch,
  which only happens absent fingerprints. 1,318 cross-tool overlaps were
  recovered, so those findings carried no fingerprints.

Conclusion: **the contextHash defect and its fix do not touch ROC-AUC 0.755.**
Tier: deductive from the code plus the recorded 1,318 figure — NOT an inspection
of the artifact.

### SEPARATE AND MORE SERIOUS — the rest of the item-2 fix MAY move 1,318
The degeneracy fix is a no-op there, but the OTHER item-2 changes are not:
cross-tool keying on location+CWE-class, real `_norm_uri` normalization, and the
+8 map entries can only ADD merges. Re-running the Lipp ingest under the new
code may therefore no longer reproduce **1,318** — and that exact-match
cross-check is one of this project's load-bearing validation anchors.

This is not a defect; it is expected, since the point of the fix was to enable
merges that could not previously happen. But the anchor must be RE-ESTABLISHED
rather than assumed to still hold. Until the Lipp data is re-obtained and
re-ingested, treat "dedup 22,403→21,061, overlaps 1,318 exact" as a result of
the PRE-FIX code, not a current property. Added to HANDOFF pending work.

## ROC-AUC 0.755 IS UNANCHORED TO ANY SHIPPED CONFIGURATION (2026-07-26)

Larger consequence of the item-2 fix than the 1,318 dedup cross-check, and not
previously recorded.

### The chain
0.755 was produced by ranking the Lipp envelope with PRE-FIX code. The fix
changes `n_tools`; `n_tools` feeds the score directly
(`consensus = 1.6 * n_tools`, `score = consensus + severity + kind - noise`);
and the 0.755 measurement WAS a ranking by agreeing-tool count at file level.
So the fix changes the very quantity the number measured, over that same input.

**0.755 is a property of retired code.** It described a path that could not
merge. It does not describe the one that can.

### What must NOT be said
The obvious reading is that it should be BETTER post-fix — more genuine merges
ought to sharpen the consensus term. That is plausible and it is exactly the
kind of unmeasured assertion this project does not make. It is not recorded as
a expectation, a prior, or a likelihood. It is unmeasured.

### The tension with the sequencing argument — both are true
VALIDATION.md's sequencing argument (2026-07-26) says the fix moves the shipped
configuration TOWARD the validated one. BOUND 2 then warned that direction is
not a transfer guarantee. Neither anticipated this:

> The fix moves shipped toward validated in MECHANISM, and away from it in
> OUTPUT. The change justified by a measurement invalidates that measurement.

Both statements hold simultaneously. The mechanism argument is about the shipped
path becoming able to merge, as the validated path could. The output problem is
that the validated NUMBER was computed under the old mechanism, so it no longer
describes either path. A later session will meet these together and must not
resolve the tension by discarding one — the resolution is to re-measure, not to
pick whichever framing is convenient.

### Practical consequence — this is now a prerequisite, not a nice-to-have
Re-earning 0.755 on the Lipp data under CURRENT code is a precondition for
quoting the number at all. Until then it may not be cited as a property of the
shipped tool, in the README or anywhere else.

That makes **re-obtaining the Lipp artifact the gating dependency for the README
decision** (HANDOFF §7 item 1), which has now been held three times: first
pending the fix, then pending the three-tool result, now pending re-measurement.
The decision must not be re-opened without the artifact — every prior attempt to
settle it has been overturned by evidence that arrived afterwards.

## Map/deny criterion, established 2026-07-26: CLASS-COHERENCE, not abstraction

Governs every future `_CWE_CLASS` / `_CWE_DENY` edit, in any language. Recorded
here because an earlier hypothesis was refuted and the refutation is the useful
part.

**Refuted hypothesis:** map Base/Variant CWEs, deny Class/Pillar, per MITRE's
own abstraction levels. MITRE does state Base is the preferred mapping level and
that Class/Pillar entries are too abstract (`[fetched]`). But the two entries
that actually matter to us are backwards from it:

| CWE | abstraction | MITRE mapping | our experience |
|---|---|---|---|
| 676 use of potentially dangerous function | Base | **Allowed** | dangerous — spans buf/fmt/cmdi |
| 119 improper restriction within buffer bounds | Class | **Discouraged** | safe — already mapped to `buf` |

MITRE's guidance answers "what should this CVE be filed against"; ours is
"when do two tools mean the same thing." Different questions.

**The criterion that holds:**

> Map a CWE if everything it covers lands in ONE class of our taxonomy.
> Deny it if it spans several. The distinction is EFFECT vs MECHANISM, not
> general vs specific.

- 119 is abstract but all descendants are buffer issues -> coherent -> map.
- 676 is specific-sounding but is a *mechanism*; `strcpy`->buf, `scanf`->fmt,
  `system`->command injection -> incoherent -> deny.
- 664, 758, 20, 74, 707 span everything -> deny.

A mechanism category collects weaknesses sharing a CAUSE but differing in
CONSEQUENCE, and consequence is what our classes encode. This is why the
conservative instinct was right in C/C++ without anyone being able to say why.

**Consequence for Java (docs/SPEC_java_admission.md §6):** the apparent conflict
— "C/C++ says the map is close to correct, Java needs it doubled" — dissolves.
Java's candidates (89 SQLi, 79 XSS, 502 deserialization, 611 XXE, 918 SSRF,
22 path traversal) are effect categories naming one sink each, so each is
class-coherent and safe to map. Java's PARENT categories (20, 74, 707) are the
same trap as 676 and remain deny candidates.

BOUND: reasoned from CWE definitions plus two fetched entries, not from observed
merge behaviour on Java data. It predicts lower false-merge risk; it does not
demonstrate it. A false-merge audit on real Java output must follow the first
extension.

## Engine-lineage guard implemented (2026-07-26) — HANDOFF item 0

Closes the only defect found in this session that INFLATES `n_tools`. Every
other defect cost recall; this one corrupted the headline signal.

### The defect
Phase 2's diversity guard was `recs[a]["tools"] & recs[b]["tools"]` — a set
intersection on driver NAME. Two drivers of ONE engine passed it. The
diversity-aware merge was name-aware, not diversity-aware.

### What changed (src/audit.py only)
- `_TOOL_LINEAGE`: engine lineage per known driver. SpotBugs / FindBugs /
  Find Security Bugs -> `findbugs`; Semgrep* -> `semgrep`; SonarQube /
  SonarJava / SonarCloud -> `sonarqube`; plus cppcheck, flawfinder, codeql,
  pmd, checkstyle, errorprone.
- `_lineage_of()` falls back to the driver's own lowercased name, with prefix
  tolerance for version/edition suffixes (verified: "Semgrep OSS" -> `semgrep`).
  **Unknown tools therefore behave exactly as before. Nothing regresses.**
- The merge guard now intersects LINEAGE.
- `n_tools` counts DISTINCT ENGINES, not driver names. Needed independently of
  the guard: a transitive chain (A/engine1 - B/engine2 - C/engine1) can place
  two same-engine drivers in one record. Regression-tested.
- Quality weighting takes one representative driver per engine, so an engine
  cannot be weighted twice.
- Output gains `tool_lineages`, `distinct_engines`, `lineage_warnings`; the CLI
  prints the engine count when it differs from the tool count, and prints each
  independence caveat.

### Verified
25-check harness, all passing. New checks: SpotBugs+FindBugs do not inflate
n_tools; SpotBugs+FindSecBugs plugin likewise; different engines still merge
(no regression); unknown tools keep prior behaviour; transitive chains count
engines not names; the SonarQube caveat is disclosed. Real-data non-regression:
the 3-tool zlib ingest is unchanged at 2 merges, all three engines distinct.

### HONEST LIMIT — the SonarQube case is DISCLOSED, not PREVENTED
Running the documented exploit through the real CLI:

```
$ audit.py --ingest sb.sarif sq.sarif
  tools: SonarQube, SpotBugs
  ⚠ independence: SonarQube is present alongside findbugs. SonarQube can IMPORT
    those tools' reports (sonar.java.*.reportPaths), so its findings may not be
    independent ... verify the scanner configuration ...
  #1  score=7.7  SQL_INJECTION  src/Login.java:42  [SonarQube+SpotBugs] 2tools
```

The warning fires, but **the finding still scores `n_tools=2`.** SonarQube's
lineage (`sonarqube`) differs from SpotBugs' (`findbugs`), and the guard only
blocks IDENTICAL lineages. So in the exact exploit scenario the signal is still
inflated — loudly, but inflated.

This is deliberate and is NOT resolved here. Blocking the merge outright would
penalize the legitimate configuration, where SonarJava analyses independently
and SpotBugs runs separately — genuinely two engines. Whether the ambiguous case
should default to counting (disclose only) or to not counting (conservative, per
the asymmetric-cost rule) is a design decision with real cost either way, and
HANDOFF item 0 explicitly left it open with two options. **Not picked
unilaterally.** See the open decision recorded in item 0.

Second gap, same shape as the display-dedup one: `lineage_warnings` is in the
JSON but `audit_html_report.build()` does not render it, so Action users see
the finding and not the caveat.

Tier: `[self-tested]` for the implementation. The LINEAGE FACTS are `[fetched]`
(docs/SPEC_java_admission.md §2 sources).

### DECISION 0a (2026-07-26, inventor): conservative default + operator escape hatch

The SonarQube ambiguity — disclosed but not prevented in the shipped code — is
resolved as **option (b)**: do not count SonarQube agreement with an importable
tool as consensus unless the operator declares independence. Explicitly NOT a
declaration flag with a permissive default; the DEFAULT is conservative.

**The reasoning generalizes and should govern future ambiguities.** Everywhere
else in this codebase, uncertainty resolves to NO-MERGE:

| uncertainty | current resolution |
|---|---|
| CWE class unresolvable | no merge |
| CWE in `_CWE_DENY` | no merge |
| tool lineage unknown | own name, no self-merge |
| fingerprint degenerate | fall back to location key |
| line offset beyond exact match | no merge at scoring |

Option (a) would have been the ONLY place uncertainty resolved to
merge-with-a-note. **The asymmetric-cost rule does not get an exception because
the ambiguous case is uncommon** — rarity changes how often the cost is paid,
not which direction the error runs.

**Counter-argument, recorded because it is genuine.** SonarJava analysing
independently IS SonarQube's default configuration; report-importing is opt-in.
So (b) under-counts the COMMON case, and that is a real cost, not a hypothetical
one. What makes it acceptable is the escape hatch specifically: the operator who
configured the import is precisely the person able to declare the relationship.
The cost falls on the party holding the knowledge required to remove it — which
is the right place for it to fall, and is why the hatch is not decoration.

**0b is a PRECONDITION, not a sibling.** `lineage_warnings` never reaches the
HTML report, so on the Action path the caveat informs nobody. That killed option
(a)'s justification outright — it rested on the operator being informed. It
matters equally under (b), in the opposite direction: consensus silently
WITHHELD, with no rendered explanation, trades an inflated signal for an
unexplained one. Withholding without disclosure is its own honesty failure.
Render first, then implement 0a.

Status: DECIDED, NOT IMPLEMENTED. Neither is scheduled work yet.

## 0b + 0a implemented (2026-07-26)

### 0b — independence caveats now reach the report
`lineage_warnings` was in the JSON and dropped on the floor by
`audit_html_report.build()`, so on the Action path — the only path most users
see — the caveat informed nobody. `build()` now renders a warning box ABOVE the
findings table, plus a "distinct engines" stat whenever the engine count differs
from the scanner count (that difference IS the finding). Verified across three
cases: SonarQube+SpotBugs renders the caveat; SpotBugs+FindBugs renders both the
caveat and `engines=1` against `scanners=2`; flawfinder+cppcheck renders neither
(no empty box on the clean path).

### 0a — ambiguous independence resolves to NO-MERGE, operator can override
Implemented as decided: conservative DEFAULT, operator declaration as the escape
hatch, NOT a permissive default with an opt-out.

Behaviour, verified through the real CLI:

```
$ audit.py --ingest sb.sarif sq.sarif
  ⚠ independence: ... NOT counted as consensus. If this deployment analyses
    independently, declare it: AUDIT_INDEPENDENT_TOOLS="SonarQube"
  2 raw results → 2 unique after dedup
  #1  score=6.1  SQL_INJECTION  src/Login.java:42  [SpotBugs]

$ AUDIT_INDEPENDENT_TOOLS="SonarQube" audit.py --ingest sb.sarif sq.sarif
  ⚠ independence: ... IS being counted as consensus because independence was
    DECLARED by the operator. This is an operator assertion, not something the
    tool verified.
  2 raw results → 1 unique after dedup
  #1  score=7.7  SQL_INJECTION  src/Login.java:42  [SonarQube+SpotBugs] 2tools
```

Both directions are DISCLOSED. Suppression says why and names the hatch;
declaration says the count rests on an operator assertion the tool did not
verify. Neither silently changes the number.

Scope kept narrow deliberately: only the SonarQube-import ambiguity is
suppressed, and only against lineages SonarQube can actually import
(findbugs/pmd/checkstyle). SonarQube + CodeQL still merges — regression-tested,
so the conservative rule cannot quietly grow into blanket over-blocking.

### Verified
Harness at 31 checks, all passing. New: default suppression; suppression is
disclosed; the disclosure names the hatch; non-importable pairs unaffected;
declaration re-enables the merge; the declaration is itself disclosed. Real
zlib 3-tool ingest unchanged (1,164 raw / 1,135 dedup / 2 merges / 3 engines /
0 warnings) — the new rule is inert where it should be. `--help` and the render
harness unaffected.

### Honest note on the accepted cost
This under-counts SonarQube's DEFAULT configuration, where SonarJava analyses
independently and importing is opt-in. That cost was accepted knowingly: the
operator who configured an import is the one able to declare the relationship,
so the burden falls on the party with the knowledge to lift it. Recorded so a
later session reading a low consensus count on a Sonar-based deployment
recognizes it as a deliberate policy, not a bug.

Tier: `[self-tested]`. Lineage facts remain `[fetched]`.

## 3d + Java class-map extension (2026-07-26)

### 3d — test-directory heuristic widened
`TEST_DIR` required a path segment matching exactly `tests?`, so zlib's
`contrib/testzlib/` — benchmark code — was scored as ordinary library source.
Both cross-tool merges on that corpus landed there.

Added `TEST_DIR_PREFIX`, matching directory segments beginning with `test` or
named `bench`/`benchmark(s)`. **Directory-only by construction** (requires a
trailing `/`): a FILE named `testzlib.c` is still left to `TEST_NAME`, so
widening here cannot begin down-weighting production sources whose filename
happens to start with "test".

Calibrated against zlib's real tree rather than guessed —
`contrib/{blast,puff,minizip,untgz}` are genuine utilities and must not match;
only `contrib/testzlib` does. 9 regression cases, and the NEGATIVES are the
point: `src/tester.c` (file, not dir), `src/latest/`, `src/contest/`
(substring, not prefix) all correctly do not match.

Effect on the zlib merges: both now `noisy_loc=True`, score 6.7 -> 4.7. This
confirms the starker statement recorded earlier — **zero cross-tool merges in
zlib's library sources** — and now the tool itself knows it, rather than a human
having to notice.

### Java class-map extension — first application of the coherence criterion
`_CWE_CLASS` held only memory-safety classes, so Java class resolution was ~0
and no Java cross-tool merge could occur at all (SPEC_java_admission.md §6).

Added 15 effect categories, each naming ONE sink and therefore class-coherent:
`sqli` (89, 564) · `cmdi` (78) · `xss` (79, 80, 83) · `path` (22, 23, 36) ·
`deser` (502) · `xxe` (611) · `ssrf` (918) · `ldapi` (90) · `xpathi` (643) ·
`csrf` (352) · `redirect` (601) · `crypto` (326, 327) · `hash` (328) ·
`creds` (259, 798) · `random` (330, 338).

`crypto` and `hash` deliberately kept SEPARATE. Merging them would have been the
only unforced widening in this batch, and the OWASP Benchmark analysis treated
them as distinct categories where BOTH were perfect discriminators
(100% TPR / 0% FPR) — no reason to blur a boundary that measured cleanly.

Denied as MECHANISM/parent categories, the same trap as CWE-676: 20 (improper
input validation), **74 (injection — the direct analogue, parent of
77/78/79/89/90/643, so it spans sqli+cmdi+xss+ldapi+xpathi at once)**, 77, 93,
116, 200, and the Pillars 693/707/710. CWE-676 itself is now explicitly denied
rather than merely unmapped, since real semgrep output showed 31 of 33 zlib
findings carrying it.

Map is now 22 classes over 58 CWEs, with 19 denied.

### FALSE-MERGE AUDIT — the check that mattered
Extending a shared map risks creating spurious merges in the language it was NOT
extended for. Measured on the real zlib 3-tool corpus:

```
before extension:  1,164 raw / 1,135 dedup / 2 merges
after  extension:  1,164 raw / 1,135 dedup / 2 merges
```

Identical, and the same two findings. No new C/C++ merges were manufactured.

**CORRECTION — this does NOT satisfy the required false-merge audit, and an
earlier version of this section wrongly implied it did "for C/C++".** The check
is INERT, not passing. Measured on the same corpus:

```
newly-added CWEs appearing anywhere in 1,164 zlib findings:  CWE-327 x3
                                                             (1 of 23 entries)
CWE-327 by tool: flawfinder 1, cppcheck 0, semgrep 0
```

22 of the 23 new CWEs never appear in that corpus at all, and the one that does
appears on a SINGLE finding from a SINGLE tool — so it could not have produced a
cross-tool merge under any outcome. The run exercised essentially none of the
extension. "No new merges" was guaranteed by absence, not by the classes being
correctly drawn.

What the zlib run legitimately shows: the extension did not REGRESS existing
C/C++ behaviour. That is worth having and is all it is.

**THE FALSE-MERGE AUDIT IS OUTSTANDING.** It requires Java output, because the
risk being audited — do the 15 new classes merge findings that are not the same
bug — can only materialize where those classes actually resolve. Gated on the
first real Java ingest. A later session must not read "no false merges on zlib"
as clearance.

### Bound
`[self-tested]`. The class assignments are reasoned from CWE definitions under
the coherence criterion, and the false-merge audit is real (non-Claude tools,
non-Claude input) but covers C/C++ ONLY. **No Java SARIF has been ingested by
this project since the map changed.** The extension makes Java measurement
POSSIBLE; it does not demonstrate the classes are right for Java. A4 remains
unmeasured.

## Lipp artifact fetched and inspected (2026-07-26) — 3c closes as VOID

Zenodo 10.5281/zenodo.6515687, 6.9 MB, 15 files, all MD5-verified. Contains
per-project `sca_results.json` `{file, line, cwe, found_by[]}`, `functions.json`,
`cve_data.json` (CVE -> affected functions), a 5-analyzer rule-id->CWE mapping,
the CWE hierarchy, and the authors' derived CSVs + R notebook.
**There is no SARIF in the archive.** Totals: 96,875 findings / 98,417 tool-flags
/ 55,202 functions / 193 CVEs across 9 projects.

### The 1,318 anchor is a round-trip identity, not a cross-check
All three reported numbers are direct properties of the source file:

```
rows in findings (php)   = 21,061   <- reported as the "dedup" result
sum of len(found_by)     = 22,403   <- reported as "raw"
rows with >1 tool        =  1,318   <- reported as "overlaps, matched exactly"
```

The prior session expanded that table into one SARIF result per (finding, tool)
and fed it to `--ingest`, which collapsed it back to the table. Any correct
implementation returns the original row count by construction. It is recorded in
this file as "independently MATCHES the hand-computed count. Not approximate;
exact" — which reads as corroboration and is not. **Reclassified: a smoke test
that dedup inverts expansion.** It must not be re-run as validation. The
expansion also gave co-flagging tools identical `(file, line, cwe)`, so merging
was guaranteed — exactly the condition real scanners fail.

### ROC-AUC 0.755 — the earlier "unanchored" record was WRONG IN ITS REASON
That record claimed the item-2 fix invalidated 0.755 by changing `n_tools`.
It does not. On Lipp data the fix changes nothing: co-flagging rows share
identical `(file, line, cwe)` and carry no fingerprints, so they merged pre-fix
and post-fix alike.

Further, `audit.py` is a **pass-through** on this input. Severity is absent
(defaults to `warning`, `sev_n=2`) and every text contains "cwe" so `kind` is
always `security` (`KIND_W=1.5`). Hence
`score = 1.6*n_tools + 3.5 - 2.0*noisy` — monotone in `n_tools`. Measured on a
2,578-file reconstruction, where exactly one file trips the noise term:

```
raw n_tools           ROC-AUC=0.745   PofB@20%=0.495
audit.py-equivalent   ROC-AUC=0.745   PofB@20%=0.495     (identical)
```

**So the number stands and must not be retracted or softened.** 0.755 measures
Lipp's premise — tool agreement predicts vulnerability — against real CVE ground
truth across 9 projects. That is externally valid. What it does not measure is
this implementation's ranking, which contributes nothing on that input.

**The defect is ATTRIBUTION, not the number.** Both the previous "unanchored"
framing and the "MECHANISM vs OUTPUT tension" are withdrawn: they rested on the
fix having changed the measurement, which it did not.

BOUND: the reconstruction gave 0.745 vs 0.755 and PofB 0.495 vs 0.655, so the
exact universe/labelling differs from the original. Consensus AUC ranged
0.735-0.815 across nine plausible universe definitions and 0.755 sits inside,
but this is a close reproduction, not an exact one.

## Java class-resolution pass — semgrep on OWASP Benchmark v1.2 (2026-07-26)

First real Java scanner output this project has ingested. Single tool, so this
is a RESOLUTION test, not a merge test. `semgrep 1.171.0 --config=p/java` over
2,766 files / 283,895 LOC -> 1,909 findings from 60 rules.

### The 15 Java classes DO fire, and resolution is near-total
```
resolved to a class : 1,848 / 1,909  (97%)
  via RESULT TEXT   :     0
  via RULE METADATA : 1,848
unresolved          :    61   (all one rule: tainted-session-from-http-request)
```

**The rule-metadata fix accounts for 100% of Java resolution.** Without it this
corpus would have resolved 0 of 1,909. That fix was written and verified against
semgrep's C rules; this is an independent confirmation on a completely different
rule set, where it turns out to be not merely helpful but load-bearing.

### CORRECTION (2026-07-26, same day): these figures were the HARNESS's, not ingest's
The per-tool resolution numbers in this section and the SpotBugs one below
(97% / 1,848 for semgrep; 15% / 3,155 for SpotBugs) were computed by an
ANALYSIS HARNESS that read `fullDescription`. `ingest_sarif` did NOT read that
field, nor `relationships`. **What ingest actually resolved for SpotBugs was
ZERO**, which is why the first merge computation returned zero merges.

So these figures describe what the metadata COULD support, not what the shipped
code did with it. They are retained because the underlying finding — that Java
resolution comes essentially entirely from rule metadata rather than result
text — is unaffected and was independently reconfirmed after the fix. But any
claim of the form "the tool resolves N%" must be recomputed through
`ingest_sarif`, not through an analysis script.

### Class distribution, and which classes are silent
```
xss 456 · sqli 388 · crypto 301 · path 288 · cmdi 221 · hash 113 · ldapi 54 · xpathi 27

fire   (8/15): cmdi, crypto, hash, ldapi, path, sqli, xpathi, xss
silent (7/15): creds, csrf, deser, random, redirect, ssrf, xxe
```

`random` is silent despite **493 planted weakrand cases** — because semgrep
`p/java` produced ZERO findings in that category (and zero in securecookie).
The class is not wrong; the ruleset has no rule for it. The other six silent
classes have no corresponding category in this benchmark at all.

### The class assignments match ground truth exactly
```
labelled cases with >=1 resolved class : 1,511
  planted class present in resolved set: 1,511
  planted class ABSENT                 :     0
```

Zero mismatches. Where semgrep resolves a class on a labelled case, our map
never disagreed with the planted CWE. That is real evidence the Java class
assignments are drawn correctly — on ground truth, not by argument.

### Multi-class cases — the false-merge risk sites, identified not resolved
56 labelled files resolved to MORE than one class: `sqli + xss` (29) and
`xpathi + xss` (27). These are file-level co-occurrences, not necessarily
same-line, and are plausible for this benchmark (a test that both queries and
echoes input has genuinely two sinks). **They are the places a cross-tool merge
could go wrong, and a single tool cannot settle whether it would.** Carried into
7a as the sites to check first once a second Java engine is available.

### Scanner coverage is partial
1,511 of 2,740 cases (55%) produced any semgrep finding. Two categories produced
none at all: weakrand (0/493) and securecookie (0/67).

### Tier and scope
`[self-tested]` analysis over `[externally-grounded]` inputs — real semgrep on a
real published benchmark with human labels. It establishes that the Java classes
resolve and agree with ground truth. It does NOT establish a merge rate, a false
merge rate, or anything about real (non-synthetic) Java. See §6a of
SPEC_java_admission.md for why this corpus cannot serve A4.

## The Java class map, measured against external labels (2026-07-26)

This is the strongest evidence the Java class map has, and it is MEASUREMENT
against human labels, not an argument.

```
labelled OWASP Benchmark cases with >=1 semgrep-resolved class : 1,511
  planted CWE's class PRESENT in the resolved set              : 1,511
  planted CWE's class ABSENT                                   :     0
```

Every labelled case where semgrep resolved a class agreed with the CWE the
benchmark authors planted. Zero contradictions across 9 distinct vulnerability
categories (sqli, xss, cmdi, path, ldapi, xpathi, crypto, hash, random).

**AMENDED 2026-07-26 — this metric is WEAKER than first presented.** The
file-level comparison CANNOT distinguish "our class is wrong" from "the tool
found a second real bug in the same file". The benchmark labels FILES with one
planted vulnerability; scanners legitimately find other real issues in those
files. Running the same metric over SpotBugs produced 549 apparent
"mismatches", and every bucket examined was a CORRECT classification of a
genuine additional finding (`XSS_SERVLET` on weakrand tests that echo the
random value; `PATH_TRAVERSAL_IN` on crypto/hash tests that read a
parameter-named file).

semgrep scored 1,511/1,511 because its rules are NARROW and fire almost only on
the planted category — not because the instrument is sound. The result is
consistent with a correct map; it is not strong evidence FOR one.

**The correct instrument is the rule-by-rule audit**, which inspects each rule's
metadata->class assignment directly. Run over SpotBugs' 27 class-resolving
rules, it found TWO errors that the file-level metric could never surface (see
"Multi-class metadata" below). Prefer it for any future map validation.

### The coherence criterion's prediction held
SPEC_java_admission.md §6 predicted, before any Java data existed, that Java
map extension would carry LOWER false-merge risk than the C/C++ experience
suggested — because Java's candidate CWEs are EFFECT categories naming one sink
each (CWE-89 spans nothing), whereas C/C++'s problem cases were MECHANISM
categories (CWE-676 spans buf+fmt+cmdi). That prediction was recorded as
reasoned-not-demonstrated, with a false-merge audit required to follow.

The prediction held on first contact with real Java labels. Recorded because the
criterion now has a successful out-of-sample test, not just an explanatory fit.

### BOUND — what this does and does not establish
- **Does** establish: the classes are drawn correctly. Where a tool says "this
  is SQL injection", our map calls it `sqli`, and the ground truth agrees.
- **Does NOT** establish that MERGING is safe. A single tool cannot produce a
  cross-tool merge, so no merge was tested and no false merge could have been
  observed. 7a remains OUTSTANDING.
- The 56 multi-class files (`sqli+xss` 29, `xpathi+xss` 27) are the sites where
  a merge could go wrong. Identified, not adjudicated.
- Synthetic corpus. Correct class assignment on generated code is weaker
  evidence than it would be on real code, though the failure mode it rules out
  (a class that simply does not match what tools mean) is largely
  corpus-independent.

Tier: `[standard-checked]` — validated against a published, human-labelled
reference artifact, with our harness. Not `[externally-verified]`: no non-Claude
judge assessed the merging behaviour, because none was exercised.

## Java engine availability — A4 is ECOSYSTEM-CONSTRAINED, not blocked (2026-07-26)

Question: which Java engine PAIRS could produce a valid consensus measurement —
genuinely distinct lineage, both with real security coverage, both free?

### Disqualified, with reasons
- **FindSecBugs** — a SpotBugs PLUGIN. One engine with SpotBugs; cannot
  self-corroborate. `[fetched]`
- **SonarQube Community Build** — **has NO taint analysis.** Taint/injection
  detection starts at Developer Edition; the free tier cannot detect the
  dominant Java vulnerability class. Also subject to 0a suppression against
  SpotBugs/PMD/Checkstyle. `[fetched]`
- **PMD**, **Error Prone** — general-purpose correctness/style engines; thin
  security coverage, no injection taint.
- **Infer** — null/resource/concurrency focus, not injection.

### The three qualifying engines
| engine | security coverage | build needed | runnable here |
|---|---|---|---|
| SpotBugs + FindSecBugs | real (~128 security detectors) | YES — analyses bytecode | needs JDK + Maven |
| semgrep OSS | real but INTRAPROCEDURAL only; demonstrated 1,848 findings incl. sqli/xss/cmdi/path/ldapi/xpathi | no | **YES, today** |
| CodeQL | deepest (interprocedural); free for OSI-licensed open source and academic use, commercial licence for closed source `[fetched]` | YES | NO — arm64/Rosetta |

### The answer: 3 engines, 3 valid pairs. NOT CodeQL-or-nothing.
```
SpotBugs+FindSecBugs x semgrep    <- needs JDK + Maven + SpotBugs. NO Rosetta.
SpotBugs+FindSecBugs x CodeQL     <- needs JDK + Maven + Rosetta.
semgrep              x CodeQL     <- needs build + Rosetta.
```
The cheapest valid pair avoids Rosetta entirely, so **the JDK is the decision,
not Rosetta** — unless the goal is specifically the deepest-coverage pair.

### The constraint that DOES bite, and it is not toolchain
Java's free security-scanner ecosystem is THIN: three engines, where C/C++ had
flawfinder, cppcheck, semgrep and CodeQL plus a commercial tool. Worse, all
three pairs sit on the pattern-vs-dataflow axis that produced ZERO overlap in
C/C++ — semgrep is source-pattern/intraprocedural; SpotBugs is bytecode
dataflow; CodeQL is interprocedural dataflow. The overlap constraint predicts
these may under-overlap for the same reason flawfinder and cppcheck did.

That is a prediction, not a result, and A4 exists to measure it. But it means an
install does not guarantee a measurable merge rate — and if all three pairs
come back near zero, that is a finding about the Java ecosystem rather than
about this tool.

## Multi-class metadata now resolves to NONE (2026-07-26)

`_cwe_class_of` took the FIRST mapped CWE in a text blob. Text order carries no
semantic meaning, so the winner was arbitrary. Found by running a SECOND Java
tool — semgrep never exposed it because its tags carry one CWE each.

### The two cases are DIFFERENT IN KIND
Recorded separately because the fix is right for one and merely safe for the
other, and a later session must not treat them as the same problem.

**(a) GENUINE AMBIGUITY — `INFORMATION_EXPOSURE_THROUGH_AN_ERROR_MESSAGE`**
Metadata lists CWE-22, 89, 209, 211. The rule is about error-message exposure;
22 and 89 are incidental prose in a "related" discussion. First-match returned
`path`. **None is the RIGHT answer** — no single class describes this rule.
9 findings.

**(b) SPECIFICITY, NOT AMBIGUITY — `WEAK_MESSAGE_DIGEST_MD5` / `_SHA1`**
Metadata lists CWE-327 and CWE-328. **Both tags are CORRECT**; CWE-328 (weak
hash) is a CHILD of CWE-327 (broken crypto) and is the more precise one. There
is a right answer — `hash` — and the fix does not find it. **None is the SAFE
answer, not the right one.** 113 findings.

### The cost, stated accurately
```
SpotBugs+FindSecBugs resolved: 3,277 -> 3,155   (-122)
  crypto 445 -> 332   (-113, the MD5/SHA1 specificity case)
  path   646 -> 637   (-9,   the genuine-ambiguity case)
semgrep resolved:      1,848 -> 1,848   (unchanged)
zlib 3-tool ingest:    unchanged (1,164 raw / 1,135 dedup / 2 merges)
```

**113 of the 122 lost findings are the MD5/SHA1 case, so the fix makes `hash`
UNREACHABLE for SpotBugs.** That is not a rounding cost. `hash` was kept
separate from `crypto` on this corpus's OWN evidence — OWASP Benchmark labels
crypto (246) and hash (236) as distinct categories, and the earlier session
recorded both as perfect discriminators. The fix silences a class we have
specific reason to believe is real and useful. It is accepted because a wrong
class can cause a FALSE MERGE (inflating n_tools, the signal every published
number rests on) while a miss only costs recall — but it is a real loss, not a
4%-of-resolution rounding error, and it is the reason item 3e exists.

Regression-tested both cases plus four non-regressions (single-class still
resolves; several CWEs mapping to ONE class still resolve; a denied CWE
alongside a mapped one does not block). Harness at 37 checks.

## DESIGN CONCLUSION: the fingerprint-first model does not hold on real SARIF

Three of three real scanners tested violate or lack the assumption that a
fingerprint identifies one finding:

| scanner | fingerprint behaviour | consequence if trusted |
|---|---|---|
| semgrep OSS | CONSTANT placeholder `"matchBasedId/v1": "requires login"` on every result | 33 zlib findings collapsed to 1 |
| flawfinder | `contextHash/v1` hashes surrounding source, so repeated idioms COLLIDE | 588 collapsed to 484 (correct: 582) |
| SpotBugs 4.10.3 | emits NO fingerprints at all | nothing to trust; location key used |

This is no longer three incidents. It is a pattern, and it falsifies the
premise `_result_key` was originally built on. DefectDojo's fingerprint-first
dedup model assumes tools emit stable per-finding identities; **on real SARIF
from real scanners, that assumption held in zero of three cases.**

Standing consequences:
1. The degeneracy check is not a patch for two bad tools — it is load-bearing
   infrastructure, and must run for every tool, always.
2. Any newly supported tool must be audited for BOTH failure modes before its
   fingerprints are trusted, and absence is a third outcome to expect.
3. Location+class is the primary identity in practice; fingerprints are an
   optimisation that frequently is not available. Design accordingly.

## Cross-tool merges + 7a false-merge audit (2026-07-26)
### SpotBugs+FindSecBugs x semgrep on OWASP Benchmark v1.2

FIRST — TWO DEFECTS THAT WOULD HAVE PRODUCED A FALSE ZERO.

**(1) Path forms are structurally incompatible between Java tools.** SpotBugs
derives paths from bytecode and emits PACKAGE-relative
(`org/owasp/benchmark/...`); semgrep emits SCAN-ROOT-relative. One is a SUFFIX
of the other, so `_norm_uri` cannot reconcile them and the merge count is zero.
Fixed here by re-running semgrep from `src/main/java`. **This is a REAL
production issue, not only a harness artifact** — a user running both tools the
obvious way gets zero merges and no diagnostic.

**(2) `ingest_sarif` read the wrong rule-metadata fields.** It built `rulemeta`
from `id + name + shortDescription + tags`, omitting BOTH:
  - `fullDescription` — where FindSecBugs puts its CWE in prose, and
  - `relationships` — the STRUCTURED SARIF CWE taxa.
So ingest resolved ZERO classes for SpotBugs and produced ZERO merges, while the
analysis harness (which read `fullDescription`) reported 3,155 resolved. The
earlier per-tool resolution figures described what ingest COULD resolve, not
what it did.

### Fix: structured taxa first, prose as fallback
SARIF `relationships` name the rule's CWE exactly, with no prose noise:
```
WEAK_MESSAGE_DIGEST_MD5   taxa=328 -> hash   (correct AND specific)
INFORMATION_EXPOSURE_...  taxa=209 -> None   (correct; 22/89 were prose noise)
SQL_INJECTION_JDBC        taxa=89  -> sqli
```
**This SUPERSEDES prose-scraping — it does not supplement it.** Prose was the
WRONG SOURCE, and the distinction matters for how the multi-class guard should
be read:

- Taxa answered BOTH problem cases **correctly**: `WEAK_MESSAGE_DIGEST_MD5` ->
  328 -> `hash` (the precise, right answer) and `INFORMATION_EXPOSURE` -> 209 ->
  correctly unmapped.
- The multi-class guard answered them only **safely**: None for both, right for
  the second and merely lossy for the first.

So **the guard was CORRECT given prose input and UNNECESSARY given structured
input.** A later session must NOT read it as the principled answer to
multi-CWE rules — it was a workaround for a PARSING DEFICIENCY (reading prose
when the file carried a structured taxon). Keep it strictly for the prose
FALLBACK path, where it remains correct; do not extend it, and prefer fixing
the input source wherever a structured one exists.

It also RECOVERS the 113 `hash` findings the guard had silenced (55 of SpotBugs'
77 rules emit taxa).

### THE HEADLINE RESULT — enrichment against external labels
```
merges on files labelled REAL VULNERABILITY : 814
merges on files labelled PLANTED FALSE POS  : 342
precision of merges vs labels               : 70.4%
benchmark base rate (real vulns)            : 51.6%
                                    ENRICHMENT: +18.8pp
```

**AMENDED SAME DAY — I OVERSTATED THIS. Read the correction below before the
paragraph that follows it.** Leading with "+18.8pp over base rate" used the
WRONG COMPARATOR. The base rate is the coin flip. The claim this tool actually
makes — and that the README makes — is that consensus beats the BEST SINGLE
TOOL. Measured on the same corpus and labels:

```
                                  per-finding      file-level
  base rate                          51.6%            51.6%
  SpotBugs+FSB (class-resolved)      64.0%            55.5%
  semgrep      (class-resolved)      68.3%            65.6%
  CONSENSUS    (merges)              70.4%            69.1%

  consensus vs BEST single (semgrep):
     per-finding  +2.1pp   z=1.20  p=0.232   NOT significant
     file-level   +3.5pp   z=1.86  p=0.063   NOT significant
  consensus vs SpotBugs:
                  +6.4pp   z=3.95  p=7.9e-05  significant
```

**VERDICT: the comparison against the better single tool DID NOT RESOLVE — the
test is UNDERPOWERED, and this is NOT a measured absence of effect.**

```
minimum detectable effect at n=1,156 vs n=1,848 : ~4.0pp
observed effect                                 : +2.1pp  (below threshold)
n needed to resolve +2.1pp at p<0.05            : ~7,562 per group (balanced)
                                                  ~107,000 merges holding the
                                                  semgrep comparator at 1,848
```

Both "consensus adds ~2pp" and "consensus adds nothing" are consistent with this
data. The file-level view reached p=0.063 with the SAME SIGN — weak corroboration
of a small positive effect, not of its absence. Consensus DOES significantly beat
the weaker tool (SpotBugs, p=7.9e-05).

**THE SYNTHETIC BOUND APPLIES TO THIS NEGATIVE TOO — stated as HYPOTHESIS, not
finding.** On a corpus where every file contains exactly one planted bug drawn
from a category BOTH tools cover, single tools should perform unusually well.
That is close to the condition LEAST favourable to consensus, whose value comes
from covering what one tool misses. A null result here is therefore weak evidence
about real code — in the same way, and to the same degree, that the positive
enrichment was. **The negative generalizes no further than the positive did.** And it surfaces 1,156
findings where semgrep alone surfaces 1,848 — so as a FILTER it would discard
449 of the 1,263 true-positive-file findings semgrep alone found, a 36% loss,
for a precision gain that does not reach significance.

Fairness note that does NOT rescue the claim: the tool RANKS rather than
filters — non-merged findings are scored lower, not dropped — so "costs recall"
overstates the operational cost. But it does not touch the precision result:
against the right comparator, consensus is not demonstrated to add signal here.

**So the correct reading is outcome (2), with a power caveat: the enrichment over
base rate is REAL but is NOT evidence FOR consensus — and the failure to
demonstrate consensus is a NON-RESULT, not a negative result.** Both single tools also beat base rate, and
the better one beats it by nearly as much as consensus does. The paragraph below
is retained because its point about the CODE PATH stands — but its claim to be
evidence for the consensus premise does not.

---

**This is the first time this IMPLEMENTATION has demonstrated the signal it is
built on, on any corpus.** Everything before it was either design-grounding
(literature), principle-validation on someone else's derived table (Lipp's
`found_by` counts, where audit.py was a pass-through), or self-test. Here the
premise reproduces THROUGH THE ACTUAL CODE PATH: real scanners -> real SARIF ->
`ingest_sarif` -> merges -> compared to human labels the tool never saw.
Where the tool says two independent engines agree, a real vulnerability is
substantially more likely to be present.

**TIER: `[standard-checked]`** for the measurement itself — validated against a
published, human-labelled reference artifact, with non-Claude engines on
non-Claude input. NOT `[externally-verified]`: the harness and the
interpretation are Claude's.

**But the CLAIM the tier attaches to must now be narrower.** What is
`[standard-checked]` is: "merges land on vulnerable files 70.4% of the time
against a 51.6% base rate, and the whole path from real scanners through
ingest_sarif to labels executes correctly." What is NOT established, in EITHER
direction, is whether consensus outperforms the best single tool: the test was
underpowered (min detectable effect ~4.0pp vs an observed +2.1pp), so it returns
no verdict rather than a negative one.

**BOUND, and it is severe:** this is measured on a corpus THIS PROJECT HAS
ALREADY RECORDED AS UNREPRESENTATIVE — synthetic, structurally uniform, and
deliberately seeded with plausible fakes (the same objection recorded against
Juliet). The enrichment is real on this corpus and is NOT evidence that the
signal holds on production Java. It is the strongest result the implementation
has, and it is still a synthetic-corpus result.

### Merge rate — corpus-specific plumbing, reported second on purpose
```
raw 23,074 -> same-tool dedup 23,064 -> cross-tool merges 1,156 -> final 21,908
merge rate 5.01%     n_tools {1: 20,752, 2: 1,156}
classes: xss 302 · path 221 · crypto 171 · cmdi 146 · sqli 126 · hash 113 · ldapi 50 · xpathi 27
```
The RATE says how often two tools happened to co-locate on this generated code.
The ENRICHMENT says whether that agreement MEANS anything. They are different
kinds of claim; the rate is the weaker one and must not overshadow the other.

### 7a FALSE-MERGE AUDIT — result: ZERO false merges found
```
merged class MATCHES the file's planted category : 1,129
merged class DIFFERS                             :    27
```
All 27 investigated, not assumed. Every one is an `xpathi`-planted file where
both tools independently flagged `response.getWriter().println(value.getTextContent()...)`
as XSS — SpotBugs `XSS_SERVLET`, semgrep `no-direct-response-writer`, SAME LINE,
SAME BUG. A genuine SECOND vulnerability, correctly merged. Not false.

Predicted false-merge sites were also checked: 452 files had >1 class resolved
(`random+xss` 218, `crypto+path` 97, `hash+path` 74, `xpathi+xss` 34,
`sqli+xss` 29), and 278 merges landed on them. **Every one merged on the
CORRECT class** — crypto files merged as `crypto`, hash files as `hash` — no
cross-contamination, because the key requires same line AND same class.

**7a is SATISFIED for this tool pair on this corpus: 0 false merges in 1,156.**

### BOUNDS — both directions, and they matter more than the numbers
1. **A4 is NOT satisfied.** This corpus is SYNTHETIC, structurally uniform, and
   deliberately plants fakes — the same objection recorded against Juliet. The
   5.01% rate is CORPUS-SPECIFIC.
2. **Do NOT compare 5.01% to zlib's 2-in-1,164.** Different language, code, and
   corpus TYPE. Not commensurable.
3. **The INVERSE artifact applies too:** one planted vulnerability per file in a
   generated shape may make agreement EASIER than real code. A HIGH merge rate
   here is as uninformative about real Java as a low one would be. 5.01% is not
   evidence that Java consensus works in production.
4. 7a's zero-false-merges is bounded by the same synthetic shape, and by the
   corpus labelling ONE bug per file — it cannot adjudicate merges on unlabelled
   second bugs beyond manual inspection, which is what was done for the 27.
5. A real-Java A4 needs a REAL Java project.

## 0c implemented — path-root mismatch is DETECTED and DISCLOSED (2026-07-26)

Option (b) of the two scoped directions. Option (a), suffix matching, was NOT
built: it can falsely unify same-named files across modules
(`a/util/Config.java` vs `b/util/Config.java`), which is a false merge — the
error direction the asymmetric-cost rule forbids.

### What it detects
Two tools whose path sets share filenames but have ZERO identical paths are
reporting relative to DIFFERENT ROOTS. `_path_root_mismatch` reports the pair,
the count of shared filenames, whether a suffix relationship holds, the likely
cause, and the fix. Surfaced in JSON (`path_warnings`), the CLI, and the HTML
report above the findings table — where the box retitles to "Scanner paths do
not line up".

### Verified on the case that motivated it
```
$ audit.py --ingest sb.sarif sg_java.sarif      (mismatched roots)
  ⚠ PATH MISMATCH: Semgrep OSS and SpotBugs report the SAME 1515 filename(s)
    but ZERO identical paths (one tool's paths are a SUFFIX of the other's) ...
    any consensus count involving this pair will be ZERO for that reason alone
    — NOT because the tools disagree.
  23074 raw -> 23064 unique      (i.e. 0 merges, now explained)

$ audit.py --ingest sb.sarif sg_java2.sarif     (roots aligned)
  (no warning)
  23074 raw -> 21908 unique      (1,156 merges)
```

Regression-tested: mismatched roots warn and name the cause; matched paths do
NOT warn and still merge; disjoint filenames do not warn; the real captured
cppcheck+flawfinder fixtures stay silent; and no suffix matching is attempted.
Real zlib 3-tool ingest: 0 path warnings. Harness at 45 checks.

### Why this matters beyond the bug
It converts a SILENT ZERO into a STATED one. Before it, the honest reading of a
zero consensus count was ambiguous between "the tools disagree" (a finding) and
"the paths never compared equal" (an artifact). That ambiguity produced a wrong
answer once already in this session, and would have produced one in the next A4
run. This is the same preference recorded for 0a/0b: withholding a result
without explanation is its own honesty failure.

## A4 PRE-REGISTRATION (2026-07-26) — fixed BEFORE the Struts run

Written before Apache Struts was fetched or built, so the synthetic-vs-real
contrast is fixed in advance rather than selected after the fact (GENESIS Part 3
method: pre-register before probing).

### The OWASP Benchmark v1.2 baseline being compared against
SpotBugs+FindSecBugs x semgrep, roots aligned:
```
raw findings                23,074
same-tool dedup             23,064
cross-tool merges            1,156
MERGE RATE / finding          5.01%
distinct files               2,755
findings per file       mean  7.95   median 7   max 26
files with >=1 merge         1,064   = 38.6% of files
MERGE RATE / file            38.62%
merges per merged file  mean  1.09   max 2
concentration           top-10 files hold 20/1,156 merges (1.7%)
class distribution      xss 302 · path 221 · crypto 171 · cmdi 146 ·
                        sqli 126 · hash 113 · ldapi 50 · xpathi 27
```

### The confound to MEASURE, not narrate around
OWASP is one planted bug per small generated file (mean 7.95 findings/file, max
26, merges almost never repeat within a file — max 2). Struts is large real files
with many findings each. **More findings per file means more chances for two
tools to co-locate coincidentally, which could inflate the merge rate for a
mechanically uninteresting reason.**

Pre-registered discriminator: if Struts merges CLUSTER in its densest files,
that is a co-location artifact rather than agreement. Specifically —
- report merge rate per FINDING and per FILE;
- report findings-per-file for both corpora;
- report what share of merges the top-10 files hold (OWASP: 1.7%, i.e. spread).
If Struts' top-10 share is high while its per-file merge rate is not
correspondingly high, the per-finding rate is inflated by density and must be
reported as such BEFORE it is quoted.

### Bounds fixed in advance
1. **No per-file answer key for Struts.** This measures merge RATE, not merge
   CORRECTNESS.
2. **7a's zero-false-merges does NOT transfer.** It was measured on generated
   code with one planted bug per file, every divergent case hand-checked against
   labels that will not exist here. Real code has multiple genuine issues per
   file, deeper call graphs and framework indirection; its false-merge rate is
   simply UNMEASURED.
3. Path alignment is checked FIRST (item 0c). A zero must be diagnosed, not
   quoted.
4. If the 7-module Struts build fails or runs long, switch to Apache Shiro and
   record why rather than sinking time into the build.

## A4 ON REAL JAVA — Apache Struts (2026-07-26). Result: ZERO merges, and WHY

Run against the pre-registration committed before Struts was fetched.

### Build and alignment
```
build      38s, 19/20 modules, 1,220 classes (core 952). plugins/tiles failed
           on a missing Velocity dependency — partial, core intact, usable.
alignment  package-path collisions across modules: 0 of 1,484 -> prefix-strip safe
           (verified, not assumed; this is the uniqueness guard 0c option (a) demands)
0c check   NO path warnings. The zero below is REAL, not a path artifact.
```

### The measurement, against the pre-registered baseline
```
                        OWASP (synthetic)     STRUTS (real)
raw findings                     23,074              1,549
same-tool dedup                  23,064              1,495
CROSS-TOOL MERGES                 1,156                  0
merge rate / finding              5.01%             0.000%
distinct files                    2,755                432
findings per file           mean   7.95               3.46   (median 7 / 2, max 26 / 41)
merge rate / file                38.62%             0.000%
n_tools distribution        {1:21908, 2:1156}      {1:1495}
merged class distribution   xss/path/crypto/...       n/a
```

### THE DENSITY CONFOUND RUNS THE OPPOSITE WAY
The pre-registered worry was that Struts' large real files would INFLATE the
merge rate through coincidental co-location. Measured: Struts is **less** dense
(3.46 findings/file vs OWASP's 7.95). The confound does not apply, and no
concentration analysis is needed because there are no merges to concentrate.

### CAUSE 1 — semgrep is near-silent on real Java
```
semgrep p/java   OWASP: 1,909 findings / 2,740 files   = 0.70 per file
                 STRUTS:     1 finding  / 1,484 files  = 0.0007 per file
```
A ~1000x collapse in finding density. Verified NOT a scan failure: semgrep
reported "Ran 60 rules on 776 files", ~100% parsed, zero skipped. semgrep CE's
rules are tuned to the direct source->sink shapes OWASP GENERATES; real framework
code routes through interfaces, configuration and reflection, which an
intraprocedural engine does not follow. SpotBugs was unaffected (1,494 findings,
265 class-resolved).

### CAUSE 2 — the ONE genuine agreement was missed BY THREE LINES
The single semgrep finding and a SpotBugs finding are **the same bug**:
```
org/apache/struts2/result/ServletRedirectResult.java
  semgrep   line 244  class=redirect  unvalidated-redirect      <- method signature
  SpotBugs  line 247  class=redirect  UNVALIDATED_REDIRECT      <- response.sendRedirect(...)
  SpotBugs  line 250  class=redirect  UNVALIDATED_REDIRECT      <- setHeader("Location", ...)
```
Same file, same CWE class, same vulnerability. semgrep anchors at the taint
SOURCE (method signature); SpotBugs anchors at the SINK instruction. Delta: 3
lines. **The scoring key requires an EXACT line match, so it did not merge.**
The display layer's `TOL=3` would have caught it (|244-247| = 3).

This is the strongest available evidence on the exact-line design decision,
recorded when that decision was made as "conservative on purpose". On GENERATED
code the sink sits on one line and both tools point at it. On REAL code the
tools anchor at different points of the same dataflow, and exact matching
discards the agreement. The choice was defensible and it has a measured cost:
on this corpus it cost 100% of the available cross-tool agreement.

### What this establishes, and what it does not
**Establishes:** the SpotBugs+semgrep pair cannot demonstrate consensus on real
Java, for two independent and separately-diagnosed reasons. Neither is "the
tools disagree" — they agreed exactly once and the key missed it.

**Does NOT establish** that consensus fails on real Java. n=1 project, and one
of the two tools contributed one finding, so the pair never had a chance. This
is a measurement of THIS PAIR on THIS PROJECT.

**BOUNDS fixed in advance and still binding:** no per-file answer key, so this
measures RATE not CORRECTNESS; 7a's zero-false-merges does NOT transfer here —
with zero merges there was nothing to audit, and real-code false-merge rate
remains UNMEASURED.

### Consequence: A4 is not answerable with this tool pair
A4 asks for measured partial overlap. This pair produces no overlap on real Java
because one member is silent on it. Answering A4 needs either a tool pair where
both members fire on real framework code (CodeQL is the obvious candidate and is
Rosetta-blocked), or semgrep Pro's interprocedural engine, which is commercial.
The ecosystem constraint recorded earlier now has a concrete instance.

## THE CENTRAL OPEN QUESTION (2026-07-26): is cross-methodology agreement
## OBSERVABLE AT ALL under a co-location requirement?
## >>> ANSWERED LATER THE SAME DAY, AND THE ANSWER IS YES. SEE "GRANULARITY IS
## >>> THE LEVER" AND "THE DECISIVE MEASUREMENT" BELOW IN THIS FILE, WHICH STATE
## >>> IN TERMS: "Cross-methodology agreement may not be observable" IS
## >>> WITHDRAWN. The MEASUREMENTS in this section stand exactly as recorded —
## >>> they are line-level and correct at that unit. The BOLD CONCLUSION drawn
## >>> from them does not.

>>> WHY THIS POINTER WAS ADDED (2026-07-26, reconciliation sweep). This file is
>>> a chronological log, so a superseded entry is not an error — the later entry
>>> is the record. But HANDOFF §8 rule 11 requires that anything entering a
>>> PUBLIC artifact be RE-DERIVED FROM THIS FILE, and a session doing that
>>> greps. Grep this file for "co-located agreement" and THIS section is the
>>> first hit; its refutation is 528 lines further down under a heading that
>>> shares no vocabulary with it. The false claim that reached the README was
>>> therefore re-derivable from the evidence record itself, at the first place a
>>> conscientious session would look.
>>> THE GENERAL RULE THIS YIELDS: chronological ordering is not enough for a
>>> document that gets consulted by search rather than read front to back. When
>>> an entry here is overturned, the OVERTURNED entry gets the forward pointer —
>>> not only the new one, which the reader has by definition not found yet.

Promoted above tool selection and class-map coverage. Two measurements, two
language ecosystems, two corpus types, two DIFFERENT mechanisms, ONE consequence.

```
zlib (C/C++)    flawfinder (pattern)  vs  cppcheck (dataflow)
                CLASSES anti-correlated: fmt/buf vs null/uninit/int
                14 exact co-locations, 0 with matching class -> 0 merges

Struts (Java)   semgrep (pattern)     vs  SpotBugs (dataflow)
                CLASSES matched exactly: redirect / redirect
                LOCATIONS differed: 244 (taint SOURCE) vs 247 (SINK) -> 0 merges
```

**Pattern tools and dataflow tools do not produce CO-LOCATED agreement. The
consensus premise AS IMPLEMENTED requires co-location.**

### Why this outranks the other open items
- Tool selection (0d, A4) asks WHICH tools to pair. Irrelevant if no
  methodologically-diverse pair can produce observable agreement.
- Class-map coverage (item 3) asks whether we can READ what tools say. Struts
  shows the classes can match perfectly and the merge still fails.
- The diversity argument that motivates the whole tool says that
  METHODOLOGICALLY DIFFERENT tools are the valuable ones — disjoint miss-sets,
  independent evidence. This finding says that is exactly the pairing whose
  agreement our mechanism cannot see. **The premise and the implementation
  disagree about which pairs matter.**

### The Struts miss is STRUCTURAL, not jitter
semgrep anchors at the taint SOURCE; SpotBugs at the SINK. Both are correct
answers to "where is this bug" — they are answers to different questions. The
3-line gap is the distance between two correct answers, not an error. It
therefore recurs systematically wherever such a pair agrees, and its magnitude
is ARBITRARY: same function here, DIFFERENT FUNCTIONS elsewhere — already on
record as the open cross-function source/sink problem.

**Consequence: TOL=3 caught this by luck.** A tolerance window is the wrong
SHAPE of fix for a structural mismatch — it works when the sink is near the
source and fails otherwise, with no principled cutoff. Any evaluation of
tolerant matching must measure the SOURCE-SINK SEPARATION DISTRIBUTION on real
code rather than sweeping a window, and must not treat TOL=3 as validated by
this single instance.

### Status
The consequence is MEASURED (twice). That it generalizes as a structural law is
a HYPOTHESIS. Directions worth considering, none evaluated:
  - match on a code ENTITY (enclosing method/function) rather than a line;
  - match source-to-sink RANGES where a tool reports both;
  - accept that same-methodology pairs are the only ones that co-locate, and
    state plainly that the tool measures agreement-within-methodology — which
    the ensemble literature says is the LESS informative kind.
The last is not a fix; it is the honest fallback if the others fail, and it
would require amending what the tool claims.

## Sizing the two structural directions (2026-07-26) — measured on SARIF on disk

Not implemented. Reachability assessed against the files we already have, not
against what the SARIF spec permits.

### DIRECTION A — match on enclosing code entity. **NOT REACHABLE.**
```
SpotBugs+FindSecBugs : logicalLocations on 1,548/1,548 results (100%)
                       kinds: function 513 · member 558 · type 122 · variable 355
                       FQN example, and it is exactly what A needs:
                       org.apache.struts2.result.ServletRedirectResult
                         .sendRedirect(HttpServletResponse, String)
                       — carried by BOTH near-miss findings (lines 247 and 250)
semgrep CE           : logicalLocations on 0/1 results. `properties` is EMPTY.
```
**One side supplies the enclosing entity structurally; the other supplies
nothing.** Matching needs both sides, so this direction is blocked.

The near-miss is misleading here: semgrep's SNIPPET happens to begin
`protected void sendRedirect(...)` because that rule matched at the method
signature. That is incidental. A semgrep rule matching a single expression
mid-method yields a snippet with no method name in it, so the enclosing entity
is NOT recoverable from semgrep output in general — it needs a Java parser.
**That is a different project.**

CAVEAT on the SpotBugs side even so: only 513 of 1,548 (33%) have
`kind: function`. The rest name a member, type or variable, so "enclosing
method" is not uniformly available even from the tool that emits the field.

### DIRECTION B — point-in-range matching. **REACHABLE, BUT LOW COVERAGE.**
```
                       endLine present        span (lines)
SpotBugs Struts          167/1,548  (11%)     mean 83.5  max 738
SpotBugs OWASP         6,374/21,165 (30%)     mean 23.6  max 141
semgrep  Struts              1/1   (100%)     mean 21.0
semgrep  OWASP           1,909/1,909 (100%)   mean  0.7  max 16
```
It WOULD have caught the near-miss — SpotBugs' points 247 and 250 both fall
inside semgrep's range 244-265, and a point-in-range test is principled in a way
a tolerance window is not (it uses a boundary the TOOL declared, not one we
invented).

But coverage is thin, and for two independent reasons:
1. **SpotBugs omits `endLine` in 70-89% of results**, so on most findings there
   is no range on that side.
2. **semgrep's range is usually a POINT** — mean span 0.7 lines on OWASP. It
   reports the matched expression, not the enclosing construct. The Struts case
   had span 21 only because that particular rule matches a whole method.
So point-in-range degenerates to exact matching in the common case. It is a
real improvement on a minority of findings, not a fix for the structural
mismatch.

### A PARTIAL HYBRID, noted not endorsed
SpotBugs' `logicalLocations` + line effectively yield a partial method->line map
derived from SpotBugs' OWN findings, which could bucket semgrep's points. It
only covers methods SpotBugs already flagged, so it cannot find agreement in
methods only semgrep saw — the coverage is defined by one tool, which is an
odd property for a consensus mechanism. Recorded for completeness.

### Verdict
- **Reachable with current data:** Direction B, on the minority of findings
  where a genuine multi-line range exists. Worth evaluating; not a fix.
- **Needs tooling we do not have:** Direction A. It requires parsing Java to
  recover semgrep's enclosing method. Out of scope as a side-quest.
- **Out of scope:** anything requiring tool changes we do not control (e.g.
  asking semgrep CE to emit logicalLocations).

## THE THIRD DIRECTION CHANGES WHAT THE TOOL CLAIMS — not what it caveats

If A and B both fail, the fallback is to accept that only SAME-METHODOLOGY pairs
co-locate, and describe the tool as measuring agreement WITHIN a methodology.

**Recorded explicitly so nobody adopts this quietly as a footnote:**

The README's premise is that DIFFERENT tools agreeing is the signal —
"rank findings higher where *independent tools agree*", justified by tools with
different methods having different blind spots. Same-methodology agreement is a
DIFFERENT AND WEAKER claim, and it is one the ensemble literature specifically
distinguishes: correlated errors provide no ensemble benefit, and this project
already recorded that redundant-tool overlap amplifies shared false positives
(framing sweep, claim 4).

So adopting the third direction would mean:
- the HEADLINE needs rewriting, not annotating;
- the ROC-AUC 0.755 provenance needs re-examining, since Lipp's result came from
  6 methodologically diverse tools — the configuration the fallback concedes we
  cannot reproduce;
- the tool's central justification changes from "independent evidence" to
  "corroboration within a method", which is a materially smaller claim.

**This is a claim change, not a caveat.** It must not be adopted as a quiet
fallback, and any session that reaches for it should treat rewriting the
README's premise as part of the work, not a follow-up.

## DIRECTION B PRE-REGISTRATION (2026-07-26) — decision rule fixed before computing

Bounded evaluation of point-in-range matching: when one tool reports a RANGE
(startLine..endLine) and another reports a POINT inside it, treat as co-located.
Evaluated on OWASP Benchmark and Struts using SARIF already on disk.

### IMPLEMENT only if ALL of:
- **(a) Material yield.** New cross-tool pairs >= 10% of current merges on OWASP
  (>= 116), OR >= 3 on Struts (where current merges = 0, so any recovered real
  agreement is materially informative).
- **(b) Correctness.** Same-bug rate among NEW matches >= 80% — on OWASP judged
  by the answer key (new match's class == planted category), on Struts by direct
  inspection of every case if few enough to enumerate.
- **(c) Bounded false-merge risk.** Median span of the ranges that ACTUALLY
  PRODUCE new matches <= 25 lines, AND < 10% of producing ranges exceed 100
  lines. (The failure mode is a 200-line method whose range happens to contain
  an unrelated finding.)
- **(d) Determinism.** Order-independent, or made so at trivial cost.

### RECOMMEND AGAINST if ANY of:
- New matches < 5% of merges on OWASP AND < 3 on Struts
- Same-bug rate among new matches < 60%
- Median producing span > 50 lines, OR > 25% of producing ranges exceed 100 lines
- Order dependence requiring a non-trivial fix

### Anything between the two -> report as AMBIGUOUS, make no recommendation.

### Prior being tested (not accommodated)
The inventor's prior: coverage is low enough (SpotBugs emits `endLine` on
11-30% of results; semgrep's spans average ~0.7 lines) that this adds few
matches and cannot address the structural source-vs-sink mismatch. This
evaluation is designed to be capable of refuting that, and a negative is
recorded as a result rather than as a reason to keep the option open.

## DIRECTION B RESULT (2026-07-26) — PASSES the pre-registered rule. Prior REFUTED.

### Measured
```
OWASP Benchmark
  semgrep  class-resolved 1,848 — 442 (24%) carry a real range
  SpotBugs class-resolved 3,268 —   0 (0%)  carry a range
  exact-line matches (current)      1,156
  NEW point-in-range matches          427   = 36.9% of existing
  producing-range spans   median 2 · mean 2.8 · max 16 · >100 lines: 0 (0%)
  same-bug by answer key  427 match planted category, 0 differ  -> 100%

Apache Struts
  exact-line matches (current)          0
  NEW point-in-range matches            2   (both enumerated and inspected)
    ServletRedirectResult.java 244 vs 247, span 21, class=redirect
    ServletRedirectResult.java 244 vs 250, span 21, class=redirect
  -> the near-miss recovered; both are the same unvalidated-redirect bug
```

### Against the pre-registered criteria
```
(a) material yield      427 = 36.9% of merges (threshold >=10% on OWASP)  PASS
(b) same-bug rate       100% (threshold >=80%)                            PASS
(c) false-merge risk    median producing span 2 lines; 0% exceed 100      PASS
                        (thresholds <=25 median, <10% over 100)
(d) determinism         order-independent: shuffled input -> identical
                        grouping. Max component size 4; >2-member
                        components are same-line multi-findings, NOT range
                        chaining.                                          PASS
```
**All four pass. The pre-registered decision is IMPLEMENT.**

### The prior was refuted — and it is worth recording exactly HOW
The prior held that coverage was too low to matter (SpotBugs `endLine` on
11-30%, semgrep spans ~0.7 lines). Both input figures were CORRECT; the
inference from them was not:
- The 11-30% SpotBugs figure is over ALL findings. Among CLASS-RESOLVED ones it
  is **0%** — worse than the prior assumed, and irrelevant, because SpotBugs
  contributes no ranges at all here.
- semgrep's 0.7-line MEAN is dominated by zero-span findings. Among the 442
  that carry a real range, the median span is 2 and the mechanism fires 427
  times.
So the whole effect runs one way: **semgrep's range containing SpotBugs' point.**
An average computed over the wrong population hid a real effect.

### BUT IT DOES NOT ADDRESS THE STRUCTURAL MISMATCH — the prior was RIGHT there
This is the part that must not be lost in a PASS verdict. The 427 OWASP
recoveries have a median span of **2 lines**. They are LINE-JITTER recoveries on
generated code — the same bug, reported one or two lines apart. They are not
source-to-sink recoveries.

The one genuine source-vs-sink case in the entire evaluation is the Struts
near-miss (span 21), and it is **n=1**.

So Direction B is:
- a real, well-behaved mechanical improvement that recovers ~37% more agreement
  on the synthetic corpus and the single real agreement available;
- **NOT** a resolution of HANDOFF §6.2. It cannot recover agreement when the
  source and sink are in different functions, because neither tool emits a range
  spanning them — which is precisely the open cross-function problem.

Adopting it would improve the mechanism without changing the central finding
that methodologically diverse tools do not co-locate. **§6.2 stands, and the
acquisition freeze with it.**

### Honest bounds on this result
- The 100% same-bug rate is on a corpus where the answer key labels ONE bug per
  file, so "class matches planted category" is a weak same-bug test — it cannot
  catch a new match that pairs two genuine but DIFFERENT findings of the same
  class in one file. On generated single-vulnerability files that is unlikely;
  on real code it is not, and it is unmeasured.
- Struts contributes n=2 matches from n=1 underlying bug. It cannot support any
  rate claim.
- SpotBugs contributing zero ranges means this is really a measurement of ONE
  tool's range emission. A different pair could behave entirely differently.

## DIRECTION B IMPLEMENTED (2026-07-26) — phase 2b, point-in-range containment

Adopted after the pre-registered evaluation passed all four criteria. Relaxes
the LOCATION test only.

### What changed
- Phase 2b runs after the exact-key unions: where one record declares a RANGE
  (`endLine > startLine`) and another's `startLine` falls inside it, they union.
- **Same CWE class is still required**; so is different engine lineage, and the
  0a suppression still applies. Containment is not a licence to merge different
  kinds of finding that sit near each other.
- **`_RANGE_SPAN_CAP = 21`**, derived from the measured distribution rather than
  chosen round: OWASP's 442 ranged findings have producing spans maxing at 16
  and an available-range p99 of 16; Struts' one VERIFIED true match spans 21,
  while its other two ranges are SpotBugs method-wide spans of **463 and 524
  lines** — the exact "wide method swallows an unrelated finding" failure mode.
  21 is the largest span observed to produce a verified same-bug match.
  **Coverage cost of the cap:** OWASP loses 0 of 442 ranges and retains all 427
  matches; Struts keeps 1 of 3, the 2 excluded being the 463/524-line ranges.
- Output gains `merge_rules` per finding, plus per-run counts in three
  explicitly-named units (see the reconciliation section below).

### Effect
```
OWASP    1,156 -> 1,584 merges   by rule: exact-line 1,156 · range-containment 351
Struts       0 ->     2 merges   by rule: range-containment (the recovered near-miss)
zlib         2 ->     2 merges   by rule: exact-line only — NO regression
```

### TWO BOUNDS, both load-bearing

**1. The yield figure measures ONE TOOL'S RANGE EMISSION, not point-in-range
matching in general.** SpotBugs contributed **zero** ranges among class-resolved
findings on OWASP (0 of 3,268). Every gain came from semgrep's ranges containing
SpotBugs' points. A different pair could yield nothing, or behave differently
again. The 36.9% is not a property of the technique; it is a property of semgrep
emitting `endLine` and SpotBugs not.

**2. THE 100% SAME-BUG RATE CANNOT DETECT THE FAILURE MODE THIS CHANGE
INTRODUCES.** It was computed against an answer key that labels ONE bug per
file, so "new match's class == planted category" cannot distinguish a correct
pairing from **two genuine, different, same-class findings in one file being
merged**. On generated single-vulnerability files that is unlikely. On real code
— multiple real issues per file, deeper methods — it is plausible, and it is
**exactly the false-merge mode point-in-range containment creates**: a declared
range now legitimately contains points that exact matching kept apart.

>>> CHECK THIS FIRST on the first real-code corpus where BOTH tools emit ranges.
>>> Until then the false-merge rate of phase 2b on real code is UNMEASURED, and
>>> the 100% figure must not be quoted as if it covered it.

### What this does NOT change
Phase 2b recovers line-jitter (median producing span 2 lines) and, in one
observed case, a short source-to-sink gap. It does NOT address cross-function
source/sink separation, because neither tool emits a range spanning functions.
**HANDOFF §6.2 stands, and the acquisition freeze with it.**

## RECONCILIATION: 427 vs 351 (2026-07-26) — three units, one renamed API

A discrepancy was raised between the evaluation's **427** new matches and the
implementation's reported **351**. Diagnosed rather than assumed. **No matches
were being dropped** — but the investigation found a real labelling defect and a
reporting hazard, both now fixed.

### The diagnosis
The two figures counted different things, and a third existed as well:
```
427   containment EDGES (unordered pairs the matcher joined)
+427  increase in ABSORBED RECORDS (verified by re-running with the cap at 0:
      1,156 -> 1,583)
+271  increase in MERGED FINDINGS (surviving records with n_tools > 1)
```
Union-find collapses many edges into fewer components, so edges > merged
findings by construction. Neither the span cap (0 of 442 OWASP ranges lost) nor
double-counting of exact-line matches accounted for it.

### A REAL DEFECT found on the way: exact-line merges mislabelled as containment
Phase 2b tested `a_start <= b_start <= a_end`, which INCLUDES `b_start ==
a_start` — i.e. exact-line coincidences were also being counted and TAGGED as
range-containment. That inflated containment edges to 497 and tagged 351
findings. **Fixed** by excluding `b_start == a_start`, which is exact-line
territory already handled. After the fix containment edges are **427**, exactly
matching the evaluation, and 69 findings are correctly relabelled exact-line.
Without this the two populations could not have been measured separately —
which was the whole point of tagging them.

### The reporting hazard, fixed by RENAMING not documenting
`cross_tool_merges` counted absorbed records; `merges_by_rule` counted tagged
findings. Two fields both named "merges", carrying different units, with nothing
in the name to say so. That is the same failure mode as the 96% denominator,
the base-rate comparator and the average over the wrong population: **a figure
that reads as one thing and is another.** A doc comment does not reach someone
reading the JSON or the HTML report, so the fields were renamed:
```
cross_tool_merges   -> cross_tool_absorbed_records
merges_by_rule      -> findings_by_merge_rule
(new)               -> cross_tool_merged_findings
(new)               -> cross_tool_edges_by_rule      <- the evaluation's unit,
                       previously derivable only by re-running with the cap off
```
Regression-tested invariant, so the units cannot silently desynchronise:
**edges >= merged_findings** and **absorbed >= merged_findings**, checked on
four configurations.

### THE YIELD, stated in every unit
Direction B on OWASP Benchmark, SpotBugs+FindSecBugs x semgrep:
```
+427  containment EDGES            <- the unit the 36.9% refers to (427/1,156)
+427  ABSORBED RECORDS             (1,156 -> 1,583)
+271  MERGED FINDINGS              (1,156 -> 1,427)
 282  findings TAGGED range-containment (211 range-only + 71 also exact-line)
```
**The pre-registered 10% threshold was assessed on EDGES, and 36.9% is the edge
figure.** The decision is robust to the unit: 427/1,156 = 36.9%, 427/1,156 =
36.9% absorbed, 271/1,156 = 23.4% components — all clear 10%.
Do NOT quote "282" (or the former "351") as the yield; it is a tag count.

## OPEN ITEM 2 — is a principled ENTITY-LEVEL match reachable? **NOT REACHABLE.**

Checked in order of cost, against tools and data on disk.

### Check 1 — can semgrep be made to emit method context? NO.
semgrep's NATIVE JSON (richer than its SARIF) carries only:
```
check_id · path · start · end
extra{engine_kind, fingerprint, lines, message, metadata, severity, validation_state}
```
**No enclosing function, method, or symbol field in any output format.** The
`metadata` block is RULE metadata (cwe, owasp, source-rule-url), not location
context. No flag adds it.

A pattern METAVARIABLE could bind an enclosing function (`function $F(...) {...}`),
but only by REWRITING EVERY RULE in `p/java`. That is a rule-authoring project
of the same order as writing a parser, not a cheap route.

INCIDENTAL FINDING, relevant to independence: semgrep's unvalidated-redirect
rule carries `source-rule-url: find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT`.
**semgrep's rule is DERIVED FROM FindSecBugs' rule.** The one cross-tool
agreement found on real Java is between a rule and its own descendant — which is
shared-lineage agreement at the RULE level, a layer below the engine-lineage
guard (item 0). Not pursued here; recorded because it bears on what that
agreement was worth.

### Check 2 — bucket semgrep's points by SpotBugs' logicalLocations? FAILS WHERE NEEDED.
Sized on both corpora:
```
OWASP   8,169 method buckets across 2,751 files
        1,662 of 1,848 semgrep findings (89.9%) fall inside a bucket
        0 ambiguous · bucket spans: median 0, p90 50, max 104
Struts    365 buckets across 203 files
        0 of 1 semgrep findings fall inside a bucket
```

**It fails on the one case that motivates entity matching.** The bucket is
derived from SpotBugs' FINDINGS, not the method's real extent, so it cannot
extend ABOVE the first SpotBugs finding:
```
sendRedirect(HttpServletResponse, String)
  SpotBugs findings at 247, 250  ->  derived bucket [247, 250]
  semgrep finding at 244 (the method SIGNATURE)  ->  OUTSIDE the bucket
```
Since semgrep systematically anchors at the taint SOURCE and SpotBugs at the
SINK, and a source precedes its sink, the derived bucket **systematically
excludes exactly the anchoring mismatch it was meant to bridge.**

Three further objections, any one sufficient:
1. **Coverage is defined by one tool.** Only methods SpotBugs already flagged
   become buckets, so agreement in methods only semgrep saw is unreachable.
2. **The boundary is INFERRED, not DECLARED.** Direction B was adopted because a
   tool-declared range is principled where an invented window is not. A bucket
   spanning findings is invented — it is a tolerance window with extra steps and
   a wider span (p90 50, max 104 lines vs the adopted cap of 21).
3. **It cannot be validated.** Same-bug checking on OWASP rests on
   one-bug-per-file labels, which cannot distinguish a correct pairing from two
   genuine same-class findings in one 104-line method.

### Check 3 — a parser. OUT OF SCOPE.
Recovering semgrep's enclosing method needs Java (and C) parsing. Stated as the
answer, not worked around.

### VERDICT: NOT REACHABLE
No route to a principled entity-level match exists from the data and tools on
disk. The one route with real yield on OWASP (bucketing, 1,662 candidates) is
unprincipled by this project's own adopted standard, and fails on the motivating
case.

## ITEMS 1 AND 2 ARE EXHAUSTED. ITEM 3 IS WHAT REMAINS.

Of the three open questions recorded under HANDOFF §6.2:
```
1. Direction B, point-in-range        -> EVALUATED, ADOPTED. Recovers line
                                         jitter (median span 2). Does NOT
                                         address cross-methodology anchoring.
2. Principled entity-level match      -> NOT REACHABLE (this section).
3. Is the honest description
   SAME-METHODOLOGY agreement?        -> REMAINS.
```

**ITEM 3 IS NOT A MEASUREMENT. IT IS A DECISION ABOUT WHAT THE TOOL CLAIMS.**

No further experiment settles it. The measurements are already in: pattern and
dataflow tools do not co-locate (measured twice, two ecosystems, two
mechanisms); the mechanism requires co-location; neither reachable fix changes
that. What remains is a choice about how the tool describes itself, and it is
the inventor's to make, not a result to be computed.

Stated before going near it, so it is not mistaken for further analysis:
- The README's premise is that DIFFERENT tools agreeing is the signal.
- Adopting item 3 means that premise is not what the tool measures.
- That is a HEADLINE rewrite, a re-examination of the 0.755 provenance (Lipp
  used six methodologically diverse tools), and a materially smaller claim —
  from "independent evidence" to "corroboration within a method".

## RULE-LEVEL LINEAGE MEASURED (2026-07-26) — the concern was real; most numbers survive, ONE does not

Triggered by finding that semgrep's `unvalidated-redirect` rule declares
`source-rule-url: find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT` — i.e.
it is DERIVED FROM the FindSecBugs rule it later "agreed" with.

### 1. How much of semgrep's Java output is FindSecBugs-derived?
```
p/java rules that fired on OWASP        : 11
...declaring FindSecBugs provenance     :  5
semgrep findings from those rules       : 702 / 1,909  (36.8%)
```

### 2. How many merges are a rule agreeing with its OWN ANCESTOR?
```
co-located semgrep x SpotBugs rule pairs : 1,588
RULE-AND-ITS-OWN-ANCESTOR                :   483  (30.4%)
independent provenance                   : 1,105  (69.6%)

by location: 1,229 co-located locations — 278 derived-ONLY (22.6%)

the four ancestor pairs:
  httpservlet-path-traversal <- PATH_TRAVERSAL_IN            199
  des-is-deprecated          <- DES_USAGE                    171
  use-of-sha1                <- WEAK_MESSAGE_DIGEST_SHA1      85
  use-of-md5                 <- WEAK_MESSAGE_DIGEST_MD5       28
```

### 3. Do the C rules show the same? NO — zlib is unaffected.
All four semgrep C rules that fired on zlib (`insecure-use-printf-fn`,
`-scanf-fn`, `-strcat-fn`, `-string-copy-fn`) declare **no source**. The zlib
numbers carry no rule-level lineage.

### 4. RESTATED: the enrichment SURVIVES
```
base rate                                       51.6%
ALL co-located merges          867/1,229 = 70.5%   (+18.9pp)
EXCLUDING derived-only pairs   663/  951 = 69.7%   (+18.1pp)
```
**Excluding 22.6% of the merge population moves the enrichment by 0.8pp.** The
70.4% enrichment is NOT an artifact of shared provenance. It holds on the
independent-provenance subset alone.

7a's zero-false-merges also survives: the 27 divergent cases audited were all
`XSS_SERVLET`, which is not among the derived rules, so the audit's conclusion
stands for the independent population.

### 5. THE ONE NUMBER THAT DOES NOT SURVIVE — and it is the important one
**The single real-code agreement this project has ever found is a
rule-and-ancestor pair.** The Struts near-miss — semgrep
`unvalidated-redirect` vs SpotBugs `UNVALIDATED_REDIRECT` — is exactly the
derived case. So:

- The only cross-methodology agreement observed on REAL code was **not
  independent corroboration**; it was a rule agreeing with its own parent.
- That agreement motivated Direction B's adoption (it was the one verified true
  match at span 21) and framed open item 2.
- Direction B still passes on OWASP evidence, which is largely independent
  (69.6% of pairs). But its *real-code* justification is now one derived pair.

**Restated honestly: on real code, this project has observed ZERO instances of
independent cross-methodology agreement.** The previous count was one, and that
one was shared provenance.

### Consequence for §6.2
It does not soften §6.2 — it sharpens it. The co-location finding stands, and
the one apparent counter-example is removed. Acquisition remains not-the-lever,
and the case that methodologically diverse tools produce observable independent
agreement now has no supporting real-code instance at all.

## GRANULARITY IS THE LEVER (2026-07-26) — §6.2's conclusion is OVERTURNED

External corroboration was sought for §6.2 and it arrived with a correction
attached. Both sources checked directly, not summarised.

### Lenarduzzi et al., arXiv:2101.08832 `[fetched]` — 47 Java projects, 6 tools
Verified from the PDF, not from an abstract:
```
Overlap at BOTH "class-level" and "line-level" is "always low".
Best pair Findbugs-PMD  : 9.378%  (3,161 of 33,704 possible)
Worst pair Checkstyle-PMD: 0.144%
Total across pairs      : 18,004 of 4,430,023 = 0.4%
"we did find no warnings pair ... considering more than two tools"
Scale: 13,554,762 warning violations across 936 warning types.
```
NOTE ON COMPARABILITY: their metric is RULE-PAIR co-occurrence (occurrences /
possible occurrences), NOT "fraction of code units flagged by >1 tool". It is
not directly comparable to our merge rate — but it independently establishes
that agreement is scarce at line AND class granularity, at industrial scale.
§6.2's finding is NOT a corpus artifact or a tooling error.

### But Lipp is not an outlier — it is measured at a DIFFERENT GRANULARITY
Computed directly from the Lipp artifact on disk, same 6 tools, same real C code:
```
LINE level   (file, line, CWE) :  96,875 units,  1,507 multi-tool =  1.56%
FUNCTION level                 :  14,656 units,  5,269 multi-tool = 35.95%
                                                            a 23x increase
```
**Lipp's 1.56% at line level is consistent with Lenarduzzi.** The papers do not
conflict. Lipp's headline results were computed at FUNCTION level all along —
already recorded in this file as "Unit = FUNCTION (the paper's validated
granularity choice; Section 3.2, FEC metric)". We had the fact and did not
connect it to our key.

### THE DECISIVE MEASUREMENT — cross-methodology agreement EXISTS at function level
```
TOOL PAIR                     line-lvl  func-lvl   methodologies
CommSCA + Flawfinder                 2     1,191   commercial x PATTERN   (596x)
CodeQL + Flawfinder                 37       669   dataflow x PATTERN      (18x)
Flawfinder + Infer                   2       274   PATTERN x dataflow     (137x)
CodeChecker + Flawfinder             0       136   dataflow x PATTERN    (0->136)
Cppcheck + Flawfinder                0        66   dataflow-lite x PATTERN (0->66)

CROSS-METHODOLOGY total:        1,169     7,514                          (6.4x)
```

**`Cppcheck + Flawfinder` is EXACTLY our zlib pair.** Line level: 0. Function
level: 66. Our zlib zero was a GRANULARITY ARTIFACT, not a property of the tools.

### §6.2 RESTATED
The old claim — "pattern tools and dataflow tools do not produce co-located
agreement" — is TRUE AT LINE LEVEL and FALSE AT FUNCTION LEVEL. The premise and
the mechanism do not pull against each other; **the mechanism is simply matching
at the wrong granularity.**

- "Acquisition is not the lever" STILL HOLDS, and is now better explained: a
  fourth tool would also have been matched at line level.
- "Nothing purchasable resolves that" HOLDS.
- **"Cross-methodology agreement may not be observable" IS WITHDRAWN.** It is
  observable. We were not looking at the level where it occurs.

### Consequences
1. **Open item 2 (entity-level matching) changes from marginal to the main
   event.** Its verdict "NOT REACHABLE without a parser" stands on the evidence
   — but the payoff is now measured at 6.4x on cross-methodology pairs, not
   speculative. A parser may be justified where it was not before.
2. **Item 3's premise is FALSIFIED.** "Same-methodology agreement is the honest
   description" is wrong: cross-methodology agreement is real and abundant at
   function level. Item 3 should NOT proceed as framed.
3. Direction B (point-in-range) is a partial, accidental approximation of
   function-level matching — semgrep's method-spanning range in the Struts case
   was a function boundary in disguise.

### Honest bound
Function sizes in Lipp: median 14 lines, p90 107, max 8,444. Function-level
matching is coarser and its false-merge rate is UNMEASURED — the same question
Direction B raised, now at larger scale and with a larger payoff. The 35.95%
and 6.4x are agreement RATES, not correctness; nothing here shows those merges
are the same bug.

## DOES FUNCTION-LEVEL AGREEMENT CARRY SIGNAL? (2026-07-26) — YES, but with a
## significant negative attached that must travel with it

Computed on the Lipp artifact: real C code, 6 tools, CVE ground truth,
function boundaries. Everything from disk.

### 1-2. Precision and enrichment by granularity
```
LINE LEVEL (file,line,CWE)   base 1.18%
  single-tool 95,368 units  precision 1.19%
  MULTI-tool   1,507 units  precision 0.80%   -0.39pp   z=-1.40 p=0.163  n.s.
  -> line-level agreement carries NO signal, and trends NEGATIVE

FUNCTION LEVEL               base 0.92%
  single-tool  9,387 units  precision 0.58%
  MULTI-tool   5,269 units  precision 1.54%   +0.96pp   z=5.85 p=4.9e-09  ***
  -> function-level agreement carries REAL SIGNAL

FILE LEVEL                   base 2.34%
  single-tool  2,685 units  precision 0.34%
  MULTI-tool   2,736 units  precision 4.17%   +3.83pp
```
**The 6.4x extra merges are not noise.** At function level, multi-tool units are
2.7x more likely to be genuinely vulnerable than single-tool units, at
p=4.9e-09. At LINE level the same comparison is flat-to-negative — which is
precisely where our key operates.

### 3. n_tools monotonicity — holds at function/file level, INVERTS at line level
```
LINE      1 tool 1.19%  ->  2 tools 0.82%  ->  3 tools 0.00%      DECREASING
FUNCTION  1 tool 0.58%  ->  2 tools 1.42%  ->  3 1.91%  ->  4 2.33%   rising
          (5 tools 0.0% n=31, 6 tools 0.0% n=4 — collapses on tiny n)
FILE      1 tool 0.34%  ->  2 1.43%  ->  3 2.40%  ->  4 9.60%  ->  5 14.97%
```
**The monotonicity the whole premise rests on is a FUNCTION/FILE-level property.
At line level it runs backwards.**

VALIDATION.md's recorded "1 tool 0.9% -> 4 tools 11.6%" is FILE-level in kind.
It does not reproduce exactly here (0.34% -> 9.60%) because that figure used a
5-tool subset and a different file universe; same shape, different parameters.
Recorded as a near-match, not a match.

### 4. THE NEGATIVE — function-level consensus LOSES to the best single tool
```
CodeChecker   flags   608 functions  precision 2.63%   <- best single
Flawfinder    flags 2,423            precision 1.73%
CommSCA       flags 7,994            precision 1.16%
Cppcheck      flags   488            precision 1.23%
Infer         flags 2,146            precision 1.07%
CodeQL        flags 7,764            precision 0.82%

CONSENSUS     flags 5,269 functions  precision 1.54%
  vs best single: -1.09pp   z=-2.01  p=0.0449   SIGNIFICANTLY WORSE
```
This is a real negative and must not be buried under the positive above.
**Consensus beats SINGLE-TOOL-AVERAGE decisively and loses to the BEST single
tool significantly.**

HONEST CAVEAT, which does not rescue it: this is a PRECISION-ONLY comparison
between selectors with very different recall. CodeChecker flags 608 functions
(4%); consensus flags 5,269 (36%). A selector that flags less can have higher
precision trivially. The fair comparison for a RANKER is ranking quality at
equal review budget (ROC-AUC / PofB), not raw precision — and that is exactly
what Lipp's own 0.755 measured. So this does not show consensus is useless; it
shows consensus is not a high-precision FILTER, and that "beats the best single
tool" needs the ranking framing to be defensible.

### 5. FALSE-MERGE SIGNATURE: NOT FOUND — and the predicted pattern is INVERTED
```
size (lines)   multi n  multi prec  single n  single prec     gain
0-10               399       0.00%      1983        0.05%   -0.05pp
11-25            1,027       0.29%      2793        0.18%   +0.11pp
26-50            1,116       0.54%      2141        0.42%   +0.12pp
51-107           1,260       1.59%      1481        1.22%   +0.37pp
108-300            971       2.99%       742        2.02%   +0.97pp
301+               496       4.64%       247        2.43%   +2.21pp
```
The predicted signature was "gain concentrates in SMALL functions and INVERTS in
large ones", which would argue for a size cap as Direction B needed a span cap.
**The measured pattern is the exact opposite: the gain grows monotonically with
function size**, reaching +2.21pp in functions over 300 lines.

**So a size cap is NOT indicated on this evidence.** But the large-function
result is CONFOUNDED: base vulnerability rate also rises with size (single-tool
precision rises 0.05% -> 2.43% across the same buckets), because a bigger
function is more likely to contain a CVE. Multi-tool keeps roughly a 2x
advantage throughout, which is consistent with real signal rather than
co-residence — but the confound is not resolved here, and co-residence cannot be
excluded on this data alone.

### Bottom line
Function-level matching is where the premise's signal actually lives. Line-level
matching — what we implement — is measurably the wrong granularity: agreement
there is uninformative and anti-monotonic. That is the actionable finding.

## EFFORT-AWARE EVALUATION (2026-07-26) — the granularity question ANSWERED, and
## a serious finding about the headline metric

Prior comparisons were unit-normalised, which flatters coarse granularity
mechanically: 20% of files is far more code than 20% of functions. Redone with
the budget measured in LINES OF CODE. Motivated by the known
prediction-vs-localization tradeoff (Koru & Liu 2005; Calikli et al. 2009, via
the systematic review arXiv:2210.02236) and by Rahman et al. ICSE'14,
"Comparing static bug finders and statistical prediction", which found ASATs and
file-level defect predictors give **no statistically significant difference** in
ranking performance `[snippet]` — corroborated across several secondary sources;
the ICSE paper itself was not fetched.

### PofB@20% of LOC reviewed (effort-aware), Lipp artifact, real CVE labels
```
FUNCTION level  (14,656 flagged units, 597,704 LOC, 135 vulnerable)
  CONSENSUS (n_tools)        0.185      <- the tool's signal
  baseline: LOC alone        0.185      <- IDENTICAL
  baseline: finding count    0.230      <- BEATS consensus
  best single (Flawfinder)   0.259      <- BEATS consensus
    consensus vs LOC          +0.000  p=0.522  not significant
    consensus vs findcount    -0.044  p=0.910  consensus WORSE
    consensus vs best single  -0.074  p=0.955  consensus WORSE

FILE level      (2,678 flagged units, 1,159,586 LOC, 123 vulnerable)
  CONSENSUS (n_tools)        0.228
  baseline: LOC alone        0.081
  baseline: finding count    0.114
  best single (Infer)        0.317
    consensus vs LOC          +0.146  p=0.000  SIGNIFICANT
    consensus vs findcount    +0.114  p=0.018  SIGNIFICANT
    consensus vs best single  -0.089  p=0.953  consensus worse (n.s.)
```

### ANSWER: neither granularity change is justified
- **FUNCTION level does NOT win once effort is priced.** Its consensus is
  *indistinguishable from ranking by LOC alone* (delta +0.000, p=0.522) and is
  beaten by simply counting findings. The 6.4x extra merges and the +0.96pp
  unit-normalised precision gain do NOT survive effort-normalisation.
  **=> Open item 2 is NOT justified as a parser project. The measured payoff
  disappears when the metric prices localization cost.**
- **FILE level consensus DOES beat both trivial baselines significantly**, so it
  is not merely tracking size. But it loses to the best single tool, so it does
  not support a "beats the best single tool" claim either.
- Neither granularity's consensus beats the best single tool effort-aware.

### THE SERIOUS FINDING — a trivial size baseline BEATS the headline number
ROC-AUC, reported here **explicitly as NOT effort-aware**:
```
                    FUNCTION   FILE
  CONSENSUS           0.628    0.763   <- file-level reproduces the published 0.755
  baseline: LOC alone 0.803    0.845   <- HIGHER AT BOTH GRANULARITIES
  finding count       0.694    0.783
```
**Ranking files by LINES OF CODE ALONE scores ROC-AUC 0.845 on the same data
where this tool's published headline is 0.755.** A ranker that reads no tool
output, no CWE, no agreement — only file size — outperforms the consensus signal
on the metric the README quotes.

This is Rahman's result reproducing on our own corpus, and it is why
non-effort-aware ROC-AUC is the wrong metric to headline: bigger units are more
likely to contain a bug, so any size-correlated score scores well without
carrying information about WHERE the bug is.

It does NOT mean consensus is worthless — effort-aware, file-level consensus
beats the LOC baseline decisively (0.228 vs 0.081, p=0.000), which is the
inverse ordering. It means **0.755 is the wrong number to lead with**, and the
effort-aware comparison is the defensible one.

### Bounds
- 135 vulnerable functions / 123 vulnerable files — small positive counts, so
  PofB estimates are noisy; bootstrap (400 resamples) is reported for the
  key comparisons rather than eyeballed.
- Single-tool PofB values are not coverage-matched: tools flag very different
  numbers of units, and PofB does not penalise a tool for flagging little.
- Ties broken by ascending LOC (review smaller units first), applied identically
  to every ranker.
- One corpus, C/C++, six tools.

## AGAINST THE FIELD'S ESTABLISHED BASELINES (2026-07-26) — ManualUp / ManualDown

Prior effort-aware comparison used DESCENDING LOC, which is **ManualDown — the
NON-effort-aware baseline**. The correct effort-aware baseline is **ManualUp
(ascending size)**. Definitions verified in arXiv:2302.00394 `[fetched]`:
Zhou et al. 2018 advocated both, "separately for non-effort-aware evaluation and
effort-aware evaluation"; ManualDown classifies the top 50% LARGEST modules as
defective, ManualUp the top 20% SMALLEST. Metric definitions cross-checked
against arXiv:2504.19181 `[fetched]` (Popt = 1 - delta_opt, Mende & Koschke).

**So the earlier "+0.146 effort-aware win" was measured against the wrong
baseline and is WITHDRAWN.**

### Results — Lipp artifact, real CVE labels, bootstrap n=300
```
FUNCTION level (14,656 units, 597,704 LOC, 135 vulnerable = 0.92%)
  ranker              PofB@5   @10   @20   @50    Popt    IFA   PMI@20
  CONSENSUS            0.030  0.067 0.185 0.585   0.530    142    0.161
  ManualUp (asc)       0.015  0.067 0.185 0.511   0.494  1,746    0.602
  ManualDown (desc)    0.022  0.067 0.185 0.489   0.508      2    0.022
  random               0.052  0.096 0.222 0.459   0.497    260    0.206

FILE level (2,678 units, 1,159,586 LOC, 123 vulnerable = 4.59%)
  CONSENSUS            0.033  0.122 0.228 0.577   0.535      5    0.062
  ManualUp (asc)       0.049  0.098 0.195 0.577   0.547    614    0.706
  ManualDown (desc)    0.000  0.016 0.081 0.423   0.453      3    0.013
  random               0.065  0.073 0.146 0.455   0.475     16    0.171

  consensus vs ManualUp, FILE level:
    PofB@20  +0.033  p=0.323   not significant
    Popt     -0.013  p=0.603   not significant
    PMI@20   consensus inspects 6.2% of files vs 70.6%   p=0.000  SIGNIFICANT
    IFA      5 vs 614
```

### What this establishes
1. **On detection (PofB@20, Popt) consensus and ManualUp are STATISTICALLY
   INDISTINGUISHABLE** at both granularities. Neither wins. The predicted
   "consensus loses on PofB@20" did not occur — but neither did a win.
2. **On inspection cost consensus wins decisively.** At file level it reaches
   the same bug yield having inspected **6.2% of files with 5 initial false
   alarms**, where ManualUp needs **70.6% of files and 614 false alarms**.
3. **No baseline dominates, and that is the real result.** ManualDown has
   excellent IFA (3) and terrible yield (PofB@20 = 0.081). ManualUp has
   comparable yield and catastrophic IFA (614). **Consensus is the only ranker
   that is good on BOTH** — the standard shape in this literature.

### THE DAMAGING RESULT — function level fails against RANDOM
At function level, **random ordering beats consensus on PofB@20 (0.222 vs
0.185)**, and all three non-random rankers tie at 0.185. Function-level
consensus does not merely fail to beat ManualUp; it fails to beat chance on the
headline effort-aware metric. Combined with the earlier finding that it is
indistinguishable from LOC-alone, **the function-level direction is dead, and
open item 2 stays closed.** A parser would buy nothing measurable.

### The defensible claim, if one is wanted
Effort-aware, at FILE level, on real CVE ground truth:
> Reviewing the same 20% of code, consensus ranking finds as many vulnerable
> files as the standard effort-aware baseline while inspecting **6.2% of files
> instead of 70.6%**, and hitting its first true positive after **5 false
> alarms instead of 614**.

That is narrower than "beats the best single tool" and narrower than 0.755. It
is a claim about WASTED INSPECTION, not detection rate, and it is the one the
evidence supports.

### Bounds
- Detection parity, not superiority. Consensus does NOT find more bugs.
- 123-135 positives; PofB is noisy, hence bootstrap rather than eyeballing.
- One corpus, C/C++, six tools; ManualUp is documented as strongest on highly
  skewed data, and this corpus is highly skewed (0.92% at function level).
- IFA is a single-run order statistic, not bootstrapped; it is stable here only
  because the gap (5 vs 614) is enormous.

## SIZE CONFOUND CHECK (2026-07-26) — the re-headlining candidate DOES NOT SURVIVE

Run before drafting any README language. It is as well it was run first.

### Literature verified against arXiv:2504.19181 `[fetched]`
- Shihab et al.: "LOC does not appear to be a reliable predictor of module
  analysis effort … complexity measures correlate with effort better than LOC …
  effort-aware models should not assume that LOC is a good measure of effort."
- Lavazza et al.: "the measure used as the module effort driver crucially
  influences the results."
- Mende & Koschke: "some SDP models may have a performance that appears to be
  reasonably good according to traditional metrics, while it is in fact worse
  than the performance obtained by picking the modules to analyze at random."

### CHECK 1 — the size confound is REAL and large
```
corpus          n=2,678   mean LOC   433   median   168
consensus@20%   n=  165   mean LOC 1,379   median 1,018   = 3.18x mean, 6.04x median
Spearman(n_tools, LOC) = +0.629     <- MORE TOOLS FLAG BIGGER FILES
```
Against a SIZE-MATCHED random baseline (same size distribution as consensus's
own within-budget selection, drawn randomly within size deciles, 500 draws):
```
              consensus   size-matched random   P(random >= consensus)
PofB@20         0.228        0.196 +/- 0.030          0.184   NOT significant
IFA             5            21.8 +/- 12.4            (~1.3 SD, not significant)
```

**Once size is controlled, consensus has NO statistically significant advantage
on any metric measured.** The headline 6.2%-vs-70.6% inspection figure is
largely mechanical: consensus selects large files, so a LOC budget is exhausted
on few of them. Fewer files for the same code is a real ergonomic benefit, but
it follows from SIZE SELECTION, not from agreement carrying information.

### The precise, more interesting finding
```
ManualDown (pure descending size)  PofB@20 = 0.081   <- picking the BIGGEST is BAD
consensus                                   = 0.228
size-matched random                         = 0.196   <- most of the gap
```
Consensus is NOT "review the biggest files" — that scores 0.081. It selects a
FAVOURABLE SIZE DISTRIBUTION (large but not extreme), and **within that
distribution it adds little that random selection does not.** The value is in
the size profile it picks, not in which specific files it picks within it.

### CHECK 2 — function level at-or-below random, CONFIRMED
500 random draws, identical budget, identical tie-breaking, identical unit set:
```
FUNCTION  consensus 0.185   random 0.199 +/- 0.034   P(random >= consensus) = 0.696
FILE      consensus 0.228   random 0.201 +/- 0.036   P(random >= consensus) = 0.256
```
Function level is below the random MEAN and random beats it ~70% of the time.
This is Mende & Koschke's documented phenomenon, cited above — **expected, not
anomalous, and not a harness artifact.** File level is above random but NOT
significantly.

### VERDICT: DO NOT RE-HEADLINE ON THIS CLAIM
The drafted claim — "same yield, 6.2% of files instead of 70.6%, 5 false alarms
instead of 614" — is arithmetically true against ManualUp but **substantially
attributable to size selection**, and it does not survive a size-matched
control. Publishing it would repeat the exact error 0g identified in 0.755:
leading with a number that a trivial size-correlated baseline matches.

The framing hope — that PMI and IFA escape the LOC-as-effort critique because
they count modules rather than lines — is correct in principle and **defeated in
practice here**, because PMI is itself driven by the size of the modules chosen.
The critique is dodged; the confound is not.

### What is left that is defensible
Only this, and it is thin: consensus reaches its first true positive after 5
false alarms where the effort-aware baseline needs 614, and it beats pure
size-ranking (ManualDown) decisively on yield (0.228 vs 0.081). Both are true.
Neither is significant against a size-matched control, and both must carry that
qualification.

**No README language drafted. On this evidence there is no claim worth
promoting to a headline.**

## 0g CONCLUSION (2026-07-26) — THE RANKER HAS NOT BEEN SHOWN TO ADD INFORMATION
## BEYOND THE SIZE PROFILE IT SELECTS

Recorded as one finding, not three, because the PATTERN is the finding.

### The three collapses, in sequence
```
1. ROC-AUC 0.755 (the published headline)
     -> ManualDown, ranking files by DESCENDING SIZE and reading no tool output,
        scores 0.845 on the same data. The headline metric is not effort-aware,
        and a trivial size baseline beats it.

2. "Effort-aware, consensus beats the baseline +0.146, p=0.000"
     -> measured against ManualDown, which is the NON-effort-aware baseline.
        Against ManualUp (ascending size), the correct effort-aware baseline:
        PofB@20 +0.033 p=0.323, Popt -0.013 p=0.603. Both NOT significant.

3. "Same yield, 6.2% of files inspected instead of 70.6%, IFA 5 vs 614"
     -> against a SIZE-MATCHED random control: PofB@20 0.228 vs 0.196
        (P=0.184), IFA 5 vs 21.8 +/- 12.4. Neither significant. The inspection
        advantage is largely mechanical — consensus selects files averaging
        3.18x corpus mean LOC, so a LOC budget is spent on few of them.
```
**Each claim survived until a better-matched control was applied, and none
survived the next one.** Three different metrics, three different baselines,
same outcome. Spearman(n_tools, LOC) = +0.629: agreement count is substantially
a size proxy on this corpus.

**CONCLUSION: on this corpus, the ranker has not been shown to add information
beyond the size profile it selects.** Consensus is not merely "pick the biggest"
— pure descending size scores 0.081 against consensus's 0.228 — but within the
size distribution consensus chooses, random selection performs comparably.

### WHAT IS *NOT* REFUTED — state with equal force
1. **Lipp's premise stands on Lipp's own data.** Their function-level detection
   result, the +15pp lift from tool combination, and the diversity argument are
   theirs and are untouched by any of this. We measured OUR ranker, not their
   finding.
2. **Consensus DOES carry signal at function level.** Multi-tool functions are
   1.54% vulnerable vs 0.58% single-tool, **p=4.9e-09** on real CVE labels. That
   result is unaffected by the effort-aware collapses — it is a statement about
   PRECISION, and it is strongly significant. What fails is converting that into
   a ranking advantage once inspection cost is priced.
3. **A size-matched control is a HARD baseline.** Mende & Koschke document that
   models can look good on traditional metrics while being worse than random
   under effort-awareness; the literature reports ManualUp beating many
   published models. Failing this control puts our ranker in large company, and
   is not evidence of a defect unique to it.

**This is a NULL RESULT ABOUT OUR RANKER. It is not a refutation of consensus,
of Lipp, or of the diversity premise.**

### Status
The README leads with 0.755. No replacement claim is ready, and none should be
manufactured. Decision pending (see HANDOFF 0g).

## The function-level precision result SURVIVES size matching (2026-07-26)

> **[SIGNIFICANCE LANGUAGE WITHDRAWN 2026-07-28 — READ BEFORE QUOTING THE BLOCK
> BELOW. The RATIO stands; the P-VALUE and "highly significant" do not.]**
> The line `P(size-matched control >= multi) = 0.0000   SURVIVES` and the
> sentence "The residual 1.51x is real and **highly significant**" were both
> withdrawn by the 0j work later the same day — see **"0j RESULT (2026-07-26)"**
> below in this file, §"!! THE p<0.0001 IS NOT SUPPORTABLE !!" and §"WHAT THE
> README MAY AND MAY NOT SAY".
> **Why:** that statistic holds the multi group's own 81/5,269 FIXED and
> resamples only the controls, so it ignores sampling variability in the
> numerator population and is anti-conservative by orders of magnitude. The
> honest figure is **p ~ 0.03–0.08 unclustered (p ~ 0.001 clustered on
> project)**, with a project-bootstrap 95% CI of **[0.99x, 2.58x]** — the effect
> is marginal, not overwhelming.
> **What SURVIVES, unchanged:** the 1.51x size-matched point estimate itself
> (1.43x–1.53x across every stratification, direction consistent in 9/9
> projects). The README's "~1.5x, size-matched" is correct and is not affected.
> **Why this pointer exists here rather than only at 0j:** the rule this file
> derived for itself at §"THE CENTRAL OPEN QUESTION" — *when an entry here is
> overturned, the OVERTURNED entry gets the forward pointer, not only the new
> one, which the reader has by definition not found yet.* The withdrawal sits
> ~300 lines below under a heading sharing no vocabulary with this one, and this
> block is quotable in isolation.

Checked before the 2.7x figure was allowed into the README — it would have been
incoherent to ship an uncontrolled number immediately after retiring three
others for being uncontrolled.

```
UNMATCHED      multi 1.54% (n=5,269)  vs single 0.58% (n=9,387)   = 2.67x
SIZE-MATCHED   multi 1.54%            vs single 1.02% +/- 0.14    = 1.51x
               (2,000 draws, single-tool controls matched by size decile)
               P(size-matched control >= multi) = 0.0000   SURVIVES
```
**Roughly 40% of the apparent 2.67x effect is size.** The residual 1.51x is real
and highly significant.

### Why this survives when the ranking did not
```
Spearman(n_tools, size)   FILE level    +0.629
                          FUNCTION level +0.304
```
The size confound is **less than half as strong at function level**. That is the
mechanical reason the precision finding holds up while every file-level ranking
claim collapsed — not an inconsistency between the two results.

**README now quotes 1.5x, size-matched, with the uncontrolled 2.7x named and
attributed to size.** This is the first performance-adjacent number in the
project to be published with its control already applied rather than applied
afterwards by a reviewer.

## 0i STUDY (2026-07-26) — consensus-density is the WRONG construction. Searched
## before proposing, and the proposal did not survive the search.

### 1. Ratio variables with a common denominator — Kronmal `[snippet]`
Kronmal (1993, JRSS-A, "Spurious Correlation and the Fallacy of the Ratio
Standard Revisited"): dividing by a common denominator **induces correlation
between the ratio and its denominator** even when the numerators are
independent. "If the relationship between a ratio's numerator and denominator is
not zero, then the use of a ratio variable will create a spurious correlation
between the ratio and its denominator." Using a ratio as a variable in
regression "can lead to incorrect or misleading inferences."

**The standard remedy is to use the denominator as a COVARIATE IN REGRESSION,
not to form a ratio.**

=> `consensus / LOC` is precisely the construction this literature warns
against. It would not remove the size confound; it would replace a positive size
correlation with an induced negative one.

### 2. What the defect-prediction field actually does `[snippet]`
- Zhou et al. model size as a CONFOUNDER on a causal diagram (paths m->s->d and
  m->d) and adjust for it; an improved model exists (MDPI Appl. Sci. 13(6):3459).
- **Zhou et al. (2014): "After controlling for size, none of the
  object-oriented metrics were associated with fault-proneness anymore."**
  That is the same result SHAPE this project just produced, from a different
  field, a decade earlier.
- Methods used: covariate adjustment, causal diagrams, stratification, and
  half-sibling regression for unobserved confounding.
- **Ratio normalization is NOT the field's answer.** Nothing found recommends it.

### 3. Defect density specifically — a contested measure `[snippet]`
- Rosenberg argued the observed DECREASE in defect density with module size may
  be an ARTIFACT of how the metrics are analysed — i.e. Kronmal's problem showing
  up in this exact measure. Malaiya & Denton evaluated the argument and called
  the observation misleading.
- Hatton reports a U-shaped size/density curve (a ~200-400 LLOC minimum), so
  density is not monotone in size and a density ranker has no single expected
  behaviour.
- General critique: density is sensitive to language and author verbosity, and
  a count does not reflect severity.

=> Density-based prioritization is not new, is contested, and its interaction
with size is exactly the thing under dispute. **Do not rediscover it.**

### PREDICTION, recorded before any computation
A per-LOC density ranker will favour SMALL units, which is ManualUp — the
baseline this project already fails to beat and which the literature reports as
strong on skewed data. **Expect density to reproduce ManualUp, not to beat it.**

## 0i PRE-REGISTRATION — candidate formulations and how each will be judged

### The question is now sharper than "control for size"
The 1.5x size-matched precision result already shows `n_tools` carries
information beyond size at FUNCTION level (p<0.0001). What has never worked is
converting that into a RANKING advantage under effort-aware evaluation. So 0i
asks: **can any formulation convert a size-independent precision signal into a
size-independent ranking advantage?**

### Candidate A — logistic regression with size as a covariate  [the Kronmal remedy]
`P(vulnerable) ~ n_tools + log(LOC)`; rank by fitted probability.
- CONTROLS FOR: size, directly and without forming a ratio.
- DOES NOT CONTROL FOR: complexity, churn, language; non-linear size effects
  unless explicitly modelled (Hatton's U-curve suggests they exist).
- JUDGED BY: (i) is the `n_tools` coefficient significant with `log(LOC)` in the
  model? (ii) does the fitted ranker beat a size-only model (`~ log(LOC)` alone)
  on PofB@20 and IFA? (iii) does it beat SIZE-MATCHED random?

### Candidate B — size-residualized consensus
Regress `n_tools` on `log(LOC)`, rank by the RESIDUAL.
- CONTROLS FOR: size by construction; avoids the ratio entirely.
- DOES NOT CONTROL FOR: anything else; residuals are noisy where size is extreme.
- JUDGED BY: same three tests as A.

### Candidate C — consensus density per LOC  [the ORIGINAL proposal, retained to be TESTED not assumed]
`n_tools / LOC`.
- CONTROLS FOR: nominally size.
- DOES NOT CONTROL FOR: it INTRODUCES a spurious negative size correlation
  (Kronmal), and is predicted to behave like ManualUp.
- JUDGED BY: same three tests. **Predicted to fail; recorded so the prediction
  is falsifiable rather than a post-hoc excuse.**

### Candidate D — THE NULL: no formulation adds ranking information beyond size
- ESTABLISHED IF: A, B and C all fail to beat size-matched random on PofB@20 and
  IFA, AND the `n_tools` coefficient in A is not significant once `log(LOC)` is
  included.
- **NOTE: the null is NOT already established.** The 1.5x size-matched precision
  result is evidence against it. If the null holds for RANKING while precision
  survives, that is itself the finding: the signal is real but not orderable
  under an effort budget — which would be an honest terminal answer for this
  direction rather than a failure to find one.

### Standing rule, unchanged
Nothing gets headlined until it survives a SIZE-MATCHED CONTROL — not merely
ManualUp, not merely ManualDown. Three claims have already died in the gap
between "beats a named baseline" and "beats a size-matched control".

### Not implemented. No computation performed in this pass.

## 0i RESULT (2026-07-26) — D HOLDS. Terminal answer for this direction.

Pre-registered evaluation run as filed. Function level, 14,656 units, 135 vulnerable.

### Regression diagnostics — the coefficient does not survive size adjustment
```
n_tools alone            b=+0.5249  z=+5.66  p=1.56e-08  ***
log(LOC) alone [FLOOR]   b=+1.0546  z=+13.37 p<1e-15     ***
n_tools + log(LOC)
    n_tools              b=+0.0573  z=+0.55  p=0.582      NOT SIGNIFICANT
    log(LOC)             b=+1.0388  z=+12.36 p<1e-15     ***
+ quadratic
    n_tools              b=+0.0598  z=+0.58  p=0.563      NOT SIGNIFICANT
    log(LOC)^2           b=-0.0950  z=-1.74  p=0.083      marginal (Hatton U-curve)

Pearson(n_tools, log(LOC)) = +0.305   VIF = 1.10  -> TOLERABLE
```
**The n_tools coefficient attenuates 89% (+0.525 -> +0.057) and loses all
significance when log(LOC) enters.** VIF 1.10 rules out collinearity instability:
this is genuine confounding, not an unstable fit. It reproduces Zhou et al.
(2014) — "after controlling for size, none of the metrics were associated with
fault-proneness anymore" — on our data.

### Ranking evaluation vs SIZE-MATCHED random (400 draws)
```
ranker                        PofB@20   IFA   PMI@20   vs size-matched random
A logistic n_tools+log(LOC)     0.185     2    0.022   BEATS (0.098, p=0.000)
SIZE-ONLY [FLOOR]               0.185     2    0.022   BEATS (0.096, p=0.000)
B size-residualized             0.185   142    0.161   does NOT beat (p=0.468)
C density n_tools/LOC           0.170  1334    0.571   does NOT beat (p=0.603)
raw consensus                   0.185   142    0.161   does NOT beat (p=0.443)
```
**A IS the size-only model.** Its n_tools coefficient is ~0, so the fitted
ranker is driven entirely by log(LOC) — identical PofB, IFA and PMI to the
floor. A does not CLEAR the floor; it collapses onto it.

### C — the pre-registered prediction is CONFIRMED
Predicted before computing: "a per-LOC density ranker will favour SMALL units,
i.e. reproduce ManualUp." Measured: C has PMI@20 = 0.571 and IFA = 1,334, against
ManualUp's 0.602 and 1,746. Near-identical behaviour, and the worst PofB of any
candidate. **Density is ManualUp with extra steps, exactly as Kronmal predicts.**

### VERDICT: D — THE NULL — HOLDS. 0i IS CLOSED.
No formulation adds ranking information beyond size on this corpus. A collapses
to the floor; B, C and raw consensus all fail to beat size-matched random.

**"The signal is real but not orderable under an effort budget" is the finding.**
It closes this direction honestly rather than leaving it to be reattempted.

### !! UNRESOLVED — THIS RUN PUTS THE README'S 1.5x CLAIM IN DOUBT !!
> **[RESOLVED 2026-07-26 — see "0j RESULT" at the end of this file. The doubt
> recorded below was reasonable but the hypothesis in it is now MEASURED AND
> REFUTED: refining the strata does NOT decay the effect (1.51x at K=10, 1.52x
> at K=200) and residual size imbalance is gone by K=50. The real disagreement
> was that 0i's linear-in-n_tools slope and the matched test estimate DIFFERENT
> QUANTITIES. What did not survive is the `p<0.0001`, for an unrelated reason.
> Do not cite the paragraphs below as the current state.]**
The README currently states multi-tool functions are ~1.5x more likely to
contain a real CVE than SIZE-MATCHED single-tool functions (p<0.0001). That was
measured by DECILE matching. This run's logistic model, using CONTINUOUS
log(LOC) — the finer and Kronmal-recommended control — puts n_tools at p=0.582.

The two disagree, and the likely reason is that decile matching leaves large
residual size variation inside each stratum on a heavily skewed distribution.
**If that is right, the README's last remaining number is not adequately
size-controlled and must be corrected or removed.**

NOT RESOLVED. The check was in flight when this session ended: re-run the
matched test at 10 / 50 / 200 strata and see whether the effect decays as strata
are refined. If it decays toward the logistic result, the 1.5x does not survive
and the README needs a fourth correction. **Treat the 1.5x as SUSPECT until
this is settled.**

## 0j RESULT (2026-07-26) — RESOLVED. The 1.5x SURVIVES; the p<0.0001 DOES NOT.
## The hypothesised mechanism was measured and REFUTED.

Tier: `[self-tested]` analysis over `[externally-grounded]` inputs (Lipp et al.
CVE labels, Zenodo 10.5281/zenodo.6515687). Same tier the 1.5x already carried.
**This is not a tier move.** Scripts: `analysis/scripts/run_0j.py`,
`analysis/scripts/fix_clusterperm.py`. Output: `analysis/results/0j_*.txt`.

### STUDY first (the method question, settled before the test was run)
Brenner H, Blettner M. "Controlling for continuous confounders in epidemiologic
research." *Epidemiology* 1997;8(4):429-34. PMID 9209859. `[fetched]`, abstract
retrieved verbatim this session:

> "…inclusion of the confounder as a single linear term often provides
> satisfactory control for confounding even in situations in which the model
> assumptions are clearly violated. In contrast, categorization of the
> confounder may often lead to serious residual confounding **if the number of
> categories is small**."

This is why the covariate-adjusted logistic was treated as the REFERENCE and
decile matching as the SUSPECT, rather than the reverse. It corrects the
inherited framing, in which decile matching had been chosen because there is no
numpy on this machine — a tooling constraint that had silently become a
methodological choice (SESSION_HANDOFF §3b).

### REPRODUCTION CHECK, run before anything was allowed to be overturned
`run_0j.py` reproduces the prior session's recorded decile figures exactly,
without being fitted to them:

```
recorded (prior session)  multi 1.54%   size-matched single 1.02% +/- 0.14   = 1.51x
reproduced (this session) multi 1.54%   size-matched single 1.02% +/- 0.12   = 1.51x
```
Unit construction is copied verbatim from `run_0i.py`, so 0i and 0j are
comparable by construction.

### TEST 1 — the effect does NOT decay as strata refine
```
strata      multi   matched single      ratio   mean LOC multi / control
K=10        1.54%   1.02% +/-0.12       1.51x        59 / 55
K=20        1.54%   1.08% +/-0.13       1.43x        59 / 58
K=50        1.54%   1.05% +/-0.12       1.47x        59 / 60
K=100       1.54%   1.00% +/-0.12       1.53x        59 / 60
K=200       1.54%   1.01% +/-0.11       1.52x        59 / 60
exact LOC   1.21%   0.92% +/-0.11       1.31x        47 / 47   (207 multi unmatchable)
```
K=500 (1.83x) and K=1000 (1.91x) are NOT evidence of a growing effect and must
not be quoted: at K=1000 the median multi unit has only 7 distinct single-tool
controls in its stratum and 16.8% have fewer than 5, so the same few controls
are resampled and the ratio moves for reasons unrelated to size. Reported here
so the rise is not later mistaken for signal.

### THE HYPOTHESISED MECHANISM IS REFUTED, NOT MERELY UNCONFIRMED
The prior session's stated reason for doubting the 1.5x was that "decile
matching leaves large residual size variation within strata on a heavily skewed
distribution." Measured directly:
```
K=10   mean LOC multi 59.4 vs available controls 54.9   imbalance +4.4 LOC (+8.1%)
K=50   mean LOC multi 59.4 vs available controls 59.5   imbalance -0.2 LOC (-0.3%)
K=200  mean LOC multi 59.4 vs available controls 60.1   imbalance -0.7 LOC (-1.2%)
```
Deciles carried an +8% size imbalance favouring the multi group; it is gone by
K=50. If residual size variation were driving the result, the ratio would fall
as that imbalance vanished. It does not — it is 1.51x at K=10 and 1.52x at
K=200. **Deciles were adequate here.** Brenner & Blettner's warning is about
what CAN happen with few categories; on this variable and this contrast, it did
not.

### WHY 0i AND THE MATCHED TEST APPEARED TO DISAGREE — DIFFERENT ESTIMANDS
This is the substantive correction, and it is a correction to the HANDOFF's
framing of 0j, not to the measurement.

0i fitted `n_tools` as a **single linear slope** (b=+0.057, p=0.582). The
matched test is a **binary multi(n>1) vs single(n=1)** contrast. Those are not
the same quantity. Fitting the MATCHING contrast with the continuous covariate:
```
multi alone                    b=+0.9927  p=1.9e-08   OR=2.70   (= the uncontrolled 2.7x)
multi + log(LOC)               b=+0.3294  p=0.076     OR=1.39   <-- direct analogue
multi + log(LOC) + log(LOC)^2  b=+0.3045  p=0.100     OR=1.36
```
OR=1.39 under continuous adjustment against 1.47-1.52x under fine matching:
**the two methods agree on magnitude.** They differed only because the two
numbers being compared were answering different questions.

### 0i's NULL WAS A FUNCTIONAL-FORM ARTIFACT
The HANDOFF pre-registered this branch: "If it HOLDS at 200 strata, the
logistic's linear-in-n_tools specification is the suspect instead." It held, so
the specification was tested. `n_tools` as a factor + log(LOC):
```
n_tools=1:  9,387 units,  54 vuln (0.58%)   reference
n_tools=2:  4,017 units,  57 vuln (1.42%)   b=+0.384  p=0.051   OR=1.47
n_tools=3:  1,045 units,  20 vuln (1.91%)   b=+0.303  p=0.273   OR=1.35
n_tools>=4:   207 units,   4 vuln (1.93%)   b=-0.394  p=0.478   OR=0.67
log(LOC)                                    b=+1.040  p<1e-30   OR=2.83
```
Levels 5 and 6 (31 and 4 units, ZERO vulnerable) are perfect separation — the
6-level factor has a singular Hessian and no standard errors exist. Collapsing
to 1/2/3/>=4 is forced by the data, not chosen.

**Essentially all of the effect is the 1 -> 2 step; the response is flat at 3
and negative above.** A single linear slope averages a real first step against a
flat-to-falling tail and returns ~0. So 0i's p=0.582 is an artifact of the
functional form, not an absence of signal. **0i's headline finding — that the
signal is not ORDERABLE under an effort budget — is untouched by this** and
still stands; what is corrected is only the inference that `n_tools` carries no
precision signal at all.

### !! THE p<0.0001 IS NOT SUPPORTABLE — THIS IS WHAT THE README GETS WRONG !!
The recorded p<0.0001 came from `P(size-matched control >= multi)`, which holds
the multi group's own 81/5,269 **FIXED** and resamples only the controls. Both
arms are random samples, so that statistic ignores sampling variability in the
numerator population and is anti-conservative by orders of magnitude.

Replaced with tests that vary both arms:
```
                                            K=10      K=50      K=200
two-proportion z (both groups random)      p=0.054   p=0.051   p=0.041
within-stratum label permutation           p=0.030   p=0.058   p=0.035
logistic multi + log(LOC)                            p=0.076
```
**The honest p is ~0.03-0.08, not <0.0001.** The effect is marginal, not
overwhelming. This error is independent of the strata question and would have
been present at any K.

### CLUSTERING — checked, because 81 events across 9 projects is not 81 draws
```
project     multi n   m.rate   single n   s.rate   raw ratio
binutils        426    4.69%        906    2.10%     2.24x
ffmpeg          872    0.46%      1,774    0.28%     1.63x
libpng           10   10.00%         64    6.25%     1.60x
libtiff          39   10.26%         89    4.49%     2.28x
libxml2         410    3.90%        752    0.40%     9.78x
openssl       1,197    1.25%      2,133    0.33%     3.82x
php           2,025    0.40%      2,641    0.08%     5.22x
poppler          78    5.13%        606    1.65%     3.11x
sqlite3         212    4.25%        422    0.00%      inf
```
**The direction is consistent in all 9 of 9 projects.** Leave-one-project-out
(K=50) gives 1.25x-1.61x, so no single project carries it.

Cluster permutation, permuting the multi/single label within (project x size
stratum) cells and computing the statistic over INFORMATIVE (mixed) cells only —
pure cells carry no information about the contrast and letting them contribute a
fixed offset would narrow the null:
```
K=10    84 informative cells, 99.6% of units   p=0.0000  (0/4000)
K=50   330 informative cells, 97.0% of units   p=0.0008  (3/4000)
K=200  708 informative cells, 94.1% of units   p=0.0022  (9/4000)
```
Conditioning on project SHARPENS the result rather than weakening it, because
between-project base rates vary enormously (php 0.08% to libpng 6.25%) and
removing that heterogeneity removes noise, not signal.

**But the generalisation bound is wide.** Cluster bootstrap resampling the 9
PROJECTS with replacement — the honest interval if the project, not the
function, is the sampling unit:
```
matched ratio 95% CI over projects: [0.99x, 2.58x]   median 1.51x
fraction of project-bootstraps with ratio <= 1.0: 0.033
```
Within this corpus the effect is solid; across a different sample of nine
projects, no-effect is barely inside the interval. Nine clusters is few.

### WHAT THE README MAY AND MAY NOT SAY
MAY: multi-tool functions are ~1.5x more likely to contain a real CVE than
size-matched single-tool functions. Point estimate stable at 1.43x-1.53x across
every stratification from 10 to 200, 1.39x under continuous covariate
adjustment, direction consistent in 9/9 projects.

MAY NOT:
1. **`p < 0.0001`.** Withdrawn. The honest figure is p~0.03-0.08 unclustered
   (p~0.001 clustered on project), with a project-bootstrap 95% CI of
   [0.99x, 2.58x].
2. **Any suggestion that MORE agreement means MORE signal.** The data support
   ">=2 tools beats 1 tool" and nothing beyond it: the response is flat at 3
   tools and point-estimate NEGATIVE at >=4 (OR 0.67). "Independent tools agree"
   as a graded confidence signal is NOT supported by this result.

### The pattern SESSION_HANDOFF §3a predicted, with the sign reversed
Five claims died this session-series when a better-matched control was applied,
and the handoff expected a sixth. It did not happen: refining the control left
the point estimate where it was. What was wrong was never the comparator — it
was the **significance test**, which nobody had re-examined because the effect
size kept being the thing under suspicion. The lesson generalises: check the
test as well as the control.

## 0h IMPLEMENTED (2026-07-26) — per-run size-correlation disclosure, GATED

Tier: `[self-tested]` implementation; the GATE THRESHOLD is `[externally-grounded]`
(calibrated on the Lipp artifact's real file-level distribution). Method choices
are `[fetched]`. Disclosure only — it never filters, suppresses, or reweights.

### STUDY, and one citation that did not survive checking
- Ruscio J. (2008), "Constructing Confidence Intervals for Spearman's Rank
  Correlation with Ordinal Data: A Simulation Study Comparing Analytic and
  Bootstrap Methods", *J. Modern Applied Statistical Methods* 7(2), art. 7,
  DOI 10.22237/jmasm/1225512360. `[fetched]`, abstract verbatim: "Research shows
  good probability coverage using analytic confidence intervals (CIs) for
  Spearman's rho with continuous data, but poorer coverage with ordinal data. A
  simulation study examining the latter case replicated prior results and
  revealed that coverage of bootstrap CIs was usually as good or better than
  coverage of analytic CIs." → bootstrap percentile CI, not analytic.
- Ties: the exact permutation distribution and the asymptotic approximation both
  assume untied ranks, and the asymptotic standard error uses the no-tie
  variance. n_tools is integer-valued and heavily tied by construction, so the
  p-value is a PERMUTATION p, and rho is tie-corrected (Pearson on midranks).
- **arXiv:2602.07842 §D.4 DOES NOT EXIST and does not support this design.**
  That ID is "Evaluating and Calibrating LLM Confidence on Questions with
  Multiple Correct Answers" (Wang et al., 2026); its Appendix D has one
  subsection, D.1, and the paper does not discuss tied ranks, dispersion checks
  or degenerate variables. Recorded so the citation is not propagated.

### The gate threshold is MEASURED, not chosen
`analysis/scripts/calibrate_0h.py`, output `analysis/results/0h_gate_calibration.txt`.
Parent population: Lipp file-level units, Spearman(n_tools, LOC) = **+0.629** —
a strong correlation, so a gate that cannot detect it cannot detect anything.
Subsampling at realistic run sizes, power of a permutation test at alpha=0.05:

```
non-modal m   1     2     3     4     5     6     8    10    12    15    20
power       0.19  0.41  0.48  0.57  0.67  0.72  0.85  0.95  0.95  0.98  0.99
```
**m* = 8**, and it is stable: run size 40 → 8, 80 → 8, 120 → 6, 300 → 8. Below 8
non-modal units the check cannot detect even a strong size correlation, so no
coefficient is reported. alpha=.05/power=.80 are conventions; m* is measured.

### !! THE OBVIOUS SIZE PROXY IS CIRCULAR — CAUGHT BEFORE SHIPPING !!
The first implementation used `max(startLine)` per file as a size proxy, since
SARIF carries no file length. **That proxy manufactures the correlation it is
meant to detect.** Measured on real zlib output:
```
files flagged by 1 tool : n=15  median findings= 2  median max-line= 58
files flagged by 2 tools: n=44  median findings=16  median max-line=457
```
A maximum over reported lines is a higher ORDER STATISTIC — more findings means
a higher max, independent of file length. Findings rise with tool count, so the
proxy rises with n_tools mechanically.

CONSEQUENCE, measured on the same real run:
```
with the circular proxy : rho=+0.402  CI[+0.128,+0.624]  p=0.0025  -> WOULD HAVE WARNED
with real file lengths  : rho=+0.232  CI[-0.045,+0.459]  p=0.0860  -> correctly silent
```
**The circular proxy would have fired a FALSE size-correlation alarm on a real
run.** The shipped code therefore reads real file lengths from disk
(`AUDIT_SOURCE_ROOT` to resolve paths) and reports NOT APPLICABLE, naming the
circularity, when it cannot. It never infers size from SARIF alone.

This is HANDOFF §8 rule 10 applied to our own feature, exactly as intended: a
number derived from what SARIF happened to carry was a claim about SARIF, not
about the code.

### Behaviour
- Unit = FILE; variable = distinct ENGINES flagging that file. **Not** the
  per-finding `n_tools` in `ranked` — a file can draw two tools with zero merged
  findings, and conflating the two is the denominator error this project keeps
  correcting. The JSON spells the variable out.
- Gate order: ≥3 units → ≥2 distinct n_tools values (else rank variance is zero
  and rho is UNDEFINED, not merely weak) → size variation present → ≥8 non-modal
  units. Any failure returns `applicable: false` with a `reason` and NO
  coefficient.
- When it applies: tie-corrected rho, 2,000-sample bootstrap percentile CI,
  2,000-permutation p, and an interpretation sentence. Seeded, so the same input
  gives the same interval.
- Surfaced in JSON (`size_correlation`), CLI, and HTML, beside the existing
  lineage/path warnings.
- A quiet result is explicitly NOT clearance: the wording says so.

### Regression tests (in `verify_cross_tool_key.py`; harness 67 → 84 checks)
concentrated n_tools → NOT APPLICABLE with no coefficient; genuine spread + size
correlation → warns, with CI and permutation p; genuine spread, no correlation →
applies and stays silent; the m*=8 boundary in both directions; no readable
sizes → refuses the circular proxy and names why; existing fixtures do not start
warning; output deterministic across runs.

## 0c OPTION (a) IMPLEMENTED (2026-07-26) — deterministic suffix linkage,
## cardinality-1 guard. Diagnostic ran FIRST and authorised building it.

Tier: `[self-tested]` implementation, verified against `[externally-grounded]`
real scanner output on three corpora. Framing is `[fetched]` record-linkage
literature.

### FRAMING — this is RECORD LINKAGE, using the field's vocabulary
- **Deterministic linkage**: matching on exact predefined rules. Splink (MoJ)
  `[fetched]`, verbatim: "✅ Capable of achieving high precision (few False
  Positives)" / "❌ Prone to Low recall (False Negatives)".
- **Probabilistic linkage (Fellegi-Sunter)** is the alternative: it weighs
  partial agreement, assigning weights from m- and u-probabilities so a
  near-match can contribute.
- **We choose deterministic DELIBERATELY**, and the price is recorded with the
  choice: **it will miss real matches.** Correct here because the error costs
  are asymmetric — a false merge silently inflates `n_tools`, the signal the
  whole tool rests on, while a missed merge costs only a merge. Consistent with
  every other uncertainty in this codebase resolving to NO-MERGE.
- The uniqueness requirement is a **BLOCKING KEY with a CARDINALITY-1
  CONSTRAINT**: the path suffix is the key, "exactly one path per side" is the
  constraint.
- HONESTY NOTE on one citation, per rule 8a: Splink documents the
  precision/recall trade but does **not** discuss loosening rules raising false
  positives. That part of the framing is supported by the general linkage
  literature (relaxations proposed to absorb formatting variation), not by
  Splink, and is not attributed to it.

### DIAGNOSTIC FIRST — block-size distribution, which decided whether to build
`analysis/scripts/blocking_diagnostic.py` → `analysis/results/0c_blocking_diagnostic.txt`.
Standard practice is to observe block sizes as criteria change. Run on the RAW
scanner output (not the hand-aligned copies, which are the thing being replaced):

```
corpus / side          paths   non-singleton basename blocks   at depth >= 2
Struts SpotBugs          432   4  (0.9%)                       0  (0.0%)
Struts semgrep(raw)        1   0                               0
OWASP  SpotBugs        2,755   0  (0.0%)                       0  (0.0%)
OWASP  semgrep(raw)    1,515   0  (0.0%)                       0  (0.0%)
zlib   flawfinder         44   1  (2.3%, `zfstream.h`)         0  (0.0%)
zlib   cppcheck           59   1  (1.7%)                       0  (0.0%)

exact path match today:  Struts 0 · OWASP 0 · zlib 44
both-unique suffix matches: Struts 1 · OWASP 1,515 · zlib 44
```
**VERDICT: the guard is NOT too strict.** Basename ALONE is unsafe — real
collisions exist on two of three corpora — but the segment-aligned suffix plus
cardinality-1 permits 1,515 matches on OWASP and 1 on Struts while refusing only
a handful of genuinely ambiguous names. That is what authorised building it.

### VERIFICATION ON REAL DATA — linkage reproduces hand-alignment EXACTLY
```
                        merges   linkage  paths        merges via
                                 active   reconciled   suffix match
Struts  hand-aligned         1   False             0             0
Struts  RAW                  1   True              1             1
OWASP   hand-aligned     1,427   False             0             0
OWASP   RAW              1,427   True         1,515         1,427
zlib                         0   False             0             0   (1 refused)
```
Both RAW runs go from **0 merges to exactly the hand-aligned count**. That is
the strongest available check: the feature reproduces what a human did by hand,
to the merge.

CORRECTION to the brief: Struts hand-aligned is **1** merge, not 2. (2 was
zlib's figure in an earlier configuration.) The target was set from measurement,
not from the recollection.

### Behaviour
- Basename blocking → segment-aligned suffix relation (`a/util/Config.java`
  never matches `b/utilConfig.java`) → cardinality-1 on BOTH sides.
- Ambiguity resolves to **NO-MERGE**, and is **counted and disclosed**, never
  silently dropped. zlib: `zfstream.h` refused, 2 paths each side.
- Suffix-assisted merges reported **separately** (`suffix_linkage`), as
  range-containment is, because a merge needing path reconciliation rests on
  more inference than one where both tools already agreed.
- The output states its own known cost: deterministic matching is low-recall by
  construction.
- Surfaced in JSON, CLI and HTML.
- **The root-mismatch warning was AMENDED.** It previously asserted the count
  "will be ZERO for that reason alone"; once linkage rescues the pair that is
  false, so the text now says linkage reconciled it and the configuration is
  still worth fixing. A warning contradicting the merge count beside it would be
  its own honesty failure. When linkage does NOT fire, the original wording is
  retained in full — verified.

### THE NAMED TRAP, and why it was not entered
The literature documents the pattern: formatting differences cause false
negatives → teams relax the rules → false positives rise. The instruction was to
stop rather than loosen if the guard proved too strict. **It did not prove too
strict**, so nothing was loosened. The guard is unchanged from its strictest
form: unique on both sides or no merge. If a future corpus shows the guard
blocking useful matches, the recorded decision is to accept the loss or move to
an explicitly probabilistic layer with its own disclosure — NOT to relax the
cardinality constraint.

### Regression tests (harness 84 → 98 checks)
suffix-related paths merge and are attributed to the linkage layer; two files
sharing a basename in different directories do NOT merge and the ambiguity is
disclosed by name; substring-but-not-segment-aligned paths do not merge;
identical paths still merge with linkage inactive; existing fixtures do not
activate it; the amended warning is asserted in both directions.

## 3e IMPLEMENTED (2026-07-26) — hierarchy-aware CWE resolution.
## CORRECT, TESTED, AND CURRENTLY INERT ON EVERY CORPUS ON DISK.

Tier: `[self-tested]` implementation over a `[fetched]` CC-BY-4.0 hierarchy
(Lipp `cwe_mapping/buckets.json`, 162 CWEs).

### STUDY, and what checking the citations changed
- **V2W-BERT** (Das et al., arXiv:2102.11498) `[fetched]`, verbatim: "According
  to the MITRE classification, a CWE can have multiple parents and multiple
  children"; "Some CWEs have multiple parents in different levels and are
  counted twice"; and "the hierarchical CWE relations available in NVD omit some
  of the parent-child relations available in MITRE." All three of the supplied
  claims about multiple parents and NVD omission are CONFIRMED.
- **TreeVul** is real — Pan, Bao, Xia, Lo & Li, *Fine-grained Commit-level
  Vulnerability Type Prediction by CWE Tree Structure*, ICSE'23 — but the
  supplied arXiv ID ("arXiv:2302") does not resolve, and the PeerOf claim could
  NOT be verified from the paper text (extraction reached 118 KB and contains
  neither "PeerOf" nor "ChildOf"). Per rule 8a: recorded as UNVERIFIED, not
  cited as support.
- **It did not need to be.** The constraint is satisfied by the artifact, which
  is a stronger check than the citation would have been: `buckets.json` carries
  exactly `child_of`, `parent_of` and `description` — measured, no PeerOf, no
  CanPrecede. Non-hierarchical relations cannot leak in because they are not
  there. Asserted in the harness so a future hierarchy swap cannot introduce
  them silently.

### WORLD-STATE FACTS, measured not assumed
```
entries                                     162
`child_of` value type                       str, ALWAYS  (never a list)
CWEs with MULTIPLE parents in our copy      0 of 162
CWE-328 child_of CWE-327                    present  -> 327+328 resolves to hash
CWE-22 -> CWE-664 ; CWE-89 -> CWE-707       different pillars -> None
CWE-209, CWE-211, CWE-326                   ABSENT (confirms the recorded gap)
```
**The ambiguity case is UNREACHABLE FROM THIS FILE.** It is implemented and
tested anyway, with an injected hierarchy, because our copy is a simplification
of MITRE and any replacement may be multi-parent. An untested branch guarding
against a false merge is worse than no branch.

### THE RULE
Ancestor-related CWEs resolve to the MOST SPECIFIC; everything else resolves to
None. "Everything else" is three distinct situations that deliberately share one
answer: genuinely unrelated CWEs; a non-unique "most specific" (two maximal
elements — never an arbitrary pick, which is the first-match-wins error the
multi-class guard was built to fix); and a connecting edge MISSING from our copy.

### !! WHY IT IS SAFE UNDER AN INCOMPLETE HIERARCHY — AND WHY THAT CAN INVERT !!
Our copy is 162 CWEs, C-focused, and measurably missing entries. So "no ancestor
path between A and B" is **ambiguous between "genuinely unrelated" and "the edge
is absent from our copy."** Both resolve to None, and that is safe because a
missing edge then costs a MERGE rather than manufacturing one.

**That safety is a property of the rule's DIRECTION, not of the data.** Any
future change making "no path found" resolve to anything other than None — a
default class, a nearest common ancestor, a guess — silently converts every
missing edge into a potential FALSE MERGE, and the hierarchy's incompleteness
stops being harmless the moment the direction flips. Same shape as the SARIF
Appendix D rule (HANDOFF §8 rule 10): absence in an incomplete artifact is
evidence about the artifact, not about the world. Regression-tested both ways.

### COVERAGE — and the honest headline
Prose path, rules whose text yields more than one CLASS:
```
corpus / tool      multi-class rules   findings RECOVERED   still None
OWASP  SpotBugs                    3                  113           9
Struts SpotBugs                    1                    0           5
OWASP  semgrep                     0                    0           0
zlib   flawfinder / cppcheck       0                    0           0
```
113 + 9 = **122**, reconciling exactly with the figure 3e was filed against.
The 113 are the WEAK_MESSAGE_DIGEST_MD5/_SHA1 (CWE-327 + CWE-328) case; the 9
are INFORMATION_EXPOSURE (CWE-22/89/209/211), which is genuine ambiguity and
CORRECTLY stays None. Of the still-None findings, 0 are blocked by a missing
hierarchy edge — they are all genuinely unrelated.

### **BUT: END-TO-END EFFECT ON EVERY CORPUS ON DISK IS ZERO.**
Measured by running each corpus with the hierarchy loaded and again with it
emptied, and diffing the resolved-class distribution:
```
OWASP RAW   class distribution change: NONE
Struts RAW  class distribution change: NONE
zlib        class distribution change: NONE
merge counts: Struts 1->1, OWASP 1,427->1,427, zlib 0->0
```
**The 113 is a PROSE-PATH figure, not a shipped-path effect.** Every one of those
findings already had its class resolved by the SARIF `relationships` taxa, which
ingest consults FIRST — the WEAK_MESSAGE_DIGEST_MD5 rule declares taxon 328
alone, with no 327 to conflict with. So the prose branch is never reached for
them.

3e is therefore **correct, guarded, tested, and INERT on all available data.**
Its value is conditional and precisely bounded: it matters only for a tool that
emits NO taxa AND whose prose names several ancestor-related CWEs. That is
exactly what HANDOFF 3e predicted ("still WANTED for tools that emit NO taxa —
22 of SpotBugs' 77 rules, and semgrep — where prose scraping is the only
source"). **Do not report this as "recovers 113 findings" without the
qualifier**; on the shipped path today it recovers none.

### Regression tests (harness 98 -> 112 checks)
Both known cases on both paths (327/328 -> hash, 22/89 -> None); the hierarchy
file contains only child_of/parent_of; AMBIGUITY via injected siblings -> None;
chains of two and three -> most specific; a multi-parent diamond with a unique
maximal element still resolves; MISSING EDGE with an emptied hierarchy -> None
end-to-end; a cycle terminates rather than hanging; real fixtures unchanged.
One pre-existing test was INVERTED, not deleted: it asserted the 327/328 pair
resolves to None, which was the safe-not-right answer 3e exists to correct.

## 0f REGISTRY ARM (2026-07-26) — prevalence estimation under incomplete detection
> **[NUMBERS SUPERSEDED — see "0f REGISTRY ARM ADDENDUM" at the end of this
> file. S1 was UNDERCOUNTED (73 -> 131) because most declarations point at a
> GitHub repo rather than a docs host, so the union moves 105 -> 158 and the
> recall denominator used below was wrong. The METHOD and the rewriting finding
> stand. Do not quote 13.04%, 18.75%, 30.1% or N-hat 157 from the section
> below.]**
## ONE REGISTRY (semgrep). NOT the ecosystem. Say so wherever the number appears.

Tier: `[self-tested]` analysis over `[externally-grounded]` inputs (semgrep's live
registry; FindSecBugs 1.14.0 plugin jar). Methodology `[fetched]`.
Pre-registration was committed BEFORE computing (commit `2e00ba2`).

### STUDY
Khosravani & Mockus, *Detecting AI Coding Agents in Open Source: A Validated
Multi-Method Census of 180 Million Repositories*, arXiv:2606.24429 `[fetched]`,
verbatim:
> "These multi-method counts are relative-recall improvements over single-method
> baselines, not absolute recall estimates."
> "The true total ... is bounded below by our multi-method union but may be
> larger if additional detection signals remain unprobed."
> "absolute recall is unknown"

**One nuance not in the brief and carried through the whole design:** their 30x
figure compares ONE SIGNAL against THEIR UNION — not detection against reality.
Every undercount factor below inherits that limit.

Bomfather, arXiv:2503.02097 `[fetched]`: "A gap remains between declared and
actual dependencies." The declared-vs-actual gap is independently named in
supply-chain work; a declaration is a lower bound on the fact.

### RESULTS — 560 distinct registry rules, 9 packs
```
1. PER-SIGNAL
   S1 declared source-rule-url        73/560 = 13.04%
   S2 attribution fields              10/560 =  1.79%
   S3 rule-id name match              48/560 =  8.57%
   S4 description similarity           0/560 =  0.00%
   S5 CWE overlap [WEAK, excluded]   415/560 = 74.11%

2. MULTI-SIGNAL UNION (S1..S4) = 105/560 = 18.75%   <- improved lower bound
   (with the weak S5 admitted it would read 76.07% — which is why S5 was
    pre-registered as excluded, not judged afterwards)

3. UNDERCOUNT FACTOR = 105/73 = 1.4x, RELATIVE recall between signals only.
   77.1% of the union (81 of 105) is found by EXACTLY ONE signal — the tail is
   fragile, and a single-signal study would have missed 32 of 105.
```

### THE SUBSTANTIVE FINDING: S4 = 0 IS REAL, AND IT IS THE MECHANISM
S4 returning exactly zero was checked as a possible instrument failure before
being reported. It is not one — messages parse, tokens extract, and the observed
best Jaccard tops out at 0.359 against a pre-registered threshold of 0.50.

Because S1 is a GROUND-TRUTH SUBSET (a rule declaring FindSecBugs as its source
IS derived, by its own admission), each other signal's RECALL can be validated:
```
recall on the 73 self-declared-derived rules
  S2 attribution        4/73 =  5.5%
  S3 rule-id match     22/73 = 30.1%
  S4 text similarity    0/73 =  0.0%
best Jaccard of those 73 against their own FindSecBugs original:
  median 0.101, max 0.359
```
**Ported rules are rewritten.** Text similarity is not a weak detector of
derivation here — it is a NULL one. That is not a limitation of the measurement,
it is the mechanism by which a ported rule comes to look independently authored.

POST-HOC SENSITIVITY, reported for transparency and NOT substituted for the
pre-registered threshold: 0.50 -> 0, 0.40 -> 0, 0.30 -> 2, 0.20 -> 5,
0.10 -> 237 (42% of the registry, i.e. noise). No threshold rescues S4; the
pre-registered 0.50 stands and was not retuned to the result.

### ADDITION, NOT PRE-REGISTERED — capture-recapture rather than a bare bound
Available only because S1 turned out to be ground truth. Treating declaration
(S1) and rule-id retention (S3) as two detection passes, Chapman-corrected
Lincoln-Petersen:
```
n1 = 73   n2 = 48   overlap = 22
N-hat = 157  (SE 19)  = 28.0% of 560 rules
vs the multi-signal union lower bound of 105 (18.8%)
```
ASSUMPTIONS AND THEIR DIRECTION: capture-recapture assumes independent passes and
homogeneous detectability. Both are doubtful here, in a KNOWABLE direction — a
faithful port is more likely to BOTH declare its source AND keep the upstream
name, so S1 and S3 are positively correlated, which inflates the overlap and
DEPRESSES N-hat. So 157 is more likely an under-estimate than an over-estimate.
It raises the floor; it does not establish a ceiling.

### WHAT REMAINS UNDETECTABLE — the floor of what is knowable
A rule ported but undeclared, renamed AND reworded is silent to all five
signals. No format requires disclosure of derivation, so that population cannot
be bounded from artifacts at all. Two further ceilings, both pre-registered:
the upstream reference set is FindSecBugs ONLY (semgrep's FAQ names ESLint,
RuboCop and Bandit besides, all invisible to S3/S4), and 560 rules is ONE
REGISTRY.

**Therefore a LOW number here is UNINFORMATIVE, not clearance.** Every signal is
a positive marker; absence of a marker is not absence of derivation.

### THE CLAIM THIS SUPPORTS, STATED CAREFULLY
Supported by the measurement:
> In one registry, at least 18.8% of rules carry a detectable marker of
> derivation from another tool, and a capture-recapture estimate puts it near
> 28%. Among rules KNOWN to be derived, the markers that do not depend on
> voluntary disclosure recover at most 30% of them, and textual similarity
> recovers none.

The consequence, which is the part with reach beyond this project:
> **If ported rules cannot reliably be distinguished from independently authored
> ones, then a consumer of multi-tool consensus has no way to assess the
> independence their consensus assumes.** The information needed is not merely
> absent from SARIF — it is absent from the rules themselves once ported rules
> are rewritten, which is the normal case.

NOT supported, and must not be claimed: that ~28% of static-analysis rules
generally are ported; that other registries behave like this one; or that a
specific consensus finding is contaminated. This is one registry, one upstream
reference set, and an estimate with stated assumptions.

## 0f REGISTRY ARM — ADDENDUM (2026-07-26). Corrects the numbers above.
## Script: `analysis/scripts/rule_provenance_registry_addendum.py`

### CORRECTION 1 — S1 undercounted DECLARED provenance by 44%
The first run matched upstream *documentation hosts*. Most declarations point at
a GitHub **repo** instead, so they were missed. All declared upstream tools:
```
FindSecBugs             44   ( 7.86%)
Bandit                  44   ( 7.86%)
Brakeman                19   ( 3.39%)
gosec                   15   ( 2.68%)
eslint-plugin-security   6   ( 1.07%)
gixy                     2   ( 0.36%)
hadolint                 1   ( 0.18%)
                       ---
S1 first reported       73/560 = 13.04%
S1 CORRECTED           131/560 = 23.39%      (+58 rules)
union(S1..S4)          158/560 = 28.21%      (was 105 = 18.75%)
```
**Semgrep's FAQ named four upstreams; the registry declares seven.** FindSecBugs
is only a third of the declared population.

### CORRECTION 2 — the recall denominator was wrong, in the direction that
### FLATTERED the failure of the undeclared-detection signals
S3/S4 compare against a **FindSecBugs** reference set only. Rules declaring
Bandit, Brakeman, gosec, eslint-plugin-security, gixy or hadolint could never
match, so scoring them as misses overstates the signals' failure. Fair
denominator = the FindSecBugs-declared subset.
```
FindSecBugs-declared (testable)   44
other upstreams (NEVER TESTED)    87   = 66.4% of the declared set

                         recall on FSB-declared
S2 attribution               2/44 =  4.5%
S3 rule-id match            22/44 = 50.0%     (was reported as 30.1%)
S4 text similarity           0/44 =  0.0%     (unchanged)
```
**Two thirds of the declared population was never testable by S3/S4.** That is
now stated rather than silently absorbed into a recall figure.

**THE REWRITING FINDING IS UNAFFECTED.** S4 was always measured against the
FindSecBugs text; it now simply has the right denominator. 0 of 44 rules that
declare FindSecBugs as their source retain enough of its wording to be detected.

### CORRECTION 3 — capture-recapture must run on a COHERENT population
The earlier N-hat=157 paired n1=73 (mixed upstreams) with n2=48 (FindSecBugs
name-matching). Those address different populations, so the estimate was
malformed. Restricted to rules derived FROM FINDSECBUGS:
```
n1 (declares FSB) = 44   n2 (FSB name match) = 48   overlap = 22
Chapman N-hat = 95
BOOTSTRAP 95% CI (5,000 resamples) = [83, 117]   SD 9   CV 10%
```
Bootstrap quoted in preference to the asymptotic SE, which the literature
reports "often perform[s] poorly with small sample sizes". CV = 10%, inside the
conventional 20% threshold, so the precision is acceptable — checked, not
assumed.

So for the ONE upstream with a reference set: **44 declared, ~95 estimated
actually derived — a 2.2x undercount of declaration.** Whether that factor
applies to the other 87 declared rules is **UNTESTED and must not be
extrapolated**; no reference sets exist here for those six upstreams.

### THE THREE INDEPENDENT NEGATIVE BIASES — all point the same way
Verified individually rather than taken as one caveat:

1. **Positive dependence between sources → UNDERestimation.** Bonander et al.,
   *Epidemiology* 2024 (PMC11022997) `[fetched]`, verbatim: "positive
   ascertainment covariance leads to an underestimation of outcome
   probabilities, whereas negative ascertainment covariance leads to
   overestimation", citing Brenner (1995), *Use and limitations of the
   capture–recapture method in disease monitoring with two dependent sources*.
   HERE: a faithful port is more likely to both declare its source and keep the
   name. Positive dependence.

2. **Heterogeneous capture probability → UNDERestimation, SEPARATELY.**
   `[fetched]`: "Heterogeneous capture probabilities cause underestimation of
   population size"; failure to account for it "has long been known to cause
   substantial bias". On-point citation: Mao, *Petersen estimator, Chapman
   adjustment, list effects, and heterogeneity*, Biometrics 2017.
   HERE, AND NOT PREVIOUSLY NOTED: a faithful port that keeps its upstream name
   is easy for BOTH passes to catch; a rewritten port is hard for both. Capture
   probability is strongly heterogeneous across the population, and this
   depresses N-hat independently of the S1/S3 correlation in (1).

3. **Chapman's own negative bias under violated conditions.** `[fetched]`: "when
   certain conditions are violated, the Chapman estimator can experience
   negative bias and provides a lower bound for the true population size, with
   this underestimation bias being mainly relevant for population sizes below
   50." **This is the one BOUNDED component**: N-hat = 95 is above 50, so this
   term is likely minor here.

### CONSEQUENCE — REPORT TWO FLOORS, NOT AN ESTIMATE AND AN INTERVAL
```
FLOOR 1 (most conservative)  union of all signals   158/560 = 28.2%
FLOOR 2 (less conservative)  Chapman, FSB only      95 FSB-derived [83, 117]
CEILING                      UNBOUNDED by this method
```
All three biases push down; none pushes up. The bootstrap interval [83, 117]
quantifies **sampling** uncertainty only — it does not cover any of the three
structural biases, and must not be read as a range for the true value.

### WHAT THIS DOES AND DOES NOT CHANGE
UNCHANGED: the rewriting mechanism (text similarity recovers 0 of 44 known
FindSecBugs-derived rules); that a low number is uninformative rather than
clearance; that this is ONE REGISTRY.
STRENGTHENED: declared provenance is 23.4% not 13.0%, and seven upstreams appear
where semgrep's own documentation names four — so the practice is broader than
the vendor's own description of it.

## ITEM 2 EVALUATED AND CLOSED (2026-07-26) — function-level matching does not
## earn a boundary-extraction dependency

Pre-registered in commit `2f0bd52` BEFORE computing. Script
`analysis/scripts/eval_function_level.py`, output
`analysis/results/item2_function_level.txt`. Run on Lipp's `functions.json`
ground-truth boundaries, so **no parser was introduced**; function-level matching
was implemented as a pre-ingest location canonicalisation, leaving `audit.py`
unmodified.

### Result 1 — merges rise, but only slightly, and the reason matters
```
                  raw     unique    cross-tool merges    n_tools
LINE level      98,417    95,195    3,009  (3.16%)      {1:92186, 2:2944, 3:65}
FUNCTION level  98,417    67,280    3,155  (4.69%)      {1:64125, 2:2797, 3:335, 4:20, 5:3}
                                    1.0x
```
Deeper agreement does appear — n_tools of 4 and 5 exist at function level and
did not at line level — but total merged findings move only **+4.9%**.

### !! RECONCILIATION with the recorded 6.4x granularity gain — NOT a conflict !!
The +4.9% appeared to contradict "THE DECISIVE MEASUREMENT" above (1,169 →
7,514 cross-methodology pairs, 6.4x). Checked rather than left standing, per
§8 rule 11:
```
CO-OCCURRENCE (tools sharing a unit, CWE class IGNORED)
  line level       1,507
  function level   5,269    (3.5x)   <- reproduces the granularity gain in kind

OF those 5,269, all findings agreeing on CWE?
  class-agreeing        410  =  7.8%
  class-DISAGREEING   4,859  = 92.2%
```
**The two measurements are different quantities and both are right.**
Granularity DOES restore co-location — 3.5x, consistent in direction and order
with the recorded 6.4x (which counts cross-methodology *pairs*, a different
unit). Our pipeline then additionally requires the tools to **agree on what the
bug is**, and that requirement rejects **92.2%** of the recovered co-locations.

**This REFINES the §6.2 correction; it does not reverse it again.** "Diverse
tools do not co-locate" remains FALSE. What is true is narrower and was not
previously stated: *at function level they co-locate readily and then disagree
about the bug class 92% of the time.* Requiring class agreement is correct —
merging two different bugs in one function is a FALSE MERGE — so this is a cost
of a correct guard, not a defect.

### Result 2 — precision consistency check PASSES
```
multi 1.54%  single 0.58%  uncontrolled 2.67x
size-matched control 1.02%   ratio 1.51x
```
Identical to 0j's recorded 1.51x. This means the pipeline reproduces the
finding; it does not re-establish it.

### Result 3 — the deciding question: ranking still fails
```
ranker                        PofB@20     IFA   PMI@20
consensus (n_tools desc)        0.185     142    0.161
ManualUp (size asc)             0.185   1,746    0.602
size-only floor (desc)          0.185       2    0.022

consensus vs SIZE-MATCHED random: 0.185 vs 0.178 +/- 0.032, P(rand>=) = 0.447
```
Consensus does not beat size-matched random, does not beat ManualUp on PofB, and
its IFA is **0.01x** the size-only floor against a rule wanting ≥2x. Routing
through the real merge machinery changed nothing versus 0i's `found_by`-based
result.

### DECISION — against the rule fixed before computing: **CLOSE ITEM 2**
The pre-registered rule said to close if consensus fails to beat a size-matched
control **regardless of how far merge counts rise**, because observability that
does not become ranking cannot justify a dependency whose failure mode is false
merges. It failed. Item 2 closes.

**Same shape as Direction B:** yield improved, ranking did not follow. That is
now twice, and it is worth stating as a pattern rather than a coincidence —
mechanisms that recover more agreement have not once produced a better ordering
on this corpus.

### The parser question — REACHABLE BUT UNMEASURED, and now moot
`[fetched]` universal-ctags can emit function end lines (`--fields=+ne`; the
`end` field "indicates the line number of the end lines of the language object"),
so boundary extraction without a full parser is reachable. Its documented failure
mode: it follows only the first branch of a preprocessor conditional "because
following both branches would result in ambiguous syntax with unbalanced braces",
and where that fails it "falls back to relying upon a closing brace (`}`) in
column 1 as indicating the end of a block". **A wrong boundary assigns a finding
to the wrong function — a FALSE MERGE, the forbidden direction.** Unmeasured, and
item 2's closure means it stays that way. Not foreclosed; not needed.
