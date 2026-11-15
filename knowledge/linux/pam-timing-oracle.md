---
title: PAM — oráculo de temporización en un módulo modificado
tags: [linux, pam, timing-attack, authentication, privesc]
---

# PAM — oráculo de temporización en un módulo modificado

[🇬🇧 English](pam-timing-oracle.en.md) | **Español**

## Concepto

Un módulo PAM que compara la contraseña carácter a carácter y sale en el primer fallo filtra información por el tiempo de respuesta. Si el módulo se ejecuta en `su` o `sshd`, un atacante local puede recuperar la contraseña de root midiendo cuánto tarda cada intento.

## Cuándo aplica

- Hay un `.so` sospechoso en `/lib/security` o `/usr/lib/security`.
- El ticket o el código mencionan una contraseña de longitud fija.
- `su` tarda más con prefijos correctos.

## Procedimiento

1. Localizar módulos PAM con fechas o hashes anómalos.
2. Confirmar que la comparación es incremental (Ghidra/objdump).
3. Medir el tiempo de `su` para cada candidato y quedarse con el más lento.
4. Repetir carácter a carácter y validar la contraseña completa.

```bash
for c in {a..z} {0..9}; do
  printf '%s' "$candidate$c" | timeout 1 su -c true root 2>/dev/null
  printf '%s %s\n' "$c" "$(date +%s%N)"
done
```

## Variantes

- El módulo puede comparar hashes en lugar de texto; el ataque sigue funcionando si la comparación es incremental.
- Usar `perf stat` o `hyperfine` para reducir el ruido.
- Si el módulo bloquea tras varios fallos, espaciar los intentos.

## Limitaciones

- El ruido del sistema puede ocultar diferencias de microsegundos.
- La contraseña debe tener un alfabeto y longitud manejables.
- Se necesita acceso local para invocar `su` repetidamente.

## Mitigación y detección

- Usar comparaciones en tiempo constante (`CRYPTO_memcmp`).
- Revisar la integridad de los módulos PAM (`dpkg -V`, hashes).
- Limitar los intentos y alertar de patrones de `su` repetidos.
- No almacenar contraseñas en claro en módulos personalizados.

## Referencias

- <https://www.man7.org/linux/man-pages/man8/pam.8.html>
- <https://www.man7.org/linux/man-pages/man3/pam_authenticate.3.html>
- <https://cwe.mitre.org/data/definitions/208.html>
