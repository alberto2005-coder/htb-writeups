#!/bin/sh
# Ejecuta la prueba del hook y las verificaciones antes de publicar (push).
set -u

root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "pre-publish: ejecuta esta tarea dentro del repositorio" >&2
    exit 1
}
cd "$root" || exit 1

if [ -n "${PYTHON:-}" ]; then
    py=$PYTHON
elif command -v python >/dev/null 2>&1; then
    py=python
elif command -v python3 >/dev/null 2>&1; then
    py=python3
else
    echo "pre-publish: no encuentro python ni python3" >&2
    exit 1
fi

if ! "$py" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
    echo "pre-publish: se requiere Python 3.8 o posterior ($py)" >&2
    exit 1
fi

for f in .githooks/test.sh private/scripts/verify.py private/scripts/audit-indices.py; do
    if [ ! -f "$f" ]; then
        echo "pre-publish: falta $f" >&2
        exit 1
    fi
done

status=0
echo "== prueba del hook =="
sh .githooks/test.sh || status=1
echo "== enlaces =="
PYTHONIOENCODING=utf-8 "$py" private/scripts/verify.py || status=1
echo "== índices =="
PYTHONIOENCODING=utf-8 "$py" private/scripts/audit-indices.py || status=1

if [ "$status" -ne 0 ]; then
    echo "" >&2
    echo "pre-publish: publicación bloqueada; corrige los problemas anteriores." >&2
    exit 1
fi

echo "pre-publish: verificación OK"
