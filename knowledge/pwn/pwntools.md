---
topic: pwntools
tags: [pwn, pwntools, exploit, rop, shellcode, remote]
---

# pwntools

[🌐 English](pwntools.en.md) | **Español**

## Concepto

pwntools es una biblioteca de Python para interactuar con procesos y servicios, construir payloads y resolver direcciones. `ELF`, `process`, `remote`, `cyclic`, `ROP` y `shellcraft` cubren el ciclo habitual de un reto de pwn.

## Cuándo aplica

- Retos con binario local o remoto.
- Cálculo de offsets y direcciones.
- Construcción de cadenas ROP.
- Interacción con prompts y menús.

## Procedimiento

1. Cargar el binario y revisar protecciones.
2. Calcular el offset con un patrón cíclico.
3. Elegir la técnica y construir el payload.
4. Probar en local y ajustar.
5. Ejecutar contra el servicio remoto.

```python
from pwn import *
context.binary = elf = ELF('./challenge')
p = process('./challenge')
p.sendline(cyclic(128))
p.wait()
# p = remote('<HOST>', <PORT>)
```

## Variantes

- `ROP` para cadenas con gadgets.
- `shellcraft` para shellcode.
- `fmtstr_payload` para format strings.
- `tube` para interactuar con el proceso.

## Limitaciones

- Las direcciones cambian con ASLR y PIE.
- La libc remota puede diferir de la local.
- El payload debe respetar el protocolo.
- Algunos retos requieren emulación.

## Mitigación y detección

- Aplicar ASLR, PIE, NX y canarios.
- Compilar con `FORTIFY_SOURCE`.
- Monitorizar servicios que reciben payloads anómalos.
- Probar los binarios antes de desplegarlos.

## Referencias

- <https://docs.pwntools.com/>
- <https://github.com/Gallopsled/pwntools>
- <https://ctf-wiki.org/pwn/linux/user-mode/environment/>
