---
topic: AES ECB
tags: [crypto, aes, ecb, block-cipher, pattern-leak, padding]
---

# AES ECB

**English** | [🇪🇸 Español](aes-ecb.md)

## Concept

AES-ECB encrypts each 16-byte block independently. Equal blocks produce the same ciphertext, so the mode leaks patterns and structure. It is not a secure choice for data with repetition, although it appears in apps and legacy protocols.

## When it applies

- Ciphertext with repeated blocks.
- A key embedded in an app or configuration.
- Data with predictable fields.
- Comparing messages of equal length.

## Procedure

1. Identify the algorithm and mode.
2. Split the ciphertext into 16-byte blocks.
3. Look for identical blocks.
4. Compare ciphertexts of controlled messages.
5. Recover the key if embedded and decrypt.

```bash
python3 - <<'PY'
from collections import Counter
c = bytes.fromhex('<CIPHERTEXT>')
blocks = [c[i:i+16] for i in range(0, len(c), 16)]
print(Counter(blocks).most_common(5))
PY
openssl enc -d -aes-128-ecb -K <KEY> -in data.bin
```

## Variants

- ECB with a 128-bit or 256-bit key.
- Data compressed before encryption.
- Block encryption with a fixed IV.
- A key derived from a weak password.

## Limitations

- ECB alone does not recover the key.
- Repetition depends on the data.
- Padding can hide the last block.
- A random key and unique data reduce the leak.

## Mitigation and detection

- Use AES-GCM or CBC with a random IV and MAC.
- Do not encrypt structured data with ECB.
- Protect and rotate keys.
- Review legacy configurations and libraries.

## References

- <https://csrc.nist.gov/publications/detail/sp/800-38a/final>
- <https://owasp.org/www-project-cryptographic-storage-cheat-sheet/>
- <https://attack.mitre.org/techniques/T1573/>
