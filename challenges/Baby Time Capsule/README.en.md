---
challenge: Baby Time Capsule
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, small-modulus, factoring]
---

# Baby Time Capsule — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

Three "time capsules": **RSA** triplets `(n, e, ct)` with **small** moduli and the same message. With an `n` of few bits, factoring is trivial (Factordb or `sympy.factorint`), then `φ(n)` and `d` follow and the message decrypts. The cipher is fine; the key size is not.

## Evidence

- `source.py` and `output.txt` with the triplets.

## Method

1. **Look at the numbers**: under ~256 bits, `n` is broken by design.

```python
for n, e, ct in capsules:
    print(n.bit_length(), e)
```

2. **Factor** `n = p * q`:

```bash
# paste n into factordb.com
python -c "from sympy import factorint; print(factorint(n))"
```

3. **Private key**:

```python
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(ct, d, n)
print(m.to_bytes((m.bit_length() + 7)//8, 'big'))
```

4. **Check** the message starts with `HTB{`.

## Pitfalls

- **Small `e` with small `m`**: if `m^e < n`, no decryption is needed — the integer `e`-th root is the message.
- **Bytes vs integer**: use `long_to_bytes`, never `str()`.
- **`pow(..., -1, ...)`**: needs Python 3.8+; otherwise `sympy.invert`.

## Lessons

- RSA security comes from the size and quality of `n`, not the algorithm.
- A factorable modulus voids all security, however clean the code.
- `e=3` with short messages is the other classic: without padding, one root breaks it.
