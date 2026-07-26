# Session handoff — 2026-07-26

Things the next session needs that are NOT already in HANDOFF.md or
VALIDATION.md. Read HANDOFF.md §0 items first; this is the residue.

## 1. WHAT WAS IN FLIGHT WHEN THE SESSION ENDED

One command, interrupted mid-run: the **stratification-refinement check** for
item 0j. It was going to re-run the size-matched precision test at 10 / 50 / 200
strata to see whether the 1.5x effect decays as strata refine.

**Do this first.** It decides whether the README's last remaining number stands.
The script fragment is straightforward — group units by log-LOC strata, sample a
single-tool control per multi-tool unit within stratum, compare rates, vary K.

If the effect decays toward the logistic's null: the 1.5x goes.
If it survives at K=200: suspect the logistic's *linear-in-n_tools*
specification instead — n_tools runs 1..6 and may not be linear in log-odds.
Try it as a categorical factor before concluding either way.

## 2. THE THING I WOULD HAVE DONE NEXT, AND WHY

Beyond 0j, nothing. 0i is closed as a terminal answer, and I would NOT have
opened a new direction. My read is that the project has reached a natural
resting point: the machinery is correct and tested, and the ranking claim is
honestly unproven. The remaining open items (0c/0f/0h) are small and
independent.

If 0j goes against the 1.5x, the right move is the fourth README correction —
removing the number and leaving the correctness inventory as the only claim.
That would be a smaller README but a fully defensible one.

## 3. WHAT SHAPED DECISIONS BUT DID NOT MAKE IT INTO A RECORD

**a. The pattern that should govern the next session's scepticism.**
Five claims died this session, each in the same way: a number looked solid until
a *better-matched control* was applied. 0.755 vs ManualDown. The effort-aware win
vs ManualUp. IFA/PMI vs size-matched random. The 6.4x function-level gain vs
effort-normalisation. And now possibly the 1.5x vs continuous covariate. **The
failure was never the measurement; it was always the comparator.** Before
believing any new number here, ask what it is being compared *to*, and whether a
trivial size-correlated baseline would score the same.

**b. Why I trusted decile matching too readily.**
I used decile matching because it was easy to implement without numpy. That is a
tooling constraint that silently became a methodological choice. The literature
(Kronmal) recommends covariate adjustment, and when I finally implemented it, it
disagreed. **Do not let the absence of numpy/scipy on this machine select the
statistical method.** Pure-Python IRLS works fine — it is in
`scratchpad/run_0i.py` and took ~2 minutes on 14,656 units.

**c. An unexplored thread with real teeth.**
semgrep's rule metadata declares `source-rule-url` pointing at FindSecBugs — its
rules are DERIVED from FindSecBugs rules. Measured: 30.4% of OWASP co-located
rule pairs are a rule agreeing with its own ancestor. Filed as 0f. But the
broader question is unasked: **how much of the entire static-analysis ecosystem
is ported rules?** If rule porting is widespread, "independent tools" is a much
weaker notion than the whole premise assumes, and the diversity argument is
undermined at a level below tool selection. Nobody has measured this. It could
matter more than anything else in the backlog.

**d. Scratchpad artifacts worth keeping.**
`scratchpad/` has the Lipp dataset (`lipp/`), OWASP Benchmark built
(`owasp/BenchmarkJava-master`, with `target/classes`), Struts built
(`struts/struts-main`), and captured SARIF from every scanner run. Rebuilding
those cost most of a session. The analysis scripts —
`run_0i.py`, `manualup.py`, `size_confound.py`, `effort_aware.py`,
`granularity_signal.py`, `rule_lineage.py`, `direction_b.py` — are the working
record of every measurement quoted in VALIDATION.md. **They are in a temp
directory and will not survive a reboot.** If any of it matters, copy it out.

**e. A judgement call I made that could reasonably go the other way.**
I kept the correctness inventory in the README ("What has been checked") even
though it is not a performance claim, on the grounds that it is honest and
substantive. An equally defensible view is that a README should say what a tool
DOES and not enumerate its own bug fixes. If the 1.5x falls, that section becomes
the entire evidential content of the README, and it may read as
compensating. Worth revisiting then.

## 4. STATE AT HANDOFF
- working tree clean, local == origin/main
- harness: 67 checks passing; render harness clean; CLI ok
- README carries no retired figure; its one remaining number (1.5x) is
  flagged SUSPECT pending 0j
- tools installed this session: openjdk@17, maven, spotbugs, findsecbugs,
  semgrep (venv), codeql (unusable — arm64/Rosetta)
