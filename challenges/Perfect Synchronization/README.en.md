---
challenge: Perfect Synchronization
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, aes, ecb, frequency-analysis]
---

# Perfect Synchronization — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

Several messages sharing a template are encrypted with **AES** in **ECB** mode. ECB encrypts each 16-byte block independently, with no chaining: identical blocks produce identical ciphertext. With enough messages the plaintext is rebuilt by block-level **frequency analysis**, without the key.

## Evidence

- `source.py` (the cipher) and `output.txt` (a list of hex ciphertexts).

## Method

1. **Confirm ECB**: the same 16-byte block in equivalent positions → the same ciphertext across messages.

```python
from collections import Counter
blocks = [c[i:i+16] for c in ct_list for i in range(0, len(c), 16)]
Counter(blocks).most_common(5)
```

2. **Align the template**: messages share structure; each block position maps to a field (greeting, name, closing).

3. **Frequency**: at each position the most repeated block is the most common character or word of the language/template; test hypotheses (`' '`, frequent letters, known header words).

4. **Iterate**: replace blocks with their value and check the text reads coherently; the messages "synchronise" and the plaintext emerges.

## Pitfalls

- **Padding**: the last blocks carry PKCS#7 padding; ignore them when comparing.
- **Encoding**: work in bytes, not `str`, or 16-byte blocks break.
- **Confusing it with CBC**: in CBC the same block changes with the IV and predecessor; no repeats means not ECB.

## Lessons

- ECB leaks structure: the one mode never to use on patterned data.
- Block frequency turns a "strong" cipher into a solvable cryptogram.
- AES-CBC, or better AES-GCM with a unique nonce, avoids the problem.
