---
challenge: Makeshift
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, custom-cipher, permutation, reverse-engineering]
---

# Makeshift — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

«Cifrado» propio de tres líneas: invierte la cadena y luego rota cada bloque de tres caracteres. Ambas operaciones son invertibles, así que se deshace en orden inverso: primero la permutación, después la inversión.

## Enunciado y superficie

```python
flag = FLAG[::-1]
new_flag = ''
for i in range(0, len(flag), 3):
    new_flag += flag[i+1]
    new_flag += flag[i+2]
    new_flag += flag[i]
print(new_flag)
```

Se entrega la salida. No hay clave.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Dos capas, ambas triviales:

1. **Inversión**: `FLAG[::-1]` da la vuelta a toda la cadena.
2. **Permutación por bloques**: en cada terna `(a, b, c)` se emite `b, c, a`.

El cifrado se lee tal cual; el trabajo es escribir el inverso sin equivocarse en los índices.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

Se deshace de dentro hacia fuera: primero la permutación, luego la inversión.

```python
c = "<texto cifrado>"
restored = [''] * len(c)

j = 0
for i in range(0, len(c), 3):
    restored[i + 1] = c[j]; j += 1
    restored[i + 2] = c[j]; j += 1
    restored[i] = c[j]; j += 1

print(''.join(restored)[::-1])
```

Comprobación rápida: el resultado debe empezar por `HTB{`. Si sale desplazado un carácter, el error está en asignar `i+1` donde toca `i`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Longitud no múltiplo de 3**: el bucle original lanzaría `IndexError`; si el texto tiene relleno, hay que tratarlo antes.
- **Orden de las capas**: invertir primero y permutar después da basura; es al revés.
- **Índices**: usar una lista mutable evita el clásico `string index out of range`.
- **Confundir con ROT**: aquí no hay sustitución de letras, solo posición.

- Un cifrado «casero» sin clave no aporta confidencialidad: es una permutación.
- Con el código delante, el reto es invertir con cuidado, no criptoanalizar.
- Mitigación: cifrado autenticado estándar (AES-GCM, ChaCha20-Poly1305) y nunca algoritmos propios.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
