#!/usr/bin/env bash
# Regenerate the SARIF fixtures from REAL scanner runs.
#
# The fixtures must never be hand-authored. An earlier hand-authored pair
# modelled a tool combination that does not exist — wrong flawfinder ruleId
# namespace (CWE-120 instead of FF1001), no fingerprints where real flawfinder
# always emits them, and a CWE number written into a cppcheck message where
# real cppcheck never puts one. Tests built on it could not detect the
# structural defect it was hiding.
#
# Run from the repo root:
#     bash examples/fixtures/regen_fixtures.sh
#
# Requires: flawfinder, cppcheck (brew install flawfinder cppcheck)
set -euo pipefail

cd "$(dirname "$0")/../.."
SRC="examples/fixtures/overlap.c"
OUT="examples/fixtures"

command -v flawfinder >/dev/null || { echo "flawfinder not installed"; exit 1; }
command -v cppcheck   >/dev/null || { echo "cppcheck not installed";   exit 1; }

echo "flawfinder $(flawfinder --version 2>/dev/null | head -1)"
echo "$(cppcheck --version)"

# flawfinder writes SARIF to stdout.
flawfinder --sarif "$SRC" > "$OUT/flawfinder_min.sarif" 2>/dev/null

# cppcheck writes XML to STDERR (not stdout — the redirect matters), then the
# repo's converter turns it into SARIF.
cppcheck --enable=all --xml --xml-version=2 "$SRC" 2> "$OUT/cppcheck.xml" 1>/dev/null
python3 src/cppcheck_xml_to_sarif.py "$OUT/cppcheck.xml" "$OUT/cppcheck_min.sarif"
rm -f "$OUT/cppcheck.xml"

# Pretty-print so fixture diffs are reviewable. Content is unmodified.
python3 - "$OUT/flawfinder_min.sarif" "$OUT/cppcheck_min.sarif" <<'PY'
import json, sys
for p in sys.argv[1:]:
    json.dump(json.load(open(p)), open(p, "w"), indent=2)
    open(p, "a").write("\n")
PY

echo
echo "regenerated. verifying:"
python3 examples/fixtures/verify_cross_tool_key.py
