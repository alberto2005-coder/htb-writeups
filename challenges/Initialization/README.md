---
challenge: Initialization
type: Crypto
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [crypto, aes, ctr, key-reuse, python]
---

# Initialization — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega el código que cifra varios mensajes con AES-CTR. La inicialización de las claves comparte la misma lista interna por un alias de listas, de modo que todos los mensajes usan la misma clave. Con varios ciphertexts y los contadores conocidos se alinean los keystreams y se recupera el texto claro.

## Enunciado y superficie

- Crypto, Medium, retirado.
- Se entregan `source.py`, `messages.txt` y `output.txt`.
- Cada línea de salida es un mensaje cifrado en hexadecimal.

```bash
file source.py output.txt
head -2 output.txt
```

## Reconocimiento

- `source.py` importa `AES`, `Counter` y `pad`.
- `MSG` se carga con `eval` desde `messages.txt`.
- Cada mensaje se cifra con una entrada de `KEYS` y un `CTR` propio.

## Análisis del código

La clase crea `self.KEYS = [[b'\x00'] * 16] * len(MSG)`. La multiplicación de listas repite la referencia a la misma lista interna, así que asignar `keys[i][j]` modifica todas las filas. El resultado es una única clave de 16 bytes compartida por todos los mensajes.

Los contadores se crean con `Counter.new(128)`, pero el cifrado CTR y la reutilización de clave permiten relacionar los keystreams cuando se conoce la estructura de los mensajes.

## Explicación del fallo

La entropía de la clave no es el problema: el problema es el alias de la lista. Todos los mensajes comparten clave y el nonce no se gestiona como un valor único y verificado. Con dos ciphertexts se puede calcular el XOR de los plaintexts y explotar texto conocido.

## Reproducción local

```bash
python3 source.py
# Comparar las claves efectivas de cada mensaje
```

## Explotación

```python
from Crypto.Cipher import AES

# c1, c2: ciphertexts; k: clave recuperada
p1 = bytes(a ^ b for a, b in zip(c1, keystream))
```

Se usa un mensaje conocido o la estructura repetida para obtener suficientes bytes del keystream y reconstruir la flag.

## Evidencia

- Código con el alias de listas.
- Claves efectivas idénticas.
- Texto claro recuperado y flag redactada.

## Lecciones aprendidas

- `[[x] * n] * m` comparte la lista interna.
- Una clave compartida en CTR es un fallo crítico.
- El texto conocido convierte un cifrado en un XOR recuperable.

## Mitigaciones y detección

- Generar claves independientes con `os.urandom(16)` por mensaje.
- Usar AES-GCM o ChaCha20-Poly1305 con nonce único.
- Revisar tests que comparen claves y nonces.
- Referencias: NIST SP 800-38A, PyCryptodome, HTB Initialization.

## Referencias

- <https://www.hackthebox.com/challenges/Initialization>
- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/initialization/>
- <https://csrc.nist.gov/pubs/sp/800/38/a/final>
- <https://attack.mitre.org/techniques/T1556/>
