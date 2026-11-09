---
challenge: Iced Tea
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, tea, block-cipher, decryption]
---

# Iced Tea — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

Blocks encrypted with **TEA** (Tiny Encryption Algorithm) and the key included in the code. There is no vulnerability: it is about implementing the standard decryption. The traps are integer packing and *endianness*.

## Brief

The encryption script ships with `key` and two 64-bit blocks in hex. TEA uses 32 rounds, the constant `delta = 0x9e3779b9`, and a 128-bit key split into four 32-bit words.

## Analysis

Encryption adds `delta` and mixes `v0`/`v1` with shifts; decryption does the same in reverse, subtracting `delta`:

```python
def decrypt(v, k):
    v0, v1 = v
    delta = 0x9e3779b9
    s = (delta * 32) & 0xffffffff
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & 0xffffffff
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & 0xffffffff
        s = (s - delta) & 0xffffffff
    return v0, v1
```

Details that break it if ignored:

- All sums are **modulo 2³²**: mask with `& 0xffffffff`.
- `s` decrements **after** each round.
- `k` is four 32-bit integers, not the key as bytes.

## Exploitation

```python
from struct import pack, unpack

key = [<k0>, <k1>, <k2>, <k3>]

for block in [<block1>, <block2>]:
    v = unpack('>2I', bytes.fromhex(block))
    d = decrypt(v, key)
    print(pack('>2I', *d).decode(errors='ignore'), end='')
```

If the text comes out garbled, try `<2I` instead of `>2I`: block endianness is the most common mistake.

Check: the concatenated result must start with the flag prefix.

## Pitfalls

- **Endianness**: `struct.unpack('>2I')` for big-endian; the encryption script usually uses the format you must invert.
- **32-bit masking**: without `& 0xffffffff` the shifts overflow and decryption yields garbage.
- **Word order**: `k[0..3]` in the encryptor's order; swapping them decrypts nothing.
- **Not AES**: no IV, no mode; each block is independent.

## Lessons

- TEA is a toy cipher: 64-bit blocks, 128-bit key, with known weaknesses (key equivalence, related-key).
- With the key in the code, the challenge is a correct inverse implementation, not breaking anything.
- Mitigation: use AES-GCM or ChaCha20-Poly1305, never TEA/XTEA in production.
