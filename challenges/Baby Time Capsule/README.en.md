---
challenge: Baby Time Capsule
category: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, hastad, crt, small-exponent]
---

# Baby Time Capsule — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

`server.py` encrypts **the same flag** with RSA and `e = 5`, generating a fresh 1024-bit modulus on every query. With five ciphertexts under coprime moduli, the Chinese Remainder Theorem recovers `m^5` **without modular reduction**, and an integer fifth root returns the message: Håstad's broadcast attack. No factoring involved.

## Statement and surface

A remote service hands out "time capsules": each request returns a new ciphertext and public key. Category Crypto, difficulty Very Easy.

## Recon

```python
from pwn import remote
io = remote("<HOST>", <PORT>)
# answer 'Y' five times and keep (ct_i, n_i)
```

## Code analysis

```python
self.e = 5
m = bytes_to_long(self.msg)
m = pow(m, e, n)
```

Fixed small exponent, same message, a different `n` per query: exactly Håstad's setting.

## Root cause

With `e = 5` and five coprime moduli, `c_i = m^5 (mod n_i)`. CRT yields a unique `C < prod(n_i)` with `C = m^5`; since `m^5 < prod(n_i)` for a short flag, `C` equals `m^5` and the exact fifth root reveals it with no private key.

## Local reproduction

```python
from sympy.ntheory.modular import crt
from gmpy2 import iroot
from Crypto.Util.number import long_to_bytes

M = crt(ns, cts)[0]
m, exact = iroot(M, 5)
print(exact, long_to_bytes(int(m)))
```

## Exploitation

1. Request five capsules (five distinct `n`, same `e = 5`).
2. Combine with CRT to get `m^5` over the integers.
3. `iroot(M, 5)`; if `exact` is `True`, that is the message.

## Evidence

- `server.py` with `e = 5` and a new modulus per query.
- The five `(n, ct)` pairs and the rebuilt `C`.

## Lessons

- **Small `e`, same message, different moduli** is Håstad, not factoring.
- **CRT turns congruences into an integer equality** once the product of moduli exceeds `m^e`.
- **Check `exact` from `iroot`** so you do not accept a truncated root.

## Mitigations and detection

- Use a standard `e` (65537) and **randomised padding** (OAEP) so the same message encrypts differently.
- Never reuse a message across keys; key rotation is not a substitute for padding.

## References

- [block-ciphers](../../knowledge/crypto/block-ciphers.md)
- Håstad, *Solving simultaneous modular equations of low degree* (1988).
