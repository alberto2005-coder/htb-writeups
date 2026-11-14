---
challenge: Tsayaki
type: Crypto
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [crypto, aes, ctr, nonce-reuse, xor]
---

# Tsayaki — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The service encrypts messages with AES-CTR and reuses the nonce across sessions. Repeating the keystream lets two ciphertexts reveal the XOR of their plaintexts; the known format of one recovers the other and the flag.

## Prompt and surface

- Crypto, Hard, retired.
- A remote service returns encrypted messages with a fixed format.
- The goal is to decrypt the secret.

```bash
nc <IP> <PORT>
```

## Reconnaissance

- Each connection returns a `nonce`, a ciphertext and a length.
- The service lets the user choose part of the message.
- The nonce repeats between queries.

## Analysis

In CTR, `C = P XOR KS`. With the same nonce and key, `KS` is identical. For two ciphertexts:

```text
C1 XOR C2 = P1 XOR P2
```

If `P1` is known or has a predictable format, `P2` follows. The challenge requires aligning messages and handling padding or length.

```python
from pwn import xor
print(xor(c1, c2))
```

## Exploitation

Collect two ciphertexts with the same nonce, compute the XOR and rebuild the message using the known format. Validate the flag locally and do not publish it.

```python
known = b'...'
stream = xor(c1, known)
print(xor(c2, stream))
```

## Evidence

- Repeated nonce in two responses.
- Ciphertext XOR with readable text.
- Recovered and validated flag.

## Lessons

- CTR is a stream cipher: nonce reuse breaks confidentiality.
- XOR of two plaintexts reveals patterns and structure.
- A known format turns the XOR into a full decryption.
- The nonce must be unique per message and key.

## Mitigations and detection

- Use a unique random nonce or a non-repeating counter.
- Rotate keys and use AEAD.
- Test the service with known messages to detect repetition.
- Review implementations that reuse the same IV.
- References: NIST SP 800-38A, AES-CTR nonce reuse.

## References

- <https://www.hackthebox.com/challenges/Tsayaki>
- <https://csrc.nist.gov/pubs/sp/800/38/a/final>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)>
- <https://attack.mitre.org/techniques/T1556/>
