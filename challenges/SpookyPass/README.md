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

Se entrega un único fichero, `pass`, un ELF de 64 bits. `file` y `strings -n 6` responden casi todo: la contraseña aparece como literal y, con `-e l` (UTF-32 little endian), también la flag.

## Análisis del código

No hay código fuente y no hace falta: la comprobación es un `strcmp` en `main` contra un literal de `.rodata`, y la flag vive en la misma sección. En Ghidra/IDA se ven las dos cadenas juntas; en estático, `strings` ya las separa.

```bash
strings -n 6 pass | less
strings -e l pass | grep -i htb
objdump -d -M intel pass | grep -A2 strcmp
```

## Explicación del fallo

Un ELF de 64 bits pide una contraseña; si es correcta, imprime la flag. La contraseña está **en claro** en el binario: `strings` la encuentra sin abrir un desensamblador. La flag también aparece en el binario como cadena UTF-32 (un carácter por cada cuatro bytes).

## Reproducción local

El binario se puede ejecutar en una VM aislada: con la contraseña correcta imprime la flag, sin red ni dependencias externas. Aun así, el análisis estático ya la da sin ejecutar nada.

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

- No incrustar secretos ni contraseñas en binarios: cualquiera con `strings` los lee.
- Si hay que comparar una contraseña en cliente, usar un hash con sal y comparación en tiempo constante; aun así el binario es público.
- La ofuscación (strip, packers, cifrado de cadenas) sólo retrasa el análisis; no protege un secreto embebido.
- Detección: publicación de binarios con cadenas sensibles, y comprobación en CI de secretos en artefactos compilados.

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
