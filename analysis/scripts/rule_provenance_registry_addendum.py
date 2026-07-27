#!/usr/bin/env python3
"""0f REGISTRY ARM — ADDENDUM. Two corrections to the first run.

(1) S1 UNDERCOUNTED DECLARED PROVENANCE. The first run's upstream-host list was
    built from the tool names semgrep's FAQ mentions, and matched hosts like
    `bandit.readthedocs.io` and `brakemanscanner.org`. But most declarations
    point at a GitHub REPO, not a docs site — `pycqa/bandit`,
    `presidentbeef/brakeman`, `nodesecurity/eslint-plugin-security` — so they
    were missed. This restates S1 over ALL declared upstream tools.

(2) THE RECALL DENOMINATOR WAS WRONG. S3/S4 were tested against a FindSecBugs
    reference set only, but their recall was reported over the whole S1 set,
    which includes rules declaring Bandit, gosec and others. Those rules could
    never have been matched — no reference corpus exists for them here. The fair
    denominator is the FINDSECBUGS-DECLARED SUBSET, and the rest must be
    reported as NEVER TESTED rather than as misses.

Also bootstraps the capture-recapture interval (asymptotic SE is documented as
performing poorly at small/moderate n).
"""
import sys, os, re, json, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rule_provenance_registry as R          # noqa: E402

random.seed(0xF0F)

# Upstream ANALYSIS TOOLS, matched on repo path or docs host. Deliberately
# excludes documentation sites that are not tools (expressjs.com,
# nodebestpractices, youtube, pypi) and semgrep's own self-links.
UPSTREAM_TOOLS = {
    "FindSecBugs": ["find-sec-bugs.github.io", "find-sec-bugs/"],
    "Bandit":      ["pycqa/bandit", "bandit.readthedocs.io"],
    "Brakeman":    ["presidentbeef/brakeman", "brakemanscanner"],
    "gosec":       ["securego/gosec"],
    "eslint-plugin-security": ["nodesecurity/eslint-plugin-security", "eslint.org"],
    "gixy":        ["yandex/gixy"],
    "hadolint":    ["hadolint/hadolint"],
    "RuboCop":     ["rubocop"],
    "PMD":         ["pmd.github.io", "pmd.sourceforge"],
    "Checkstyle":  ["checkstyle.org", "checkstyle.sourceforge"],
    "SpotBugs":    ["spotbugs.readthedocs", "spotbugs.github"],
}
NOT_A_TOOL = ["semgrep.dev", "expressjs.com", "nodebestpractices", "youtube.com",
              "pypi.org", "nodesecroadmap", "cwe.mitre.org", "owasp.org"]


def upstream_of(url):
    u = str(url).lower()
    for tool, pats in UPSTREAM_TOOLS.items():
        if any(p in u for p in pats):
            return tool
    if any(p in u for p in NOT_A_TOOL):
        return None
    return "__unclassified__" if "http" in u else None


def main():
    seen, rules = set(), []
    for p in R.PACKS:
        for r in R.parse_rules(R.fetch_pack(p)):
            if r["id"] not in seen:
                seen.add(r["id"])
                rules.append(r)
    n = len(rules)
    print("=" * 78)
    print("0f ADDENDUM — corrected declared set, fair recall denominator,")
    print("bootstrapped interval.  ONE REGISTRY (semgrep), NOT the ecosystem.")
    print("=" * 78)
    print(f"\npopulation: {n} distinct registry rules")

    # ---- (1) full declared set ----
    decl = {}
    for i, r in enumerate(rules):
        up = upstream_of(r["source_rule_url"])
        if up:
            decl[i] = up
    byup = Counter(decl.values())
    print("\n" + "=" * 78)
    print("1. DECLARED PROVENANCE, BY UPSTREAM (corrected)")
    print("=" * 78)
    for k, v in byup.most_common():
        print(f"  {k:26} {v:5}  ({100*v/n:5.2f}% of registry)")
    old_s1 = 73
    print(f"\n  S1 as first reported : {old_s1}/{n} = {100*old_s1/n:5.2f}%")
    print(f"  S1 CORRECTED         : {len(decl)}/{n} = {100*len(decl)/n:5.2f}%")
    print(f"  previously missed    : {len(decl)-old_s1} rules, because their"
          f" declaration points at a\n                         GitHub repo"
          f" rather than a docs host.")

    # recompute the other signals on the same population
    fsb_txt, fsb_cwe = R.load_fsb()
    fsb_norm = {R.norm_id(k): k for k in fsb_txt}
    fsb_tok = {k: R.toks(v) for k, v in fsb_txt.items()}
    S2, S3, S4 = set(), set(), set()
    for i, r in enumerate(rules):
        if any(R.host_hit(r[f]) for f in ("references", "source", "license")):
            S2.add(i)
        seg = R.norm_id(r["id"].split(".")[-1])
        for fn in fsb_norm:
            if seg == fn or (len(fn) >= 8 and fn in seg) or \
               (len(seg) >= 8 and seg in fn):
                S3.add(i); break
        rt = R.toks(r["message"])
        if rt and max((R.jacc(rt, t) for t in fsb_tok.values()), default=0) >= 0.5:
            S4.add(i)
    S1 = set(decl)
    union = S1 | S2 | S3 | S4
    print("\n" + "=" * 78)
    print("2. UNION RESTATED WITH THE FULL DECLARED SET")
    print("=" * 78)
    print(f"  S1 corrected {len(S1):5}   S2 {len(S2):5}   S3 {len(S3):5}   S4 {len(S4):5}")
    print(f"  union(S1..S4) {len(union):5}/{n} = {100*len(union)/n:5.2f}%"
          f"   (was 105 = 18.75%)")

    # ---- (2) fair recall denominator ----
    fsb_declared = {i for i, u in decl.items() if u == "FindSecBugs"}
    other_declared = set(S1) - fsb_declared
    print("\n" + "=" * 78)
    print("3. RECALL, ON THE ONLY DENOMINATOR IT CAN FAIRLY BE MEASURED ON")
    print("=" * 78)
    print(f"""  S3 and S4 compare against a FINDSECBUGS reference set only. Rules
  declaring any OTHER upstream could never match, so scoring them as misses
  overstates the failure. Fair denominator = FindSecBugs-declared rules.

  FindSecBugs-declared (testable)     {len(fsb_declared):5}
  other upstreams (NEVER TESTED)      {len(other_declared):5}"""
          f"  = {100*len(other_declared)/max(1,len(S1)):.1f}% of the declared set")
    for lbl, sig in (("S2 attribution", S2), ("S3 rule-id match", S3),
                     ("S4 text similarity", S4)):
        a = len(sig & fsb_declared)
        b = len(sig & other_declared)
        print(f"    {lbl:22} on FSB-declared {a:3}/{len(fsb_declared)} "
              f"= {100*a/max(1,len(fsb_declared)):5.1f}%"
              f"   | on never-tested upstreams {b:3} (uninterpretable)")
    print(f"""
  So the earlier "S3 recovers 30.1%" was computed over a denominator that
  included {len(other_declared)} rules it had no reference set for. Corrected, S3 recovers
  {100*len(S3 & fsb_declared)/max(1,len(fsb_declared)):.1f}% of FindSecBugs-derived rules. S4 still recovers
  {100*len(S4 & fsb_declared)/max(1,len(fsb_declared)):.1f}% — the rewriting finding is UNAFFECTED, because it was
  always measured against the FindSecBugs text and now has the right denominator.""")

    # ---- capture-recapture on a COHERENT population ----
    print("\n" + "=" * 78)
    print("4. CAPTURE-RECAPTURE, ON THE FINDSECBUGS SUB-POPULATION ONLY")
    print("=" * 78)
    n1, n2 = len(fsb_declared), len(S3)
    m = len(fsb_declared & S3)
    chap = ((n1 + 1) * (n2 + 1) / (m + 1)) - 1 if m >= 0 else None
    print(f"""  Both passes must address the SAME population. Pass 1 = declares
  FindSecBugs; pass 2 = rule-id matches a FindSecBugs pattern. Neither can see
  a Bandit- or gosec-derived rule, so the target is FindSecBugs-derived rules
  IN THIS REGISTRY, not derived rules in general.
    n1 (declares FSB) = {n1}   n2 (FSB name match) = {n2}   overlap = {m}
    Chapman N-hat = {chap:.0f}""")

    # bootstrap the interval
    idx = sorted(set(list(fsb_declared) + list(S3)))
    boots = []
    for _ in range(5000):
        samp = [idx[random.randrange(len(idx))] for _ in idx]
        c = Counter(samp)
        b1 = sum(v for k, v in c.items() if k in fsb_declared)
        b2 = sum(v for k, v in c.items() if k in S3)
        bm = sum(v for k, v in c.items() if k in fsb_declared and k in S3)
        boots.append(((b1 + 1) * (b2 + 1) / (bm + 1)) - 1)
    boots.sort()
    lo, hi = boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]
    import statistics as st
    sd = st.pstdev(boots)
    print(f"""    BOOTSTRAP 95% CI (5,000 resamples) : [{lo:.0f}, {hi:.0f}]
    bootstrap SD {sd:.0f}   CV = {100*sd/max(1e-9,chap):.0f}%
  Asymptotic SE is documented as performing poorly at small and moderate n, so
  the bootstrap interval is quoted in preference to it.""")
    json.dump({"population": n, "declared_by_upstream": dict(byup),
               "s1_corrected": len(S1), "union_corrected": len(union),
               "fsb_declared": n1, "s3": n2, "overlap": m,
               "chapman": chap, "boot_ci95": [lo, hi], "boot_sd": sd},
              open(os.path.join(HERE, "..", "results",
                                "0f_registry_addendum.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
