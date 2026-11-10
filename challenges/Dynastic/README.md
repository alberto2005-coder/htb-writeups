---
challenge: Dynastic
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, classical, caesar, trithemius, reverse-engineering]
---

# Dynastic — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Cifrado clásico con **desplazamiento progresivo**: cada letra se mueve una posición más que la anterior (cifrado de Trithemius, un César incremental). Se invierte el proceso con el mismo bucle y sale el texto claro.

## Enunciado y superficie

Se entrega un script corto y el texto cifrado. El script mapea cada carácter a un índice (`ord(c) - 0x41`), suma un desplazamiento que crece, y vuelve a mapear con módulo 26.

```python
def to_identity_map(a):
    return ord(a) - 0x41

def from_identity_map(a):
    return chr(a % 26 + 0x41)

def encrypt(m):
    c = ''
    for i in range(len(m)):
        ch = m[i]
        if not ch.isalpha():
            ech = ch
        else:
            chi = to_identity_map(ch)
            ech = from_identity_map(chi + i)
        c += ech
    return c
```

## Reconocimiento

Dos ficheros: `source.py` y `output.txt`. El segundo empieza con la instrucción de envolver el resultado en `HTB{}` y sigue con una cadena de mayúsculas, `_`, `?!` y comas.

## Análisis del código

`encrypt` suma `i` al índice de cada letra y deja intacto lo que no es alfabético. `from_identity_map` aplica `% 26`, así que el resultado siempre cae en `A-Z`.

## Explicación del fallo

Tres detalles lo resuelven:

1. **Solo letras**: los caracteres no alfabéticos pasan intactos, así que las llaves `{}` y los guiones bajos sobreviven y sirven de ancla.
2. **Desplazamiento = índice**: la primera letra no se mueve, la segunda una, la tercera dos…
3. **Módulo 26**: es aritmética de César, sin sustitución dependiente del texto.

Con eso, descifrar es restar en lugar de sumar.

## Reproducción local

```bash
python3 - <<'PY'
from source import to_identity_map, from_identity_map
c = open('output.txt').read().splitlines()[-1]
print(''.join(ch if not ch.isalpha() else from_identity_map(to_identity_map(ch) - i)
              for i, ch in enumerate(c)))
PY
```

El `import` funciona porque el script del reto no ejecuta nada al cargarse.

## Explotación

```python
def decrypt(c):
    m = ''
    for i in range(len(c)):
        ch = c[i]
        if not ch.isalpha():
            mch = ch
        else:
            chi = to_identity_map(ch)
            mch = from_identity_map(chi - i)
        m += mch
    return m
```

Si el texto cifrado empieza por `HTB{`, la comprobación es inmediata: la `H` no se desplaza, la `T` se desplazó 1, la `B` 2. Se valida el bucle con esas tres letras antes de ejecutarlo entero.

Alternativa sin código: en CyberChef, «ROT13 Brute Force» o un script de una línea; también se puede reconocer a ojo porque el patrón de desplazamiento creciente es el del cifrado de Trithemius.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Mayúsculas**: el script asume alfabeto `A-Z`. Con minúsculas hay que ajustar la base (`0x61`) y el módulo.
- **Signo del desplazamiento**: restar el índice; sumarlo otra vez devuelve el cifrado.
- **Índices negativos**: en Python `% 26` ya devuelve positivo, pero en otros lenguajes hay que corregirlo.
- **No es Vigenère**: aquí no hay clave, solo la posición.

- Reconocer la familia del cifrado ahorra escribir fuerza bruta: desplazamiento creciente = Trithemius.
- Si el script de cifrado es invertible y se entrega, el reto es leerlo, no adivinar.
- Mitigación (contexto real): los cifrados clásicos no son cifrado; usar AES-GCM con nonce único.

## Mitigaciones y detección

Aquí no hay sistema que proteger: el reto enseña a leer un cifrado clásico. En un sistema real, un desplazamiento fijo o progresivo no es cifrado: cualquier analista lo revierte sin clave.

- Usar AES-GCM con nonce único y clave fuera del código.
- No llamar «cifrado» a una codificación o a un César: cambia el modelo de amenaza.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
