---
challenge: Nightmare
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, format-string, got-overwrite, libc, pwntools]
---

# Nightmare — Hack The Box (Challenge)

[🐬 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario imprime la entrada con `printf` sin formato fijo. Una cadena de formato filtra direcciones de la pila y de libc; con la dirección de `system` se sobrescribe una entrada GOT y se ejecuta `/bin/sh` en la siguiente llamada.

## Enunciado y superficie

- Pwn, Easy, retirado.
- Se entrega un ELF y un servicio remoto.
- El objetivo es obtener una shell y leer la flag.

```bash
file nightmare
checksec --file=nightmare
```

## Reconocimiento

```bash
./nightmare
python3 -c 'print("AAAA.%p.%p.%p")' | ./nightmare
```

- Binario de 64 bits, PIE y NX.
- `printf(buf)` con la entrada del usuario.
- Existe una llamada posterior a una función de libc.

## Análisis

La cadena de formato permite leer argumentos posicionales (`%7$p`) y escribir con `%n`. Se localiza el desplazamiento hasta la pila y se filtra la dirección de retorno o una entrada GOT para calcular la base de libc.

```python
from pwn import *
elf = ELF('./nightmare')
libc = ELF('./libc.so.6')
```

## Explotación

Se calcula `system` y `/bin/sh`, se escribe `system` en la GOT de `printf` o `exit` con `fmtstr_payload`, y se envía `/bin/sh` como siguiente entrada.

```python
payload = fmtstr_payload(offset, {elf.got['printf']: libc.symbols['system']})
```

## Evidencia

- Fuga de una dirección de libc.
- GOT sobrescrita con `system`.
- Shell y flag leída sin publicarla.

## Lecciones aprendidas

- `printf(user_input)` es una vulnerabilidad de formato.
- Una fuga de libc derrota ASLR.
- GOT sigue siendo un objetivo si no hay RELRO completo.
- `pwntools` automatiza el cálculo del payload.

## Mitigaciones y detección

- Usar `printf("%s", buf)` y formatos constantes.
- Compilar con `-Wformat-security` y RELRO completo.
- Aplicar ASLR y PIE; no confiar solo en NX.
- Monitorizar crashes y cadenas con muchos `%p`/`%n`.
- Referencias: OWASP Format String, pwntools.

## Referencias

- <https://www.hackthebox.com/challenges/Nightmare>
- <https://owasp.org/www-community/attacks/Format_string_attack>
- <https://docs.pwntools.com/en/stable/fmtstr.html>
- <https://attack.mitre.org/techniques/T1203/>
