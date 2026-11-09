---
challenge: Primary Knowledge
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, small-modulus, euler-phi, textbook-rsa]
---

# Primary Knowledge — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

Broken RSA: the modulus `n` **is prime**. Therefore `φ(n) = n − 1`, the private key needs no factorisation, and the message decrypts in two lines. The challenge name is the hint: if `n` is prime, there are no two primes to find.

## Brief

```python
from Crypto.Util.number import getPrime, bytes_to_long
from secret import FLAG

n = getPrime(1024)          # a single prime, not a product
e = 0x10001
c = pow(bytes_to_long(FLAG), e, n)
print(f'n = {n}')
print(f'e = {e}')
print(f'c = {c}')
```

## Analysis

Normal RSA has `n = p·q` and `φ(n) = (p−1)(q−1)`. Here only one prime was generated, so:

- `φ(n) = n − 1`
- `d = e⁻¹ mod (n − 1)`
- `m = cᵈ mod n`

No factorisation, no Coppersmith: plain algebra.

## Exploitation

```python
from Crypto.Util.number import long_to_bytes

n = <n>
e = <e>
c = <c>

d = pow(e, -1, n - 1)
m = pow(c, d, n)
print(long_to_bytes(m).decode())
```

`pow(e, -1, m)` exists since Python 3.8; on older versions use `inverse()` from `Crypto.Util.number` or extended Euclid.

Check: `e*d % (n-1) == 1`, and the output must start with `HTB{`.

## Pitfalls

- **Mixing up φ and n**: use `n − 1`, not `n`.
- **Negative `d`**: `pow(e, -1, m)` normalises it; hand-rolled Euclid needs adding `m` until positive.
- **`long_to_bytes`**: if leading nulls appear, strip nulls only, not spaces.
- **1024-bit `n`**: the challenge does not ask for factorisation; trying wastes time.

## Lessons

- RSA security depends on `n` being the product of two large distinct primes.
- If `n` is prime, `φ(n)` is public by definition: anyone can invert the encryption.
- Mitigation: generate keys with vetted libraries (`cryptography`, OpenSSL) and assert `n = p·q` with `p ≠ q`.
