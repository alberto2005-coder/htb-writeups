---
challenge: Perfect Synchronization
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, substitution, frequency-analysis, custom-cipher]
type: Crypto
---

# Perfect Synchronization — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; the flag is not published.

## Brief

You get a ciphertext and the code fragment that produced it. There is no AES to break: you have to understand what the script actually did.

## What the cipher does

The script takes **each character on its own**, adds a **salt of 15** and writes the result:

```python
salt = 15
encrypted = ''.join(chr(ord(c) + salt) for c in text)
```

That is a **per-character substitution**: every plaintext letter always becomes the same ciphertext letter. No blocks, no key, no ECB: the "perfect synchronization" in the name is the flaw itself.

```python
# decrypt
plain = ''.join(chr(ord(c) - 15) for c in encrypted)
```

## Solving it

1. Apply the inverse shift — if the salt is known, the challenge ends here.
2. If the salt were not given, the simple substitution structure allows **frequency analysis**: the most repeated ciphertext letters map to the language's own (`e`, `a`, `o` in Spanish; `e`, `t`, `a` in English).
3. For short texts with many known words, the repetition pattern falls to **quipqiup** or a cryptogram solver.

```bash
python3 - <<'PY'
ct = open('ciphertext.txt').read().strip()
print(''.join(chr(ord(c) - 15) for c in ct))
PY
```

## Findings

- This is not encryption: it is a **monoalphabetic shift/substitution** dressed up as a modern scheme.
- The challenge name describes the flaw: each character transforms identically, so the pattern survives.
- With the salt in sight no cryptanalysis is needed; without it, frequencies and patterns suffice.

## Lessons

- Reading the cipher's code saves hours of assuming AES/ECB.
- Repeating a per-character transform preserves the language's structure.
- A fixed, public salt adds no security at all.
- Mitigation: real authenticated encryption (AES-GCM) with a secret key and a unique nonce; never "add a number" per character.
