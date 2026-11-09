---
challenge: xorxorxor
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, xor, known-plaintext]
---

# xorxorxor — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

El cifrado es un **XOR** del mensaje con una clave corta que se repite. Como el texto empieza por `HTB{`, los primeros bytes de la clave salen directamente; con esos bytes se descifra el resto y se comprueba que el resultado es texto imprimible. Sin fuerza bruta.

## Evidencia

- `challenge.py` (cifrado) y `output.txt` (ciphertext en hexadecimal).

## Método

1. **Leer el script**: `bytes([a ^ b for a, b in zip(flag, key)])`, con `key` más corto que la flag y repetido.

2. **Recuperar la clave** con el prefijo conocido:

```python
ct = bytes.fromhex(open("output.txt").read().strip())
known = b"HTB{"
key = bytes(c ^ p for c, p in zip(ct, known))
print(key)          # empieza la clave
```

3. **Extender la clave**: repetirla para alinear con el ciphertext y descifrar todo.

```python
pt = bytes(c ^ key[i % len(key)] for i, c in enumerate(ct))
print(pt)
```

4. **Validar**: el texto debe ser ASCII imprimible y terminar en `}`.

## Tropiezos

- **Longitud de la clave**: si la clave recuperada no cuadra con el alfabeto, probar longitudes de 1 a 8 y quedarse con la que dé texto legible.
- **Hex con saltos**: limpiar el fichero antes de `fromhex`.
- **Confundir con one-time pad**: aquí la clave se repite; por eso es rompible.

## Lecciones

- XOR con clave repetida es un cifrado de Vigenère en binario: cae con texto conocido.
- El formato de la flag es información pública y suficiente para arrancar.
- Un cifrado sin más que un XOR no aporta confidencialidad.
