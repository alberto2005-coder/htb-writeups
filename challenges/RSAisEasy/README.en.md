---
challenge: RSAisEasy
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, gcd, shared-prime, modular-arithmetic]
---

# RSAisEasy — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides two RSA moduli and two ciphertexts encrypted with the same exponent. The moduli are not coprime: a `gcd` recovers a shared factor, factoring both and decrypting the two flag blocks.

## Brief and surface

- Crypto, Easy, retired.
- `RSAisEasy.py` and `output.txt` are provided.
- `output.txt` contains `n1`, `n2`, `e`, `c1`, `c2`.

```bash
cat output.txt
```

## Recon

Read the script: it generates two RSA keys and encrypts two parts of the flag. The exponent is small and the moduli are built from related primes.

```python
from math import gcd
p = gcd(n1, n2)
```

## Analysis

If `p > 1`, both moduli share a prime. Compute:

```python
q1 = n1 // p
q2 = n2 // p
phi1 = (p - 1) * (q1 - 1)
d1 = pow(e, -1, phi1)
m1 = pow(c1, d1, n1)
```

Repeat for `n2` and concatenate the bytes of `m1` and `m2`. If the direct `gcd` is not enough, try a linear combination of the moduli; the principle is the same: a shared factor breaks RSA.

## The bug

RSA relies on `n = p*q` being hard to factor. If two moduli share a prime, `gcd` reveals it in polynomial time and both keys fall. Block encryption adds no security.

## Local reproduction

1. Read `n1`, `n2`, `e`, `c1`, `c2`.
2. Compute `gcd(n1, n2)`.
3. Factor and compute `d` for each modulus.
4. Decrypt and join the blocks.

```bash
python3 solve.py
```

## Evidence

- `gcd` different from 1.
- Factorisation and decryption of both blocks.
- Reconstructed flag, redacted.

## Lessons learned

- RSA breaks if moduli share a factor.
- `gcd` is the first check with multiple moduli.
- Block encryption does not compensate for a weak key.
- Challenge scripts often reveal the prime relation.

## Mitigation and detection

- Generate and audit independent primes.
- Use proven RSA libraries and standard exponents.
- Rotate keys if a shared factor is found.
- In CTFs, check `gcd` across all moduli.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/rsaiseasy/>
- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)>
- <https://en.wikipedia.org/wiki/Greatest_common_divisor>
