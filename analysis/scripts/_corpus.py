"""Path resolution for the analysis scripts. NO analysis logic lives here.

WHY THIS EXISTS. 12 of 21 scripts hard-coded an absolute path — 5 of them into a
session scratchpad under /private/tmp, which does not survive a reboot on this
machine, let alone exist on anyone else's. Zero scripts ran from a clean clone.
See docs/ARTIFACT_SELF_ASSESSMENT.md §3.

WHAT IT DELIBERATELY DOES NOT DO. It does not touch any script's analysis logic.
Those scripts are the instruments that produced the numbers recorded in
VALIDATION.md; changing how they compute would change what those numbers mean.
This module only answers "where is the corpus" and "where is src".

USAGE
    corpus root:  export AUDIT_CORPUS_ROOT=/path/to/dir/holding/lipp/owasp/...
    then:         python3 analysis/scripts/run_0j.py

If AUDIT_CORPUS_ROOT is unset, scripts that need a corpus exit with a message
naming the corpus and pointing at analysis/README.md §2 for the fetch commands,
rather than failing on a stale absolute path.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
SRC = os.path.join(REPO_ROOT, "src")
DATA = os.path.normpath(os.path.join(_HERE, "..", "data"))


def add_src():
    """Put the repo's src/ on sys.path, resolved RELATIVE to this file rather
    than hard-coded, so the repo can live anywhere."""
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    return SRC


def corpus_root(required=True):
    """Directory holding lipp/ owasp/ struts/ lib/. None if unset and optional."""
    root = os.environ.get("AUDIT_CORPUS_ROOT")
    if root and os.path.isdir(root):
        return root
    if not required:
        return None
    sys.stderr.write(
        "\n  AUDIT_CORPUS_ROOT is not set (or does not exist).\n"
        "  This script needs a corpus that is NOT committed to the repo —\n"
        "  the corpora total ~690 MB. Fetch/build commands, pinned commit\n"
        "  SHAs and Software Heritage SWHIDs are in analysis/README.md §2.\n\n"
        "      export AUDIT_CORPUS_ROOT=/path/to/corpora\n\n"
        "  The directory should contain lipp/ and whichever of owasp/,\n"
        "  struts/, lib/ the script needs.\n\n")
    raise SystemExit(2)


def corpus(*parts, required=True):
    """Join a path under the corpus root."""
    root = corpus_root(required=required)
    return os.path.join(root, *parts) if root else None
