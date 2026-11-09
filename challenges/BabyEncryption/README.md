---
challenge: BabyEncryption
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, affine, modular-inverse, python]
type: Crypto
---

# BabyEncryption — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Se entrega `chall.py` y `msg.enc`. El cifrado es aritmética escolar sobre cada byte: `((123 * c) + 18) % 256`. Es una función **afín** sobre `Z/256`, así que se invierte multiplicando por el inverso modular de 123, que es **179** (porque `123 * 179 ≡ 1 mod 256`).

## Enunciado y superficie

- Categoría Crypto; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Se entrega `chall.py` y `msg.enc`. El cifrado es aritmética escolar sobre cada byte: `((123 * c) + 18) % 256`. Es una función **afín** sobre `Z/256`, así que se invierte multiplicando por el inverso modular de 123, que es **179** (porque `123 * 179 ≡ 1 mod 256`).

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `chall.py` (cifrado) y `msg.enc` (mensaje cifrado, binario).

## Lecciones aprendidas

- **`pow(123, -1, 256)`**: existe desde Python 3.8; si no, calcularlo a mano (179).
- **Multiplicar por 123 después de restar**: invertir el orden produce basura.
- **`msg.enc` binario**: abrirlo en modo `rb`, nunca como texto.

- Toda función afín `a*x + b (mod m)` es reversible si `gcd(a, m) = 1`.
- Un cifrado "casero" sin clave es una codificación: se rompe con álgebra, no con fuerza bruta.
- Comprobar con el prefijo conocido de la flag es el test más rápido.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
## Método

1. **Leer el cifrado**:

```python
def encryption(msg):
    ct = []
    for char in msg:
        ct.append(((123 * char) + 18) % 256)
    return bytes(ct)
```

2. **Invertir el orden**: primero restar 18, luego multiplicar por el inverso.

```python
def decryption(msg):
    return bytes((179 * (c - 18)) % 256 for c in msg)

print(decryption(open("msg.enc", "rb").read()).decode())
```

3. **Comprobar** que el resultado empieza por `HTB{`; si no, el módulo o el desplazamiento están mal copiados.
