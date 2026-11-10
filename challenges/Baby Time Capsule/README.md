---
challenge: Baby Time Capsule
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, hastad, crt, small-exponent]
type: Crypto
---

# Baby Time Capsule — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

`server.py` cifra **la misma flag** con RSA y `e = 5`, generando un módulo de 1024 bits nuevo en cada consulta. Con cinco cifrados bajo módulos coprimos, el teorema chino del resto reconstruye `m^5` **sin reducción modular** y una raíz quinta entera devuelve el mensaje: ataque de difusión de Håstad. No hay que factorizar nada.

## Enunciado y superficie

Servicio remoto que entrega "cápsulas del tiempo": cada petición devuelve un cifrado y una clave pública nuevos. Categoría Crypto, dificultad Very Easy.

## Reconocimiento

```python
from pwn import remote
io = remote("<HOST>", <PORT>)
# responder 'Y' cinco veces y guardar (ct_i, n_i)
```

## Análisis del código

```python
self.e = 5
m = bytes_to_long(self.msg)
m = pow(m, e, n)
```

Exponente fijo pequeño, mismo mensaje y un `n` distinto por consulta: el escenario exacto de Håstad.

## Explicación del fallo

Con `e = 5` y cinco módulos coprimos, `c_i = m^5 (mod n_i)`. El TCR da un único `C < prod(n_i)` con `C = m^5`; como `m^5 < prod(n_i)` para una flag corta, `C` es el valor entero de `m^5` y la raíz quinta exacta lo revela sin clave privada.

## Reproducción local

```python
from sympy.ntheory.modular import crt
from gmpy2 import iroot
from Crypto.Util.number import long_to_bytes

M = crt(ns, cts)[0]
m, exact = iroot(M, 5)
print(exact, long_to_bytes(int(m)))
```

## Explotación

1. Pedir cinco cápsulas (cinco `n` distintos, mismo `e = 5`).
2. Combinar con TCR para obtener `m^5` sobre los enteros.
3. `iroot(M, 5)`; si `exact` es `True`, ese es el mensaje.

## Evidencia

- `server.py` con `e = 5` y módulo nuevo por consulta.
- Los cinco pares `(n, ct)` y el `C` reconstruido.

## Lecciones aprendidas

- **`e` pequeño con el mismo mensaje y módulos distintos** es firma de Håstad, no de factorización.
- **El TCR convierte congruencias en una igualdad entera** cuando el producto de módulos supera a `m^e`.
- **Comprobar `exact` en `iroot`** evita aceptar una raíz truncada.

## Mitigaciones y detección

- Usar `e` estándar (65537) y **padding aleatorio** (OAEP) para que el mismo mensaje cifre distinto.
- No reutilizar el mensaje entre claves; rotar claves no sustituye al padding.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
- Håstad, *Solving simultaneous modular equations of low degree* (1988).
