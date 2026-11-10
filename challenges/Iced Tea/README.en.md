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

You are given the **encryption code** (a **TEA**, Tiny Encryption Algorithm, implementation), the key in hex and the ciphertext. There is no vulnerability to break: you must **implement the inverse**. The traps are *endianness*, mod-2³² arithmetic and the final `unpad`.

## Brief

`crypto_iced_tea.zip` with `source.py` and `output.txt`:

```text
Key : <32 hex chars = 16 bytes>
Ciphertext : <hex, a multiple of 8 bytes>
```

`source.py` defines `class Cipher` with `BLOCK_SIZE = 64`, a `Mode(ECB, CBC)` enum, `encrypt_block`/`decrypt_block` and `DELTA = 0x9e3779b9`; it **only implements encryption**.

## Recon

```bash
unzip crypto_iced_tea.zip && cat source.py
python3 -c "print(int('9e3779b9',16))"
```

## The flaw

TEA works on 64-bit blocks split into two 32-bit words (`v0`, `v1`), a 128-bit key in four words (`k0..k3`) and **32 rounds**. Encryption adds `DELTA` and mixes with `<<4`, `>>5` and XOR; decryption mirrors it, **subtracting** `DELTA`.

Nothing secret needs recovering: the key is in the prompt. The challenge tests inverting a primitive and respecting the format.

## Exploitation

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

key = [unpack(">I", bytes.fromhex(h))[0] for h in [c0, c1, c2, c3]]  # 4 words
ct = bytes.fromhex("<ciphertext>")
pt = b"".join(decrypt_block(ct[i:i+8], key) for i in range(0, len(ct), 8))
print(unpad(pt, 8))
```

Details that ruin the result if ignored:

- **32-bit mask** on every operation (`& 0xffffffff`).
- **`s` decrements after** each round, starting at `DELTA*32`.
- **Key order**: the same one the encryptor uses when splitting the key.
- **Mode**: if `output.txt` came from CBC, XOR with the previous block (or the IV) while decrypting.

```text
HTB{...T1ny_3ncrypt10n_4lg0r1thm...}
```

## Evidence

- Trimmed output of the key commands; no real flags.
- Real values live in `private/` and are not published.

## Lessons

- **`>2I` vs `<2I`**: endianness is mistake number one; odd characters mean try the other.
- **`unpad` fails** when the mode is CBC but you decrypt as ECB.
- **Key in the source** turns this into an implementation exercise, not cryptanalysis.

- TEA has a 64-bit block and 128-bit key with known weaknesses (equivalent keys, related-key): never production-grade.
- Reproducing a primitive's inverse is a core applied-crypto skill.
- Mitigation: AES-GCM or ChaCha20-Poly1305; never TEA/XTEA in real systems.
