#!/bin/sh
set -eu
root=$(git rev-parse --show-toplevel)
cd "$root"

sh .githooks/test.sh

GITLEAKS=".tools/gitleaks.exe"

GITLEAKS_BIN="${GITLEAKS:-gitleaks}"
if [ -x "$GITLEAKS_BIN" ]; then
    :
elif ! command -v "$GITLEAKS_BIN" >/dev/null 2>&1; then
    echo "pre-publish: Gitleaks no está instalado." >&2
    echo "Instala Gitleaks 8.24.3 o define GITLEAKS=/ruta/al/binario." >&2
    exit 1
fi

version=$("$GITLEAKS_BIN" version 2>/dev/null || true)
case "$version" in
    8.24.3*) ;;
    *) echo "pre-publish: aviso: Gitleaks ${version:-desconocido}; el CI usa 8.24.3." >&2 ;;
esac

echo "Ejecutando Gitleaks sobre todo el historial..."
if ! "$GITLEAKS_BIN" detect --source . --redact --no-banner --exit-code 2 \
    --log-opts="--no-merges --first-parent"; then
    echo "pre-publish: Gitleaks encontró hallazgos o falló; push bloqueado." >&2
    exit 1
fi
echo "Gitleaks: sin hallazgos."
