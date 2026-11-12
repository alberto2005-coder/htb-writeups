---
challenge: Lost Modulus
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, cube-root, gmpy2]
---

# Lost Modulus — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flag.

## TL;DR

The script encrypts the flag with RSA and `e = 3`, but does not provide the modulus `n`. Because the message is short, `m^3 < n` and encryption never wraps modulo `n`; an exact integer cube root of the ciphertext recovers the message.

## Brief and surface

- Crypto, Very Easy, retired.
- An encryption script and a hexadecimal ciphertext are provided.
- The modulus `n` is not published: hence the name.

```bash
file challenge.py
python3 challenge.py
```

## Recon

The code generates two 512-bit primes, uses `e = 3` and computes `c = m^3 mod n`. It never prints `n`. The ciphertext is a large integer.

```python
ct = int(ciphertext, 16)
```

## Source analysis

The flaw is the low exponent combined with a short message. If `m^3 < n`, the `mod n` operation does not change the result and `c` is a perfect cube. The integer cube root returns the message without `p`, `q` or `d`.

```text
c = m^3
m = integer_cube_root(c)
```

## The bug

Textbook RSA is deterministic and malleable. With `e = 3` and a message of a few bytes, the attacker can test whether `c` is a perfect cube. If it is, the exact root reveals `m`.

## Local reproduction

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install gmpy2
```

```python
import gmpy2
from Crypto.Util.number import long_to_bytes

c = int(open('ciphertext.txt').read().strip(), 16)
m, exact = gmpy2.iroot(c, 3)
if exact:
    print(long_to_bytes(int(m)))
```

`iroot` returns `(root, True)` when the cube is exact. If `exact` is false, the message is larger than `n` and this attack does not apply.

## Exploitation

There is no server. Exploitation is mathematical: compute the root and decode. The correct output matches HTB's flag format; verify it on the platform and redact it.

## Evidence

- Script with `e = 3` and no `n`.
- `gmpy2.iroot(c, 3)` with `exact = True`.
- Decoded bytes with the flag redacted.

## Lessons learned

- Textbook RSA with a low exponent and a short message breaks without factorisation.
- `e = 3` is not insecure by itself; the lack of padding is.
- Testing for a perfect cube is cheap.
- `gmpy2.iroot` is the right tool for large integer roots.

## Mitigations and detection

- Use RSA-OAEP or a hybrid scheme with random padding.
- Do not use `e = 3` with short messages and no padding.
- Validate lengths and reject ciphertexts that are perfect powers.
- In CTFs, document message size and exponent.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/lost-modulus/>
- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)#Attacks_against_plain_RSA>
- <https://pypi.org/project/gmpy2/>
