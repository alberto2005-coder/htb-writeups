---
challenge: Up a Stream
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, java, streams, decompilation, encoding]
---

# Up a Stream — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un JAR transforma cada carácter con streams de Java, invierte el orden, aplica tres funciones aritméticas y repite el resultado cinco veces. Descompilando el bytecode se invierten las operaciones y se recupera la flag desde `output.txt`.

## Enunciado y superficie

- Reversing, Easy, retirado.
- Se entregan `stream.jar` y `output.txt`.
- El JAR imprime una cadena ofuscada; el archivo contiene la salida de la flag real.

```bash
file stream.jar output.txt
java -jar stream.jar
```

## Reconocimiento

- El JAR ejecuta una función `dunkTheFlag`.
- Usa `chars()`, `mapToObj`, `reduce`, `peek` y `Collectors`.
- La salida termina en `O`, no en cero.
- El resultado se repite cinco veces.

```bash
unzip -l stream.jar
```

## Análisis del código

Se descompila con CFR o `javap` y se simplifica la cadena de streams. Las llamadas `peek` no modifican el valor, así que `hydrate` y `waterlog` no participan en la transformación final.

Funciones relevantes:

```java
moisten(n) = n % 2 == 0 ? n : n * n
drench(n) = n << 1
dilute(n) = n / 2 + n
```

La primera reducción invierte el orden de los caracteres; la segunda concatena y la final añade `O` tras cada valor hexadecimal.

## Explicación del fallo

No hay un fallo de seguridad: el reto es un ejercicio de reversing. La ofuscación se apoya en la verbosidad de los streams y en funciones con nombres engañosos, no en criptografía.

## Reproducción local

1. Descompilar el JAR.
2. Confirmar que la salida local coincide con `java -jar stream.jar`.
3. Tomar una de las cinco repeticiones.
4. Separar por `O`, convertir de hexadecimal y aplicar las inversas.
5. Concatenar en orden inverso.

```java
undilute(n) = n * 2 / 3
undrench(n) = n >> 1
unmoisten(n) = n % 2 == 0 ? n : (int) Math.sqrt(n)
```

```bash
java Solve.java "$(cat output.txt)"
```

## Evidencia

- Salida del JAR.
- Funciones inversas y resultado intermedio.
- Flag redactada.

## Lecciones aprendidas

- `peek` no transforma el stream; solo observa.
- Los nombres de funciones no describen su efecto real.
- Repetir la salida cinco veces facilita tomar una muestra.

## Mitigaciones y detección

- No usar ofuscación como protección de secretos.
- Verificar la integridad del JAR antes de ejecutarlo.
- Analizar bytecode en un entorno aislado.
- Para secretos reales, usar cifrado y gestión de claves.

## Referencias

- <https://www.hackthebox.com/challenges/Up%20a%20Stream>
- <https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html>
- <https://www.javadecompilers.com/>
