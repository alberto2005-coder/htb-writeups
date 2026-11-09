---
challenge: SpookyPass
category: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, strings, static-analysis]
---

# SpookyPass — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un ELF de 64 bits pide una contraseña; si es correcta, imprime la flag. La contraseña está **en claro** en el binario: `strings` la encuentra sin abrir un desensamblador. La flag también aparece en el binario como cadena UTF-32 (un carácter por cada cuatro bytes).

## Evidencia

- `pass`, ejecutable ELF.

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

## Tropiezos

- **Cadenas UTF-32**: `strings` normal no las ve como texto continuo; hay que usar `-e l` o mirar el volcado hexadecimal.
- **Ejecutar fuera de la VM**: innecesario; basta el análisis estático.
- **Pipes que cortan la salida**: la flag puede salir partida en la terminal; redirigir a fichero.

## Lecciones

- Un binario sin ofuscar filtra secretos por sus cadenas.
- No siempre hace falta depurador: muchas veces `strings` resuelve el reto.
- Comprobar las variantes de codificación (ASCII, UTF-16, UTF-32) cuando el texto parece basura.
