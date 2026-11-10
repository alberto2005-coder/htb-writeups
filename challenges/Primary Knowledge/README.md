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

El material del reto es el propio **script de generación** y su salida: `n`, `e` y `c`. No hay servicio, ni endpoint, ni binario: es criptografía pura y el ataque se hace sobre los números.

## Análisis del código

Sí se entrega código, y ahí está el fallo: `getPrime(1024)` devuelve **un primo**, no un producto de dos primos. `n` no tiene factores que buscar porque no es un módulo RSA: es un número primo de 1024 bits.

- `φ(n) = n − 1` en lugar de `(p−1)(q−1)`.
- No hace falta factorizar ni Coppersmith: con `d` conocido, el mensaje sale directo.

## Explicación del fallo

En RSA normal `n = p·q` y `φ(n) = (p−1)(q−1)`. Aquí solo se generó un primo, así que:

- `φ(n) = n − 1`
- `d = e⁻¹ mod (n − 1)`
- `m = cᵈ mod n`

No hay factorización ni Coppersmith: es álgebra directa.

## Reproducción local

Con `pycryptodome` instalado basta; no hace falta red ni contenedor:

```bash
python3 - <<'PY'
from Crypto.Util.number import long_to_bytes
n, e, c = <n>, <e>, <c>
d = pow(e, -1, n - 1)
print(long_to_bytes(pow(c, d, n)).decode())
PY
```

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

- Generar `n` como producto de **dos primos** de tamaño comparable y verificar que es compuesto antes de publicar la clave.
- Usar una librería de alto nivel (`cryptography`, `PyCryptodome` con `RSA.generate`) en vez de montar el esquema a mano.
- Nunca implementar RSA de libro de texto: sin padding OAEP, un `e` pequeño y un módulo primo se rompen igual de fácil.
- Detección: tests de la clave pública (comprobar que `n` es compuesto, tamaño de `e`, presencia de padding) en CI.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
