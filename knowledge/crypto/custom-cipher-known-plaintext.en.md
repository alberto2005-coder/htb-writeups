---
topic: Homemade ciphers and known-plaintext attacks
tags: [crypto, custom-cipher, known-plaintext, brute-force]
---

# Homemade ciphers and known-plaintext attacks

[🌐 Español](custom-cipher-known-plaintext.md) | **English**

## Concept

A homemade cipher often combines additions, XOR or rotations with a short key. If part of the plaintext or the output format is known, the transformation can be inverted and the key space reduced until the passphrase is recovered.

## When it applies

- A cipher script and ciphertext are available.
- Part of the content is known or guessable.
- The key is a dictionary password.

## Procedure

1. Read the script and express the cipher as an inverse function.
2. Test with known text to validate the implementation.
3. Iterate a wordlist and check whether the result is printable.
4. Use the recovered passphrase on the next system.

```python
def decrypt(data, key):
    out = bytearray()
    for i, b in enumerate(data):
        out.append((b - key[i % len(key)]) % 256)
    return bytes(out)

for key in open("rockyou.txt", "rb").read().splitlines():
    p = decrypt(ciphertext, key)
    if p.startswith(b"<KNOWN>"):
        print(key, p)
        break
```

## Variants

- Repeating-key XOR and frequency analysis.
- Block cipher with a fixed IV.
- Base64 obfuscation plus a constant subtraction.

## Limitations

- Without known plaintext the space may be large.
- A long random key is not dictionary-attackable.
- The output format must be recognizable.

## Mitigation and detection

- Do not design custom ciphers; use AES-GCM or ChaCha20-Poly1305.
- Derive keys with Argon2 or PBKDF2 and a unique salt.
- Do not reuse passwords across volumes and services.

## References

- <https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html>
- <https://en.wikipedia.org/wiki/Known-plaintext_attack>
- <https://attack.mitre.org/techniques/T1552/>
