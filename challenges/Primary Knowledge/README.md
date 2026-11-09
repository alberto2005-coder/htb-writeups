---
challenge: Primary Knowledge
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, small-modulus, euler-phi, textbook-rsa]
---


# Primary Knowledge — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

RSA mal construido: el módulo `n` **es primo**. Entonces `φ(n) = n − 1`, la clave privada sale sin factorizar nada y el mensaje se descifra en dos líneas. El nombre del reto es la pista: si `n` es primo, no hay dos primos que buscar.

## Enunciado y superficie

```python
from Crypto.Util.number import getPrime, bytes_to_long
from secret import FLAG

n = getPrime(1024)          # un único primo, no un producto
e = 0x10001
c = pow(bytes_to_long(FLAG), e, n)
print(f'n = {n}')
print(f'e = {e}')
print(f'c = {c}')
```

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

En RSA normal `n = p·q` y `φ(n) = (p−1)(q−1)`. Aquí solo se generó un primo, así que:

- `φ(n) = n − 1`
- `d = e⁻¹ mod (n − 1)`
- `m = cᵈ mod n`

No hay factorización ni Coppersmith: es álgebra directa.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

```python
from Crypto.Util.number import long_to_bytes

n = <n>
e = <e>
c = <c>

d = pow(e, -1, n - 1)
m = pow(c, d, n)
print(long_to_bytes(m).decode())
```

`pow(e, -1, m)` existe desde Python 3.8; en versiones anteriores, `inverse()` de `Crypto.Util.number` o el algoritmo extendido de Euclides.

Comprobación: `e*d % (n-1) == 1`, y el resultado debe empezar por `HTB{`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Confundir φ con n**: hay que usar `n − 1`, no `n`.
- **`d` negativa**: `pow(e, -1, m)` ya la normaliza; si se calcula a mano con Euclides, sumar `m` hasta que sea positiva.
- **`long_to_bytes`**: si el mensaje sale con ceros delante, usar `strip` solo de nulos, no de espacios.
- **`n` de 1024 bits**: el reto no pide factorizar; si se intenta, se pierde el tiempo.

- La seguridad de RSA depende de que `n` sea producto de dos primos grandes y distintos.
- Si `n` es primo, `φ(n)` es público por definición: el cifrado es reversible por cualquiera.
- Mitigación: generar claves con librerías contrastadas (`cryptography`, OpenSSL) y validar que `n = p·q` con `p ≠ q`.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
