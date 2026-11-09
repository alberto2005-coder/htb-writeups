---
challenge: Dynastic
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, classical, caesar, trithemius, reverse-engineering]
---

# Dynastic — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A classical cipher with a **progressive shift**: each letter moves one position further than the previous one (Trithemius, an incremental Caesar). Invert the same loop and the plaintext falls out.

## Brief

A short script and the ciphertext are provided. It maps each character to an index (`ord(c) - 0x41`), adds a growing shift, and maps back modulo 26.

```python
def to_identity_map(a):
    return ord(a) - 0x41

def from_identity_map(a):
    return chr(a % 26 + 0x41)

def encrypt(m):
    c = ''
    for i in range(len(m)):
        ch = m[i]
        if not ch.isalpha():
            ech = ch
        else:
            chi = to_identity_map(ch)
            ech = from_identity_map(chi + i)
        c += ech
    return c
```

## Analysis

Three details solve it:

1. **Letters only**: non-alphabetic characters pass through, so the `{}` and underscores survive as anchors.
2. **Shift = index**: the first letter does not move, the second moves one, the third two…
3. **Modulo 26**: plain Caesar arithmetic, no text-dependent substitution.

So decryption subtracts instead of adding.

## Exploitation

```python
def decrypt(c):
    m = ''
    for i in range(len(c)):
        ch = c[i]
        if not ch.isalpha():
            mch = ch
        else:
            chi = to_identity_map(ch)
            mch = from_identity_map(chi - i)
        m += mch
    return m
```

If the ciphertext starts with `HTB{`, the check is immediate: `H` did not move, `T` moved 1, `B` moved 2. Validate those three letters before running the whole loop.

Without code: CyberChef's brute-force ROT, or recognise the increasing-shift pattern as Trithemius by eye.

## Pitfalls

- **Case**: the script assumes `A-Z`. For lowercase, adjust the base (`0x61`) and the modulo.
- **Sign**: subtract the index; adding it again returns the ciphertext.
- **Negative indices**: Python's `% 26` is already positive, other languages need a fix.
- **Not Vigenère**: there is no key, only position.

## Lessons

- Recognising the cipher family beats writing brute force: increasing shift means Trithemius.
- When the invertible encryption script is handed over, the challenge is reading it, not guessing.
- Mitigation (real world): classical ciphers are not encryption; use AES-GCM with a unique nonce.
