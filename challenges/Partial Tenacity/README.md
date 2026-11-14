---
challenge: Partial Tenacity
type: Crypto
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [crypto, rsa, partial-key, factorization, python]
---

# Partial Tenacity — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega una clave RSA con bits conocidos de `p` y `q` y un mensaje cifrado. Los bits desconocidos se recuperan con una búsqueda guiada por la relación `n = p*q`, y la clave privada resultante descifra el mensaje.

## Enunciado y superficie

- Crypto, Medium, retirado.
- Se entrega `n`, `e`, `c` y una representación parcial de los primos.
- El objetivo es recuperar el texto claro.

## Reconocimiento

```bash
python3 - <<'PY'
from Crypto.PublicKey import RSA
# Cargar n, e y c del archivo del reto
PY
```

- `n` tiene un tamaño normal para RSA.
- Se conoce un porcentaje de bits de `p` y `q`.
- No hay servicio remoto: el ataque es offline.

## Análisis

Los bits conocidos se alinean desde el bit menos significativo. Para cada posición se prueban las combinaciones de bits de `p` y `q` que hacen que el producto coincida con `n` en esa posición. La búsqueda se poda porque solo unas pocas combinaciones son válidas.

```python
# pseudo-código: crecer p y q desde LSB
for bit in range(known_bits):
    for dp in (0, 1):
        for dq in (0, 1):
            if ((p + dp) * (q + dq)) % (1 << (bit + 1)) == n % (1 << (bit + 1)):
                # conservar la rama
                ...
```

## Explotación

Se implementa la búsqueda, se reconstruyen `p` y `q`, se calcula `d = e^{-1} mod φ(n)` y se descifra `c`. Se valida que `p*q == n` antes de usar la clave.

```python
from Crypto.Util.number import long_to_bytes, inverse
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
print(long_to_bytes(pow(c, d, n)))
```

## Evidencia

- Factores reconstruidos que multiplican exactamente `n`.
- Clave privada válida.
- Mensaje descifrado con formato legible.

## Lecciones aprendidas

- RSA no es seguro si se filtra una parte suficiente de los primos.
- La relación modular permite podar la búsqueda bit a bit.
- Validar `p*q == n` evita ramas falsas.
- El ataque es offline y no depende de la red.

## Mitigaciones y detección

- No exponer bits de primos ni valores intermedios.
- Usar claves nuevas tras cualquier fuga parcial.
- Emplear bibliotecas que generen primos con suficiente entropía.
- Revisar retos y sistemas que publican metadatos de claves.
- Referencias: RSA partial key exposure, Boneh.

## Referencias

- <https://www.hackthebox.com/challenges/Partial%20Tenacity>
- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)>
- <https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf>
- <https://attack.mitre.org/techniques/T1556/>
