---
challenge: Behind the Scenes
category: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, gdb, ud2, anti-decompilation]
---

# Behind the Scenes — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un ELF `stripped` que pide una contraseña de 12 caracteres. El autor insertó instrucciones **`UD2`** para que el descompilador se pierda: Ghidra muestra un `main` casi vacío. La solución es bajar a **GDB**, ver los cuatro `strncmp` y leer los literales comparados.

## Evidencia

- `behindthescenes`, ejecutable ELF `stripped`.

## Método

1. **Comprobar la pista**: al ejecutarlo pide `./challenge <password>`; `strings` no revela la contraseña.

2. **GDB en vez de descompilador**:

```bash
gdb -q ./behindthescenes
(gdb) disas main
```

`UD2` es una instrucción "inválida" que corta el análisis estático; el flujo real se ve en ensamblador.

3. **Los cuatro `strncmp`**: cada uno compara un trozo de 3-4 caracteres. Poner breakpoint en cada llamada y leer el segundo argumento (`x/s $rsi`), o inspeccionar el hexdump que hay junto al código.

4. **Reconstruir**: la contraseña es la concatenación de los fragmentos (`Itz` + `_0n` + `Ly_` + `UD2`).

```bash
./behindthescenes Itz_0nLy_UD2
```

5. La flag es `HTB{<contraseña>}`.

## Tropiezos

- **`UD2` y Ghidra**: si el decompilador da basura, no es un reto imposible: cambiar a GDB.
- **Parchear**: convertir los `UD2` en `NOP` permite seguir el flujo, pero no es necesario.
- **Longitud**: el programa exige 12 bytes; contar los fragmentos antes de probar.

## Lecciones

- La "anti-descompilación" es ofuscación: el ensamblador sigue contando la verdad.
- Comparar cadenas troceadas es una forma de esconder un secreto en el código.
- Saber cuándo abandonar una herramienta vale tanto como saber usarla.
