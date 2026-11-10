---
challenge: Behind the Scenes
category: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, gdb, ud2, anti-decompilation]
type: Reversing
---

# Behind the Scenes — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

El binario instala un manejador de `SIGILL` y ejecuta `UD2` (`0f 0b`): la excepción de opcode inválido salta, el manejador reanuda en la instrucción siguiente y el flujo real queda escondido para el desensamblador. Ghidra muestra un `main` casi vacío; con **GDB** (o marcando el byte tras cada `UD2` como código) aparecen los cuatro `strcmp` y los literales.

## Enunciado y superficie

«Después de mucho pelear por proteger nuestras cadenas secretas, dimos con la solución: hacer la descompilación más difícil». Se entrega un único ELF de 64 bits (`behindthescenes`) que pide la contraseña por argumento.

## Reconocimiento

```bash
file behindthescenes
./behindthescenes            # ./challenge <password>
strings -a behindthescenes | head
```

`strings` no da la contraseña y `ltrace`/`strace` tampoco: el binario ejecuta `UD2` a propósito y la lógica real vive en el manejador de `SIGILL`.

## Análisis del código

`main` registra un manejador con `sigaction(SIGILL, ...)` y termina en `ud2` (`0f 0b`). Al ejecutarse, la CPU lanza `SIGILL`, el manejador avanza el `RIP` y continúa. Ghidra deja de desensamblar tras el primer `UD2`; de ahí que `main` parezca vacío.

## Explicación del fallo

Un ELF `stripped` que pide una contraseña de 12 caracteres. El autor insertó instrucciones **`UD2`** para que el descompilador se pierda: Ghidra muestra un `main` casi vacío. La solución es bajar a **GDB**, ver los cuatro `strncmp` y leer los literales comparados.

## Reproducción local

```bash
chmod +x behindthescenes
./behindthescenes Itz_0nLy_UD2
```

No necesita red ni contenedor: la contraseña se valida en local.

## Explotación

1. Ejecutar sin argumentos para ver el uso. 2. Desensamblar `main` con GDB o marcar como código el byte posterior a cada `UD2`. 3. Leer los cuatro `strcmp` y concatenar los fragmentos.

## Evidencia

- `behindthescenes`, ejecutable ELF `stripped`.

## Lecciones aprendidas

- **`UD2` y Ghidra**: si el decompilador da basura, no es un reto imposible: cambiar a GDB.
- **`SIGILL`, no `NOP`**: el binario no se rompe al llegar al `UD2`; el manejador lo salta y sigue. Parchear a `NOP` es una comodidad, no un requisito.
- **Longitud**: exige 12 bytes; contar los fragmentos antes de probar.

- La "anti-descompilación" es ofuscación: el ensamblador sigue contando la verdad.
- Comparar cadenas troceadas es una forma de esconder un secreto en el código.
- Saber cuándo abandonar una herramienta vale tanto como saber usarla.

## Mitigaciones y detección

Aquí no hay vulnerabilidad: el reto demuestra que **ofuscar no protege un secreto**. Si la contraseña se valida en el cliente, se extrae; `UD2` solo molesta a la herramienta, no al analista.

- Regla práctica: ningún secreto embebido en un binario distribuido; si hace falta, clave derivada por usuario y verificación en servidor.
- Detección (si se usara en malware): ejecutables con `SIGILL`/`SIGTRAP` como flujo normal y secciones sin desensamblar son señal de ofuscación.

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
