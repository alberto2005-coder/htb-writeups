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

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Tres detalles lo resuelven:

1. **Solo letras**: los caracteres no alfabéticos pasan intactos, así que las llaves `{}` y los guiones bajos sobreviven y sirven de ancla.
2. **Desplazamiento = índice**: la primera letra no se mueve, la segunda una, la tercera dos…
3. **Módulo 26**: es aritmética de César, sin sustitución dependiente del texto.

Con eso, descifrar es restar en lugar de sumar.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

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

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
