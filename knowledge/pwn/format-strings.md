---
title: "Format strings: leer y escribir con printf"
tags: [pwn, format-string, printf, cwe-134, x86-64]
---

# Format strings: leer y escribir con `printf`

[🇬🇧 English](format-strings.en.md) | **Español**

## 1. Cuándo mirar aquí

El programa pasa entrada del usuario como primer argumento de `printf`, `fprintf`, `sprintf` o `snprintf`. No hace falta desbordar nada: el formato permite leer la pila y escribir en direcciones.

```c
printf(user_input);        // vulnerable
printf("%s", user_input);  // correcto
```

## 2. Qué hace cada especificador

| Especificador | Efecto |
|---|---|
| `%lx` | lee un argumento (8 bytes) y lo imprime en hex |
| `%s` | trata el argumento como puntero a cadena |
| `%n` | escribe en el puntero el número de caracteres impresos |
| `%hn` | igual, pero como `unsigned short` (2 bytes) |
| `%hhn` | igual, como un byte |

Sin argumentos suficientes, `printf` toma valores de la pila y de los registros de guardado. Por eso `%lx.%lx.%lx` va revelando el contenido.

## 3. Argumentos posicionales

`%6$lx` lee el sexto argumento sin consumir los anteriores; `%7$hn` escribe en el séptimo. El índice depende de la arquitectura y del build: en x86-64 los primeros van en registros (`rsi`, `rdx`, `rcx`, `r8`, `r9`) y el resto en la pila, así que no se puede asumir.

Enumerar es la forma fiable:

```text
%lx.%lx.%lx.%lx.%lx.%lx.%lx.%lx
```

Cuando aparece el valor conocido (por ejemplo `deadbeef`), ese es el índice del valor; el de la dirección suele ser el siguiente.

## 4. Escribir con `%n`

`%n` escribe el contador acumulado, no un valor arbitrario. Para escribir `0x1337`:

```text
%4919c%7$hn
```

- `%4919c` imprime 4919 caracteres (0x1337).
- `%7$hn` escribe esos 2 bytes en la dirección del argumento 7.

Para valores mayores se reparte en dos escrituras (`%hn` bajo y alto) o se usa `%hhn` byte a byte. El orden importa: el contador solo crece, así que se escribe primero el valor menor y se ajusta con relleno.

## 5. Cuando la dirección no está en la pila

Si el puntero no aparece, se coloca en el propio formato (alineado a 8 bytes) y se referencia con un índice calculado. En x86-64 el formato se pasa en `rdi`, así que los primeros bytes del payload pueden ser la dirección; el índice se ajusta hasta que `%N$hn` apunte a ella.

## 6. Límites y errores

- **`%n` bloqueado por glibc**: con `_FORTIFY_SOURCE` y formatos en memoria de solo lectura puede abortar; en un CTF se comprueba en local.
- **Índice equivocado**: el payload escribe en una dirección basura y el proceso muere.
- **Cadena demasiado larga**: el `read` limita los bytes; si no caben dirección y relleno, se usan varios pasos.
- **`%s` con puntero inválido**: segfault; sirve para probar índices, no para filtrar.
- **PIE y ASLR**: si el objetivo está en el binario o en la pila, hay que filtrar primero su dirección con `%lx` o `%s`.

## 7. Detección y mitigación

- Nunca pasar entrada como formato; usar `printf("%s", buf)` o `fputs`.
- Compilar con `-Wformat -Wformat-security` y `_FORTIFY_SOURCE=2`.
- Detección: peticiones con `%n`, `%hn`, `%s` o cadenas de `%lx`; caídas con SIGSEGV tras una entrada con `%`.
- CWE-134 (uncontrolled format string); MITRE T1190.

Referencias: `man 3 printf`, CWE-134 y las notas de pwntools sobre `fmtstr_payload`.
