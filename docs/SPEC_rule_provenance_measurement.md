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
after. Note the two criteria disagree on the current data (D says middle, Δ says
bottom); the pre-committed reading is that **Δ governs the action and D governs
the disclosure**, because Δ is the measured harm and D is the exposure.

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
