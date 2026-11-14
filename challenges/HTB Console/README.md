---
challenge: HTB Console
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, stack, ret2system, rop, pwntools]
---

# HTB Console — Hack The Box (Challenge)

[🐬 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una consola vulnerable a desbordamiento de pila permite sobrescribir la dirección de retorno. El binario incluye una función que llama a `system`; se coloca `/bin/sh` o el comando en el registro adecuado y se obtiene una shell.

## Enunciado y superficie

- Pwn, Easy, retirado.
- Se entrega un ELF y un servicio remoto.
- El objetivo es leer la flag del servidor.

```bash
file htb-console
checksec --file=htb-console
```

## Reconocimiento

```bash
python3 -c 'print("A"*200)' | ./htb-console
```

- Binario de 64 bits, sin PIE.
- `gets`/`read` copia más de lo que cabe en el buffer.
- Existe una función `system` o un `win` que ejecuta un comando.

## Análisis

Se calcula el offset con `cyclic` y se localiza la dirección de la función objetivo. Si el binario es de 32 bits, el argumento se pasa en la pila; si es de 64 bits, se usa un gadget `pop rdi; ret` y la dirección de `/bin/sh`.

```python
from pwn import *
elf = ELF('./htb-console')
rop = ROP(elf)
```

## Explotación

Se construye el payload con el offset, el gadget y la dirección de `system`, y se envía al servicio. Se mantiene la conexión interactiva para leer la flag.

```python
payload = flat(b'A'*offset, rop.find_gadget(['pop rdi','ret'])[0], next(elf.search(b'/bin/sh')), elf.plt['system'])
```

## Evidencia

- Crash con offset controlado.
- Dirección de retorno sobrescrita.
- Shell y flag leída sin publicarla.

## Lecciones aprendidas

- Un buffer sin límites permite controlar la pila.
- `ret2system` es el caso más directo de ROP.
- El offset se calcula con un patrón cíclico.
- La arquitectura cambia la convención de argumentos.

## Mitigaciones y detección

- Usar `fgets`/`read` con tamaño y validar la entrada.
- Compilar con canarios, NX, PIE y RELRO.
- Aplicar ASLR y no exponer funciones internas.
- Monitorizar crashes y cadenas largas en el servicio.
- Referencias: OWASP Buffer Overflow, pwntools ROP.

## Referencias

- <https://www.hackthebox.com/challenges/HTB%20Console>
- <https://owasp.org/www-community/vulnerabilities/Buffer_Overflow>
- <https://docs.pwntools.com/en/stable/rop/rop.html>
- <https://attack.mitre.org/techniques/T1203/>
