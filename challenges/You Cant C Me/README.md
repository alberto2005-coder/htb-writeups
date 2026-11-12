---
challenge: You Cant C Me
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ltrace, strcmp]
---

# You Cant C Me — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flag real.

## TL;DR

El binario `auth` pide una clave y la compara con `strcmp`. Está stripped, pero `ltrace` muestra la llamada y el segundo argumento: la clave correcta. Al introducirla, el programa imprime la flag.

## Enunciado y superficie

- Reversing, Very Easy, retirado.
- Se entrega un ELF `auth`.
- El programa solo pide una clave por stdin.

```bash
file auth
checksec --file=auth
```

## Reconocimiento

```bash
./auth
# Welcome!
# Insert key:
```

Si se introduce cualquier cosa, responde con un mensaje negativo. `strings` no revela la comparación porque el binario está stripped, pero `ltrace` sí muestra las funciones de libc.

## Análisis del código

```bash
ltrace ./auth
```

La traza incluye:

```text
strcmp("<KEY>", "<INPUT>")
```

El primer argumento es la clave esperada; el segundo, la entrada del usuario. No hace falta descompilar: la comparación ocurre en libc y `ltrace` la intercepta.

## Explicación del fallo

La comprobación se hace en el cliente con `strcmp`, y la clave está en memoria. Cualquier usuario puede observarla con un depurador o `ltrace`. No hay ofuscación ni comparación por hash.

## Reproducción local

```bash
ltrace ./auth
# Introducir una cadena cualquiera
```

También se puede usar `gdb`:

```bash
gdb -q ./auth
break strcmp
run
```

Al romper, `$rdi` y `$rsi` contienen las dos cadenas.

## Explotación

Se ejecuta el binario con la clave observada:

```bash
printf '<KEY>\n' | ./auth
```

La salida correcta contiene la flag. Se redacta en la evidencia.

## Evidencia

- `file` y `checksec`.
- Traza de `ltrace` con la llamada a `strcmp`.
- Ejecución con la clave y flag redactada.

## Lecciones aprendidas

- `ltrace` es suficiente para comparaciones con libc.
- Un binario stripped no oculta las llamadas a funciones dinámicas.
- `gdb` con breakpoint en `strcmp` confirma la clave.
- La clave en claro en memoria es trivial de extraer.

## Mitigaciones y detección

- No almacenar secretos en binarios de cliente.
- Usar comparación de hashes con sal y verificación en servidor.
- Ofuscar no sustituye a un diseño seguro.
- Detección: poco aplicable en CTF; en producción, revisar exposición de secretos.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/you-cant-c-me/>
- <https://sourceware.org/gdb/current/onlinedocs/gdb/>
- <https://man7.org/linux/man-pages/man1/ltrace.1.html>
