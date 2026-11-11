#!/bin/sh
# Prueba el instalador en un repo temporal y el bloqueo del hook ante un enlace roto.
set -u

root=$(git rev-parse --show-toplevel) || exit 1
cd "$root" || exit 1

pass=0
fail=0
ok() { pass=$((pass + 1)); echo "ok - $1"; }
ko() { fail=$((fail + 1)); echo "FAIL - $1" >&2; }

tmp=$(mktemp -d)
broken="private/.hook-broken-$$.md"
cleanup() { rm -rf "$tmp"; rm -f "$root/$broken"; }
trap cleanup EXIT INT TERM

# Instalador en un repositorio aislado, sin los scripts privados.
git -C "$tmp" init -q
mkdir -p "$tmp/.githooks" "$tmp/private/scripts"
cp .githooks/install.sh .githooks/pre-commit "$tmp/.githooks/"

if (cd "$tmp" && sh ./.githooks/install.sh) >"$tmp/out1" 2>&1; then
    ko "el instalador debe fallar sin los scripts privados"
else
    ok "el instalador falla sin los scripts privados"
fi
if [ -z "$(git -C "$tmp" config --get core.hooksPath || true)" ]; then
    ok "no activa el hook cuando faltan los scripts"
else
    ko "activó core.hooksPath pese a faltar los scripts"
fi

: >"$tmp/private/scripts/verify.py"
: >"$tmp/private/scripts/audit-indices.py"
if (cd "$tmp" && sh ./.githooks/install.sh) >"$tmp/out2" 2>&1; then
    ok "el instalador activa el hook con todos los requisitos"
else
    ko "el instalador falló con todos los requisitos"
    sed -n '1,5p' "$tmp/out2" >&2
fi
if [ "$(git -C "$tmp" config --get core.hooksPath || true)" = ".githooks" ]; then
    ok "core.hooksPath queda en .githooks"
else
    ko "core.hooksPath no quedó configurado"
fi

if (cd "$tmp" && PYTHON=false sh ./.githooks/install.sh) >"$tmp/out3" 2>&1; then
    ko "el instalador debe rechazar un Python inválido"
else
    ok "el instalador rechaza un Python inválido"
fi

# Hook real: un enlace roto en un fichero temporal debe bloquear.
mkdir -p private
printf '[roto](no-existe.md)\n' >"$broken"
if sh .githooks/pre-commit >"$tmp/hook-broken" 2>&1; then
    ko "el hook no bloqueó un enlace roto"
else
    ok "el hook bloquea un enlace roto"
fi
if grep -q "BROKEN LINK" "$tmp/hook-broken"; then
    ok "el hook informa del enlace roto"
else
    ko "el hook no informó del enlace roto"
fi

rm -f "$broken"
if sh .githooks/pre-commit >"$tmp/hook-ok" 2>&1; then
    ok "el hook acepta el árbol limpio"
else
    ko "el hook falló con el árbol limpio"
    tail -5 "$tmp/hook-ok" >&2
fi

echo "pruebas: $pass ok, $fail fallos"
[ "$fail" -eq 0 ]
