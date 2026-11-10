---
challenge: xorxorxor
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, xor, known-plaintext]
type: Crypto
---

# xorxorxor — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

El cifrado es un **XOR** del mensaje con una clave corta que se repite. Como el texto empieza por `HTB{`, los primeros bytes de la clave salen directamente; con esos bytes se descifra el resto y se comprueba que el resultado es texto imprimible. Sin fuerza bruta.

## Enunciado y superficie

- Categoría Crypto; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- El reto entrega dos ficheros: `challenge.py` (el cifrado) y `output.txt` con el resultado en hexadecimal.
- `challenge.py` hace XOR del mensaje con una clave de **4 bytes** que repite; la clave no viaja en el fichero.
- No hay más material: el ataque es de **texto plano conocido**, no de fuerza bruta.

## Análisis del código

- `challenge.py` recorre el mensaje byte a byte y lo XOR con `key[i % len(key)]`, con `len(key) == 4`.
- Al repetir la clave cada 4 bytes, el cifrado es un XOR posicional; cada posición se resuelve por separado.
- La flag empieza por `HTB{`, así que los cuatro primeros bytes de la clave salen de `ciphertext ^ b'HTB{'`.

## Explicación del fallo

El cifrado es un **XOR** del mensaje con una clave corta que se repite. Como el texto empieza por `HTB{`, los primeros bytes de la clave salen directamente; con esos bytes se descifra el resto y se comprueba que el resultado es texto imprimible. Sin fuerza bruta.

## Reproducción local

```python
ct = bytes.fromhex(open('output.txt').read().strip())
key = bytes(c ^ p for c, p in zip(ct, b'HTB{'))
print(key)                    # 4 bytes
print(bytes(c ^ key[i % 4] for i, c in enumerate(ct)).decode())
```

## Explotación

1. Se derivan los 4 bytes de clave con el prefijo conocido `HTB{`.
2. Se descifra todo el fichero repitiendo la clave cada 4 posiciones.
3. Se verifica que el resultado es ASCII imprimible y termina en `}`: si no, la longitud de la clave no era 4.

## Evidencia

- `challenge.py` (cifrado) y `output.txt` (ciphertext en hexadecimal).

## Lecciones aprendidas

- **Longitud de la clave**: si la clave recuperada no cuadra con el alfabeto, probar longitudes de 1 a 8 y quedarse con la que dé texto legible.
- **Hex con saltos**: limpiar el fichero antes de `fromhex`.
- **Confundir con one-time pad**: aquí la clave se repite; por eso es rompible.

- XOR con clave repetida es un cifrado de Vigenère en binario: cae con texto conocido.
- El formato de la flag es información pública y suficiente para arrancar.
- Un cifrado sin más que un XOR no aporta confidencialidad.

## Mitigaciones y detección

- No usar XOR con clave corta y reutilizada: AES-GCM o un keystream aleatorio por mensaje. Detección: ficheros con entropía baja y longitud múltiplo de la clave.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
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
