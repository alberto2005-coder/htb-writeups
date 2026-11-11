#!/bin/sh
# Comprueba Python y los scripts privados antes de activar el hook de pre-commit.
set -u

root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "install-hook: ejecuta este script dentro del repositorio" >&2
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
    echo "install-hook: no encuentro python ni python3" >&2
    exit 1
fi

if ! "$py" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
    echo "install-hook: se requiere Python 3.8 o posterior ($py)" >&2
    exit 1
fi

missing=0
for f in .githooks/pre-commit .githooks/pre-push .githooks/pre-publish.sh private/scripts/verify.py private/scripts/audit-indices.py; do
    if [ ! -f "$f" ]; then
        echo "install-hook: falta $f" >&2
        missing=1
    fi
done
if [ "$missing" -ne 0 ]; then
    echo "install-hook: copia los scripts privados antes de activar el hook" >&2
    exit 1
fi

chmod +x .githooks/pre-commit .githooks/pre-push .githooks/pre-publish.sh 2>/dev/null || true
if ! git config core.hooksPath .githooks; then
    echo "install-hook: no se pudo configurar core.hooksPath" >&2
    exit 1
fi

echo "install-hook: hook activo (core.hooksPath=.githooks)"
echo "  manual: .githooks/pre-commit"
echo "  desactivar: git config --unset core.hooksPath"
