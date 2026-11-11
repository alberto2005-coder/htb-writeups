#!/bin/sh
set -eu
root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "install-hooks: run this script inside the repository" >&2
    exit 1
}
cd "$root"
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then PYTHON=python; fi
command -v "$PYTHON" >/dev/null 2>&1 || {
    echo "install-hooks: Python 3 is required" >&2
    exit 1
}
"$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' || {
    echo "install-hooks: Python 3.8 or later is required" >&2
    exit 1
}
chmod +x .githooks/pre-commit .githooks/pre-push .githooks/pre-push.sh
git config core.hooksPath .githooks
echo "Git hooks installed (core.hooksPath=.githooks)"
