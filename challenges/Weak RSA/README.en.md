---
challenge: Weak RSA
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, wiener, factorization, openssl]
---

# Weak RSA — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flags.
> Reference note based on technical writeups. No keys or ciphertext are published.

## TL;DR

The challenge ships an RSA public key and an encrypted file. The modulus is too small or the private exponent meets **Wiener's attack** conditions, so the private key is recovered from the public one. The private key decrypts `flag.enc`.

## Brief and surface

- Crypto, Very Easy, retired.
- `Weak RSA.zip` contains `key.pub` and `flag.enc`.
- The brief only asks to decrypt the message.

```bash
unzip 'Weak RSA.zip'
file key.pub flag.enc
```

## Recon

```bash
openssl rsa -pubin -in key.pub -text -noout
```

The output shows modulus `n` and public exponent `e`. If `n` is small, factor it; if `e` is huge and `d` is small, use Wiener. `RsaCtfTool` tests several weaknesses:

```bash
python3 RsaCtfTool.py --publickey key.pub --private
```

## Source analysis

There is no source: the flaw is in the cryptographic parameters. RSA is safe only if `n = p·q` is large enough and `d` is not small. A small modulus factors in seconds; a small `d` allows approximating `e/n` with continued fractions.

```text
n = p * q
φ(n) = (p - 1)(q - 1)
d = e^(-1) mod φ(n)
m = c^d mod n
```

## The bug

Wiener proved that if `d < n^(1/4)/3`, `d` appears among the convergents of `e/n`. `RsaCtfTool` implements that check and, if it fails, tries factorisation and common-prime attacks. The weakness is key generation, not the cipher.

## Local reproduction

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install pycryptodome gmpy2
python3 RsaCtfTool.py --publickey key.pub --private --output key.pri
```

For manual factorisation, reconstruct the key with `pow(c, d, n)` or build a PEM with `PyCryptodome`.

## Exploitation

```bash
openssl pkeyutl -decrypt -inkey key.pri -in flag.enc -out flag.txt
```

For raw RSA (no padding), direct Python decryption is more reliable:

```python
from Crypto.Util.number import long_to_bytes
m = pow(c, d, n)
print(long_to_bytes(m))
```

The correct output starts with HTB's flag format; verify it without publishing the value.

## Evidence

- `openssl rsa -pubin -text -noout` with the modulus truncated.
- RsaCtfTool output showing the detected attack.
- `flag.txt` with the flag redacted.

## Lessons learned

- RSA is not "secure" just because it is RSA: modulus size and `d` generation matter.
- `RsaCtfTool` speeds up triage, but understand which attack it applied.
- Raw encryption has no padding; decryption may need `pow` instead of `openssl pkeyutl`.
- Never reuse a weak public key in production.

## Mitigations and detection

- Use at least 2048-bit moduli and a CSPRNG.
- Avoid small `d`; rely on proven libraries (OpenSSL, WebCrypto).
- Rotate keys if a modulus is factorable or `e` is anomalous.
- Detection is preventive: weak-key scanning and minimum-length policy.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/weak-rsa/>
- <https://github.com/RsaCtfTool/RsaCtfTool>
- <https://en.wikipedia.org/wiki/Wiener%27s_attack>
