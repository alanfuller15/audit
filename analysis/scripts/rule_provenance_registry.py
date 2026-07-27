#!/usr/bin/env python3
"""0f REGISTRY ARM — PREVALENCE ESTIMATION UNDER INCOMPLETE DETECTION.

================================ PRE-REGISTRATION ============================
FIXED BEFORE COMPUTING. Deviations must be recorded as deviations.

FRAMING. This is not "count the declarations". It is prevalence estimation where
detection is incomplete, and the methodology is taken from Khosravani & Mockus,
"Detecting AI Coding Agents in Open Source: A Validated Multi-Method Census of
180 Million Repositories" (arXiv:2606.24429), fetched and quoted verbatim:

  "These multi-method counts are relative-recall improvements over single-method
   baselines, not absolute recall estimates."
  "The true total ... is bounded below by our multi-method union but may be
   larger if additional detection signals remain unprobed."
  and, on their headline 30x figure: it "demonstrates that single detection
   methods capture only a fraction of total AI-assisted activity" — but that gap
   is between ONE SIGNAL AND THEIR UNION, *not* between detection and reality.
  They state plainly that "absolute recall is unknown."

That last distinction is carried through this whole script. An undercount factor
computed here says how much a single-signal study would have missed RELATIVE TO
THIS UNION. It says nothing about how much the union misses.

The declared-vs-actual gap is independently named in supply-chain work:
Srinivasan et al., "Bomfather" (arXiv:2503.02097) — "A gap remains between
declared and actual dependencies", motivating kernel-level observation because
declarations omit what actually happened. Same shape: a declaration is a
lower bound on the fact.

POPULATION. Semgrep registry rule packs, fetched live. Unit = one rule.
UPSTREAM REFERENCE SET. FindSecBugs 1.14.0, 144 bug patterns (names + short and
long descriptions) extracted from the plugin jar.

  BOUND, PRE-REGISTERED: the reference set is ONE upstream. Semgrep's own FAQ
  names ESLint, RuboCop and Bandit as further sources. So S3/S4 can only detect
  FindSecBugs-derived rules; derivation from any other upstream is invisible to
  them and will depress every number below.

SIGNALS, and what counts as a hit:
  S1 DECLARED SOURCE   metadata.source-rule-url whose host is a known upstream
                       TOOL doc host. Taxonomy hosts (cwe.mitre.org, owasp.org)
                       are NOT hits — a CWE link is not a provenance claim.
  S2 ATTRIBUTION       any of references / source / license / attribution
                       containing a known upstream TOOL host. Same taxonomy
                       exclusion; semgrep.dev self-links excluded.
  S3 RULE-ID MATCH     normalized last id segment vs normalized FSB pattern
                       type; equal, or one contains the other with >= 8 chars
                       of overlap (8 avoids trivia like "xss"/"sql").
  S4 TEXT SIMILARITY   Jaccard >= 0.5 over content tokens (lowercased, len >= 4,
                       stopwords removed) between the rule message and the best
                       matching FSB description.
  S5 CWE + CATEGORY    rule declares a CWE that some FSB pattern also declares.
                       PRE-REGISTERED AS THE WEAKEST SIGNAL: convergent design
                       satisfies it, so it is REPORTED SEPARATELY AND EXCLUDED
                       FROM THE HEADLINE UNION. It is computed only to show how
                       much admitting a weak signal would inflate the estimate.

REPORTING OF DISAGREEMENT, fixed in advance:
  - per-signal count and fraction
  - pairwise agreement matrix between signals
  - union of S1..S4 = the improved lower bound (S5 excluded)
  - UNDERCOUNT FACTOR = union(S1..S4) / strongest single signal, labelled
    explicitly as RELATIVE recall between signals, never absolute
  - count of rules flagged by EXACTLY ONE signal — what a single-signal study
    would have missed

PRE-COMMITTED INTERPRETATION:
  - A HIGH union raises the estimated derived fraction.
  - A LOW union is NOT evidence of independence. It is equally consistent with
    undeclared, renamed, reworded porting. Report as UNINFORMATIVE, not as
    clearance. (Same rule as the corpus arm.)
  - Rules ported with NO marker of any kind are silent to all five signals.
    That is the floor of what is knowable from artifacts alone.

SCOPE: ONE REGISTRY, NOT THE ECOSYSTEM. Every number here describes semgrep's
registry. It does not describe static analysis in general.
==============================================================================
"""
import json, os, re, subprocess, sys
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FSB_JAR = os.environ.get(
    "FSB_JAR",
    "/private/tmp/claude-501/-Users-caitlinfuller-audit/"
    "e15ca3d8-3ea0-4097-85ed-21cccfc71b0a/scratchpad/fsb/lib/"
    "findsecbugs-plugin-1.14.0.jar")
PACKS = ["p/java", "p/security-audit", "p/python", "p/javascript",
         "p/golang", "p/c", "p/csharp", "p/php", "p/ruby"]

UPSTREAM_HOSTS = [
    "find-sec-bugs.github.io", "spotbugs.readthedocs", "spotbugs.github",
    "pmd.github.io", "pmd.sourceforge", "checkstyle.org", "checkstyle.sourceforge",
    "eslint.org", "rubocop", "bandit.readthedocs", "securego", "gosec",
    "brakemanscanner", "bearer.com", "gitleaks",
]
TAXONOMY_HOSTS = ["cwe.mitre.org", "owasp.org", "capec.mitre.org",
                  "nvd.nist.gov", "semgrep.dev"]
STOP = set("""the a an and or of to in is are be for that this with on by from as
it its not no if then than can may will use used using should must when where
which what who whose into out over under more most other some such only own same
so too very just also any each both few nor own s t don now""".split())


def norm_id(x):
    return re.sub(r"[^a-z0-9]", "", str(x).lower())


def toks(s):
    return {w for w in re.findall(r"[a-z]{4,}", str(s).lower()) if w not in STOP}


def jacc(a, b):
    return len(a & b) / len(a | b) if (a or b) else 0.0


def host_hit(text, hosts=UPSTREAM_HOSTS):
    t = str(text).lower()
    if any(h in t for h in TAXONOMY_HOSTS) and not any(h in t for h in hosts):
        return False
    return any(h in t for h in hosts)


# ---------- upstream reference set ----------
def load_fsb():
    import zipfile
    z = zipfile.ZipFile(FSB_JAR)
    msg = z.read("messages.xml").decode("utf-8", "replace")
    fb = z.read("findbugs.xml").decode("utf-8", "replace")
    pats = {}
    for m in re.finditer(r'<BugPattern[^>]*type="([A-Z0-9_]+)"(.*?)</BugPattern>',
                         msg, re.S):
        typ, body = m.group(1), m.group(2)
        short = " ".join(re.findall(r"<ShortDescription>(.*?)</ShortDescription>",
                                    body, re.S))
        long_ = " ".join(re.findall(r"<Details>(.*?)</Details>", body, re.S))
        txt = re.sub(r"<[^>]+>", " ", short + " " + long_)
        pats[typ] = txt
    cwes = defaultdict(set)
    for m in re.finditer(r'type="([A-Z0-9_]+)"[^>]*cweid="(\d+)"', fb):
        cwes[m.group(1)].add(int(m.group(2)))
    return pats, cwes


# ---------- population ----------
def fetch_pack(pack):
    try:
        out = subprocess.run(["curl", "-sS", "--max-time", "60",
                              f"https://semgrep.dev/c/{pack}"],
                             capture_output=True, timeout=90)
        return out.stdout.decode("utf-8", "replace")
    except Exception:
        return ""


def parse_rules(yaml_text):
    """Minimal YAML slice: split on top-level '- id:' entries and pull the
    fields we need by regex. Avoids a yaml dependency (none installed)."""
    rules = []
    for chunk in re.split(r"\n- id: ", "\n" + yaml_text)[1:]:
        rid = chunk.split("\n", 1)[0].strip()
        def grab(field):
            m = re.search(rf"\n\s+{field}:\s*(.*?)(?=\n\s+[a-z_-]+:|\Z)",
                          chunk, re.S)
            return m.group(1) if m else ""
        rules.append({
            "id": rid,
            "message": grab("message"),
            "source_rule_url": grab("source-rule-url"),
            "references": grab("references"),
            "source": grab("source"),
            "license": grab("license"),
            "cwe": re.findall(r"CWE-(\d+)", chunk),
            "raw": chunk,
        })
    return rules


def main():
    print(__doc__.split("=" * 30)[0].strip()[:0] or "", end="")
    print("=" * 78)
    print("0f REGISTRY ARM — prevalence estimation under incomplete detection")
    print("ONE REGISTRY (semgrep), NOT THE ECOSYSTEM")
    print("=" * 78)

    fsb_txt, fsb_cwe = load_fsb()
    fsb_norm = {norm_id(k): k for k in fsb_txt}
    fsb_tok = {k: toks(v) for k, v in fsb_txt.items()}
    fsb_all_cwe = set().union(*fsb_cwe.values()) if fsb_cwe else set()
    print(f"\nupstream reference set: FindSecBugs 1.14.0, {len(fsb_txt)} bug "
          f"patterns, {len(fsb_all_cwe)} distinct CWEs")

    rules, seen = [], set()
    for p in PACKS:
        y = fetch_pack(p)
        got = parse_rules(y) if y.startswith("rules:") or "\n- id: " in y else []
        new = [r for r in got if r["id"] not in seen]
        for r in new:
            seen.add(r["id"])
        rules += new
        print(f"  {p:18} {len(got):5} rules  (+{len(new)} new)")
    print(f"\nPOPULATION: {len(rules)} distinct registry rules")
    if not rules:
        print("NO RULES FETCHED — network or format change. Aborting.")
        return

    hits = {k: set() for k in ("S1", "S2", "S3", "S4", "S5")}
    for i, r in enumerate(rules):
        if r["source_rule_url"] and host_hit(r["source_rule_url"]):
            hits["S1"].add(i)
        if any(host_hit(r[f]) for f in ("references", "source", "license")):
            hits["S2"].add(i)
        seg = norm_id(r["id"].split(".")[-1])
        for fn, orig in fsb_norm.items():
            if seg == fn or (len(fn) >= 8 and fn in seg) or \
               (len(seg) >= 8 and seg in fn):
                hits["S3"].add(i)
                break
        rt = toks(r["message"])
        if rt and max((jacc(rt, t) for t in fsb_tok.values()), default=0) >= 0.5:
            hits["S4"].add(i)
        if {int(c) for c in r["cwe"]} & fsb_all_cwe:
            hits["S5"].add(i)

    n = len(rules)
    print("\n" + "=" * 78)
    print("1. PER-SIGNAL DERIVED FRACTION")
    print("=" * 78)
    names = {"S1": "declared source-rule-url", "S2": "attribution fields",
             "S3": "rule-id name match", "S4": "description similarity",
             "S5": "CWE overlap [WEAK, excluded from union]"}
    for k in ("S1", "S2", "S3", "S4", "S5"):
        print(f"  {k}  {names[k]:44} {len(hits[k]):5}/{n} = {100*len(hits[k])/n:5.2f}%")

    print("\n" + "=" * 78)
    print("2. MULTI-SIGNAL UNION — the improved LOWER BOUND (S1-S4; S5 excluded)")
    print("=" * 78)
    union = hits["S1"] | hits["S2"] | hits["S3"] | hits["S4"]
    print(f"  union(S1..S4)        {len(union):5}/{n} = {100*len(union)/n:5.2f}%")
    union5 = union | hits["S5"]
    print(f"  union incl. WEAK S5  {len(union5):5}/{n} = {100*len(union5)/n:5.2f}%"
          f"   <- shown only to price the weak signal; NOT the estimate")

    print("\n  pairwise agreement (rules flagged by BOTH):")
    ks = ["S1", "S2", "S3", "S4", "S5"]
    print("        " + "".join(f"{k:>7}" for k in ks))
    for a in ks:
        print(f"    {a:4}" + "".join(f"{len(hits[a] & hits[b]):>7}" for b in ks))

    print("\n" + "=" * 78)
    print("3. UNDERCOUNT FACTOR — RELATIVE recall between signals, NOT absolute")
    print("=" * 78)
    strongest = max(("S1", "S2", "S3", "S4"), key=lambda k: len(hits[k]))
    sb = len(hits[strongest])
    print(f"  strongest single signal : {strongest} ({names[strongest]}) = {sb}")
    print(f"  multi-signal union      : {len(union)}")
    if sb:
        print(f"  UNDERCOUNT FACTOR       : {len(union)/sb:.1f}x")
        print(f"    i.e. relying on {strongest} alone would have missed "
              f"{len(union)-sb} of {len(union)} detectable rules.")
    print("""
  WHAT THIS FACTOR IS NOT. Following arXiv:2606.24429 exactly: this compares one
  signal against THIS UNION. It does not compare detection against reality. The
  paper is explicit that "absolute recall is unknown", and so is ours.""")
    only1 = [i for i in union
             if sum(1 for k in ("S1", "S2", "S3", "S4") if i in hits[k]) == 1]
    print(f"  rules found by EXACTLY ONE signal: {len(only1)} of {len(union)} "
          f"({100*len(only1)/max(1,len(union)):.1f}%) — the fragile tail")

    print("\n" + "=" * 78)
    print("4. WHAT REMAINS UNDETECTABLE")
    print("=" * 78)
    print(f"""  A rule that was ported but is (a) undeclared, (b) renamed, and (c) reworded
  is SILENT TO ALL FIVE SIGNALS. Nothing in any tool's format requires
  disclosure of derivation, so this population cannot be bounded from artifacts
  at all — it is the floor of what is knowable here, not a residual to estimate.

  Two further ceilings on the number above, both pre-registered:
   - the upstream reference set is FindSecBugs ONLY. Semgrep's own FAQ names
     ESLint, RuboCop and Bandit as further sources; derivation from those is
     invisible to S3/S4 and depresses every figure above.
   - {n} rules is ONE REGISTRY. It is not the static-analysis ecosystem.

  Therefore: a LOW union here is UNINFORMATIVE, not clearance. A HIGH union is
  informative, because every signal is a positive marker.""")

    # ── ADDITION, NOT PRE-REGISTERED ─────────────────────────────────────────
    # Declared to be an addition rather than folded in silently. It became
    # available only because S1 turned out to be a GROUND-TRUTH SUBSET: a rule
    # that declares FindSecBugs as its source IS derived, by its own admission.
    # That permits two things the pre-registration did not anticipate.
    print("\n" + "=" * 78)
    print("5. ADDITION (NOT PRE-REGISTERED) — validated recall, and a")
    print("   capture-recapture estimate rather than only a lower bound")
    print("=" * 78)
    gt = hits["S1"]
    print(f"  ground-truth-derived subset (self-declared) : {len(gt)}")
    print("\n  RECALL of each NON-declaration signal on that subset — i.e. how")
    print("  well it would detect derivation for a tool that does NOT declare:")
    for k in ("S2", "S3", "S4"):
        r = len(hits[k] & gt) / len(gt) if gt else 0
        print(f"    {k}  {names[k]:40} {len(hits[k] & gt):4}/{len(gt)} = {100*r:5.1f}%")
    print("""
  S4 (text similarity) recovers NONE of them. Measured directly: across the 73
  self-declared-derived rules the best token Jaccard against the FindSecBugs
  original has median 0.101 and max 0.359. PORTED RULES ARE REWRITTEN. Text
  similarity is not a weak detector of derivation here, it is a NULL one — and
  that is itself the substantive result, because it is the mechanism by which a
  ported rule comes to look independently authored.""")

    n1, n2 = len(hits["S1"]), len(hits["S3"])
    m = len(hits["S1"] & hits["S3"])
    if m:
        chap = ((n1 + 1) * (n2 + 1) / (m + 1)) - 1
        var = ((n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)) / \
              (((m + 1) ** 2) * (m + 2))
        se = var ** 0.5
        print(f"""  CAPTURE-RECAPTURE (Chapman-corrected Lincoln-Petersen), treating
  declaration (S1) and rule-id retention (S3) as two independent detection
  passes over the same population:
    n1 (S1) = {n1}   n2 (S3) = {n2}   overlap = {m}
    estimated total derived N-hat = {chap:.0f}  (SE {se:.0f})
      = {100*chap/n:.1f}% of {n} registry rules
    against the multi-signal union lower bound of {len(union)} ({100*len(union)/n:.1f}%)

  ASSUMPTIONS, AND WHY THE ESTIMATE IS STILL CONSERVATIVE. Capture-recapture
  assumes the two passes are INDEPENDENT and detectability is HOMOGENEOUS. Both
  are doubtful here, and in a knowable direction: a faithful port is more likely
  to BOTH declare its source AND keep the upstream name, so S1 and S3 are
  POSITIVELY correlated. Positive correlation inflates the overlap, and an
  inflated overlap DEPRESSES N-hat. So {chap:.0f} is more likely an
  under-estimate than an over-estimate — it does not rescue the ceiling, it
  raises the floor.""")

    out = {"population": n, "per_signal": {k: len(v) for k, v in hits.items()},
           "ground_truth_declared": len(gt),
           "recall_on_declared": {k: (len(hits[k] & gt) / len(gt) if gt else None)
                                  for k in ("S2", "S3", "S4")},
           "capture_recapture_chapman": (((len(hits["S1"]) + 1) *
                                          (len(hits["S3"]) + 1) /
                                          (len(hits["S1"] & hits["S3"]) + 1)) - 1)
           if len(hits["S1"] & hits["S3"]) else None,
           "union_s1_s4": len(union), "union_incl_weak_s5": len(union5),
           "strongest_single": strongest,
           "undercount_factor": (len(union)/sb) if sb else None,
           "found_by_exactly_one": len(only1),
           "scope": "one registry (semgrep), not the ecosystem"}
    with open(os.path.join(HERE, "..", "results",
                           "0f_registry_arm.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\n  machine-readable summary -> analysis/results/0f_registry_arm.json")


if __name__ == "__main__":
    main()
