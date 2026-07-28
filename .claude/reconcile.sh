#!/usr/bin/env bash
# reconcile.sh — the MECHANICAL layer of docs/RECONCILIATION.md §5.
#
# CONTRACT, the same one verify.sh keeps: exit 0 only if every check RAN and
# found nothing. A check that cannot run makes the whole run INCONCLUSIVE and
# exits non-zero. This script must never report clean over a check it skipped.
#
# SCOPE. Only checks whose inputs are the TREE ITSELF. Every field-reading check
# in RECONCILIATION.md §5 is deliberately NOT built — see NOT-BUILT below.
#
# Usage:  bash .claude/reconcile.sh
#
# ─────────────────────────────────────────────────────────────────────────────
# NOT BUILT, AND WHY — no claim in this repository has these fields populated,
# so the checks would read nothing and report clean, which is worse than absent:
#   S1  grounds-checked-at < restated-at   (form-3 candidate)
#   M2  retrieval-depth ceiling violation
#   M3  artifact integrity / locator liveness
#   M4  malformed claim: no ARTIFACT REF and grounds.kind != DEDUCTION
# All four are specified in docs/PROVENANCE_FIELDS.md and none is populated.
# S1 is additionally SEMI-mechanical per §5 and would need a reader anyway.
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail
cd "$(dirname "$0")/.." || { echo "reconcile: cannot reach repo root"; exit 2; }

# --quiet: one line when clean, full detail when there is anything to say.
# Exists so this can sit on SessionStart without spending context every session
# on a result that is almost always "nothing changed".
QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1
OUT=""
FINDINGS=0
RAN=0
EXPECTED_CHECKS=4

say_()  { if [ "$QUIET" = "1" ]; then OUT="$OUT$*"$'\n'; else echo "$*"; fi; }
find_() { say_ "  [FIND] $*"; FINDINGS=$((FINDINGS+1)); }
ok_()   { say_ "  [ok  ] $*"; }
ran_()  { RAN=$((RAN+1)); }
die_()  { echo "  [FATAL] $*"; echo; echo "INCONCLUSIVE — a check could not run."; exit 2; }

say_ "reconcile — mechanical layer (docs/RECONCILIATION.md §5)"
say_ ""

# ── C1 · TREE-ORPHAN ────────────────────────────────────────────────────────
# Every .md under docs/ or analysis/ referenced by name from somewhere else in
# the tree. Rule 11 second form, strongest version: unreachable from ANYWHERE.
#
# FALSE-POSITIVE MODE: a document deliberately unreferenced — a superseded
# session handoff, or a draft kept for the record. There are none today. If one
# appears, the fix is an explicit marker, not disabling the check.
say_ "C1 tree-orphan — .md with zero inbound references"
git rev-parse --git-dir >/dev/null 2>&1 || die_ "C1: not a git repository"
MD=$(git ls-files 'docs/*.md' 'analysis/*.md') || die_ "C1: git ls-files failed"
[ -n "$MD" ] || die_ "C1: no markdown found — refusing to report clean"
for f in $MD; do
  b=$(basename "$f")
  n=$(git grep -l -F -- "$b" -- '*.md' '*.py' '*.sh' '*.yml' 2>/dev/null \
        | grep -v -x -F "$f" | wc -l | tr -d ' ')
  [ "$n" -eq 0 ] && find_ "C1 orphan: $f — no inbound reference anywhere in the tree"
done
ok_ "C1 ran over $(echo "$MD" | wc -w | tr -d ' ') files"
ran_

# ── C2 · INDEX COMPLETENESS, BOTH DIRECTIONS ────────────────────────────────
# HANDOFF §5.1 against `git ls-files`. Rule 11 second form as actually recorded:
# unreachable from THE ENTRY POINT, which is a weaker and more common condition
# than C1 and is the one the third sweep found (index listed 12 of 18).
#
# FALSE-POSITIVE MODE: HANDOFF.md itself is the index and cannot list itself —
# excluded by name, the only exclusion in this check.
say_ ""
say_ "C2 index completeness — HANDOFF §5.1 vs the tree, both directions"
[ -f docs/HANDOFF.md ] || die_ "C2: docs/HANDOFF.md absent"
awk '/^## 5\.1 DOCUMENT INDEX/,/^## 6\. CURRENT PROJECT STATE/' docs/HANDOFF.md \
  > /tmp/reconcile_idx.$$ || die_ "C2: could not extract §5.1"
[ -s /tmp/reconcile_idx.$$ ] || die_ "C2: §5.1 DOCUMENT INDEX not found in HANDOFF.md"
grep -oE '(docs|analysis)/[A-Za-z0-9_.-]+\.md' /tmp/reconcile_idx.$$ | sort -u > /tmp/reconcile_i.$$
git ls-files 'docs/*.md' 'analysis/*.md' | grep -v -x 'docs/HANDOFF.md' | sort > /tmp/reconcile_t.$$
while read -r f; do
  [ -n "$f" ] && find_ "C2 unindexed: $f — present in tree, absent from §5.1"
done < <(comm -23 /tmp/reconcile_t.$$ /tmp/reconcile_i.$$)
while read -r f; do
  [ -n "$f" ] && find_ "C2 phantom: $f — listed in §5.1, absent from tree"
done < <(comm -13 /tmp/reconcile_t.$$ /tmp/reconcile_i.$$)
ok_ "C2 ran: $(wc -l < /tmp/reconcile_t.$$ | tr -d ' ') tracked, $(wc -l < /tmp/reconcile_i.$$ | tr -d ' ') indexed"
rm -f /tmp/reconcile_idx.$$ /tmp/reconcile_i.$$ /tmp/reconcile_t.$$
ran_

# ── C3 · HARNESS COUNT ASSERTED vs ACTUAL ───────────────────────────────────
# Catches rule 11 instance 8 — WHERE_IT_STANDS.md said 67 when the harness held
# 112. Run the harness, count, compare against present-tense assertions.
#
# FALSE-POSITIVE MODES — the first draft of this check produced 30 findings, all
# but zero of them false, and had to be narrowed twice. Both modes are real and
# both are handled by NARROWING THE MATCH, not by suppressing output:
#
#   FP-1  "checks" IS HEAVILY OVERLOADED IN THIS CORPUS. `cppcheck --errorlist`
#         has 342 checks; the CWE coverage cascade counts 31/149/116/46/20
#         checks; OASIS schema validation is 46 checks. None is our harness.
#         HANDLED: the match must anchor on "harness" or "test suite".
#
#   FP-3  A QUOTED EXAMPLE IS NOT AN ASSERTION. Found by this check firing on
#         docs/RECONCILIATION.md §12 the first time it ran after being written:
#         that section QUOTES "harness 67 -> 84 checks" while explaining FP-2.
#         The document asserts nothing about the harness; it cites a string.
#         HANDLED: a match whose number sits inside quotation marks or backticks
#         on that line is skipped. Quoting a count is reporting, not claiming.
#
#   FP-2  APPEND-ONLY RECORDS CARRY CORRECT HISTORY. VALIDATION.md logs harness
#         growth as it happened — "harness 67 -> 84 checks", "Harness at 31
#         checks" — and each is right for its entry. Session handoffs are dated
#         snapshots for the same reason. Flagging either would be the check
#         crying wolf about accurate history.
#         HANDLED: docs/VALIDATION.md and docs/SESSION_HANDOFF_* excluded.
#         Exclusion is by DOCUMENT ROLE (append-only) and is a short, stable
#         list; every other document is covered by default, so a new one is
#         covered without editing this script.
#
# Calibrated: 0 findings on the current tree, and it fires on 423a2b50 where
# WHERE_IT_STANDS.md asserted 67 against an actual 112.
say_ ""
say_ "C3 harness count — asserted in prose vs actually run"
[ -f examples/fixtures/verify_cross_tool_key.py ] || die_ "C3: harness script absent"
ACTUAL=$(python3 examples/fixtures/verify_cross_tool_key.py 2>/dev/null | grep -c '\[ok')
[ "$ACTUAL" -gt 0 ] || die_ "C3: harness produced no [ok] lines — cannot compare"
C3_SEEN=0
while IFS= read -r hit; do
  file="${hit%%:*}"
  num=$(printf '%s' "$hit" | grep -oE '[0-9]+ checks?' | grep -oE '^[0-9]+' | head -1)
  [ -z "$num" ] && continue
  # FP-3: skip a count that is quoted rather than asserted.
  printf '%s' "$hit" | grep -qE '["`“”][^"`]*'"$num"' checks?' && continue
  C3_SEEN=$((C3_SEEN+1))
  [ "$num" = "$ACTUAL" ] && continue
  find_ "C3 count drift: $file asserts $num checks; harness runs $ACTUAL"
done < <(git grep -nE '(harness|test suite)[^.]{0,60}[0-9]+ checks?|[0-9]+ checks?[^.]{0,25}(harness|passing|and they all pass)' -- '*.md' \
           | grep -vE 'docs/(VALIDATION|SESSION_HANDOFF)')
[ "$C3_SEEN" -gt 0 ] || die_ "C3: no harness-count assertion found at all — the corpus always had one, so this is a broken match, not a clean result"
ok_ "C3 ran: harness=$ACTUAL, $C3_SEEN assertion(s) compared, append-only records excluded"
ran_

# ── C4 · INDEX ROW SHAPE ────────────────────────────────────────────────────
# Every §5.1 row names a path that resolves. Catches a typo'd index entry, which
# would make a document silently unreachable while looking indexed.
#
# FALSE-POSITIVE MODE: none known — a path in the index either resolves or does
# not. This is the narrowest check here and may never fire.
say_ ""
say_ "C4 index rows resolve"
awk '/^## 5\.1 DOCUMENT INDEX/,/^## 6\. CURRENT PROJECT STATE/' docs/HANDOFF.md \
  | grep -oE '(docs|analysis)/[A-Za-z0-9_.-]+\.md' | sort -u \
  | while read -r p; do [ -f "$p" ] || echo "$p"; done > /tmp/reconcile_bad.$$
while read -r p; do
  [ -n "$p" ] && find_ "C4 dangling index row: $p does not exist on disk"
done < /tmp/reconcile_bad.$$
ok_ "C4 ran"
rm -f /tmp/reconcile_bad.$$
ran_

# ── VERDICT ─────────────────────────────────────────────────────────────────
if [ "$RAN" -ne "$EXPECTED_CHECKS" ]; then
  [ "$QUIET" = "1" ] && printf '%s' "$OUT"
  echo
  echo "INCONCLUSIVE — $RAN of $EXPECTED_CHECKS checks ran. Not reporting clean."
  exit 2
fi
if [ "$FINDINGS" -gt 0 ]; then
  [ "$QUIET" = "1" ] && printf '%s' "$OUT"
  echo
  echo "RECONCILE: $FINDINGS finding(s) across $RAN checks."
  exit 1
fi
if [ "$QUIET" = "1" ]; then
  echo "reconcile: clean ($RAN/$EXPECTED_CHECKS mechanical checks; semi-mechanical and judgment classes NOT covered)"
  exit 0
fi
echo
echo "RECONCILE: clean — $RAN of $EXPECTED_CHECKS checks ran, 0 findings."
echo "NOTE: clean here means the four MECHANICAL checks found nothing."
echo "      It says nothing about semi-mechanical or judgment classes (§5)."
exit 0
