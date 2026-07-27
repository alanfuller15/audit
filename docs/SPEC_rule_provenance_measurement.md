# Rule provenance and the independence assumption — STUDY + pre-registered measurement

Item 0f follow-up. Written 2026-07-26. **STUDY completed; measurement
PRE-REGISTERED, NOT RUN. No guard is proposed or implemented** — the
measurement decides whether one is warranted, and the decision rule below is
fixed in advance so the result cannot select its own threshold.

---

## 1. THE QUESTION

The tool's entire premise is that agreement between *independent* tools is
evidence. The engine-lineage guard (item 0a) enforces independence at the
ENGINE level: SpotBugs and FindBugs are one engine under two names, so their
agreement is not counted twice.

Item 0f found a layer the guard does not reach. semgrep's
`unvalidated-redirect` rule declares, in its own metadata:

```
source-rule-url: https://find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT
```

semgrep and SpotBugs are genuinely different engines, so the guard correctly
lets them merge. But at the RULE level this is a rule agreeing with its own
ancestor — shared provenance, not independent corroboration. Two
implementations of the same rule have the same blind spot by construction.

**The unasked question: how much of the static-analysis ecosystem is ported
rules?** If rule porting is widespread, "independent tools" is a weaker notion
than the premise assumes, at a level *below* tool selection.

---

## 2. STUDY — what the literature actually contains

Search denominator: **6 queries, 4 fetches**, plus one local re-read of a
previously fetched paper. Negatives and empties reported as results.

### 2.1 Is rule porting between tools documented? YES — and by the vendor

`[fetched]` Semgrep's own FAQ (docs.semgrep.dev/faq/overview), verbatim:

> "Semgrep's registry includes rulesets **inspired by the rules of many popular
> linters and checkers, including ESLint, RuboCop, Bandit, and FindSecBugs**."

and

> "The Semgrep Registry can import rules from sources other than the
> `semgrep/semgrep-rules` repository, such as Trail of Bits. These rules have
> their own licenses."

**This materially widens 0f.** Our observation was FindSecBugs-specific and
looked like a quirk of one rule family. It is one instance of a *declared,
general practice* spanning at least four named upstream tools plus third-party
importers. The finding is not that semgrep borrowed from FindSecBugs; it is
that rule derivation is a normal, documented way registries are built.

### 2.2 Does the ensemble literature address SHARED PROVENANCE? NO — it
### addresses shared METHOD and measures correlated OUTCOMES

The classifier-ensemble diversity literature (Kuncheva & Whitaker's ten
diversity measures — Q statistic, correlation, disagreement, double-fault;
Tumer & Ghosh on error correlation; "A Unified Theory of Diversity in Ensemble
Learning", arXiv 2301.03962) is mature, but it models diversity as a property
of **outputs** or of **method**, and treats correlated error as something you
detect post hoc from labelled outcomes.

**Nothing found models shared PROVENANCE as a distinct cause.** This matters
because the two are not the same thing:

| mechanism | detectable how | our exposure |
|---|---|---|
| shared METHOD (both pattern-matchers) | outcome correlation, or by inspection | already known — HANDOFF §6.2 |
| shared PROVENANCE (rule B ported from rule A) | **only from rule metadata or history** | 0f, unquantified |

Convergent design and derivation produce the same outcome correlation but are
different facts. An outcome-level diversity measure would catch the symptom
*if* you had ground-truth labels for every finding — which HANDOFF §6 records
as a ground-truth-EXISTENCE limit for per-finding precision. So for this
project the outcome route is closed, and the provenance route is the only one
open. That is a real asymmetry, not a preference.

### 2.3 Has anyone NAMED the mechanism? YES, once, qualitatively

`[fetched]` di Angelo M., Salzer G., *Consolidation of Ground Truth Sets for
Weakness Detection in Smart Contracts*, arXiv:2304.11624 (2023), §6.4
"Reservations about Majority Voting", verbatim:

> "Tools form families by being **derived from common ancestors** (like Oyente),
> by implementing the same approach (like symbolic execution, taint analysis, or
> fuzzing), or by relying on the same basic components (like GigaHorse, Rattle,
> Z3, or Soufflé)."

> "**Related tools may misjudge a contract in a similar way and outnumber tools
> with the correct result.**"

This is the mechanism, stated exactly, and it is stated as a reservation about
**majority voting** — i.e. about consensus, which is what this tool does.

**But they assert it; they do not measure it.** No count of which tools descend
from which ancestor, no fraction of agreement attributable to family structure,
no effect on their results. It is a caveat in a discussion section.

BOUND ON THIS CITATION: the verbatim text comes from two independent retrievals
(a search summary and an ar5iv render) that agree. My own extraction of the PDF
bytes decoded only part of the document and did not reach §6.4, so I have not
verified it against the publisher's bytes myself. Domain is Ethereum smart
contracts, not Java/C.

### 2.4 Has anyone measured RULE OVERLAP? Yes — but semantic, not genealogical

`[fetched]` Lenarduzzi V., Pecorelli F., Saarimäki N., Lujan S., Palomba F.,
*A Critical Comparison on Six Static Analysis Tools: Detection, Agreement, and
Precision* (JSS 2023 / arXiv 2101.08832). Read from the local copy retrieved in
a prior session.

They matched rules across five tools by **containment thresholds** — "the
threshold of 100% ... indicates that a rule completely resides within the
reference rule" — finding 17,977 rule pairs at 100% and 18,025 at 70%.
Per-pair, e.g. Findbugs–PMD 3,167 pairs (9.39% of possible).

**This is SEMANTIC overlap, not PROVENANCE.** It asks "do these two rules
describe the same thing", which convergent design satisfies just as well as
derivation does. It is the right neighbour to our question and it is not our
question. Their headline is also that agreement is *low* and tools are
complementary — consistent with HANDOFF §6.2.

### 2.5 Has anyone measured what fraction of a tool's rule set is derived?
### **NO. Explicit negative.**

The targeted query returned nothing and said so: no study measuring rule
porting fractions or "rule genealogy" between static analysis tools. Consistent
with §2.3 being qualitative and §2.4 being semantic.

A second relevant pointer, `[fetched]` from the ESEM'21 study *An Empirical
Study of Rule-Based and Learning-Based Approaches for SAST* (arXiv 2107.01921),
records the need as OPEN — that the community should devise methods that
"account for possible overlaps among the rules of different SATs." Named as
future work, not done.

### 2.6 STUDY VERDICT

**This is a genuine gap, not a rediscovery.** Precisely:

- The PRACTICE is documented, first-party, and broader than we assumed (§2.1).
- The RISK to consensus voting is named once, qualitatively, in another domain
  (§2.3).
- The adjacent quantity (semantic rule overlap) is measured, at scale (§2.4).
- **The quantity we need — what fraction of agreement is a rule agreeing with
  its own ancestor — is measured nowhere** (§2.5).

We are not the first to worry about it. We would be the first to put a number
on it. That is worth doing, and it is worth doing carefully, because a number
here is load-bearing for the premise rather than for a feature.

---

## 3. WHAT OUR EXISTING OBSERVATION IS AND IS NOT

Recorded so the pre-registration is honest about its starting point.
From 0f, on OWASP Benchmark, SpotBugs+FindSecBugs × semgrep:

```
semgrep p/java rules that FIRED declaring FindSecBugs provenance : 5 of 11
semgrep FINDINGS from those rules                                : 702 of 1,909 (36.8%)
co-located semgrep×SpotBugs RULE PAIRS that are rule+ancestor    : 483 of 1,588 (30.4%)
co-located LOCATIONS that are derived-ONLY                       : 278 of 1,229 (22.6%)
```

**Three different denominators. They are not interchangeable** and the
measurement below must report all three separately every time — conflating them
is the single most likely way to produce a wrong headline number here.

Already known and NOT to be re-derived: excluding derived-only pairs moved the
enrichment from 70.5% to 69.7% against a 51.6% base rate. **The effect on the
result was small.** But the single real-code agreement this project has ever
observed (the Struts near-miss) IS a derived pair, so on real code the observed
count of independent cross-methodology agreements is still ZERO.

---

## 4. PRE-REGISTERED MEASUREMENT

Fixed before computing. Deviations must be recorded as deviations.

### 4.1 Research questions

- **RQ1 — DECLARATION RATE.** What fraction of each tool's rules carry declared
  provenance pointing at another tool? Report separately for (a) rules shipped
  in the ruleset, (b) rules that fired on the corpus, (c) findings produced.
- **RQ2 — AGREEMENT ATTRIBUTION.** What fraction of observed cross-tool
  agreement is a rule agreeing with a declared ancestor? Report by rule pair
  and by location, never merged into one figure.
- **RQ3 — CONSEQUENCE.** How much does excluding derived agreement move the
  precision estimate, with a confidence interval, not a point estimate.

### 4.2 Data and instrument

- **NATIVE tool output only.** SARIF **drops** `source-rule-url` — verified, 0
  occurrences in semgrep's SARIF rule blob versus its presence in native JSON.
  The shipped SARIF-only pipeline structurally cannot see rule provenance. Any
  measurement must read native JSON/YAML.
- Confirmed present in `owasp/sg_native.json` metadata, per rule:
  `source-rule-url` (the ancestor), `source` (semgrep's own registry URL),
  `references`, `license`. Example value:
  `https://find-sec-bugs.github.io/bugs.htm#PATH_TRAVERSAL_IN`.
- Corpora already on disk: OWASP Benchmark, Struts, zlib (see `analysis/`).

### 4.3 The signal, and its direction of error

Declared provenance is a **LOWER BOUND and can only ever be one.** A rule may be
ported without attribution; nothing in any tool's format requires disclosure.

Therefore, pre-committed:
- A HIGH measured fraction is evidence of widespread derivation.
- A LOW measured fraction is **NOT** evidence of independence. It is consistent
  with either genuine independence or undeclared porting, and the measurement
  cannot distinguish them.
- **A null result here is uninformative and must be reported as uninformative**,
  not as clearance. This is pre-registered specifically because the temptation
  on a low number will be to read it as "independence confirmed."

### 4.4 The asymmetry limit — state it before, not after

Only semgrep declares provenance in machine-readable form. SpotBugs/FindSecBugs
do not. So:
- we can measure semgrep → FindSecBugs derivation;
- we **cannot** measure the converse, nor most tool pairs;
- the ecosystem-scale claim in §1 is therefore **not reachable** from declared
  metadata alone across tools.

What IS reachable at ecosystem scale is one tool's registry: what fraction of
*all* semgrep registry rules (not just those that fired) declare an upstream
source, and how that distributes across upstream tools. **Feasibility checked:
`~/.semgrep` holds only `settings.yml` — there is no local rule cache, and the
sandbox bash has no network.** This arm requires either a network-enabled
re-fetch of the registry or a hand-download by the operator. It is NOT blocked
in principle, but it is not runnable today and must not be scoped as if it were.

### 4.5 DECISION RULE — fixed now, before any number exists

Let *D* = fraction of co-located cross-tool agreement attributable to a declared
rule-ancestor relationship, and Δ = shift in the precision estimate when derived
agreement is excluded.

| condition | conclusion | action |
|---|---|---|
| D < 10% **and** Δ < 1pp | shared provenance is a real but minor contaminant | **DISCLOSE only.** No guard. Note it in output, as with 0a/0b/0c. |
| 10% ≤ D ≤ 33% **or** 1pp ≤ Δ ≤ 3pp | material but not dominant | disclose **per-merge**, operator-visible; still **no suppression** |
| D > 33% **or** Δ > 3pp | the independence claim is substantially compromised | suppression warranted, in the **0a shape**: conservative default + operator escape hatch |

Existing evidence (§3) puts D at 22.6–30.4% and Δ at 0.8pp — i.e. **straddling
the middle band**, which is exactly why the thresholds are fixed now rather than
after. The two criteria disagree on the current data: D says middle band, Δ says
bottom. Resolved by the principle below.

### 4.5.1 GENERAL PRINCIPLE — harm governs the guard, exposure governs the
### disclosure. Record this beyond the present instance.

The straddle is not a defect in the thresholds. **The two measures answer
different questions, so they are entitled to different answers**, and a later
session hitting the same split should not treat it as a contradiction to be
resolved in favour of one number.

- **Δ (the shift in the result) is about whether the SIGNAL is CONTAMINATED.**
  At 0.8pp it barely is. This governs whether to *suppress* — i.e. whether to
  change what the tool computes. Changing computation on a 0.8pp contaminant
  would trade a small measured bias for a real loss of merges, which is the
  wrong trade.
- **D (the fraction of agreement that is derived) is about whether the CLAIM is
  HONEST.** A user told "two independent tools agreed" is owed that number
  **regardless of whether their triage decision would change.** Disclosure is
  not a weaker form of suppression that you apply when the effect is too small
  to act on; it discharges a different obligation. The user is owed an accurate
  description of the evidence they are being shown, and "independent" is a
  factual claim about provenance, not a summary of effect size.

So: **a small Δ argues against a guard. It argues for nothing whatsoever about
disclosure.** The two must be decided separately, and a low harm number must
never be used to retire a disclosure obligation.

This generalises past rule provenance. It is the same shape as 0a/0b (where
consensus is WITHHELD and the operator is still owed the reason), 0c (a silent
zero converted to a stated one), and the signal gate (which discloses that
consensus is not firing rather than pretending). In each case the project's
standing preference is that **an uninformative or contaminated signal is
disclosed rather than silently handled** — and the size of the contamination
governs the handling, never the disclosure.

### 4.6 Threats, stated in advance

1. **`source-rule-url` may be under-populated** relative to actual derivation,
   per §4.3.
2. **A declared ancestor is not proof of a shared blind spot.** A ported rule
   may have been re-implemented with different scope; §2.4's containment work
   shows "the same rule" is often not the same rule. Derivation is evidence of
   correlated blind spots, not proof.
3. **Synthetic-corpus bound.** OWASP Benchmark is synthetic; per HANDOFF 0d the
   negative generalises no further than the positive did.
4. **One ecosystem.** semgrep+FindSecBugs is one pair in one language.
5. `~1 in 3` on OWASP is a co-location statistic, and co-location on a synthetic
   corpus where every file has one planted bug is not co-location on real code.

---

## 5. EXPLICITLY NOT IN SCOPE

- **No guard is implemented or designed here.** §4.5 decides whether one is
  warranted.
- No change to `_result_key`, the lineage guard, or scoring.
- No tool acquisition — HANDOFF §6.2 governs and is not overturned by this.

---

## 6. WHY THIS IS THE RIGHT NEXT ITEM

It is the only open question that can change the PREMISE rather than the
implementation. 0a asks "are these the same engine?" This asks "did one of these
rules come from the other tool?" — and §2.1 shows the answer is routinely yes,
by design, as a documented way registries are built.

If the fraction is high, "diversity-aware consensus" is measuring something
weaker than it claims, and that is a README-level fact rather than a caveat.
If it is low, we have a lower bound and an honest statement of what we could not
rule out. Both outcomes are publishable; neither requires a new tool.

---

# 7. RESULTS — CORPUS ARM ONLY (run 2026-07-26)

Script `analysis/scripts/rule_provenance.py`, output
`analysis/results/rule_provenance_corpus_arm.txt`. **Registry arm NOT run** —
it needs a network fetch not performed, and a partial ecosystem number is worse
than none because it would be quoted as covering the ecosystem when it covers
one registry's fired subset.

**INSTRUMENT CORRECTION.** This arm was requested against "SARIF already on
disk." It is run against **native semgrep JSON** instead, because SARIF drops
`source-rule-url` — verified, 0 occurrences in `owasp/sg_java2.sarif` versus its
presence in `owasp/sg_native.json`. A SARIF-based run would have returned a
guaranteed false zero and looked like clearance.

**Every derived fraction below is a LOWER BOUND.** Nothing obliges a tool to
declare that a rule was ported.

## 7.1 RQ1 — declaration rate

### OWASP Benchmark v1.2 (Java, synthetic; run alongside SpotBugs+FindSecBugs)
```
rules LOADED in the p/java config                 60
rules that FIRED                                  11
rules that fired AND declare provenance            5   = 45.5% of fired   [LOWER BOUND]
                                                       =  8.3% of loaded  [LOWER BOUND]
findings from those rules                        702 / 1,909 = 36.8%      [LOWER BOUND]
```

### zlib 1.3.1 (C, real; run alongside flawfinder + cppcheck)
```
rules that FIRED                                   4
rules that fired AND declare provenance            0   = 0.0%             [LOWER BOUND]
findings from those rules                          0 / 33 = 0.0%          [LOWER BOUND]
```
**The zlib zero is UNINFORMATIVE AND MUST NOT BE READ AS CLEARANCE.** Per §4.3,
pre-registered: a low declaration rate is equally consistent with genuine
independence and with undeclared porting. semgrep's C rules simply carry no
`source-rule-url`; that is a fact about disclosure practice, not about ancestry.
It would be a straightforward error to conclude "the C pipeline is unaffected by
rule derivation" from this number, and this sentence exists to block it.

## 7.2 RQ2 — does the declared ancestor name a tool ALSO IN THE RUN?

This is the question that matters for consensus, because a declared ancestor
only contaminates *agreement* if the ancestor's tool is one of the tools
agreeing.

```
OWASP : 5 of 5 declaring rules name FindSecBugs, which IS in the run   (100%)
        covering 702 of 1,909 findings (36.8%)
zlib  : 0 — no declaring rules at all, so no cross-tool agreement in that
        run can be rule-and-ancestor by DECLARED provenance
```

The five, with FINDING counts (not pair counts — see §7.3):
```
  288  httpservlet-path-traversal   <- find-sec-bugs #PATH_TRAVERSAL_IN
  171  des-is-deprecated            <- find-sec-bugs #DES_USAGE
  130  desede-is-deprecated         <- find-sec-bugs #TDES_USAGE
   85  use-of-sha1                  <- find-sec-bugs #WEAK_MESSAGE_DIGEST_SHA1
   28  use-of-md5                   <- find-sec-bugs #WEAK_MESSAGE_DIGEST_MD5
```

**BOUND ON THE 100%.** Five of five is a striking ratio and it is not a random
draw. This run was *constructed* to pair semgrep with SpotBugs+FindSecBugs, and
FindSecBugs is precisely the upstream semgrep's Java security rules are known to
draw on (§2.1). The honest statement is: **where provenance was declared at all
in this run, it named a co-present tool every time** — on n=5, in a
deliberately-chosen pairing. It is not evidence that 100% of derivation
generally lands on a co-present tool.

## 7.3 THE DENOMINATORS — five of them, all different, none interchangeable

The single most likely way to produce a wrong headline here. Each figure below
is correct and they are not versions of one another.

| figure | numerator | denominator | what it answers |
|---|---|---|---|
| **8.3%** (5/60) | semgrep rules declaring FSB provenance | semgrep rules **loaded** in the `p/java` config | how much of the ruleset we *ran* is declared-derived |
| **45.5%** (5/11) | same | semgrep rules that **fired** on this corpus | how much of what actually spoke is declared-derived |
| **36.8%** (702/1,909) | semgrep **findings** from those rules | **all** semgrep findings on this corpus | how much of the *output volume* is declared-derived |
| **30.4%** (483/1,588) | co-located (semgrep rule, SpotBugs rule) **PAIRS** where the semgrep rule declares that SpotBugs rule as ancestor | all co-located semgrep×SpotBugs rule pairs | how much of the *agreement* is rule-with-its-own-ancestor |
| **22.6%** (278/1,229) | co-located **LOCATIONS** whose cross-tool agreement is derived-**ONLY** | all co-located locations | how many *places* have no independent agreement at all |

**If one number goes in the README it should be 30.4% or 22.6%**, because those
are the two that describe *agreement* — which is what the tool claims and what
the user is being shown. 36.8% describes semgrep's output volume and says
nothing directly about consensus. 8.3% is the most misleadingly low: 49 of the
60 loaded rules never fired, so the denominator is dominated by rules
irrelevant to this corpus.

RECONCILIATION with HANDOFF 0f, checked: 0f lists "the four pairs" as
PATH_TRAVERSAL_IN 199, DES_USAGE 171, WEAK_MESSAGE_DIGEST_SHA1 85,
WEAK_MESSAGE_DIGEST_MD5 28 — which sum to exactly 483, i.e. those are
**co-located PAIR counts, not finding counts**. This run finds the same 5
declaring rules and the same 702/1,909, and additionally identifies a **fifth**
rule 0f did not list (`desede-is-deprecated` ← `TDES_USAGE`, 130 findings) which
evidently contributed 0 co-located pairs. The two records agree; 0f's list was
of pairs, not of rules.

## 7.4 THE GAP THAT MATTERS — Struts is unmeasurable from local data

Only SARIF was captured for the Struts run; no native semgrep JSON. SARIF drops
`source-rule-url`, so provenance is unreadable there.

This is consequential rather than incidental: **Struts is the only REAL-CODE
Java corpus and the site of the single real-code cross-tool agreement this
project has ever observed** (the `ServletRedirectResult` near-miss, HANDOFF 0e).

The join was attempted and **failed**: the rule that fired on Struts is
`java.lang.security.audit.unvalidated-redirect.unvalidated-redirect`, and it did
NOT fire on OWASP, so its metadata is not in any locally-captured native output.
Its SARIF rule blob carries only `precision` and `tags` — no `source-rule-url`,
no `references`.

**Therefore: HANDOFF 0f's statement that the Struts near-miss "IS a derived
pair" is NOT reproducible from data on this machine.** 0f quotes a
`source-rule-url` for `unvalidated-redirect` pointing at
`#UNVALIDATED_REDIRECT`, which must have come from registry or native output
captured at the time and not retained. That claim is:
- **consistent** with everything measured here (all 5 measurable Java security
  rules declare FindSecBugs ancestry), and
- **load-bearing** — it is the basis for "on real code this project has observed
  ZERO independent cross-methodology agreements", and
- **currently unverifiable in-session.**

Per RULE 10.2 it should be treated as an inventor/prior-session-attested result
with the artifact absent, not as a checked fact. **Recovering it is cheap**: one
`semgrep --config=p/java --json` run over Struts captures the metadata, and that
single re-run would settle it.

### >>> SETTLED 2026-07-26. THE RE-RUN WAS DONE. 0f WAS RIGHT. <<<

`semgrep 1.171.0 --config=p/java --json` over `struts-main`. **Reproduced the
original run exactly** — 60 rules, 1,483 files, 1 finding — so this is the same
measurement, not a different one. Evidence:
`analysis/results/struts_derived_pair_evidence.txt`.
sha256(`struts/sg_native.json`) = `7049d9d5e32b922419da3a599f30564f2b999891f37065224b4d553b2b84685d`

```
semgrep side
  check_id        java.lang.security.audit.unvalidated-redirect.unvalidated-redirect
  location        core/src/main/java/org/apache/struts2/result/ServletRedirectResult.java:244
  source-rule-url https://find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT

SpotBugs(+FindSecBugs) side
  ruleId          UNVALIDATED_REDIRECT
  location        org/apache/struts2/result/ServletRedirectResult.java:247
  helpUri         https://find-sec-bugs.github.io/bugs.htm#UNVALIDATED_REDIRECT
```

**The two URLs are BYTE-IDENTICAL.** semgrep's declared ancestor is exactly the
rule the other tool fired — its own canonical identity URL. This is not an
inference from naming similarity or from category overlap; it is a pointer
match.

CONSEQUENCES:
1. **The Struts near-miss IS a derived pair. CONFIRMED, not attested.**
2. **"On real code this project has observed ZERO independent cross-methodology
   agreements" is CONFIRMED** and may now be cited as measured. The single
   real-code agreement ever observed is a rule agreeing with its own ancestor.
3. 0f's quoted `source-rule-url` was correct verbatim. The prior session was
   right and the gap was retention, not accuracy.
4. On REAL code the derived fraction of observed agreement is **1 of 1 = 100%**
   — on n=1, which is why the OWASP figures remain the quotable ones.

ONE DRIFT NOTE, recorded for honesty: the registry was re-fetched today, and the
rule's metadata now carries an `owasp: A01:2025` tag absent from the original
run, so the registry rule has been updated since. The finding is identical
(same rule, same file, same line 244) and `source-rule-url` is the field at
issue, so the drift does not affect the conclusion — but these are not the
original bytes.

## 7.5 What this does and does not settle against the §4.5 decision rule

It does NOT settle it. §4.5 turns on D (fraction of *agreement* that is derived)
and Δ (shift in the precision estimate) — D is unchanged at 30.4%/22.6% from 0f,
and Δ is unchanged at 0.8pp. This arm measured RQ1 and the RQ2 precondition, not
a new D or Δ.

What it adds: the declaration rate is now measured on two corpora rather than
asserted from one; the C pipeline's zero is on record *as uninformative*; the
five denominators are pinned to exact definitions; and the Struts evidence gap
is identified as the one cheap, high-value re-run outstanding.

Per §4.5.1 the standing reading is unchanged: **Δ = 0.8pp argues against a
guard and argues nothing about disclosure.** No guard is warranted on this
evidence. Disclosure remains owed.
