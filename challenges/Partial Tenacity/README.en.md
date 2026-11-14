---
challenge: Partial Tenacity
type: Crypto
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [crypto, rsa, partial-key, factorization, python]
---

# Partial Tenacity — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides an RSA key with known bits of `p` and `q` plus an encrypted message. Unknown bits are recovered with a search guided by `n = p*q`, and the resulting private key decrypts the message.

## Prompt and surface

- Crypto, Medium, retired.
- `n`, `e`, `c` and a partial representation of the primes are provided.
- The goal is to recover the plaintext.

## Reconnaissance

```bash
python3 - <<'PY'
from Crypto.PublicKey import RSA
# Load n, e and c from the challenge file
PY
```

- `n` has a normal RSA size.
- A percentage of `p` and `q` bits is known.
- There is no remote service: the attack is offline.

## Analysis

Known bits are aligned from the least significant bit. At each position, try the bit combinations for `p` and `q` that make the product match `n` at that position. The search is pruned because only a few combinations survive.

```python
# pseudocode: grow p and q from the LSB
for bit in range(known_bits):
    for dp in (0, 1):
        for dq in (0, 1):
            if ((p + dp) * (q + dq)) % (1 << (bit + 1)) == n % (1 << (bit + 1)):
                # keep the branch
                ...
```

## Exploitation

Implement the search, rebuild `p` and `q`, compute `d = e^{-1} mod φ(n)` and decrypt `c`. Verify `p*q == n` before using the key.

```python
from Crypto.Util.number import long_to_bytes, inverse
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
print(long_to_bytes(pow(c, d, n)))
```

## Evidence

- Recovered factors that multiply exactly to `n`.
- Valid private key.
- Decrypted message with readable format.

## Lessons

- RSA is not safe when enough prime bits leak.
- The modular relation prunes the search bit by bit.
- Validating `p*q == n` rejects false branches.
- The attack is offline and independent of the network.

## Mitigations and detection

- Never expose prime bits or intermediate values.
- Rotate keys after any partial leak.
- Use libraries that generate primes with sufficient entropy.
- Review challenges and systems that publish key metadata.
- References: RSA partial key exposure, Boneh.

## References

- <https://www.hackthebox.com/challenges/Partial%20Tenacity>
- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)>
- <https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf>
- <https://attack.mitre.org/techniques/T1556/>
