# audit — where it stands

*Plain-language summary, 26 July 2026. No jargon, no numbers you have to take on faith.*

*This is the friendly entry point. The README is the tool's own front door;
`VALIDATION.md` is the full evidence log. This sits in front of both.*

---

## The one-sentence version

You have a working tool that combines the output of several security scanners
and flags the code they agree on — and you now have unusually honest evidence
about what that agreement is and isn't worth.

---

## What the tool actually does

Security scanners are noisy. Point one at real code and it produces hundreds of
warnings, most of them false alarms. That's the single most-cited reason teams
stop using them.

`audit` runs several scanners, matches up the warnings that describe the same
problem, and pushes the ones that multiple tools independently flagged toward
the top of the list. The idea is simple: if two tools built on different
principles both flag the same spot, that spot is more likely to be a real bug.

It reads a standard format (SARIF), so it isn't tied to any particular scanner.
The one-click GitHub Action runs two C/C++ scanners. Java works too, but by
feeding it scanner output yourself from the command line — there's no
ready-made Java setup.

---

## What you proved works

These are things that were measurably broken and are now measurably fixed. Each
was found by running real scanners on real code — none would have shown up in
testing against made-up examples.

**The tool couldn't detect agreement at all.** The two scanners it ships with
could never be matched up, no matter what code you ran them on. A design flaw in
how findings were identified made it structurally impossible. Fixed — but read
the next section, because fixing it revealed something more awkward.

**Findings were vanishing silently.** Three separate bugs quietly deleted real
results. The worst affected one scanner (flawfinder) on every run: on the zlib
codebase it destroyed about 17% of what that scanner reported, with no error
message. That 17% is what was measured on that one library with that one
scanner — it isn't a general rate, and the other scanners lose different amounts
for different reasons. All three bugs fixed and covered by tests.

**Two names for one scanner counted as two opinions.** Some tools are forks or
plugins of other tools. The tool now knows the difference, so a scanner can't
appear to corroborate itself.

**Scanners that disagree about file paths now say so.** Two tools can describe
the same file differently, which silently produced "zero agreement" with no
explanation. It now tells you that's what happened, rather than leaving you with
an unexplained zero.

**Reading the scanners correctly.** The tool now uses the structured,
authoritative field where scanners record what kind of bug they found, instead
of guessing from descriptive text.

The main test suite holds 67 checks and they all pass. A second, smaller suite
covering how the report renders has 4 passing and 4 known gaps that are recorded
rather than hidden.

---

## The awkward part, which deserves its own section

Fixing the matching problem didn't produce agreement. It removed the *obstacle*
to agreement, and then real code showed there wasn't much agreement to find.

Run the two default scanners over a real library and they still agree on
essentially nothing — not because of a bug, but because they look for different
kinds of problem. One hunts risky string handling; the other hunts null pointers
and arithmetic mistakes. They co-locate on the same lines occasionally and mean
different things when they do.

This has now been tried three times, in three configurations, with three
different proximate causes, and it keeps coming out the same way. Adding a third
scanner produced two agreements in over a thousand findings — and both were
between the two *most similar* tools, in test code, not library source.

The uncomfortable logic underneath: the premise wants tools that are
**methodologically different**, because different methods have different blind
spots. But the mechanism requires them to point at **the same line**. Those pull
against each other. The more different two tools are, the less likely they are
to describe the same bug in the same place. **Buying another scanner does not
fix this**, which is worth knowing before spending money on one.

---

## What you proved *doesn't* work — and this is the valuable part

You started with three impressive-looking numbers in the README. All three are
gone, because each failed when tested against the right comparison.

The pattern was the same every time: **a number looked convincing until it was
compared against a fair baseline.**

The clearest example: the headline claim was that the tool ranks vulnerable
files higher about 3 times out of 4. That's true — but a stupid rule that just
sorts files by *size*, reading no scanner output at all, does better. Big files
have more bugs. The tool wasn't beating the obvious.

**Why this is worth something.** Most tools in this space publish the flattering
number and stop. You now know which of your claims survive scrutiny, because you
went looking for the ways they might not. That's a defensible position; the
alternative was an indefensible one you hadn't noticed yet.

---

## The fourth correction, which went differently

The last surviving number — the 1.5x below — was itself under suspicion, and
the obvious guess was that it would die like the other three.

It didn't. Tested against progressively stricter size controls, the number
didn't move. What turned out to be wrong was the *certainty* attached to it: the
README had claimed odds of less than one in ten thousand that the result was
chance, and that came from a test that only shuffled one of the two groups being
compared. Done properly, it's a marginal result — real, but nothing like as
certain as advertised.

So the correction removed a claim about confidence while keeping the finding.
That's a different shape from the first three, and worth noticing: **the flaw
wasn't the comparison that time, it was the test.** It had gone unexamined
because effect size kept being the thing under suspicion.

---

## What survives

**The underlying idea is validated — by someone else.** A published academic
study (Lipp et al., 2022) tested six scanners against 192 confirmed real-world
vulnerabilities across 27 open-source projects and found that combining tools
catches meaningfully more than the best single tool. That's their result on
their data. It's why your tool is built the way it is.

**One thing you measured yourself.** Using that same real-world data: code
flagged by two or more scanners is about **1.5 times** more likely to contain a
genuine, catalogued vulnerability than comparable code flagged by one.

Three honest caveats, all now printed in the README:

- **It's a threshold, not a dial.** All the benefit comes from going from one
  scanner to two. Three is no better than two, and four or more is, if anything,
  slightly worse — though too few cases to say that with confidence. "More tools
  agreeing" is not a confidence score.
- **The range is wide.** Nine projects were involved. A different nine might
  have shown anywhere from no effect at all to about 2.6x. It's real, but it's
  not a number to plan around.
- **The signal existing doesn't mean the ranking is useful.** Agreement carries
  information. Turning that information into a good "review these first" list is
  a separate problem, and that part is unproven.

---

## The honest state, in one paragraph

The machinery is correct and tested. The premise it's built on is validated by
published research. Agreement between scanners does carry a real signal, modest
in size and measured carefully. Whether that signal can be turned into a ranking
that actually saves a reviewer time is genuinely unknown — the versions tried so
far don't beat trivial baselines. And on real code, getting two different
scanners to agree at all has proved much harder than the premise assumes. Those
are real open questions, not defects.

---

## What's still open

**Small and clear:**

- Warn the user when scanner agreement is being driven by file size rather than
  by genuine consensus.
- When two scanners describe the same file by different paths, the tool now
  detects and reports it — but doesn't reconcile it. Reconciling is still open.

**Large and interesting:**

There's a question nobody in the field appears to have measured.

Security scanners copy rules from each other, and this is not a secret or an
accident — Semgrep's own documentation says its rule library includes sets
"inspired by the rules of many popular linters and checkers," naming four other
tools. It's a normal way rule libraries get built.

Which raises the problem. In your own testing, **22.6% of the places where two
scanners agreed had no independent agreement behind them at all** — the two
tools involved were running a rule and the rule it was copied from. That figure
counts *locations in the code*, not warnings or rules; those get you different
percentages, and mixing them up is easy, so it's worth saying which one you
mean. It's also a floor rather than a true figure: nothing obliges a tool to
disclose that a rule was borrowed, so the real number can only be higher.

That isn't independent corroboration. It's an echo.

The sharpest version of it: on the one *real* codebase where two different
scanners have ever agreed here, that agreement was also a rule agreeing with its
ancestor. Not a guess — one scanner's rule names the other's rule as its source,
by identical URL. Which means that on real code, the number of genuinely
independent agreements observed so far is zero.

Someone has *named* this risk before, once, in passing, about a different kind
of tool. Nobody seems to have measured it. If rule-copying is widespread, then
"independent tools agreeing" means less than this entire category of tool
assumes — and you're positioned to ask the question, because you already have
the measurement.

---

## What you'd tell someone who asked

> It combines multiple security scanners and surfaces what they agree on.
> Agreement is a real signal — code two scanners flag is about 1.5x more likely
> to have a genuine vulnerability. Whether I can turn that into a ranking that
> beats just reading the biggest files first, I haven't proven yet, and I say so
> in the README.

That last clause is the part most tools in this space can't say.
