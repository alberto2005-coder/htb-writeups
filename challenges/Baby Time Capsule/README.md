---
challenge: Baby Time Capsule
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, small-modulus, factoring]
type: Crypto
---

# Baby Time Capsule — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Tres "cápsulas del tiempo": tripletas `(n, e, ct)` de **RSA** con módulos **pequeños** y el mismo mensaje. Con `n` de pocos bits, factorizar es trivial (Factordb o `sympy.factorint`), se calcula `φ(n)` y `d`, y se descifra. El cifrado es correcto; el tamaño de la clave, no.

## Enunciado y superficie

- Categoría Crypto; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Tres "cápsulas del tiempo": tripletas `(n, e, ct)` de **RSA** con módulos **pequeños** y el mismo mensaje. Con `n` de pocos bits, factorizar es trivial (Factordb o `sympy.factorint`), se calcula `φ(n)` y `d`, y se descifra. El cifrado es correcto; el tamaño de la clave, no.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `source.py` y `output.txt` con las tripletas.

## Lecciones aprendidas

- **`e` pequeño con `m` pequeño**: si `m^e < n`, el cifrado no necesita ni descifrado: la raíz `e`-ésima del entero da el mensaje.
- **Bytes vs entero**: convertir con `long_to_bytes`, no con `str()`.
- **`d` con `pow(..., -1, ...)`**: requiere Python 3.8+; si no, `sympy.invert`.

- RSA no es seguro por el algoritmo, sino por el tamaño y la calidad de `n`.
- Un módulo factorizable anula toda la seguridad, aunque el código sea impecable.
- `e=3` con mensajes cortos es el otro clásico: sin padding, se rompe con una raíz.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
## Método

1. **Mirar los números**: si `n` tiene menos de ~256 bits, está roto por diseño.

```python
for n, e, ct in capsules:
    print(n.bit_length(), e)
```

2. **Factorizar** `n = p * q`:

```bash
# copiar n en factordb.com
python -c "from sympy import factorint; print(factorint(n))"
```

3. **Clave privada**:

```python
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(ct, d, n)
print(m.to_bytes((m.bit_length() + 7)//8, 'big'))
```

4. **Comprobar** que el mensaje empieza por `HTB{`.
