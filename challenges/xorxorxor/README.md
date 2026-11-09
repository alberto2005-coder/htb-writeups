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

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

El cifrado es un **XOR** del mensaje con una clave corta que se repite. Como el texto empieza por `HTB{`, los primeros bytes de la clave salen directamente; con esos bytes se descifra el resto y se comprueba que el resultado es texto imprimible. Sin fuerza bruta.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

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

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
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
