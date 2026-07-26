# Scope — what is actually false about the shipped consensus claim

Written 2026-07-26, BEFORE any code or README change, to fix precisely what the
defect is and what it is not. Deciding what the README owes readers comes after
this; this document does not make that decision.

Tier: `[self-tested]` — direct observation of real scanner output and the
shipped code on this machine. Every number below is reproducible with the
commands given. No external judge involved.

---

## 1. The distinction that matters

Three different things get conflated by saying "cross-tool dedup is broken."
They have different truth values.

| layer | claim | status |
|---|---|---|
| **A. `audit.py`'s code** | cross-tool merge works when inputs permit | **TRUE** — demonstrated: two tools, same ruleId, same location, no fingerprints → 1 finding, `n_tools=2`, renders with both chips and a `2 tools` badge |
| **B. CLI with arbitrary tools** | a user's own tool pair may or may not merge | **CONDITIONAL** — depends entirely on whether either tool emits `fingerprints`/`partialFingerprints`, and on ruleId namespace overlap. CodeQL + semgrep might; unverified either way |
| **C. the shipped default** | the documented flawfinder + cppcheck pair demonstrates the headline signal | **FALSE** — it cannot, on any input |

**The defect is C, not A.** The tool works. Its shipped default configuration
cannot demonstrate the thing the README highlights.

## 2. Why C is false — deductive, not sampled

`_result_key` (audit.py:521) prefers a tool's own fingerprint and falls back to
`rk:{ruleId}|{uri}|{line}`.

- Real flawfinder emits `fingerprints: {"contextHash/v1": "<sha256>"}` on
  **6 of 6** results → every flawfinder key is `fp:contextHash/v1=…`
- cppcheck (both documented paths) emits no fingerprints → every cppcheck key
  is `rk:…`
- An `fp:`-prefixed string can never equal an `rk:`-prefixed string.

So the merge is impossible for this pair **on any input** — this is a property
of the key construction, not of the sample. Confirmed empirically:
`n_tools distribution: {1: 15}`, `ANY cross-tool merge: False`.

A second, independently sufficient blocker: the ruleId namespaces are disjoint.
flawfinder emits `FF1013`, `FF1001`. cppcheck emits `CWE-415` (action path,
when a `cwe` attribute exists) or `doubleFree` (native path, always a check
name). They never collide even with fingerprints removed.

URI form is **not** a blocker — both tools emit the same relative path when
given the same argument. An earlier claim that they mismatched was a harness
artifact and is withdrawn.

## 3. Root cause

`_result_key`'s docstring cites the DefectDojo model. DefectDojo uses **two**
algorithms: fingerprint/hash for SAME-tool dedup, and location+class for
CROSS-tool dedup. `audit.py` uses the same-tool algorithm for both purposes.
Using a tool-private hash as a cross-tool identity key defeats cross-tool
consensus by construction.

This is one fix in one function, not a redesign.

## 4. WITHDRAWN — "the quickstart redirect is broken" does NOT apply to the
##    public README. Provenance failure recorded in §4a.

An earlier version of this section stated that README line 6
(`cppcheck --output-format=sarif … > cppcheck.sarif`) redirects the wrong
stream, silently degrading the two-scanner quickstart to a single-tool run, and
labelled it "PUBLIC and LIVE."

**The technical observation is true. The attribution was wrong.**

- True: cppcheck writes SARIF to **stderr**. `>` captures 38 bytes of
  `Checking <file> ...`, and feeding that to `audit.py --ingest` yields
  `⚠ parse error … tools: Flawfinder` — a single-tool run. Reproducible.
- True: that command appears at line 6 of the README **in this local
  working copy**, which is at commit `729e893`.
- **FALSE: that this is the public README.** `origin/main` is `c5f75d6`, one
  commit ahead ("Update README.md"). The local repo had never fetched. The
  PUBLISHED README is a 59-line rewrite whose quickstart uses the correct
  path:

```bash
cppcheck --enable=all --xml --xml-version=2 your_code/ 2> cppcheck.xml
python3 src/cppcheck_xml_to_sarif.py cppcheck.xml cppcheck.sarif
```

Correct stream, correct converter path. **There is no redirect defect in the
public README.** The finding applies only to a stale local copy.

Still true and worth keeping: the tool's signal gate reported
`informative here = ['severity']; ranking confidence = medium` under the
misconfiguration — it disclosed that consensus was not firing rather than
silently pretending. The honesty machinery works.

Also still true, though now moot for the README: cppcheck's NATIVE SARIF output
uses check names as ruleIds (`doubleFree`), never `CWE-<n>`, making it strictly
worse for merging than the XML→converter path the public README uses.

### 4a. How this error happened — same class as the withdrawn URI artifact

Two compounding provenance failures, both mine:

1. **A composed command acquired a line number.** The command was tested with a
   substituted target path and an added `2>` capture, then written up as
   "README L6" as though the documented command had been run verbatim. The test
   was faithful on the point at issue (the stdout redirect was unchanged), but
   citing it by line number asserted a correspondence that was not checked.
2. **A local file was attributed to the public product.** The claim was labelled
   "PUBLIC and LIVE" without checking `git fetch` / `origin/main`. The local
   repo was one commit behind and the divergent file was precisely the one under
   analysis.

This is the same failure class as the URI-mismatch artifact withdrawn earlier
in this session: a property of the local harness or working copy, presented as a
property of the world. The remedy is the same — check world state before
attaching a claim to it. `git fetch` before any claim about "the public repo"
is now the concrete check.

Note for the record: the inventor's initial challenge to this finding was
correct about the public README and incorrect about the repo (their grep
covered an uploaded zip). Refusing to amend on assertion was right; the finding
against the local tree WAS accurate. Both parties were right about different
documents, which is exactly what an unstated provenance produces.

## 5. Claim-by-claim status — against the PUBLIC README (`origin/main` c5f75d6)

Line numbers refer to the published 59-line README, verified via
`git show origin/main:README.md`. The previously-tabulated claims were from the
stale 162-line local copy and are superseded.

The public README is a markedly better document than the stale one: no broken
command, an explicit "Honest scope" section, and correctly-bounded validation
numbers. The problem is narrower and sharper.

| # | public README text | status |
|---|---|---|
| 1 | L3-5 "rank findings higher where *independent tools agree*" — the headline | **cannot be demonstrated by the README's own quickstart.** For flawfinder+cppcheck, agreement can never register |
| 2 | L9-11 "merges the ones pointing at the same bug" | **false for the quickstart pair.** Cross-tool merge is structurally impossible for it (§2) |
| 3 | L35 quickstart step 2 labelled "**re-rank by consensus**" | **the sharpest instance.** The step is named for a signal that is guaranteed to be absent given step 1's tool pair |
| 4 | L21-22 "~13x concentration — files flagged by 4 tools were ~13x more likely to be truly vulnerable" | **accurate about the Lipp experiment**, which used 5 tools on reconstructed envelopes that DID merge. A reader running the quickstart can never observe a file flagged by >1 tool |
| 5 | L18-20 ROC-AUC 0.755, ~65% at top-20% | **accurate and correctly scoped** to the validation. Not at issue |
| 6 | L45 "Validated on C/C++ with **flawfinder, cppcheck**, and CodeQL" | **where the transfer gap bites hardest** — it names the two tools that specifically cannot merge as the validated combination |
| 7 | L31-33 quickstart cppcheck invocation | **correct.** `2>` + XML converter. No defect (§4) |
| 8 | L50-52 "The newest piece (cross-tool duplicate display) handles the case where tools agree on *location*" | **accurate, and more load-bearing than it reads.** Post-analysis this is the ONLY mechanism that can surface agreement for the quickstart pair |
| 9 | L38-39 quickstart step 3 runs `audit_dedup_display.py` | **accurate for the CLI.** Note this contradicts `SPEC_dedup_shipped_path.md`'s "not in any shipped path" — it is absent from `action.yml`, but present in the documented CLI path |
| 10 | L38 describes step 3 as "**collapse** cross-tool duplicates" | **minor tension** with the resolved badge-not-collapse decision. The pass annotates; it does not collapse |

**Summary of the corrected finding.** The public README does not contain a false
statement about what the code does. It contains a headline, a quickstart step
name, and a named tool pair that together promise the reader an experience the
shipped default cannot deliver: run these two scanners, re-rank by consensus.
Consensus will be empty every time, and nothing in the output explains why —
beyond the signal gate's `informative here = ['severity']`, which a new reader
will not read as "the feature you came for is inoperative."

## 6. What the README does NOT owe readers

Guarding against overcorrection, since the pull will be to overstate now that
a real defect is found:

- It should NOT say the tool does not work. Layer A is sound.
- It should NOT retract the ROC-AUC 0.755 result. See §7.
- It should NOT claim CLI users with other tools are affected — layer B is
  genuinely conditional and unmeasured. Saying "your tools won't merge either"
  would be an unverified claim in the opposite direction.

## 7. Why fixing `_result_key` STRENGTHENS the validated number

Stated here explicitly because it inverts the usual objection that changing
ranking behaviour invalidates a published metric.

The ROC-AUC 0.755 file-level result was measured on RECONSTRUCTED Lipp SARIF
envelopes — envelopes in which cross-tool merging **did** occur (VALIDATION.md
records 1,318 multi-tool overlaps recovered, matching a hand-computed count
exactly). The validated configuration is therefore one where cross-tool merge
works.

The shipped configuration cannot merge. So:

> The two-algorithm fix moves the SHIPPED configuration TOWARD the VALIDATED
> one, not away from it.

Fixing `_result_key` does not put 0.755 at risk; the current shipped state is
what fails to reproduce the conditions 0.755 was measured under. This is an
argument FOR the fix, and it is the strongest one available.

Bound on this argument: it rests on VALIDATION.md's recorded 1,318-overlap
match, an artifact not re-opened in this session. The reconstructed envelope
itself was not re-examined. If that envelope turns out to have merged for some
other reason, this argument weakens — but the direction of the fix does not.

## 8. Open decision (inventor's)

What the public README owes, given §5 and §6. Not decided here.

The corrected picture changes the shape of the decision. There is no urgent
copy-paste breakage to patch — the public quickstart runs. What there is: a
headline, a step name ("re-rank by consensus"), and a named tool pair that
together promise an experience the default cannot deliver.

That makes the README question **substantially less urgent as a correction and
more coupled to the fix**. If `_result_key` is fixed, claims 1, 2, 3 and 6
become true as written and the README needs no change at all. Correcting the
README first would mean documenting a limitation that is about to be removed.

Recommendation: do NOT edit the README now. Fix `_result_key`, re-measure, and
revisit — at which point the likely outcome is that the README was right and the
code caught up to it. Revisit sooner only if the fix proves harder than expected
or is deferred, in which case an "Honest scope" bullet noting that the
flawfinder+cppcheck default pair does not currently produce cross-tool merges
would be the minimal honest disclosure.

## 9. Repo state note

At the time this document was first written, the local working copy was one
commit BEHIND `origin/main` (`729e893` vs `c5f75d6`), and the divergent file was
the README — the exact file under analysis. That is what produced the §4a
misattribution.

RESOLVED 2026-07-26: fast-forwarded to `c5f75d6`. The local README is now the
published one; `grep -c 'output-format' README.md` → 0, and the quickstart uses
`2> cppcheck.xml` + the converter. All §5 line numbers refer to this version and
are now checkable directly in the working tree.

`src/` and `action.yml` were byte-identical across the two commits, so every
code finding in this document held for the published product before the
fast-forward and is unaffected by it.
