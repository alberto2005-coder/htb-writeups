---
title: Block ciphers and custom ciphers (ECB, TEA, affine)
tags: [crypto, aes, ecb, tea, ctf]
---

# Block ciphers and custom ciphers

**English** | [🇪🇸 Español](block-ciphers.md)

## 1. Recognise the cipher

- **AES-ECB**: 16-byte blocks; the same plaintext block yields the same ciphertext block. Detect it by repetitions.
- **TEA/XTEA**: 8-byte blocks, constant `delta = 0x9E3779B9`, 32 rounds by default.
- **Custom cipher**: a linear function or a byte permutation; invert it by reading the code.

Start with size and patterns:

```bash
wc -c cipher.bin
python3 -c "d=open('cipher.bin','rb').read(); print(len(d), len(d)%16, len(d)%8)"
```

## 2. AES-ECB

Detect repeated blocks:

```python
from collections import Counter
d = open('cipher.bin','rb').read()
blocks = [d[i:i+16] for i in range(0, len(d), 16)]
print(Counter(blocks).most_common(3))
```

With known plaintext (challenges usually ship a clear `sample`), align blocks and compare: each 16-byte block is attacked separately. For a *byte-at-a-time* oracle, pad with `A` until the target byte lands at the end of a block and compare against a 256-entry dictionary.

```bash
openssl enc -d -aes-128-ecb -K <hex_key> -in cipher.bin
```

## 3. TEA

Reference decryption:

```python
def tea_decrypt(v, k):
    v0, v1 = v
    delta = 0x9E3779B9
    s = (delta * 32) & 0xFFFFFFFF
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & 0xFFFFFFFF
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & 0xFFFFFFFF
        s = (s - delta) & 0xFFFFFFFF
    return v0, v1
```

Mind the **half order** and the `& 0xFFFFFFFF` on every operation: without the mask Python grows unbounded and the result diverges. If the challenge uses a variant (XTEA, different round count), the `delta` and loop give it away.

## 4. Custom and classical ciphers

- **Affine mod 256**: `c = (a*m + b) % 256`; invert with `pow(a, -1, 256)` when `gcd(a,256)=1`.
- **Block permutation**: invert the permutation from the code; for 3-byte blocks, rebuild in order.
- **Caesar/Trithemius**: the shift may be the character index (`+i`), not a constant. Try both.

```python
pt = bytes((c - b) * pow(a, -1, 256) % 256 for c in ct)
```

## 5. Typical errors

- **ECB "invisible"** → short text or padding breaks alignment; shift by one byte and retry.
- **TEA returns garbage** → key or half endianness, or a round count other than 32.
- **`pow(a, -1, 256)` fails** → `a` is even; the cipher is not invertible mod 256, re-read the code.
- **Decryption "almost" works** → a single byte off usually means a mod-256 subtraction applied wrongly.

## 6. Detection and mitigation (real world)

- ECB leaks patterns: use CBC/GCM with a random IV and authentication.
- Home-made ciphers with no analysis are the most common flaw in CTFs and in real products.
- TEA is obsolete; XTEA/XXTEA are not recommended for new designs either.
- Document mode and padding: half of "crypto flaws" are implementation bugs.

MITRE: T1600.
