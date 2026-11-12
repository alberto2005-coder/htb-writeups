---
challenge: Teleport
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ghidra, setjmp, password]
---

# Teleport — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin clave ni flag reales.

## TL;DR

El binario `teleport` recibe la contraseña como argumento y la valida con decenas de funciones que usan `setjmp`/`longjmp`. Cada función compara un byte en un offset distinto y en un orden no secuencial. Exportando el decompilado de Ghidra se extraen las comparaciones, se ordenan por offset y se reconstruye la contraseña.

## Enunciado y superficie

- Reversing, Easy, retirado.
- Se entrega un ELF `teleport`.
- Uso: `./teleport <password>`.

```bash
file teleport
checksec --file=teleport
```

## Reconocimiento

```bash
./teleport
# Missing password
./teleport test
# Something's wrong...
ltrace ./teleport test
```

`ltrace` muestra `strncpy`, múltiples `_setjmp` y comparaciones de bytes. El binario no está ofuscado, pero la lógica está repartida.

## Análisis del código

En Ghidra, `main` copia el argumento a un buffer global y llama a funciones de validación. Cada función:

1. Hace `_setjmp`.
2. Compara un byte del buffer con un carácter.
3. Si falla, `longjmp(..., 101)`.

Los offsets no están en orden. Se exporta el pseudocódigo y se extraen las líneas del tipo:

```c
if (DAT_00303296 != 'p') longjmp(...);
if (DAT_003032a5 != 'n') longjmp(...);
if (DAT_00303281 != 'T') longjmp(...);
```

## Explicación del fallo

La validación está fragmentada para dificultar la lectura, pero cada comparación revela un byte y su posición. No hay hash ni transformación: la contraseña está en el binario como una serie de comparaciones inmediatas.

## Reproducción local

Se exporta el decompilado y se procesa con `grep`/`awk` para ordenar por offset:

```bash
grep -oE "DAT_[0-9a-f]+ != '[^']'" decompiled.c | sort -u
```

Se convierte el offset a índice relativo al buffer y se reconstruye la cadena. También se puede automatizar con un script de Ghidra que recorra los `CMP` y sus inmediatos.

## Explotación

```bash
./teleport '<PASSWORD>'
```

La salida correcta contiene la flag. Se verifica y se redacta.

## Evidencia

- `checksec` y `ltrace`.
- Extracto del decompilado con offsets y caracteres redactados.
- Ejecución con la contraseña y flag redactada.

## Lecciones aprendidas

- `setjmp`/`longjmp` se usa para ofuscar el flujo, no para proteger datos.
- Las comparaciones inmediatas filtran la contraseña.
- Ghidra + scripting es más rápido que seguir el flujo a mano.
- El orden de los offsets es la clave para reconstruir.

## Mitigaciones y detección

- No validar secretos en el cliente con comparaciones byte a byte.
- Usar hashes con sal y verificación en servidor.
- Ofuscar el flujo no sustituye a un diseño seguro.
- Detección: en CTF, revisar `setjmp`; en producción, evitar secretos embebidos.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/teleport/>
- <https://ghidra-sre.org/>
- <https://en.wikipedia.org/wiki/Setjmp.h>
