---
challenge: Makeshift
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, custom-cipher, permutation]
---

# Makeshift — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

«Cifrado» casero: se invierte la cadena y luego se permuta cada bloque de tres caracteres como `b, c, a`. Ambas operaciones son invertibles, así que se deshace en orden inverso: primero la permutación, después la inversión.

## Enunciado y superficie

El reto entrega `source.py` y `output.txt`:

```python
flag = FLAG[::-1]
new_flag = ''
for i in range(0, len(flag), 3):
    new_flag += flag[i+1]
    new_flag += flag[i+2]
    new_flag += flag[i]
print(new_flag)
```

No hay clave ni servidor: es un ejercicio de inversión, no de criptoanálisis.

## Reconocimiento

```bash
cat output.txt
# !?}De!e3d_5n_nipaOw_3eTR3bt4{_THB
wc -c output.txt
```

La cadena empieza por `!?}` y termina en `_THB`: la flag está al revés y permutada.

## Explicación del fallo

Dos capas triviales:

1. **Inversión**: `FLAG[::-1]` da la vuelta a toda la cadena.
2. **Permutación por ternas**: de `(a, b, c)` se emite `b, c, a`.

El cifrado se lee tal cual; el trabajo es escribir el inverso sin equivocarse en los índices.

## Explotación

```python
c = open("output.txt").read().strip()
restored = [''] * len(c)

j = 0
for i in range(0, len(c), 3):
    restored[i + 1] = c[j];     j += 1
    restored[i + 2] = c[j];     j += 1
    restored[i]     = c[j];     j += 1

print(''.join(restored)[::-1])
```

```text
HTB{<flag>}
```

Comprobación: el resultado debe empezar por `HTB{`. Si sale desplazado un carácter, el error está en asignar `i+1` donde toca `i`.

## Evidencia

- Salidas recortadas; sin flags.

## Lecciones aprendidas

- **Orden de las capas**: invertir y luego permutar (o al revés) da basura; hay que deshacer de dentro hacia fuera.
- **Longitud no múltiplo de 3**: el bucle original lanzaría `IndexError`; aquí la longitud es múltiplo.
- **Índices**: una lista mutable evita el clásico `string index out of range`.
- **Confundir con ROT**: no hay sustitución de letras, sólo posición.

- Un cifrado «casero» sin clave no aporta confidencialidad: es una permutación.
- Con el código delante, el reto es invertir con cuidado, no criptoanalizar.
- Mitigación: cifrado autenticado estándar (AES-GCM, ChaCha20-Poly1305), nunca algoritmos propios.
