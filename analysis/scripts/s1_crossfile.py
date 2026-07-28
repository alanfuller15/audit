#!/usr/bin/env python3
"""
S1 — form-3 candidate detection, CROSS-FILE.

Implements the amended S1 specified in docs/PROVENANCE_FIELDS.md §10.

  OLD (step 4 as written):
      restated-at  = newest blame over ONE line range in ONE file
      fires when   grounds-checked-at < restated-at

  NEW (§10):
      occurrences  = every tracked line matching the claim's SIGNATURE
      restated-at  = newest blame over ALL occurrences, in whatever file
      fires when   min(grounds-checked-at) < max(restated-at over occurrences)

The difference is the whole point: form 3's recorded instance corrected a claim
in three documents while its grounds sat un-re-derived in a fourth. The old rule
compares two timestamps that live in the same file and therefore move together.

Reports THREE numbers — fired / silent / unassessable — and exits INCONCLUSIVE,
not clean, whenever unassessable > 0 (POPULATION_PILOT.md §5).

Usage:
    python3 analysis/scripts/s1_crossfile.py
    python3 analysis/scripts/s1_crossfile.py --at <commit>
    python3 analysis/scripts/s1_crossfile.py --at <commit> --only C07 \
            --grounds-checked-at 2026-07-26T02:52:03-08:00
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

CLAIMS = "docs/claims.json"
# Occurrence search is restricted to prose the corpus treats as claim-bearing.
# Widening this is a spec decision, not a flag: see §10.4 FP-A.
PATHSPECS = ["*.md"]


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout


def occurrences(signature, at):
    """Every tracked line matching the signature, at the given tree state."""
    args = ["grep", "-n", "-F", "-I", signature]
    if at:
        args.append(at)
    args += ["--"] + PATHSPECS
    out = git(*args)
    if out is None:
        return []
    hits = []
    for line in out.splitlines():
        rest = line[len(at) + 1:] if at and line.startswith(at + ":") else line
        try:
            path, lineno, _ = rest.split(":", 2)
            hits.append((path, int(lineno)))
        except ValueError:
            continue
    return hits


def blame_time(path, lineno, at):
    """Committer time of the commit that last touched this line."""
    args = ["blame", "-L", f"{lineno},{lineno}", "--line-porcelain"]
    if at:
        args.append(at)
    args += ["--", path]
    out = git(*args)
    if out is None:
        return None, None
    ts = tz = sha = None
    for line in out.splitlines():
        if line.startswith("committer-time "):
            ts = int(line.split()[1])
        elif line.startswith("committer-tz "):
            tz = line.split()[1]
        elif sha is None and len(line.split()) >= 3 and len(line.split()[0]) == 40:
            sha = line.split()[0][:8]
    if ts is None:
        return None, None
    return datetime.fromtimestamp(ts, tz=timezone.utc), sha


MALFORMED = object()


def parse_iso(s):
    """None = absent (genuinely unassessable). MALFORMED = present but unreadable.

    The two are NOT the same and must not be reported as one: absent grounds is
    a fact about the claim, an unreadable field is a defect in the record. C02
    stored '2026-07-26T01:57:16-08:00 (DECISION_4)' — a timestamp with a
    provenance note glued on, which no machine check can read.
    """
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).astimezone(timezone.utc)
    except ValueError:
        return MALFORMED


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", default=None, help="run against a historical commit")
    ap.add_argument("--only", default=None, help="restrict to claim ids containing this")
    ap.add_argument("--grounds-checked-at", default=None,
                    help="override grounds-checked-at (historical replay)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    src = git("show", f"{args.at}:{CLAIMS}") if args.at else None
    if src is None:
        with open(CLAIMS) as f:
            src = f.read()
    claims = json.loads(src)

    fired = silent = unassessable = malformed = 0
    rows = []

    for cid, c in claims.items():
        if cid == "_meta":
            continue
        if args.only and args.only not in cid:
            continue

        time = c.get("time", {})
        gca = parse_iso(args.grounds_checked_at or time.get("grounds_checked_at"))
        sig = (c.get("locator") or {}).get("anchor")

        if gca is MALFORMED:
            malformed += 1
            rows.append((cid, "MALFORMED",
                         f"grounds-checked-at unparseable: "
                         f"{(args.grounds_checked_at or time.get('grounds_checked_at'))!r}", ""))
            continue
        if gca is None:
            unassessable += 1
            rows.append((cid, "UNASSESSABLE", "no grounds-checked-at (no retrievable grounds)", ""))
            continue
        if not sig:
            unassessable += 1
            rows.append((cid, "UNASSESSABLE", "no signature to locate occurrences", ""))
            continue

        occs = occurrences(sig, args.at)
        if not occs:
            unassessable += 1
            rows.append((cid, "UNASSESSABLE", f"signature not found in tree: {sig!r}", ""))
            continue

        home = (c.get("locator") or {}).get("file")
        newest_all = newest_home = None
        sha_all = sha_home = None
        where = None
        for path, lineno in occs:
            t, sha = blame_time(path, lineno, args.at)
            if t is None:
                continue
            if newest_all is None or t > newest_all:
                newest_all, sha_all, where = t, sha, f"{path}:{lineno}"
            if path == home and (newest_home is None or t > newest_home):
                newest_home, sha_home = t, sha

        if newest_all is None:
            unassessable += 1
            rows.append((cid, "UNASSESSABLE", "no blameable occurrence", ""))
            continue

        new_fires = gca < newest_all
        old_fires = newest_home is not None and gca < newest_home

        if new_fires:
            fired += 1
            verdict = "FIRED"
        else:
            silent += 1
            verdict = "silent"

        delta = ""
        if new_fires and not old_fires:
            delta = "  <<< CROSS-FILE: old S1 was SILENT here"
        rows.append((cid, verdict,
                     f"{len(occs)} occ · restated {newest_all:%Y-%m-%dT%H:%M:%SZ} ({sha_all}) "
                     f"at {where} · grounds {gca:%Y-%m-%dT%H:%M:%SZ}",
                     delta))
        if args.verbose:
            for path, lineno in occs:
                t, sha = blame_time(path, lineno, args.at)
                rows.append(("", "", f"      {path}:{lineno}  {t:%Y-%m-%dT%H:%M:%SZ} {sha}"
                             if t else f"      {path}:{lineno}  (unblameable)", ""))

    print(f"S1 cross-file — tree: {args.at or 'working tree'}")
    print("-" * 78)
    for cid, verdict, detail, delta in rows:
        if cid:
            print(f"{cid:28s} {verdict:12s} {detail}{delta}")
        else:
            print(detail)
    print("-" * 78)
    print(f"fired {fired} · silent {silent} · unassessable {unassessable} · "
          f"malformed {malformed}")
    if unassessable or malformed:
        print("VERDICT: INCONCLUSIVE — a check must not report clean over what it "
              "did not examine (POPULATION_PILOT.md §5).")
        return 2
    print("VERDICT: CLEAN" if fired == 0 else "VERDICT: CANDIDATES FOR A READER")
    return 0 if fired == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
