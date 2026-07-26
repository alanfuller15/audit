# Spec — close the cross-tool dedup gap in the shipped path

Status: ready to implement — but READ THE CORRECTION BELOW FIRST. This spec's
original framing of the gap was too broad and has been narrowed against
measured behaviour. Render decision resolved: BADGE IN PLACE, do not collapse.
Scope: `action.yml`, `src/audit_html_report.py`, `examples/fixtures/`
Out of scope: `src/audit.py`, scoring, ranking, SARIF output

## The finding

`audit_dedup_display.py` exists in the repo but is not in any shipped path.

> **CORRECTION (2026-07-26):** "not in any shipped path" is too strong. The
> PUBLISHED README (`origin/main` c5f75d6 — the local checkout was one commit
> behind and did not have it) documents the pass as step 3 of its quickstart:
> `python3 src/audit_dedup_display.py out.json out_display.json`. So it IS in
> the documented CLI path. What remains true, and is what this spec is actually
> about: `action.yml` never invokes it, and `audit_html_report.build()` ignores
> its output fields, so the HTML artifact never surfaces the annotations.
> Restated accurately: **the pass is documented for CLI users but absent from
> the Action, and its output is invisible in the HTML report either way.**
> Separately, the public README describes step 3 as "collapse cross-tool
> duplicates" — minor tension with the resolved badge-not-collapse decision;
> the pass annotates, it does not collapse.

The Action's rank step runs:

```
audit.py --ingest  ->  audit_result.json  ->  audit_html_report.py  ->  audit_report.html
```

`audit_dedup_display.py` is never invoked. And `build()` in
`audit_html_report.py` contains no reference to `display_group`,
`display_also_flagged_by`, or `display_groups_count` — so inserting the pass
alone would not change the report either.

This is a distribution gap, not a correctness bug. Scoring is unaffected and
the SARIF uploaded to the Security tab is unaffected.

## CORRECTION (2026-07-26) — this spec overstated the gap

An earlier draft of this section read: "the HTML artifact Action users receive
renders cross-tool agreement as unrelated single-tool findings." **That is
false in general.** It was corrected after the claim was checked against
`ingest_sarif._result_key` and confirmed by execution.

`cppcheck_xml_to_sarif.py:17` maps cppcheck's `cwe` attribute into the ruleId
(`"CWE-%s" % cwe`). `_result_key` (audit.py:521) falls back to
`rk:{ruleId}|{normalized_uri}|{startLine}` when a result carries no
fingerprints. So two tools flagging the same location with the SAME ruleId
produce an IDENTICAL key, merge at the SCORING layer, and already render
today — `audit_html_report.py:51-52` emits a tool chip per tool plus an
`N tools` consensus badge, and line 37 counts them in the summary.

Verified by execution, not by reading:

```
case                                     #findings   n_tools
A same rid/uri/line, no fingerprints             1       [2]   <- MERGES
B tool2 emits partialFingerprints                2    [1, 1]
C uri forms differ (src/ vs ./src/)              2    [1, 1]
D line off by one (42 vs 43)                     2    [1, 1]
```

End-to-end render of case A produces:
`<td class="tools"><span class="chip">Cppcheck</span><span class="chip">flawfinder</span><span class="consensus">2 tools</span></td>`

### The corrected bound on this gap — and a reversal

As a statement about `audit.py`'s CODE, the narrowing is: the merge path exists
and works, so the gap covers same location / **different ruleId** / same
CWE-class / different tools.

**But that narrowing does NOT hold for the shipped action, and the original
framing was closer to right than the correction.** Verified against real output
from both scanners `action.yml` actually runs:

```
uri forms match: True
n_tools distribution: {1: 15}
ANY cross-tool merge: False
```

No flawfinder finding can EVER merge with a cppcheck finding — deductive from
`_result_key`, not a property of this sample:

- real flawfinder emits `fingerprints: {"contextHash/v1": "<sha256>"}` on 6/6
  results → key is `fp:...`;
- `cppcheck_xml_to_sarif.py` emits none → key is `rk:{ruleId}|{uri}|{line}`;
- an `fp:` key can never equal an `rk:` key, on any input.

Independently sufficient second blocker: disjoint ruleId namespaces
(`FF1013` vs `CWE-415`) — they would not match even without fingerprints.

**So `audit_dedup_display.py` is not a corner-case add-on. It is the only
mechanism by which cross-tool agreement can surface at all in the shipped
action.** That raises this spec's priority rather than lowering it.

The deeper issue is in `_result_key`, which this spec puts out of scope:
preferring a tool's own fingerprint is the DefectDojo SAME-tool dedup
algorithm being used as a CROSS-tool consensus key. See VALIDATION.md
(2026-07-26) — the shipped action cannot currently produce `n_tools > 1`,
which is the signal the ROC-AUC 0.755 result was measured on.

Three further preconditions mean even SAME-ruleId agreement can fail to merge
at scoring. In each, the display pass IS the only thing that surfaces the
agreement — verified by execution (`display_groups` = groups the pass adds):

| case | merges at scoring? | display pass rescues? |
|---|---|---|
| B tool2 emits `partialFingerprints` | no (2 findings) | **yes** (1 group) |
| C uri forms differ (`src/` vs `./src/`) | no (2 findings) | **yes** (1 group) |
| D line off by one | no (2 findings) | **yes** (1 group) |
| E no CWE resolvable on one side | no (2 findings) | **no** (0 groups) |

- **B — fingerprints defeat the merge.** Any tool emitting `partialFingerprints`
  or `fingerprints` takes the `fp:` branch of `_result_key`, which is
  tool-specific, so it never merges cross-tool regardless of matching CWE.
  cppcheck's converter emits none; other tools (CodeQL, semgrep) commonly do.
- **C — path normalization is shallow.** `_norm_uri` only converts backslashes
  and strips a leading `/`. `./src/x.c` and `src/x.c` are different keys.
  The display pass compares `_basename`, so it is immune.
- **D — line offsets defeat the merge.** Scoring requires an exact `startLine`
  match; the display pass allows `TOL = 3`.

So the display pass earns its place on MORE than the different-ruleId case —
it also rescues fingerprint, path-form, and line-offset mismatches. What it
CANNOT do is case E: group anything whose CWE-class is unresolvable on either
side. That is the binding constraint, and its frequency is unmeasured.

### Unmeasured precondition — how often can this fire at all?

`_cwe_class` resolves a class from `ruleId + message + uri`. cppcheck's ruleId
is `CWE-<n>` **only when the XML carries a `cwe` attribute**; otherwise it falls
back to the check name (`nullPointer`, ...), and real cppcheck messages
generally do not contain a CWE number. Case E above is exactly this, and it
yields zero groups.

**The frequency of the no-CWE fallback in real cppcheck output is UNKNOWN.**
It determines how prominent the badge should be. Do not design the render
around an assumed frequency — measure it first (HANDOFF §7 item 4; cppcheck
2.21.0 and flawfinder are installed locally, so this is runnable).

#### Preliminary datum (NOT a frequency estimate — n=9, toy file)

Real cppcheck 2.21.0 on `examples/sample_c/demo.c` (25 lines), through the real
`cppcheck_xml_to_sarif.py` → `_cwe_class` chain:

```
  missingIncludeSystem  x3  -> class=None    (no cwe attr; check-name fallback)
  CWE-415                   -> class=uaf     <- the only groupable finding
  CWE-398               x2  -> class=None    (cwe attr present, but DENIED)
  CWE-563                   -> class=None    (cwe attr present, but DENIED)
  CWE-561                   -> class=None    (cwe attr present, but DENIED)
  staticFunction            -> class=None    (no cwe attr; check-name fallback)

  GROUPABLE: 1 / 9 = 11%
```

Confirmed on this run: 5 of 10 raw cppcheck errors carried a `cwe` attribute,
and **0 of 10 carried a CWE number in the message text** — so the check-name
fallback is genuinely ungroupable, as suspected.

But the run surfaced a SECOND suppressor the original concern did not
anticipate, and it is equally large here: of the 5 findings that DID carry a
`cwe` attribute, **4 were killed by `_CWE_DENY`** (398, 563, 561 — the
junk-drawer CWEs). The deny-list, not just the missing attribute, is holding
groupability down. Any real measurement must report both causes separately.

HONEST BOUND: n=9 on a 25-line toy file, and 3 of the 9 are
`missingIncludeSystem` — an artifact of not passing include paths, not a real
finding profile. This is a directional signal that the concern is real and has
two causes. It is NOT a frequency estimate. Item 4 still needs a real library.

## Evidence

`examples/fixtures/verify_dedup_render.py` runs the full chain against a
minimal SARIF pair with one planted cross-tool overlap. Against the current
tree:

```
  [ok  ] 1 ingest: 4 findings from 2 tools ['Cppcheck', 'flawfinder']
  [ok  ] 2 scoring: 2 separate findings at src/parse.c:42, n_tools=[1, 1]
  [ok  ] 3 dedup: 1 display group(s), 2 member(s), also_flagged_by=[...]
  [FAIL] 4 render: HTML does not surface cross-tool agreement (this is the gap)
  [ok  ] 5 invariant: rank order intact: [1, 2, 3, 4]
```

Stages 1, 2, 3, 5 pass. The gap is isolated to stage 4.

Re-confirmed against the tree on 2026-07-26: reproduces exactly as printed
above, exit 1. But read stage 4's label with the correction in mind — "HTML
does not surface cross-tool agreement" is the verifier's wording and it is too
broad. What stage 4 actually detects is that the HTML does not surface
cross-tool agreement **for this fixture pair**, which is a different-ruleId
pair. The verifier's message should be narrowed when it is next touched.

## Changes

### 1. `action.yml` — insert the dedup pass

In the "Re-rank by review-worthiness" step, between the `audit.py --ingest`
call and the `audit_html_report.py` call:

```bash
python3 "${{ github.action_path }}/src/audit_dedup_display.py" \
  audit_result.json audit_result_display.json
```

Then point the HTML report at the display file:

```bash
python3 "${{ github.action_path }}/src/audit_html_report.py" \
  audit_result_display.json audit_report.html
```

Write to a **separate file**, not in place. `audit_result.json` and
`audit_result.sarif` are already written by the ingest step and
`audit_result.sarif` is uploaded to the Security tab. Keeping the display
annotations out of both preserves the separation the post-processor was split
out to maintain.

The `findings=` output can keep reading `audit_result.json`. `annotate()` adds
fields but never adds or removes entries, so the count is identical either way.

### 2. `src/audit_html_report.py` — render the groups

`build(data)` must surface, for any finding carrying `display_group`, the fact
that independent tools agreed at that location. Two additions:

- **Per-finding**: a marker naming the tools in `display_also_flagged_by`.
- **Summary**: `display_groups_count` alongside the existing raw/dedup counts.

Both are additive. Do not reorder, do not rescore, do not merge rows in a way
that changes the finding count.

`build()` must remain correct on input that has never been through the dedup
pass — the fields are absent, not null. Guard with `.get()`.

### 3. `examples/fixtures/` — commit the fixtures

`flawfinder_min.sarif`, `cppcheck_min.sarif`, `verify_dedup_render.py`.

The repo currently has no test harness. These are the first regression
fixtures; the verifier is runnable with no scanners installed and no network.

**BOTH FIXTURES ARE UNREPRESENTATIVE — treat as illustrative only, and rebuild
from captured real scanner output (2026-07-26).**

Three separate divergences from real output, all measured:

1. **`flawfinder_min.sarif` uses `CWE-120` / `CWE-134` as ruleIds.** Real
   flawfinder emits `FF1001`, `FF1013`, `FF1016` — an `FF####` namespace that
   never contains a CWE number.
2. **`flawfinder_min.sarif` carries no fingerprints.** Real flawfinder emits
   `fingerprints: {"contextHash/v1": "<sha256>"}` on 6 of 6 results. This is
   the single most consequential divergence: it is why the fixture pair appears
   able to merge at scoring when the real pair cannot.
3. **`cppcheck_min.sarif`'s message is authored as `"…(CWE-787)"`.** Real
   cppcheck output carries no CWE string in the message (measured: 0 of 10), so
   the fixture's cppcheck finding is groupable via a number real output would
   not supply.

Consequence: the fixtures model a tool pair that does not exist. They cannot
support any claim about shipped behaviour, and the stage-4 FAIL they produce is
correct by accident rather than by construction.

They also exercise ONLY the different-ruleId / same-class path, so they do not
test the merge path at all.

Rebuild procedure: capture real `flawfinder --sarif` and real
`cppcheck --enable=all --xml` → converter output on a small real C file, trim
to a minimal pair, and commit the trimmed real output rather than hand-authored
SARIF. Hand-authoring is what introduced all three divergences.

Fixtures to ADD before calling this done:
- a **merge-path regression**: same ruleId / same uri / same line, no
  fingerprints → must stay ONE finding with `n_tools=2`, and the badge must
  not double-report what the existing consensus chip already says;
- an **ungroupable-fallback case**: cppcheck-style check-name ruleId with a
  realistic message containing no CWE → must produce zero display groups and
  render cleanly (case E);
- a **`_CWE_DENY` case**: ruleId `CWE-398` → must produce zero groups.

## Open decision — do not pick this unilaterally

Whether grouped findings should be **badged in place** (two rows, each marked
"also flagged by X") or **visually collapsed** (one row, expandable).

Badging is additive and keeps the finding count honest. Collapsing reads
better but changes what "N findings" means in the summary, which touches a
number the README quotes. Ask Alan before implementing collapse.

Recommended default: badge first.

## Verification

```
python3 examples/fixtures/verify_dedup_render.py
```

All five stages must pass. Then re-run and confirm stage 5 still passes —
that is the invariant guarding against the display layer creeping into
scoring.

Note the limits of stage 4: it checks that both tool names and a
cross-tool phrase appear in the HTML. That is a floor, not a design spec. It
can be satisfied by output that is technically correct and visually useless.
Read the rendered report before calling it done.

## What this does not do

- Does not change ROC-AUC, concentration, or any published metric. Those are
  properties of the ranking, and the ranking is untouched.
- Does not address the documented open problem of cross-function source/sink
  pairs. Still open.
- Does not validate any language beyond C/C++.
