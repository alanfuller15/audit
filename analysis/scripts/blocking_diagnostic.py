#!/usr/bin/env python3
"""0c option (a) — BLOCKING DIAGNOSTIC. Run BEFORE implementing.

Record-linkage framing: the path SUFFIX is a blocking key and "exactly one file
per side" is a cardinality-1 constraint on the block. Standard practice is to
observe the BLOCK SIZE DISTRIBUTION as the blocking criteria change, before
committing to a matching strategy — a block containing >1 record is a block the
cardinality-1 constraint will reject.

The question this answers, and it decides whether to build anything:
  at each suffix depth, how many blocks are non-singleton WITHIN one tool's
  path set? Those are the paths the uniqueness guard will refuse to match.

Uses the RAW scanner output — sg_java.sarif / sg_raw.sarif — NOT the
hand-aligned sg_java2.sarif / sg.sarif, because hand-alignment is exactly the
thing this feature would replace.
"""
import json, os
from collections import defaultdict, Counter

OLD = ("/private/tmp/claude-501/-Users-caitlinfuller-audit/"
       "e15ca3d8-3ea0-4097-85ed-21cccfc71b0a/scratchpad")


def paths_of(sarif):
    out = set()
    d = json.load(open(sarif))
    for run in d.get("runs", []):
        for r in run.get("results", []):
            for l in r.get("locations", []):
                u = ((l.get("physicalLocation") or {})
                     .get("artifactLocation") or {}).get("uri")
                if u:
                    out.add(u)
    return out


def suffix(path, depth):
    segs = [s for s in path.replace("\\", "/").split("/") if s and s != "."]
    return "/".join(segs[-depth:]) if segs else path


CORPORA = [
    ("Struts  (REAL Java)", f"{OLD}/struts/sb.sarif", "SpotBugs",
     f"{OLD}/struts/sg_raw.sarif", "semgrep(raw)"),
    ("OWASP   (synthetic Java)", f"{OLD}/owasp/sb.sarif", "SpotBugs",
     f"{OLD}/owasp/sg_java.sarif", "semgrep(raw)"),
    ("zlib    (REAL C)", f"{OLD}/lib/zf.sarif", "flawfinder",
     f"{OLD}/lib/zc.sarif", "cppcheck"),
]

MAXD = 6
for label, pa, na, pb, nb in CORPORA:
    if not (os.path.exists(pa) and os.path.exists(pb)):
        print(f"\n{label}: MISSING input, skipped")
        continue
    A, B = paths_of(pa), paths_of(pb)
    print("\n" + "=" * 78)
    print(f"{label}")
    print(f"  {na:14} {len(A):6,} distinct paths   e.g. {sorted(A)[0][:64]}")
    print(f"  {nb:14} {len(B):6,} distinct paths   e.g. {sorted(B)[0][:64]}")
    print("=" * 78)
    print(f"  {'depth':>6}{'A blocks':>10}{'A non-singleton':>17}"
          f"{'B blocks':>10}{'B non-singleton':>17}"
          f"{'both-unique matches':>21}")
    for d in range(1, MAXD + 1):
        ga, gb = defaultdict(set), defaultdict(set)
        for p in A:
            ga[suffix(p, d)].add(p)
        for p in B:
            gb[suffix(p, d)].add(p)
        nsa = sum(1 for v in ga.values() if len(v) > 1)
        nsb = sum(1 for v in gb.values() if len(v) > 1)
        # cardinality-1 on BOTH sides, key present on both
        both = [k for k in set(ga) & set(gb) if len(ga[k]) == 1 and len(gb[k]) == 1]
        ambiguous = [k for k in set(ga) & set(gb)
                     if len(ga[k]) > 1 or len(gb[k]) > 1]
        print(f"  {d:>6}{len(ga):>10,}{nsa:>10,} ({100*nsa/max(1,len(ga)):4.1f}%)"
              f"{len(gb):>10,}{nsb:>10,} ({100*nsb/max(1,len(gb)):4.1f}%)"
              f"{len(both):>14,} (+{len(ambiguous)} amb)")

    # what the CURRENT exact-match key achieves, for comparison
    exact = len(A & B)
    print(f"\n  exact path match today: {exact:,} shared paths"
          f"   ({'ZERO — this is the 0c silent failure' if exact == 0 else 'paths already align'})")

    # block-size distribution at the shallowest useful depth
    g1 = defaultdict(set)
    for p in A:
        g1[suffix(p, 1)].add(p)
    dist = Counter(len(v) for v in g1.values())
    print(f"  {na} basename block sizes: {dict(sorted(dist.items()))}")
    worst = sorted(((len(v), k) for k, v in g1.items()), reverse=True)[:3]
    for n, k in worst:
        if n > 1:
            print(f"    basename '{k}' -> {n} distinct files "
                  f"(would be REFUSED by the uniqueness guard)")
