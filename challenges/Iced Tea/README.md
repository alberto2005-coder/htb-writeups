---
challenge: Iced Tea
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, tea, cifrado-de-bloque, descifrado]
---

# Iced Tea — Hack The Box

[⚿ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Se entrega el **código que cifra** (una implementación de **TEA**, Tiny Encryption Algorithm), la clave en hexadecimal y el criptograma. No hay vulnerabilidad que romper: hay que **implementar el inverso**. Las trampas son el *endianness*, las sumas módulo 2³² y el `unpad` final.

## Enunciado y superficie

`crypto_iced_tea.zip` con `source.py` y `output.txt`:

```text
Key : <32 hex chars = 16 bytes>
Ciphertext : <hex, múltiplo de 8 bytes>
```

`source.py` define `class Cipher` con `BLOCK_SIZE = 64`, un enum `Mode(ECB, CBC)`, `encrypt_block`/`decrypt_block` y la constante `DELTA = 0x9e3779b9`; **sólo implementa el cifrado**.

## Reconocimiento

```bash
unzip crypto_iced_tea.zip && cat source.py
python3 -c "print(int('9e3779b9',16))"
```

## Explicación del fallo

TEA opera sobre bloques de 64 bits divididos en dos palabras de 32 (`v0`, `v1`), con clave de 128 bits en cuatro palabras (`k0..k3`) y **32 rondas**. El cifrado suma `DELTA` y mezcla con `<<4`, `>>5` y XOR; el descifrado hace lo mismo al revés **restando** `DELTA`.

No hay secreto que recuperar: la clave está en el enunciado. El reto mide si se sabe invertir una primitiva y respetar el formato.

## Explotación

```python
from struct import unpack, pack
from Crypto.Util.Padding import unpad

DELTA = 0x9e3779b9

def decrypt_block(block, k):
    v0, v1 = unpack(">2I", block)
    s = (DELTA * 32) & 0xffffffff
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & 0xffffffff
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & 0xffffffff
        s = (s - DELTA) & 0xffffffff
    return pack(">2I", v0, v1)

key = [unpack(">I", bytes.fromhex(h))[0] for h in [c0, c1, c2, c3]]  # 4 palabras
ct = bytes.fromhex("<ciphertext>")
pt = b"".join(decrypt_block(ct[i:i+8], key) for i in range(0, len(ct), 8))
print(unpad(pt, 8))
```

Detalles que rompen el resultado si se ignoran:

- **Máscara de 32 bits** en cada operación (`& 0xffffffff`).
- **`s` se decrementa después** de cada ronda, empezando en `DELTA*32`.
- **Orden de `k`**: el mismo que usa el cifrador al trocear la clave.
- **Modo**: si el `output.txt` viene de CBC, hay que encadenar el XOR con el bloque anterior (o con el IV) al descifrar.

```text
HTB{...T1ny_3ncrypt10n_4lg0r1thm...}
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags reales.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`>2I` vs `<2I`**: el *endianness* es el error número uno; si el texto sale con caracteres raros, se cambia y se prueba.
- **El `unpad` falla** si el modo es CBC y se descifra como ECB.
- **La clave en el código** convierte el reto en un ejercicio de implementación, no de criptoanálisis.

- TEA tiene 64 bits de bloque y 128 de clave, con debilidades conocidas (claves equivalentes, *related-key*): no es para producción.
- Reproducir el inverso de una primitiva es una habilidad base de criptografía aplicada.
- Mitigación: AES-GCM o ChaCha20-Poly1305; nunca TEA/XTEA en sistemas reales.
