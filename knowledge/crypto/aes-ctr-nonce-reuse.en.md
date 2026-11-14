---
topic: Reutilización de nonce en AES-CTR
tags: [crypto, aes, ctr, nonce, xor, keystream]
---

# AES-CTR Nonce Reuse

**English** | [🇪🇸 Español](aes-ctr-nonce-reuse.md)

## Concept

AES-CTR generates a keystream from key and nonce. If the nonce repeats, the same keystream encrypts multiple messages; XORing two ciphertexts removes the keystream and reveals the XOR of the plaintexts.

## When it applies

- Services returning a `nonce` and ciphertext.
- Implementations using a fixed IV.
- Challenges with known message formats.

## Procedure

1. Collect two ciphertexts with the same nonce.
2. Compute `C1 XOR C2`.
3. Use the format or known text to separate `P1 XOR P2`.
4. Recover the keystream and decrypt the rest.
5. Validate the flag.

```python
from pwn import xor
x = xor(c1, c2)
stream = xor(c1, known_plaintext)
plaintext = xor(c2, stream)
```

## Variants

- Predictable rather than repeated nonce.
- Stream cipher with a resetting counter.
- Dictionary attack on short messages.

## Limitations

- Unique nonces prevent direct XOR.
- Different lengths require alignment.
- The format must be sufficiently known.

## Mitigation

- Unique random nonce per message and key.
- Non-repeating counter; key rotation.
- Use AEAD (GCM/ChaCha20-Poly1305).

## Detection

- Repeated nonces in responses.
- Identical ciphertext prefixes.
- Tests with controlled messages.

## References

- <https://csrc.nist.gov/pubs/sp/800/38/a/final>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)>
- <https://attack.mitre.org/techniques/T1556/>
