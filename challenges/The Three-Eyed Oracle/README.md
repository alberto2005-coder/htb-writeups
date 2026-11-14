---
challenge: The Three-Eyed Oracle
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, aes, ecb, oracle, byte-at-a-time]
---

# The Three-Eyed Oracle — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un oráculo cifra `input || flag` en AES-ECB con una clave fija. Al elegir el prefijo se alinea cada byte desconocido con el final de un bloque y se compara con un diccionario de 256 candidatos. Es un ataque byte-at-a-time.

## Enunciado y superficie

- Crypto, Easy, retirado.
- Se conecta a un servicio que devuelve el cifrado en hexadecimal.
- No se entrega la clave.

## Reconocimiento

```bash
nc <IP> <PORT>
```

- Cada entrada devuelve un bloque cifrado.
- El mismo prefijo produce el mismo bloque: ECB.
- La longitud crece en bloques de 16.

## Análisis del código

El servicio calcula `AES-ECB(key, user_input + flag)`. ECB cifra cada bloque de 16 bytes por separado, así que bloques iguales producen ciphertext igual. No hay IV ni padding aleatorio.

## Explicación del fallo

Se envía un prefijo de 15 bytes para que el primer byte de la flag caiga al final del bloque. El oráculo devuelve el bloque; se prueba cada byte posible como último byte del prefijo y se compara. Con el byte recuperado se reduce el prefijo y se repite.

## Reproducción local

```python
def oracle(prefix):
    return encrypt(prefix + flag)

known = b''
for i in range(len(flag)):
    pad = b'A' * (15 - len(known) % 16)
    target = oracle(pad)[:16]
    for c in range(256):
        if oracle(pad + known + bytes([c]))[:16] == target:
            known += bytes([c])
            break
```

## Explotación

```bash
python solve.py --host <IP> --port <PORT>
```

El script imprime la flag; se redacta.

## Evidencia

- Bloques repetidos con el mismo prefijo.
- Longitud en múltiplos de 16.
- Byte recuperado por comparación.

## Lecciones aprendidas

- ECB filtra la estructura del texto claro.
- Un oráculo de cifrado permite ataques de recuperación byte a byte.
- Un prefijo controlable rompe la confidencialidad.

## Mitigaciones y detección

- Usar AES-GCM o CBC con IV aleatorio y MAC.
- No concatenar entrada del usuario con secretos.
- Rate-limit y monitorizar patrones de consulta repetidos.

## Referencias

- <https://www.hackthebox.com/challenges/The%20Three-Eyed%20Oracle>
- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/the-three-eyed-oracle/>
- <https://cryptopals.com/sets/2/challenges/12>
