---
challenge: xorxorxor
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, xor, known-plaintext]
---

# xorxorxor — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

The cipher is a **XOR** of the message with a short repeating key. Since the text starts with `HTB{`, the first key bytes fall out directly; with those the rest decrypts and the output is checked for printable text. No brute force.

## Evidence

- `challenge.py` (the cipher) and `output.txt` (hex ciphertext).

## Method

1. **Read the script**: `bytes([a ^ b for a, b in zip(flag, key)])`, with `key` shorter than the flag and repeated.

2. **Recover the key** from the known prefix:

```python
ct = bytes.fromhex(open("output.txt").read().strip())
known = b"HTB{"
key = bytes(c ^ p for c, p in zip(ct, known))
print(key)          # start of the key
```

3. **Extend the key**: repeat it to match the ciphertext and decrypt everything.

```python
pt = bytes(c ^ key[i % len(key)] for i, c in enumerate(ct))
print(pt)
```

4. **Validate**: the text must be printable ASCII and end in `}`.

## Pitfalls

- **Key length**: if the recovered key looks wrong, try lengths 1-8 and keep whichever yields readable text.
- **Hex with newlines**: clean the file before `fromhex`.
- **Mistaking it for a one-time pad**: here the key repeats, which is precisely why it breaks.

## Lessons

- Repeating-key XOR is binary Vigenère: known plaintext defeats it.
- The flag format is public information, and enough to start.
- A cipher that is nothing but XOR provides no confidentiality.
