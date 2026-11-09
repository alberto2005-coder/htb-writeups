---
challenge: SpookyPass
category: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, strings, static-analysis]
type: Reversing
---


# SpookyPass — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un ELF de 64 bits pide una contraseña; si es correcta, imprime la flag. La contraseña está **en claro** en el binario: `strings` la encuentra sin abrir un desensamblador. La flag también aparece en el binario como cadena UTF-32 (un carácter por cada cuatro bytes).

## Enunciado y superficie

- Categoría Reversing; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Un ELF de 64 bits pide una contraseña; si es correcta, imprime la flag. La contraseña está **en claro** en el binario: `strings` la encuentra sin abrir un desensamblador. La flag también aparece en el binario como cadena UTF-32 (un carácter por cada cuatro bytes).

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `pass`, ejecutable ELF.

## Lecciones aprendidas

- **Cadenas UTF-32**: `strings` normal no las ve como texto continuo; hay que usar `-e l` o mirar el volcado hexadecimal.
- **Ejecutar fuera de la VM**: innecesario; basta el análisis estático.
- **Pipes que cortan la salida**: la flag puede salir partida en la terminal; redirigir a fichero.

- Un binario sin ofuscar filtra secretos por sus cadenas.
- No siempre hace falta depurador: muchas veces `strings` resuelve el reto.
- Comprobar las variantes de codificación (ASCII, UTF-16, UTF-32) cuando el texto parece basura.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
## Método

1. **Triage**:

```bash
file pass; chmod +x pass
strings -n 6 pass | less
```

2. **Contraseña**: entre las cadenas aparece `s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5`. Ejecutarla la valida y muestra la flag.

3. **Flag sin ejecutar**: si el texto va en UTF-32, `strings -e l` extrae cadenas de 32 bits:

```bash
strings -e l pass | grep -i htb
```

4. **Alternativa estática**: abrir en Ghidra/IDA y mirar el `strcmp` de `main`; las dos cadenas están juntas.
