---
challenge: Oldbridge
category: Challenge
type: Pwn
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [pwn, canary, pie, stack-pivot, ret2libc, xor, brute-force]
---

# Oldbridge — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired por evidencia de writeups públicos; no comprobado con sesión en HTB.
> Sin flags ni direcciones de la instancia real.

## TL;DR

Servicio que cifra la entrada con XOR `0xd` y compara el usuario con `il{dih` («davide»). `check_username()` copia 1056 bytes en un búfer de 1032: canario, `saved rbp` y retorno quedan al alcance, pero no hay espacio para una cadena ROP. Como el servidor hace `fork()`, el canario y la base de PIE se pueden sacar byte a byte. Con ellos se monta un **stack pivot** (`leave; ret`) hacia el propio búfer y se ejecuta un ret2libc con `write`, `dup2` y `system`.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Medium**, ELF x86-64 y una instancia remota.
- El binario pide un nombre de usuario y responde `Username found!` si coincide.
- La entrada se cifra con XOR antes de compararla: hay que enviar los bytes ya codificados.

```bash
file oldbridge
checksec --file=oldbridge
```

```text
RELRO:    Partial RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```

Casi todas las protecciones están activas: canario, PIE y ASLR de libc hay que resolverlos.

## Reconocimiento

```bash
./oldbridge 1234
nc 127.0.0.1 1234
```

```text
Username: davide
Username found!
```

El usuario esperado está cifrado en el binario como `il{dih`; con XOR `0xd` se revierte:

```python
bytes(c ^ 0xD for c in b'il{dih')   # b'davide'
```

A partir de ahí, el servidor hace `fork()` por conexión: el hijo hereda el canario, la base de PIE y la pila del padre. Esa es la condición que hace viable la fuerza bruta.

## Análisis del código

`check_username()` reserva `0x430` bytes y sitúa el búfer en `rbp-0x410` (1032 bytes). Después:

```c
read(fd, rbp - 0x410, 0x420);   // 1056 bytes
...
if (strcmp(cifrado, "il{dih") == 0) write(fd, "Username found!\n", ...);
```

El `read` de `0x420` (1056) cubre exactamente:

```text
rbp-0x410  [ búfer, 1032 bytes ]
rbp-0x008  [ canario, 8 bytes ]
rbp+0x000  [ saved rbp, 8 bytes ]
rbp+0x008  [ return address, 8 bytes ]
```

1032 + 8 + 8 + 8 = 1056. No sobra ni un byte para una cadena ROP: solo se puede reescribir el retorno con **una** dirección. De ahí el pivot.

## Explicación del fallo

### Canario y PIE por fuerza bruta

El proceso padre no muere cuando el hijo falla. Enviando el usuario cifrado (`il{dih`) y relleno hasta 1032 bytes, y probando el byte siguiente (0–255), la respuesta `Username found!` aparece solo cuando el byte del canario es correcto. Se repite para los 8 bytes del canario, los 8 del `saved rbp` y los 6–7 del retorno.

- El canario acaba en `00`; el primer byte ya se conoce y el resto se prueba.
- El retorno de `check_username` termina en `0xcf` (`main+566`), lo que reduce el espacio de búsqueda.
- La base de PIE es `retorno - 0xecf`; a partir de ahí, gadgets y PLT tienen offset fijo.

La entrada va cifrada con XOR `0xd`, así que cada byte probado se envía como `valor ^ 0xd`. El `00` del canario viaja como `0x0d`.

### Stack pivot

Sin espacio para ROP, se usa el gadget `leave; ret`:

```asm
leave      ; mov rsp, rbp ; pop rbp
ret
```

El valor filtrado de `saved rbp` está `0x480` por encima del inicio del búfer; el exploit resta `0x8` más (`0x478`) para alinear la pila, de modo que la cadena empieza en el relleno.

### offsets del build

| Dato | Offset desde la base |
|---|---:|
| retorno de `check_username` | `0xecf` |
| `leave; ret` | `0xb6d` o `0xc5c` según build |
| `pop rdi; ret` | `0xf73` |
| `pop rsi; pop r15; ret` | `0xf71` |
| `pop rdx; ret` | `0xb53` |
| `write@plt` | `0x910` |
| `write@got` | `0x202020` |

Los dos writeups usan binarios distintos: no se copian offsets sin comprobar `objdump` y `ROPgadget`.

## Reproducción local

```bash
./oldbridge 1234
python3 solve.py 127.0.0.1:1234
```

Para verificar el marco:

```gdb
break *check_username+90
run
# tras el read
x/6gx $rbp-0x410
```

El canario está en `rbp-0x8`, el `saved rbp` en `rbp` y el retorno en `rbp+8`.

## Explotación

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', '<PORT>'
KEY = 0xD

def enc(data):
    return bytes(b ^ KEY for b in data)

# 1. Fuerza bruta del canario, saved rbp y retorno (servidor fork)
# 2. base = ret - 0xecf
# 3. pivot: saved rbp = buffer_addr - 0x480
# 4. ROP: write(4, write@got, 8); volver a check_username
# 5. libc.rip con los 3 nibbles bajos; dup2(4, 0/1/2); system('/bin/sh')
```

Puntos que hay que respetar:

- Todo el payload va cifrado con XOR `0xd`; un byte sin cifrar rompe el canario o la dirección.
- El `fd` del socket suele ser 4; si no, se prueban 3, 5 y 6.
- La primera cadena solo filtra `write`; la segunda vuelve a `check_username` con la base de libc ya conocida.
- `dup2` redirige el socket a stdin/stdout/stderr antes de `system`.
- Los offsets de libc se confirman con `libc.rip` a partir de los 12 bits bajos del leak.

## Evidencia

- `checksec` con canario, NX y PIE.
- Canario y retorno recuperados byte a byte con `Username found!` como oráculo.
- Base de PIE calculada y leak de `write` con la cadena ROP.
- Shell local con una flag de prueba, nunca la real.

## Lecciones aprendidas

- Un `fork()` sin `exec` convierte el canario en adivinable: el hijo hereda el secreto y el padre sigue vivo.
- El XOR de la entrada no es una protección criptográfica: se revierte con el mismo byte.
- Cuando el `read` llega justo al retorno, no hay ROP posible sin mover la pila; `leave; ret` es el pivot mínimo.
- El `saved rbp` no es relleno: es el puntero que decide dónde continúa la cadena.
- Los offsets cambian entre builds; dos writeups del mismo reto pueden diferir en `leave; ret` y en la distancia al búfer.

## Mitigaciones y detección

- `fork()` + `exec()` en cada conexión, o re Key el canario, para que no se herede.
- Compilar con `-fstack-protector-strong`, `-pie -fPIE` y `-D_FORTIFY_SOURCE=2`; el `read` debe usar `sizeof`.
- No comparar credenciales con XOR ni con cadenas embebidas; usar un hash con sal.
- Detección: muchas conexiones que fallan en el mismo byte y una que responde distinto; peticiones de 1032–1056 bytes con bytes no imprimibles; caídas repetidas del hijo.
- Referencias: CWE-121, CWE-798 (hardcoded credentials), MITRE T1190.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/old-bridge/>
- <https://shaked.delarea.cloud/posts/blog-2>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://libc.rip/>
- <https://docs.pwntools.com/en/stable/rop/rop.html>
