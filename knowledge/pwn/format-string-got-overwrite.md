---
topic: Format string y sobrescritura de GOT
tags: [pwn, format-string, got, libc, pwntools]
---

# Format string y sobrescritura de GOT

[🐬 English](format-string-got-overwrite.en.md) | **Español**

## Concepto

`printf(buf)` interpreta la entrada como formato. `%p` filtra la pila, `%s` lee punteros y `%n` escribe en una dirección. Si la GOT es escribible, se puede redirigir una función a `system`.

## Cuándo aplica

- Binarios que imprimen la entrada sin formato fijo.
- `printf`, `fprintf` o `syslog` con un buffer controlado.
- RELRO parcial o nulo.

## Procedimiento

1. Confirmar con `AAAA.%p.%p`.
2. Localizar el offset con `%N$p`.
3. Filtrar una dirección de libc o de la pila.
4. Calcular `system` y `/bin/sh`.
5. Escribir con `%n` en la GOT y llamar a la función.

```python
from pwn import *
payload = fmtstr_payload(offset, {elf.got['printf']: libc.symbols['system']})
```

## Variantes

- `%hhn` para escrituras de un byte.
- Sobrescribir `exit` o `free`.
- Usar `%s` para leer memoria.

## Limitaciones

- Full RELRO protege la GOT.
- ASLR exige una fuga previa.
- El offset cambia con la arquitectura y el stack.

## Mitigación

- `printf("%s", buf)` y formatos constantes.
- Compilar con `-Wformat-security` y RELRO completo.
- ASLR/PIE y revisión de código.

## Detección

- Cadenas con muchos `%p`, `%n` o `%s`.
- Crashes en `printf`.
- Escrituras anómalas en la GOT.

## Referencias

- <https://owasp.org/www-community/attacks/Format_string_attack>
- <https://docs.pwntools.com/en/stable/fmtstr.html>
- <https://attack.mitre.org/techniques/T1203/>
