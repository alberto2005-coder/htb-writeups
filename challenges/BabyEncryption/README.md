---
challenge: BabyEncryption
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, affine, modular-inverse, python]
---

# BabyEncryption — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Se entrega `chall.py` y `msg.enc`. El cifrado es aritmética escolar sobre cada byte: `((123 * c) + 18) % 256`. Es una función **afín** sobre `Z/256`, así que se invierte multiplicando por el inverso modular de 123, que es **179** (porque `123 * 179 ≡ 1 mod 256`).

## Evidencia

- `chall.py` (cifrado) y `msg.enc` (mensaje cifrado, binario).

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

## Tropiezos

- **`pow(123, -1, 256)`**: existe desde Python 3.8; si no, calcularlo a mano (179).
- **Multiplicar por 123 después de restar**: invertir el orden produce basura.
- **`msg.enc` binario**: abrirlo en modo `rb`, nunca como texto.

## Lecciones

- Toda función afín `a*x + b (mod m)` es reversible si `gcd(a, m) = 1`.
- Un cifrado "casero" sin clave es una codificación: se rompe con álgebra, no con fuerza bruta.
- Comprobar con el prefijo conocido de la flag es el test más rápido.
