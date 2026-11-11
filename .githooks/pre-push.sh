#!/bin/sh
set -eu
root=$(git rev-parse --show-toplevel)
cd "$root"
sh .githooks/test.sh
sh .githooks/pre-commit
