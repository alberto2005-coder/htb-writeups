---
topic: Classical ciphers — Vigenère and frequency analysis
tags: [crypto, vigenere, substitution, frequency-analysis]
---

# Classical ciphers — Vigenère and frequency analysis

[🌐 Español](classical-ciphers.md) | **English**

## Concept

Classical ciphers do not resist frequency analysis or known plaintext. For Vigenère, estimate the key length with Kasiski or the index of coincidence, split the text into columns and solve each Caesar shift.

## When it applies

- Challenges with alphabetic ciphertext.
- Passwords or notes obfuscated with Vigenère.
- Short keys or predictable plaintext.

## Procedure

1. Identify the alphabet and remove separators.
2. Estimate the key length with Kasiski or IC.
3. Split the text into columns.
4. Solve each column as a Caesar shift.
5. Test the key and validate the plaintext.

## Commands

```python
from collections import Counter
c = '...'
for shift in range(26):
    p = ''.join(chr((ord(x)-65-shift) % 26 + 65) for x in c)
    print(shift, p[:60])
```

## Variants

- Monoalphabetic substitution with frequency analysis.
- Caesar with a known shift.
- Single-byte XOR and plaintext cribbing.

## Limitations

- Long keys and short text hinder the attack.
- Mixed alphabets complicate analysis.
- Known language or format may be required.

## Mitigation

- Use modern authenticated cryptography.
- Do not use classical ciphers for secrets.
- Rotate keys and avoid reuse.

## Detection

- Text with an anomalous letter distribution.
- Strings resembling keys or shifted alphabets.

## References

- <https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher>
- <https://attack.mitre.org/techniques/T1140/>
