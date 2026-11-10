---
title: RSA with a small modulus and textbook RSA
tags: [crypto, rsa, factoring, ctf]
---

# RSA: small modulus, prime `n` and low exponent

**English** | [🇪🇸 Español](rsa-small-modulus.md)

## 1. The pattern

RSA becomes breakable when one of its assumptions fails: `n` is too small (factorable in seconds), `n` is prime (φ = n − 1), `e` is 3 and the message is short (exact cube root), or two moduli share a factor (a single `gcd`).

Always start by reading the key:

```bash
openssl rsa -pubin -in key.pub -text -noout
python3 -c "from Crypto.PublicKey import RSA; k=RSA.import_key(open('key.pub').read()); print(k.n.bit_length(), k.e)"
```

Under 1024 bits is a factoring signal.

## 2. Factor `n`

```python
from sympy import factorint
from Crypto.Util.number import long_to_bytes

n = <n>; e = <e>; c = <c>
p, q = list(factorint(n))[:2]
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
print(long_to_bytes(pow(c, d, n)))
```

SymPy's docs are explicit: rho and p−1 pull out ~10-digit factors in seconds and `ecm` factors ~35 digits comfortably; with no small factor, a 60-digit `n` does not budge. For that, use `yafu`, `msieve` or `RsaCtfTool`:

```bash
RsaCtfTool.py --publickey key.pub --uncipherfile flag.enc --private
```

## 3. Special cases

- **`n` is prime** → φ = n − 1 ("Primary Knowledge"):
  ```python
  d = pow(e, -1, n - 1)
  ```
- **`e = 3` and short `m`** → if `m³ < n` the ciphertext never wraps modulo `n` (`c = m³`) and the integer cube root returns the message:
  ```python
  from gmpy2 import iroot
  m, exact = iroot(c, 3)
  ```
- **Two moduli sharing a factor** → `gcd(n1, n2)` factors both.
- **`p` and `q` very close** → Fermat (`n = a² − b²`), implemented in `RsaCtfTool` and most writeups.

## 4. Decrypt and verify

```python
m = pow(c, d, n)
print(m.to_bytes((m.bit_length() + 7)//8, 'big'))
```

If the output is not text, try `long_to_bytes` from `pycryptodome`, check `c`'s endianness, or account for PKCS#1 v1.5 padding that must be stripped.

## 5. Typical errors

- **`ValueError: base is not invertible`** → `e` and φ are not coprime; the challenge uses another exponent or you need Bézout for `d`.
- **`factorint` hangs** → `n` is large; switch tools rather than strategy.
- **Garbage after decrypting** → `c` is hex/bytes misread, or the message was encrypted under another key.
- **`n` is even** → trivial factor 2; check you are not reading another challenge's public key.

## 6. Detection and mitigation (real world)

- NIST SP 800-57: 2048 bits is the minimum until 2030 and 3072 from then on; 1024 is deprecated (RSA-768 was factored in 2009).
- `e = 3` without OAEP padding enables root attacks; always use OAEP.
- Rotate keys on any suspicion of factoring (moduli shared across certificates).
- In CTFs, document the attack and the maths; the value is recognising the broken assumption.

MITRE: T1553 (subvert trust controls), T1600 (weaken encryption).
