---
challenge: Iced Tea
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, tea, block-cipher, decryption]
---


# Iced Tea — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Bloques cifrados con **TEA** (Tiny Encryption Algorithm) y la clave incluida en el código. No hay vulnerabilidad: es implementar el descifrado estándar. La trampa es el empaquetado de enteros y el *endianness*.

## Enunciado y superficie

Se entrega el script de cifrado con `key` y dos bloques de 64 bits en hexadecimal. TEA usa 32 rondas, la constante `delta = 0x9e3779b9` y una clave de 128 bits repartida en cuatro palabras de 32.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

El cifrado suma `delta` y mezcla `v0`/`v1` con desplazamientos; el descifrado hace lo mismo en orden inverso, restando `delta`:

```python
def decrypt(v, k):
    v0, v1 = v
    delta = 0x9e3779b9
    s = (delta * 32) & 0xffffffff
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & 0xffffffff
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & 0xffffffff
        s = (s - delta) & 0xffffffff
    return v0, v1
```

Detalles que fallan si se ignoran:

- Todas las sumas van **módulo 2³²**: hay que enmascarar con `& 0xffffffff`.
- `s` se decrementa **después** de cada ronda.
- `k` son cuatro enteros de 32 bits, no la clave como bytes.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

```python
from struct import pack, unpack

key = [<k0>, <k1>, <k2>, <k3>]

for block in [<bloque1>, <bloque2>]:
    v = unpack('>2I', bytes.fromhex(block))
    d = decrypt(v, key)
    print(pack('>2I', *d).decode(errors='ignore'), end='')
```

Si el texto sale con caracteres raros, probar `<2I` en lugar de `>2I`: el *endianness* de los bloques es el error más común.

Comprobación: el resultado concatenado debe empezar por el prefijo de la flag.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Endianness**: `struct.unpack('>2I')` para big-endian; el script de cifrado suele usar el mismo formato que hay que invertir.
- **Máscara de 32 bits**: sin `& 0xffffffff` los desplazamientos se desbordan y el descifrado da basura.
- **Orden de las palabras**: `k[0..3]` en el mismo orden que el cifrador; si se intercambian, no descifra.

- TEA es un cifrador de juguete: 64 bits de bloque y clave de 128, con debilidades conocidas (equivalentes de clave, related-key).
- Con la clave en el código, el reto es implementar bien el inverso, no romper nada.
- Mitigación: usar AES-GCM o ChaCha20-Poly1305, nunca TEA/XTEA en producción.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
