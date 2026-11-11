#!/bin/sh
set -eu
root=$(git rev-parse --show-toplevel)
cd "$root"
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then PYTHON=python; fi
"$PYTHON" tools/generate_indexes.py --check
"$PYTHON" tools/repo_check.py
echo "Hook tests passed."
